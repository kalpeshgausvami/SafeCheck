import logging
from typing import List, Dict, Any
from backend.app.agents.claims import ClaimExtractionAgent
from backend.app.agents.planner import ResearchPlannerAgent
from backend.app.agents.research import WebResearchAgent
from backend.app.agents.credibility import SourceCredibilityAgent
from backend.app.agents.verification import FactVerificationAgent
from backend.app.agents.contradiction import ContradictionDetectionAgent
from backend.app.agents.report import ReportWriterAgent
from backend.app.agents.memory import AgentMemory
from backend.app.agents.config import INPUT_TOKEN_RATE, OUTPUT_TOKEN_RATE

logger = logging.getLogger(__name__)

class MultiAgentCoordinator:
    """
    Coordinates the multi-agent state graph pipeline:
    Isolates claims -> Plans queries -> Fetches evidence -> Scores credibility -> Verifies ->
    Detects contradictions -> Compiles executive markdown report.
    """
    def __init__(self):
        self.claim_agent = ClaimExtractionAgent()
        self.planner_agent = ResearchPlannerAgent()
        self.research_agent = WebResearchAgent()
        self.credibility_agent = SourceCredibilityAgent()
        self.verify_agent = FactVerificationAgent()
        self.contradict_agent = ContradictionDetectionAgent()
        self.writer_agent = ReportWriterAgent()
        self.memory = AgentMemory()
        
        self.logs = []
        self.cost = 0.0

    def _log_agent(self, agent_name: str, message: str):
        log_entry = f"[{agent_name}] {message}"
        self.logs.append(log_entry)
        logger.info(log_entry)

    def _add_cost(self, input_len: int, output_len: int):
        # Estimate tokens (approx 4 chars per token)
        in_tokens = input_len // 4
        out_tokens = output_len // 4
        current_cost = (in_tokens * INPUT_TOKEN_RATE + out_tokens * OUTPUT_TOKEN_RATE) / 1000.0
        self.cost = round(self.cost + current_cost, 4)

    async def run_investigation(self, transcript: str, ocr_text: str, caption: str, metadata: dict) -> dict:
        self.logs = []
        self.cost = 0.0
        
        self._log_agent("Coordinator", "Initiating multi-agent fact check audit.")
        self._add_cost(len(transcript) + len(ocr_text) + len(caption), 50) # Initial routing cost

        # STEP 1: Check long term memory first
        context_claim = metadata.get("title") or (transcript[:100] + "...")
        recalled = await self.memory.recall_previous_investigation(context_claim)
        if recalled.get("recalled"):
            self._log_agent("Memory System", "Cache hit in historical vector memory. Bypassing research pipeline.")
            # Format recalled report
            return {
                "verdict": recalled["verdict"],
                "confidence": 95,
                "claims": [{"title": context_claim, "rating": recalled["verdict"], "analysis": recalled["evidence"]}],
                "evidence": [],
                "sources": [{"name": recalled["source"], "url": "https://reeltruthchecker.com", "snippet": recalled["evidence"]}],
                "report": recalled["evidence"],
                "explainability": {
                    "contradictions": [],
                    "logs": self.logs,
                    "cost": self.cost
                }
            }

        # STEP 2: Claim Extraction
        self._log_agent(self.claim_agent.role, "Extracting verifiable claims from video overlays and transcripts.")
        claims = await self.claim_agent.run(transcript, ocr_text, caption)
        self._add_cost(len(transcript) + len(ocr_text), len(str(claims)))
        self._log_agent(self.claim_agent.role, f"Extracted {len(claims)} claims for verification.")

        if not claims:
            self._log_agent("Coordinator", "No verifiable claims extracted. Terminating pipeline.")
            return self._empty_result(self.logs, self.cost)

        # STEP 3: Research Planning
        self._log_agent(self.planner_agent.role, "Designing optimized queries and scientific journal target lists.")
        research_plan = await self.planner_agent.run(claims)
        self._add_cost(len(str(claims)), len(str(research_plan)))

        # STEP 4: Evidence Collection
        self._log_agent(self.research_agent.role, "Triggering PubMed search client and Google FactcheckTools API queries.")
        evidence = await self.research_agent.run(research_plan, ocr_text, transcript)
        self._log_agent(self.research_agent.role, f"Evidence collection completed. Gained {len(evidence)} verified snippets.")

        # STEP 5: Source Credibility Evaluation
        self._log_agent(self.credibility_agent.role, "Evaluating domain credibility indices.")
        credibility_scores = await self.credibility_agent.run(evidence)
        self._add_cost(len(str(evidence)), len(str(credibility_scores)))

        # STEP 6: Fact Verification
        self._log_agent(self.verify_agent.role, "Verifying claims against evidence citations.")
        verifications = await self.verify_agent.run(claims, evidence)
        self._add_cost(len(str(claims)) + len(str(evidence)), len(str(verifications)))

        # STEP 7: Contradiction Detection
        self._log_agent(self.contradict_agent.role, "Checking for conflicting source findings or selective representation.")
        contradictions = await self.contradict_agent.run(verifications, evidence)
        self._add_cost(len(str(verifications)) + len(str(evidence)), len(str(contradictions)))

        # STEP 8: Report Writer
        self._log_agent(self.writer_agent.role, "Compiling multi-agent outputs into final Markdown verdict report.")
        report_md = await self.writer_agent.run(verifications, credibility_scores, contradictions, metadata)
        self._add_cost(len(str(verifications)) + len(str(contradictions)), len(report_md))

        # STEP 9: Save finalized audit to memory
        consensus_verdict = "Uncertain"
        refuted_count = sum(1 for v in verifications if v["status"] == "Refuted")
        supported_count = sum(1 for v in verifications if v["status"] == "Supported")
        if refuted_count > 0:
            consensus_verdict = "Likely Misinformation"
        elif supported_count > 0 and refuted_count == 0:
            consensus_verdict = "Likely Genuine"
            
        self.memory.save_to_memory(context_claim, consensus_verdict, report_md)
        self._log_agent("Coordinator", "Audit complete. Investigation logs written.")

        # Formulate output structure
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
                "analysis": v["rationale"]
            })

        flat_sources = []
        for ev in evidence:
            flat_sources.append({
                "name": ev["name"],
                "url": ev["url"],
                "snippet": ev["snippet"]
            })

        confidence_scores = [v["confidence"] for v in verifications]
        avg_confidence = int(sum(confidence_scores) / len(confidence_scores)) if confidence_scores else 70

        return {
            "verdict": consensus_verdict,
            "confidence": avg_confidence,
            "claims": formatted_claims,
            "evidence": evidence,
            "sources": flat_sources,
            "report": report_md,
            "explainability": {
                "contradictions": contradictions,
                "logs": self.logs,
                "cost": self.cost
            }
        }

    def _empty_result(self, logs: List[str], cost: float) -> dict:
        return {
            "verdict": "Uncertain",
            "confidence": 50,
            "claims": [],
            "evidence": [],
            "sources": [],
            "report": "No verifiable claims extracted. Agent investigation terminated.",
            "explainability": {
                "contradictions": [],
                "logs": logs,
                "cost": cost
            }
        }
