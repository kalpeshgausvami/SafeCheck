import os
import json
import logging
from typing import List, Dict, Any
from openai import AsyncOpenAI
from app.utils.mock_data import health_mock, tech_mock, finance_mock, default_mock

logger = logging.getLogger(__name__)

# Initialize OpenAI client. If API key is missing, operations will default to local mock generators.
api_key = os.getenv("OPENAI_API_KEY", "")
client = AsyncOpenAI(api_key=api_key) if api_key else None

class LLMService:
    @staticmethod
    async def _call_openai_with_retry(func, *args, **kwargs):
        retries = 3
        backoff = 1.0
        for i in range(retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if i == retries - 1:
                    raise e
                sleep_time = backoff * (2 ** i)
                logger.warning(f"OpenAI call failed: {str(e)}. Retrying in {sleep_time}s...")
                import asyncio
                await asyncio.sleep(sleep_time)

    @staticmethod
    async def extract_claims(context: str) -> List[Dict[str, Any]]:
        """
        Calls GPT-4o to isolate factual, verifiable claims from the video's multi-modal context.
        """
        if not client:
            logger.warning("OpenAI API key missing. Defaulting to local claim extractor.")
            return LLMService._mock_claim_extraction(context)

        prompt = """
        You are an advanced claim extraction engine.
        Your task is to analyze the multi-modal context document from an Instagram Reel (including transcripts, on-screen text, captions, and tags) and extract a list of verifiable factual claims.

        Rules:
        1. Ignore subjective opinions, jokes, sarcasm, general advice, or motivational statements.
        2. Extract only statements that can be proven or disproven by scientific research, historical facts, public records, or official datasets.
        3. For each claim, determine:
           - claim: The exact assertion.
           - category: Choose one of [Health, Politics, Finance, Science, News, Crime, Other].
           - severity: Potential real-world harm if this claim is false (Choose one of [Low, Medium, High]).

        Your response must be a valid JSON object with the following structure:
        {
          "claims": [
            {
              "claim": "Claim text here",
              "category": "Health",
              "severity": "High"
            }
          ]
        }
        """

        try:
            logger.info("Requesting claim extraction from GPT-4o...")
            response = await LLMService._call_openai_with_retry(
                client.chat.completions.create,
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Context Document:\n\n{context}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                timeout=20.0
            )
            content = response.choices[0].message.content
            if content:
                data = json.loads(content)
                logger.info(f"GPT-4o successfully extracted {len(data.get('claims', []))} claims.")
                return data.get("claims", [])
            return []
        except Exception as e:
            logger.error(f"GPT-4o claim extraction failed: {str(e)}. Falling back to local parser.")
            return LLMService._mock_claim_extraction(context)

    @staticmethod
    async def analyze_misinformation(
        context: str, 
        claims: List[Dict[str, Any]], 
        evidence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calls GPT-4o to analyze all context and fact-check citations, determining the final verdict.
        """
        if not client:
            logger.warning("OpenAI API key missing. Defaulting to local analysis simulator.")
            return LLMService._mock_misinformation_analysis(context)

        prompt = """
        You are a professional misinformation detection system.
        Your job is to analyze the provided Instagram Reel content context, its extracted claims, and the fact-check evidence compiled from trusted sources (like WHO, SEC, Snopes, etc.).

        Based on all evidence, you must output a structured analysis report.
        
        Rules:
        1. Assign a final verdict:
           - "Likely Genuine": All core claims are backed by fact checks or reliable sources. No deceptive contexts detected.
           - "Likely Misinformation": Core claims are flagged as false or misleading by reliable sources.
           - "Uncertain": Claims cannot be verified, contain mixed/ambiguous context, or lack source evidence.
        2. Assign a confidence score from 0 to 100 based on the strength of fact-check evidence.
        3. Assign a risk level: [Low, Medium, High, Critical].
        4. Provide detailed reasoning statements outlining what is flagged and why.
        5. Compile lists of supporting and contradicting evidence based on the fact checks.

        Your response must be a valid JSON object matching this structure:
        {
          "verdict": "Likely Misinformation",
          "confidence": 95,
          "risk_level": "High",
          "reasoning": [
            "Reason statement 1",
            "Reason statement 2"
          ],
          "supporting_evidence": [
            "Source A confirms..."
          ],
          "contradicting_evidence": [
            "Source B refutes the claim that..."
          ]
        }
        """

        input_payload = {
            "reel_context": context,
            "extracted_claims": claims,
            "fact_check_evidence": evidence
        }

        try:
            logger.info("Requesting misinformation analysis from GPT-4o...")
            response = await LLMService._call_openai_with_retry(
                client.chat.completions.create,
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Input Data:\n\n{json.dumps(input_payload, indent=2)}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                timeout=25.0
            )
            content = response.choices[0].message.content
            if content:
                data = json.loads(content)
                logger.info(f"GPT-4o verdict: {data.get('verdict')} with {data.get('confidence')}% confidence.")
                return data
            raise ValueError("Empty response from OpenAI")
        except Exception as e:
            logger.error(f"GPT-4o analysis failed: {str(e)}. Falling back to local analysis simulator.")
            return LLMService._mock_misinformation_analysis(context)

    @staticmethod
    def _mock_claim_extraction(context: str) -> List[Dict[str, Any]]:
        context_lower = context.lower()
        if "lemon" in context_lower or "canc" in context_lower:
            mock = health_mock
        elif "solar" in context_lower or "glass" in context_lower:
            mock = tech_mock
        elif "bank" in context_lower or "loophole" in context_lower:
            mock = finance_mock
        else:
            mock = default_mock

        return [
            {
                "claim": c["title"],
                "category": "Health" if "lemon" in context_lower else "Science" if "solar" in context_lower else "Finance",
                "severity": "High" if "lemon" in context_lower else "Low" if "solar" in context_lower else "Medium"
            }
            for c in mock["claims"]
        ]

    @staticmethod
    def _mock_misinformation_analysis(context: str) -> Dict[str, Any]:
        context_lower = context.lower()
        if "lemon" in context_lower or "canc" in context_lower:
            mock = health_mock
        elif "solar" in context_lower or "glass" in context_lower:
            mock = tech_mock
        elif "bank" in context_lower or "loophole" in context_lower:
            mock = finance_mock
        else:
            mock = default_mock

        return {
            "verdict": mock["verdict"],
            "confidence": mock["confidence"],
            "risk_level": mock["risk_level"],
            "reasoning": [mock["reasoning"]],
            "supporting_evidence": [src["snippet"] for src in mock["sources"] if "confirm" in src["snippet"].lower() or "guideline" in src["snippet"].lower()],
            "contradicting_evidence": [src["snippet"] for src in mock["sources"] if "debunk" in src["snippet"].lower() or "warn" in src["snippet"].lower()]
        }
