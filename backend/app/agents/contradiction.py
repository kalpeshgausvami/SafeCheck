import json
import logging
from typing import List, Dict, Any
from app.services.llm_service import client
from backend.app.agents.config import CONTRADICTION_PROMPT

logger = logging.getLogger(__name__)

class ContradictionDetectionAgent:
    """
    Agent responsible for detecting outdated information, cherry-picked facts,
    and conflicting source evidence.
    """
    def __init__(self):
        self.role = "Contradiction Detector Agent"

    async def run(self, verifications: List[Dict[str, Any]], evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logger.info(f"[{self.role}] Analysing conflicting evidence and outdated logs...")
        
        if not verifications:
            return []

        if not client:
            logger.warning(f"[{self.role}] OpenAI API key missing. Defaulting to local contradiction matcher.")
            return self._heuristic_contradictions(verifications, evidence)

        input_payload = {
            "verifications": verifications,
            "evidence": evidence
        }

        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": CONTRADICTION_PROMPT},
                    {"role": "user", "content": f"Inputs:\n\n{json.dumps(input_payload, indent=2)}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                timeout=20.0
            )
            content = response.choices[0].message.content
            if content:
                data = json.loads(content)
                return data.get("contradictions", [])
            return []
        except Exception as e:
            logger.error(f"[{self.role}] API request failed: {str(e)}. Using fallback.")
            return self._heuristic_contradictions(verifications, evidence)

    def _heuristic_contradictions(self, verifications: List[Dict[str, Any]], evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rule-based contradiction detector matching conflicting verification states.
        """
        contradictions = []
        
        # Check if claims verify both refuted and supported under different context keywords
        refuted_claims = [v for v in verifications if v["status"] == "Refuted"]
        supported_claims = [v for v in verifications if v["status"] == "Supported"]
        
        if refuted_claims and supported_claims:
            contradictions.append({
                "type": "Contextual Inconsistency",
                "details": f"The video presents multiple claims where some are verified as Supported (e.g. '{supported_claims[0]['claim'][:30]}...') while others are completely Refuted (e.g. '{refuted_claims[0]['claim'][:30]}...'). This indicates structural bias or selective representation of facts.",
                "severity": "Medium"
            })
            
        # Check for absolute vs. relative wording contradiction
        evidence_text = " ".join([e["snippet"].lower() for e in evidence])
        for v in verifications:
            claim_text = v["claim"].lower()
            if "cure" in claim_text or "always" in claim_text or "100%" in claim_text:
                if "no cure" in evidence_text or "prevention only" in evidence_text or "limited" in evidence_text:
                    contradictions.append({
                        "type": "Hyperbolic Claim vs. Scientific consensus",
                        "details": f"Claim asserts absolute benefits ('{v['claim'][:40]}...'), but official health studies specify limited, conditional, or prevention-only attributes.",
                        "severity": "High"
                    })
                    
        return contradictions
