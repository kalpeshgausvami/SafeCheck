import json
import logging
from typing import List, Dict, Any
from app.services.llm_service import client
from backend.app.agents.config import RESEARCH_PLANNER_PROMPT

logger = logging.getLogger(__name__)

class ResearchPlannerAgent:
    """
    Agent responsible for designing investigation plans and queries for claims.
    """
    def __init__(self):
        self.role = "Research Planner Agent"

    async def run(self, claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        logger.info(f"[{self.role}] Formulating research tasks for {len(claims)} claims...")
        
        if not claims:
            return {"tasks": []}

        if not client:
            logger.warning(f"[{self.role}] OpenAI API key missing. Defaulting to rule-based planner.")
            return self._heuristic_planner(claims)

        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": RESEARCH_PLANNER_PROMPT},
                    {"role": "user", "content": f"Factual Claims:\n\n{json.dumps(claims, indent=2)}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                timeout=20.0
            )
            content = response.choices[0].message.content
            if content:
                data = json.loads(content)
                return data
            return {"tasks": []}
        except Exception as e:
            logger.error(f"[{self.role}] API request failed: {str(e)}. Using fallback.")
            return self._heuristic_planner(claims)

    def _heuristic_planner(self, claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Rule-based research task generator.
        """
        tasks = []
        for c in claims:
            claim_text = c["claim"]
            cat = c["category"].lower()
            
            queries = []
            targets = []
            
            if "health" in cat:
                queries = [
                    f"{claim_text} clinical studies",
                    f"WHO CDC statements on {claim_text}"
                ]
                targets = ["PubMed", "WHO", "CDC"]
            elif "science" in cat:
                queries = [
                    f"scientific consensus on {claim_text}",
                    f"physical feasibility of {claim_text}"
                ]
                targets = ["PubMed", "Wikipedia", "AP Fact Check"]
            elif "finance" in cat:
                queries = [
                    f"financial loophole {claim_text} legal review",
                    f"SEC banking warnings {claim_text}"
                ]
                targets = ["Reuters", "SEC", "Snopes"]
            else:
                queries = [
                    f"fact check {claim_text}",
                    f"news verification {claim_text}"
                ]
                targets = ["Reuters Fact Check", "Snopes", "PolitiFact"]

            tasks.append({
                "claim": claim_text,
                "queries": queries,
                "targets": targets,
                "priority": c.get("importance", "Medium")
            })
            
        return {"tasks": tasks}
