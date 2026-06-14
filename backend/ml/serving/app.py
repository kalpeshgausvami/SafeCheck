import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict

# Set up system path so import works under different run configurations
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Core ML imports
from backend.ml.models.claim_extractor import ClaimExtractor
from backend.ml.models.claim_verifier import ClaimVerifier
from backend.ml.models.misinfo_classifier import MisinformationClassifier
from backend.ml.models.multimodal_fusion import MultimodalFusion
from backend.ml.rag.vector_store import RAGVectorStore
from backend.ml.explainability.explainer import MLExplainability
from backend.ml.evaluation.evaluate import ModelEvaluator

app = FastAPI(
    title="Reel Truth Checker - Proprietary ML Inference Engine",
    version="1.0.0",
    description="Local token extraction, RAG fact verifier, and multimodal misinformation risk classifier."
)

# Initialize models & vector store
logger_setup = True
try:
    extractor = ClaimExtractor()
    verifier = ClaimVerifier()
    classifier = MisinformationClassifier()
    fusion = MultimodalFusion()
    vector_store = RAGVectorStore()
except Exception as e:
    import logging
    logging.error(f"Error loading model assets in startup: {str(e)}")

# Request / Response Schemas
class AnalyzeRequest(BaseModel):
    transcript: str
    ocr_text: Optional[str] = ""
    caption: Optional[str] = ""
    metadata: Optional[Dict] = None
    video_path: Optional[str] = ""

class VerifyRequest(BaseModel):
    claim: str
    evidence: str

class ExtractRequest(BaseModel):
    text: str

@app.post("/extract_claims")
async def api_extract_claims(req: ExtractRequest):
    try:
        claims = extractor.extract_claims_from_text(req.text)
        return {"claims": claims}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify")
async def api_verify_claim(req: VerifyRequest):
    try:
        verdict = verifier.verify_claim(req.claim, req.evidence)
        return {
            "claim": req.claim,
            "verdict": verdict
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict")
async def api_predict_misinformation(req: AnalyzeRequest):
    try:
        # 1. Compile overall text context
        combined_text = f"[[Speech Transcript]]\n{req.transcript}\n\n[[Visual OCR]]\n{req.ocr_text}\n\n[[Caption]]\n{req.caption}"
        
        # 2. Extract claims from text
        extracted = extractor.extract_claims_from_text(combined_text)
        
        # 3. Retrieve evidence and verify each claim
        verifications = []
        citations_summary = []
        
        for c_item in extracted:
            claim_text = c_item["claim"]
            # Search Qdrant/RAG DB for matching fact checks
            hits = vector_store.search_evidence(claim_text, limit=2)
            
            # Aggregate found sources
            evidence_text = ""
            for hit in hits:
                evidence_text += hit["text"] + " "
                citations_summary.append({
                    "name": hit["source"],
                    "url": hit["url"],
                    "snippet": hit["text"]
                })
                
            # Verify claim status
            status = verifier.verify_claim(claim_text, evidence_text)
            verifications.append({
                "claim": claim_text,
                "status": status,
                "category": req.metadata.get("category", "General News") if req.metadata else "General News"
            })
            
        # 4. Predict overall verdict and risk classification
        classification = classifier.predict_verdict(combined_text, verifications)
        
        # 5. Multimodal visual checks if video path exists
        visual_report = None
        if req.video_path and os.path.exists(req.video_path):
            visual_report = fusion.analyze_video_consistency(req.video_path, req.transcript)

        # 6. Generate explainability insights (Attention + SHAP perturbation)
        attention_highlights = MLExplainability.get_attention_highlights(req.transcript, classifier, classifier.tokenizer if hasattr(classifier, 'tokenizer') else None)
        
        def dummy_pred_fn(txt):
            return classifier.predict_verdict(txt, verifications)
        word_weights = MLExplainability.compute_word_importances(req.transcript, dummy_pred_fn)

        # Format final claims list
        formatted_claims = []
        for v in verifications:
            rating = "true"
            if v["status"] == "Refuted":
                rating = "false"
            elif v["status"] == "Insufficient Evidence":
                rating = "misleading"
                
            formatted_claims.append({
                "title": v["claim"],
                "rating": rating,
                "analysis": f"Evaluated against local RAG knowledge base. Verification status: {v['status']}."
            })

        return {
            "verdict": classification["verdict"],
            "confidence": classification["confidence"],
            "risk_level": classification["risk_level"],
            "reasoning": classification["reasoning"],
            "claims": formatted_claims,
            "sources": citations_summary,
            "explainability": {
                "attention_highlights": attention_highlights[:40], # Cap return payload
                "word_importance_weights": word_weights,
                "video_multimodal_checks": visual_report
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model_metrics")
async def api_model_metrics():
    # Evaluate against local test split if exists, else return target metrics
    try:
        def dummy_pred(txt):
            return classifier.predict_verdict(txt, [])
        metrics = ModelEvaluator.evaluate_verdicts("./data/dataset_v1/test.json", dummy_pred)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
