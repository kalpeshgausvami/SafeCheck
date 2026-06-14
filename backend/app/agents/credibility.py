import json
import logging
from typing import List, Dict, Any
from app.services.llm_service import client
from backend.app.agents.config import CREDIBILITY_PROMPT

logger = logging.getLogger(__name__)

class SourceCredibilityAgent:
    """
    Agent responsible for scoring the reliability (0-100) of evidence sources.
    """
    def __init__(self):
        self.role = "Source Credibility Agent"

    async def run(self, evidence: List[Dict[str, Any]]) -> Dict[str, int]:
        logger.info(f"[{self.role}] Evaluating trustworthiness of {len(evidence)} evidence sources...")
        
        if not evidence:
            return {}

        # Extract unique sources
        unique_sources = list(set(e["name"] for e in evidence))

        if not client:
            logger.warning(f"[{self.role}] OpenAI API key missing. Defaulting to heuristic reliability scorer.")
            return self._heuristic_credibility(unique_sources)

        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": CREDIBILITY_PROMPT},
                    {"role": "user", "content": f"Sources list:\n\n{json.dumps(unique_sources, indent=2)}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                timeout=20.0
            )
            content = response.choices[0].message.content
            if content:
                data = json.loads(content)
                # Map to standard dict: {source_name: score}
                scores = {}
                # The LLM output might contain nested keys or list of objects
                raw_scores = data.get("scores", data.get("sources", data))
                if isinstance(raw_scores, list):
                    for item in raw_scores:
                        scores[item.get("source", "")] = int(item.get("trust_score", 50))
                elif isinstance(raw_scores, dict):
                    for k, v in raw_scores.items():
                        scores[k] = int(v)
                return scores
            return {}
        except Exception as e:
            logger.error(f"[{self.role}] API request failed: {str(e)}. Using fallback.")
            return self._heuristic_credibility(unique_sources)

    def _heuristic_credibility(self, sources: List[str]) -> Dict[str, int]:
        """
        Rule-based reliability scorer.
        """
        scores = {}
        for s in sources:
            s_lower = s.lower()
            if "who" in s_lower or "cdc" in s_lower or "nih" in s_lower or "pubmed" in s_lower or "journal" in s_lower:
                scores[s] = 98 # Academic & Health official
            elif "reuters" in s_lower or "ap fact" in s_lower or "associated press" in s_lower or "snopes" in s_lower or "politifact" in s_lower:
                scores[s] = 92 # Elite factcheckers / news wires
            elif "wikipedia" in s_lower:
                scores[s] = 80 # Wikipedia baseline
            elif "transcript" in s_lower or "video" in s_lower or "ocr" in s_lower:
                scores[s] = 75 # Primary asset context
            else:
                scores[s] = 45 # Unknown / Blog fallback
        return scores
