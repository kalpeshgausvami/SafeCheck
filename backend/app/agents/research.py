import asyncio
import logging
from typing import List, Dict, Any
from backend.app.agents.tools import AgentToolkit

logger = logging.getLogger(__name__)

class WebResearchAgent:
    """
    Agent responsible for searching factcheck APIs, PubMed database, and context.
    """
    def __init__(self):
        self.role = "Web Research Agent"

    async def run(self, research_plan: Dict[str, Any], ocr_context: str = "", transcript_context: str = "") -> List[Dict[str, Any]]:
        logger.info(f"[{self.role}] Gathering evidence for research tasks...")
        
        tasks = research_plan.get("tasks", [])
        if not tasks:
            return []

        evidence_pool = []
        search_tasks = []

        # Queue up searches concurrently
        for t in tasks:
            queries = t.get("queries", [])
            targets = t.get("targets", [])
            claim_text = t.get("claim", "")
            
            for query in queries:
                # 1. Factcheck tools search
                search_tasks.append(self._execute_factcheck(query, claim_text))
                
                # 2. PubMed search
                if any("pubmed" in target.lower() for target in targets):
                    search_tasks.append(self._execute_pubmed(query, claim_text))

            # 3. OCR context search
            if ocr_context:
                search_tasks.append(self._execute_ocr(claim_text, ocr_context))
                
            # 4. Transcript context search
            if transcript_context:
                search_tasks.append(self._execute_transcript(claim_text, transcript_context))

        # Gather all searches concurrently
        all_results = await asyncio.gather(*search_tasks)
        
        # Flatten and filter out empty lists
        for res_list in all_results:
            if res_list:
                for res in res_list:
                    # Deduplicate by url/snippet
                    if not any(e["url"] == res["url"] and e["snippet"] == res["snippet"] for e in evidence_pool):
                        evidence_pool.append(res)
                        
        logger.info(f"[{self.role}] Collected {len(evidence_pool)} evidence snippets.")
        return evidence_pool

    async def _execute_factcheck(self, query: str, claim: str) -> List[Dict[str, Any]]:
        hits = await AgentToolkit.factcheck_search(query)
        for h in hits:
            h["claim"] = claim
            h["type"] = "Fact-Check Article"
        return hits

    async def _execute_pubmed(self, query: str, claim: str) -> List[Dict[str, Any]]:
        hits = await AgentToolkit.pubmed_search(query)
        for h in hits:
            h["claim"] = claim
            h["type"] = "Scientific Journal"
        return hits

    async def _execute_ocr(self, query: str, context: str) -> List[Dict[str, Any]]:
        hits = AgentToolkit.ocr_search(query, context)
        for h in hits:
            h["claim"] = query
            h["type"] = "OCR Overlay Text"
        return hits

    async def _execute_transcript(self, query: str, context: str) -> List[Dict[str, Any]]:
        hits = AgentToolkit.transcript_search(query, context)
        for h in hits:
            h["claim"] = query
            h["type"] = "Speech Transcript"
        return hits
