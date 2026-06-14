import json
import logging
from app.services.llm_service import client
from backend.app.agents.config import WRITER_PROMPT

logger = logging.getLogger(__name__)

class ReportWriterAgent:
    """
    Agent responsible for compiling final investigative verification report.
    """
    def __init__(self):
        self.role = "Report Writer Agent"

    async def run(self, verifications: list, credibility: dict, contradictions: list, metadata: dict) -> str:
        logger.info(f"[{self.role}] Formulating final investigative report...")
        
        # Calculate final consensus verdict & confidence
        verdict = "Uncertain"
        confidence_scores = [v["confidence"] for v in verifications]
        avg_confidence = int(sum(confidence_scores) / len(confidence_scores)) if confidence_scores else 70
        
        refuted_count = sum(1 for v in verifications if v["status"] == "Refuted")
        supported_count = sum(1 for v in verifications if v["status"] == "Supported")
        
        if refuted_count > 0:
            verdict = "Likely Misinformation"
            risk_level = "High"
        elif supported_count > 0 and refuted_count == 0:
            verdict = "Likely Genuine"
            risk_level = "Low"
        else:
            verdict = "Uncertain"
            risk_level = "Medium"

        if not client:
            logger.warning(f"[{self.role}] OpenAI API key missing. Defaulting to report compiler template.")
            return self._compile_report_template(verdict, avg_confidence, risk_level, verifications, credibility, contradictions, metadata)

        input_payload = {
            "verdict": verdict,
            "confidence": avg_confidence,
            "risk_level": risk_level,
            "claims": verifications,
            "credibility_scores": credibility,
            "contradictions": contradictions,
            "metadata": metadata
        }

        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": WRITER_PROMPT},
                    {"role": "user", "content": f"Structured analysis data:\n\n{json.dumps(input_payload, indent=2)}"}
                ],
                temperature=0.3,
                timeout=25.0
            )
            content = response.choices[0].message.content
            return content or "Failed to compile markdown content from LLM."
        except Exception as e:
            logger.error(f"[{self.role}] API request failed: {str(e)}. Compiling report template.")
            return self._compile_report_template(verdict, avg_confidence, risk_level, verifications, credibility, contradictions, metadata)

    def _compile_report_template(self, verdict: str, confidence: int, risk: str, verifications: list, credibility: dict, contradictions: list, metadata: dict) -> str:
        """
        Premium local Markdown report compiler template.
        """
        # Pick color theme based on verdict
        color_alert = "WARNING"
        if verdict == "Likely Genuine":
            color_alert = "NOTE"
        elif verdict == "Likely Misinformation":
            color_alert = "CAUTION"
            
        md = f"""# Investigative Fact-Checking Report

> [!{color_alert}]
> **Executive Summary & Verdict: {verdict}**
> - **AI Confidence Rating**: {confidence}%
> - **Misinformation Risk Level**: {risk}
> - **Uploader Profile**: {metadata.get("uploader", "@unknown")}
> - **Total Claims Checked**: {len(verifications)}

---

## 1. Verified Claims Analysis

"""
        for v in verifications:
            icon = "✅" if v["status"] == "Supported" else "❌" if v["status"] == "Refuted" else "⚠️"
            md += f"### {icon} {v['claim']}\n"
            md += f"- **Verification Status**: `{v['status']}`\n"
            md += f"- **Confidence Score**: {v['confidence']}%\n"
            md += f"- **Verification Rationale**: {v['rationale']}\n\n"

        md += "---\n\n## 2. Contradiction Detection Log\n\n"
        if contradictions:
            for idx, c in enumerate(contradictions):
                md += f"#### [{idx+1}] {c['type']} (Severity: {c.get('severity', 'Medium')})\n"
                md += f"> [!IMPORTANT]\n"
                md += f"> {c['details']}\n\n"
        else:
            md += "*No structural contradictions or Selective/Outdated information patterns detected across source citations.*\n\n"

        md += "---\n\n## 3. Investigated Sources & Credibility Scores\n\n"
        md += "| Source Entity | Credibility Trust Score | Historical Authority |\n"
        md += "| :--- | :---: | :--- |\n"
        
        for source, score in credibility.items():
            authority = "Official / Peer-Reviewed" if score >= 90 else "Reputable Media / Factchecker" if score >= 80 else "User/Context reference"
            md += f"| {source} | **{score}** | {authority} |\n"

        md += "\n\n--- \n*Report generated autonomously by Reel Truth Checker Multi-Agent investigation team.*"
        return md
