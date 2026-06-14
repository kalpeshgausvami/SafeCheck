import os
import shutil
import asyncio
import uuid
import logging
from datetime import datetime, timezone
from celery.utils.log import get_task_logger
from sqlalchemy.future import select
from app.workers.celery_app import celery_app
from app.database.session import async_session
from app.models.job import AnalysisJob
from app.models.result import AnalysisResult

# Import pipeline services
from app.services.video_service import VideoService
from app.services.transcription_service import TranscriptionService
from app.services.ocr_service import OCRService
from app.services.llm_service import LLMService
from app.services.factcheck_service import FactCheckService
from app.agents.coordinator import MultiAgentCoordinator

logger = get_task_logger(__name__)

# Directory inside workspace for temporary assets
SCRATCH_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scratch"))

async def run_pipeline_async(job_id: str, reel_url: str):
    job_uuid = uuid.UUID(job_id)
    analysis_dir = os.path.join(SCRATCH_DIR, f"analysis_{job_id}")
    
    # Initialize workspace scratch folder
    os.makedirs(analysis_dir, exist_ok=True)
    
    try:
        async with async_session() as db:
            # 1. Fetch Job
            result = await db.execute(select(AnalysisJob).filter(AnalysisJob.id == job_uuid))
            job = result.scalars().first()
            if not job:
                logger.error(f"Job {job_id} not found.")
                return

            # Transition status
            job.status = "processing"
            job.progress = 10
            job.current_step = "Downloading Reel"
            await db.commit()

        # Step 1: Download Reel
        logger.info(f"[Step 1/10] Downloading Reel: {reel_url}")
        video_path, metadata = VideoService.download_reel(reel_url, analysis_dir)
        
        async with async_session() as db:
            result = await db.execute(select(AnalysisJob).filter(AnalysisJob.id == job_uuid))
            job = result.scalars().first()
            if job:
                job.progress = 30
                job.current_step = "Extracting Audio"
                await db.commit()

        # Step 2: Audio Extraction
        logger.info("[Step 2/10] Extracting audio tracks using FFmpeg")
        audio_path = os.path.join(analysis_dir, "audio.wav")
        VideoService.extract_audio(video_path, audio_path)

        async with async_session() as db:
            result = await db.execute(select(AnalysisJob).filter(AnalysisJob.id == job_uuid))
            job = result.scalars().first()
            if job:
                job.progress = 50
                job.current_step = "Transcribing Speech & Processing OCR"
                await db.commit()

        # Step 3 & 4: Speech Transcription & OCR Extraction (Concurrently)
        logger.info("[Step 3-4/10] Transcribing speech and running video OCR in parallel threads")
        
        transcription_thread = asyncio.to_thread(
            TranscriptionService.transcribe_audio, audio_path, reel_url
        )
        ocr_thread = asyncio.to_thread(
            OCRService.extract_ocr_text, video_path, reel_url
        )
        
        # Gather concurrently
        transcript_res, ocr_res = await asyncio.gather(transcription_thread, ocr_thread)

        async with async_session() as db:
            result = await db.execute(select(AnalysisJob).filter(AnalysisJob.id == job_uuid))
            job = result.scalars().first()
            if job:
                job.progress = 75
                job.current_step = "Building Multi-Modal Context"
                await db.commit()

        # Step 5: Multi-Modal Context Builder
        logger.info("[Step 5/10] Compiling multi-modal context document")
        metadata_str = f"Uploader: {metadata.get('uploader')}, Title: {metadata.get('title')}, Duration: {metadata.get('duration')}s, Views: {metadata.get('views')}, Likes: {metadata.get('likes')}"
        caption_str = f"Caption: {metadata.get('caption')}"
        hashtags_str = f"Hashtags: {', '.join(metadata.get('hashtags', []))}"
        transcript_str = f"Transcript text: {transcript_res['transcript']}"
        
        ocr_lines = [item['text'] for item in ocr_res]
        ocr_str = f"OCR visual text overlays: {'; '.join(ocr_lines)}"

        combined_context = f"[[Reel Metadata]]\n{metadata_str}\n\n[[Caption]]\n{caption_str}\n{hashtags_str}\n\n[[Speech Transcript]]\n{transcript_str}\n\n[[Visual OCR Overlay]]\n{ocr_str}"

        async with async_session() as db:
            result = await db.execute(select(AnalysisJob).filter(AnalysisJob.id == job_uuid))
            job = result.scalars().first()
            if job:
                job.progress = 80
                job.current_step = "Extracting Claims"
                await db.commit()

        # Step 6: Multi-Agent Coordinator fact-check investigation
        agent_coordinator = MultiAgentCoordinator()
        agent_success = False
        agent_report = None
        
        try:
            logger.info("Executing Autonomous Multi-Agent Fact-Checking investigation...")
            agent_report = await agent_coordinator.run_investigation(
                transcript=transcript_res["transcript"],
                ocr_text="; ".join(ocr_lines),
                caption=metadata.get("caption", ""),
                metadata={
                    "title": metadata.get("title"),
                    "uploader": metadata.get("uploader"),
                    "views": metadata.get("views"),
                    "likes": metadata.get("likes"),
                    "duration": metadata.get("duration")
                }
            )
            agent_success = True
            logger.info("Multi-Agent Coordinator completed investigation successfully.")
        except Exception as e_agent:
            logger.error(f"Multi-Agent investigation failed: {str(e_agent)}. Falling back to local ML/GPT-4o pipeline.")

        if agent_success and agent_report:
            # Map claims and sources directly from Multi-Agent report
            flat_sources = agent_report["sources"]
            formatted_claims = agent_report["claims"]
            
            # Map explainability logs & contradictions
            explainability_data = agent_report.get("explainability", {})
            final_segments = transcript_res["segments"] # Keep standard segments

            final_report = {
                "verdict": agent_report["verdict"],
                "confidence": agent_report["confidence"],
                "risk_level": "High" if agent_report["verdict"] == "Likely Misinformation" else "Low" if agent_report["verdict"] == "Likely Genuine" else "Medium",
                "uploader": metadata.get("uploader", "@unknown"),
                "duration": metadata.get("duration", "0:00"),
                "views": metadata.get("views", "0"),
                "likes": metadata.get("likes", "0"),
                "caption_text": metadata.get("caption", ""),
                "transcript": final_segments,
                "ocr_text": ocr_res,
                "claims": formatted_claims,
                "sources": flat_sources,
                "reasoning": agent_report["report"], # Agent report markdown acts as core reasoning
                "explainability": explainability_data
            }
        else:
            # Try calling the local proprietary ML service first
            ml_service_url = os.getenv("ML_SERVICE_URL", "http://ml-service:8080")
            ml_success = False
            ml_report = None
            
            try:
                logger.info(f"Connecting to proprietary ML service: {ml_service_url}")
                import httpx
                async with httpx.AsyncClient(timeout=15.0) as client_ml:
                    resp = await client_ml.post(
                        f"{ml_service_url}/predict",
                        json={
                            "transcript": transcript_res["transcript"],
                            "ocr_text": "; ".join(ocr_lines),
                            "caption": metadata.get("caption", ""),
                            "metadata": {
                                "category": "General News",
                                "uploader": metadata.get("uploader"),
                                "views": metadata.get("views"),
                                "likes": metadata.get("likes")
                            },
                            "video_path": video_path
                        }
                    )
                    if resp.status_code == 200:
                        ml_report = resp.json()
                        ml_success = True
                        logger.info("Successfully received prediction from proprietary ML service.")
            except Exception as ex:
                logger.warning(f"Failed to reach proprietary ML service: {str(ex)}. Falling back to GPT-4o pipeline.")

            if ml_success and ml_report:
                # Map claims and sources directly from ML prediction
                flat_sources = ml_report["sources"]
                formatted_claims = ml_report["claims"]
                
                # Map explainability indicators back to transcript
                explainability_data = ml_report.get("explainability", {})
                attention_highlights = {h["word"].lower(): h["weight"] for h in explainability_data.get("attention_highlights", [])}
                
                final_segments = []
                for segment in transcript_res["segments"]:
                    seg_text_lower = segment["text"].lower()
                    is_flagged = any(attention_highlights.get(word.strip(), 0.0) > 0.6 for word in seg_text_lower.split())
                    final_segments.append({
                        "time": segment["time"],
                        "text": segment["text"],
                        "flagged": is_flagged
                    })

                final_report = {
                    "verdict": ml_report["verdict"],
                    "confidence": ml_report["confidence"],
                    "risk_level": ml_report["risk_level"],
                    "uploader": metadata.get("uploader", "@unknown"),
                    "duration": metadata.get("duration", "0:00"),
                    "views": metadata.get("views", "0"),
                    "likes": metadata.get("likes", "0"),
                    "caption_text": metadata.get("caption", ""),
                    "transcript": final_segments,
                    "ocr_text": ocr_res,
                    "claims": formatted_claims,
                    "sources": flat_sources,
                    "reasoning": ml_report["reasoning"],
                    "explainability": explainability_data
                }
            else:
                # Step 6: Claim Extraction
                logger.info("[Step 6/10] Extracting factual claims via GPT-4o")
                claims = await LLMService.extract_claims(combined_context)

                async with async_session() as db:
                    result = await db.execute(select(AnalysisJob).filter(AnalysisJob.id == job_uuid))
                    job = result.scalars().first()
                    if job:
                        job.progress = 85
                        job.current_step = "Verifying Claims with Fact Check databases"
                        await db.commit()

                # Step 7: Fact Verification
                logger.info(f"[Step 7/10] Running Fact check searches for {len(claims)} claims concurrently")
                evidence_citations = []
                
                if claims:
                    fact_check_tasks = [FactCheckService.search_fact_checks(c["claim"]) for c in claims]
                    fact_results = await asyncio.gather(*fact_check_tasks)
                    
                    for idx, item_citations in enumerate(fact_results):
                        claim_text = claims[idx]["claim"]
                        evidence_citations.append({
                            "claim": claim_text,
                            "citations": item_citations
                        })
                
                async with async_session() as db:
                    result = await db.execute(select(AnalysisJob).filter(AnalysisJob.id == job_uuid))
                    job = result.scalars().first()
                    if job:
                        job.progress = 90
                        job.current_step = "Analyzing Deception & Determining Verdict"
                        await db.commit()

                # Step 8: Misinformation Analysis
                logger.info("[Step 8/10] Running final deception analysis via GPT-4o")
                verdict_res = await LLMService.analyze_misinformation(
                    combined_context, claims, evidence_citations
                )

                async with async_session() as db:
                    result = await db.execute(select(AnalysisJob).filter(AnalysisJob.id == job_uuid))
                    job = result.scalars().first()
                    if job:
                        job.progress = 95
                        job.current_step = "Compiling Report"
                        await db.commit()

                # Step 9: Explainability Report
                logger.info("[Step 9/10] Compiling user explainability report")
                
                claims_flagged = [c["claim"].lower() for c in claims if c.get("severity") in ["Medium", "High"] or verdict_res.get("verdict") == "Likely Misinformation"]
                
                final_segments = []
                for segment in transcript_res["segments"]:
                    segment_text_lower = segment["text"].lower()
                    is_flagged = any(fc in segment_text_lower for fc in claims_flagged)
                    final_segments.append({
                        "time": segment["time"],
                        "text": segment["text"],
                        "flagged": is_flagged or segment.get("flagged", False)
                    })

                flat_sources = []
                seen_urls = set()
                for ec in evidence_citations:
                    for cit in ec["citations"]:
                        if cit["url"] not in seen_urls:
                            flat_sources.append(cit)
                            seen_urls.add(cit["url"])

                formatted_claims = []
                for c in claims:
                    rating = "true"
                    if verdict_res.get("verdict") == "Likely Misinformation":
                        rating = "false"
                    elif verdict_res.get("verdict") == "Uncertain":
                        rating = "misleading"
                        
                    formatted_claims.append({
                        "title": c["claim"],
                        "rating": rating,
                        "analysis": f"Claim falls under {c['category']} category. Severity level evaluated as {c['severity']}."
                    })

                final_report = {
                    "verdict": verdict_res.get("verdict", "Uncertain"),
                    "confidence": verdict_res.get("confidence", 70),
                    "risk_level": verdict_res.get("risk_level", "Medium"),
                    "uploader": metadata.get("uploader", "@unknown"),
                    "duration": metadata.get("duration", "0:00"),
                    "views": metadata.get("views", "0"),
                    "likes": metadata.get("likes", "0"),
                    "caption_text": metadata.get("caption", ""),
                    "transcript": final_segments,
                    "ocr_text": ocr_res,
                    "claims": formatted_claims,
                    "sources": flat_sources,
                    "reasoning": " ".join(verdict_res.get("reasoning", []))
                }

        # Step 10: Save Results
        logger.info("[Step 10/10] Saving results to PostgreSQL database")
        async with async_session() as db:
            # Save rich report payload
            analysis_result = AnalysisResult(
                job_id=job_uuid,
                transcript=final_segments,
                ocr_text=ocr_res,
                caption_text=metadata.get("caption", ""),
                extracted_claims=formatted_claims,
                llm_reasoning=final_report["reasoning"],
                fact_check_sources=flat_sources,
                final_report=final_report
            )
            db.add(analysis_result)

            # Update job status
            result = await db.execute(select(AnalysisJob).filter(AnalysisJob.id == job_uuid))
            db_job = result.scalars().first()
            if db_job:
                db_job.status = "completed"
                db_job.progress = 100
                db_job.current_step = "Completed"
                # Map simple verdict string labels
                v_label = final_report["verdict"].lower()
                if "genuine" in v_label:
                    db_job.verdict = "genuine"
                elif "misinfo" in v_label:
                    db_job.verdict = "misinformation"
                else:
                    db_job.verdict = "uncertain"
                db_job.confidence_score = final_report["confidence"]
                db_job.completed_at = datetime.now(timezone.utc)
                await db.commit()
                logger.info(f"Pipeline executed successfully. Job {job_id} is complete.")

    except Exception as e:
        logger.exception(f"Fatal error in pipeline for job {job_id}: {str(e)}")
        async with async_session() as db:
            result = await db.execute(select(AnalysisJob).filter(AnalysisJob.id == job_uuid))
            db_job = result.scalars().first()
            if db_job:
                db_job.status = "failed"
                db_job.current_step = f"Failed: {str(e)}"
                await db.commit()
    finally:
        # Cleanup scratch folder to save space
        if os.path.exists(analysis_dir):
            shutil.rmtree(analysis_dir)
            logger.info(f"Cleaned up scratch directory: {analysis_dir}")

@celery_app.task(name="app.workers.tasks.analyze_reel_task", autoretry_for=(Exception,), max_retries=3, default_retry_delay=10)
def analyze_reel_task(job_id: str, reel_url: str):
    logger.info(f"Triggering pipeline async loop for job {job_id}")
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(run_pipeline_async(job_id, reel_url))
    else:
        loop.run_until_complete(run_pipeline_async(job_id, reel_url))
