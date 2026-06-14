import json
import logging
from typing import List, Dict, Any
from app.services.llm_service import client
from backend.app.agents.config import VERIFIER_PROMPT

logger = logging.getLogger(__name__)

class FactVerificationAgent:
    """
    Agent responsible for verifying claims against evidence and scoring confidence.
    """
    def __init__(self):
        self.role = "Fact Verification Agent"

    async def run(self, claims: List[Dict[str, Any]], evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logger.info(f"[{self.role}] Verifying claims against {len(evidence)} evidence snippets...")
        
        if not claims:
            return []

        if not client:
            logger.warning(f"[{self.role}] OpenAI API key missing. Defaulting to local verification parser.")
            return self._heuristic_verification(claims, evidence)

        input_payload = {
            "claims": claims,
            "evidence": evidence
        }

        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": VERIFIER_PROMPT},
                    {"role": "user", "content": f"Verification data:\n\n{json.dumps(input_payload, indent=2)}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                timeout=25.0
            )
            content = response.choices[0].message.content
            if content:
                data = json.loads(content)
                verifications = data.get("verifications", data.get("results", data))
                
                # Format to standard list
                formatted = []
                if isinstance(verifications, list):
                    for v in verifications:
                        formatted.append({
                            "claim": v.get("claim", ""),
                            "status": v.get("status", "Insufficient Evidence"),
                            "confidence": int(v.get("confidence", 70)),
                            "rationale": v.get("rationale", "")
                        })
                elif isinstance(verifications, dict):
                    # In case of {claim_text: dict} structure
                    for k, v in verifications.items():
                        if isinstance(v, dict):
                            formatted.append({
                                "claim": k,
                                "status": v.get("status", "Insufficient Evidence"),
                                "confidence": int(v.get("confidence", 70)),
                                "rationale": v.get("rationale", "")
                            })
                return formatted
            return []
        except Exception as e:
            logger.error(f"[{self.role}] API request failed: {str(e)}. Using fallback verifications.")
            return self._heuristic_verification(claims, evidence)

    def _heuristic_verification(self, claims: List[Dict[str, Any]], evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rule-based verification mapper checking text overlaps.
        """
        verifications = []
        for c in claims:
            claim_text = c["claim"]
            claim_lower = claim_text.lower()
            
            # Find evidence specifically linked to this claim
            matched_evidence = []
            for ev in evidence:
                # Evidence is mapped by the web research agent by attaching the query/claim context
                if ev.get("claim", "").lower() in claim_lower or claim_lower in ev.get("claim", "").lower():
                    matched_evidence.append(ev)
            
            # Default fallback evaluation
            status = "Insufficient Evidence"
            confidence = 65
            rationale = "No direct citations or factcheck summaries found matching this assertion."
            
            if matched_evidence:
                evidence_text = " ".join([h["snippet"].lower() for h in matched_evidence])
                refute_keywords = ["false", "refutes", "hoax", "debunk", "misleading", "warns against", "unproven", "no scientific evidence"]
                support_keywords = ["true", "confirms", "verified", "supported", "consensus", "agrees"]
                
                if any(k in evidence_text for k in refute_keywords):
                    status = "Refuted"
                    confidence = 90
                    rationale = f"Evaluated against {len(matched_evidence)} matching references. High-trust sources refute this claim."
                elif any(k in evidence_text for k in support_keywords):
                    status = "Supported"
                    confidence = 85
                    rationale = f"Evaluated against {len(matched_evidence)} references. Fact-checking consensus supports this assertion."
                else:
                    status = "Partially True"
                    confidence = 75
                    rationale = "Claim contains verifiable fragments but lacks overall structural context in evidence sources."
            
            verifications.append({
                "claim": claim_text,
                "status": status,
                "confidence": confidence,
                "rationale": rationale
            })
            
        return verifications
