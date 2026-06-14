import logging
from app.services.llm_service import client

logger = logging.getLogger(__name__)

class IntelligenceReportCompiler:
    """
    Compiles detailed trend investigation reports summarizing propagation network statistics
    and verification findings for clusters.
    """
    @staticmethod
    async def compile_cluster_report(trend_info: dict, verifications: list, network_metrics: dict) -> str:
        claim = trend_info.get("claim_cluster", "Generic Claim")
        c_id = trend_info.get("cluster_id")
        
        # Build prompt for LLM report writer
        prompt = f"""You are a Threat Intelligence Report Compiler for Reel Truth Checker.
Generate a professional intelligence investigation report for the following trending misinformation claim:
Claim: "{claim}"
Platforms: {trend_info.get("platforms")}
Total Reach: {trend_info.get("reach")}
Growth Rate: {trend_info.get("growth_rate") * 100}%
Network Nodes: {network_metrics.get("total_nodes")}, Bot Density: {network_metrics.get("density") * 100}%

Your output must be formatted in Markdown with the following sections:
1. Executive Summary (verdict risk, virality velocity, uploader hub summary)
2. Key Claims & Variations
3. Propagation Network Analysis (nodes, bots, platforms spread)
4. Fact-Checking Evidence & Contradictions (what Snopes/PubMed/WHO says)
5. Recommended Action Items (content tags, platform reporting dockets, warning triggers)
"""
        
        if not client:
            logger.warning("OpenAI API key missing. Defaulting to local report compiler template.")
            return IntelligenceReportCompiler._compile_fallback(trend_info, verifications, network_metrics)

        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a threat intelligence report writer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                timeout=25.0
            )
            content = response.choices[0].message.content
            return content or "Failed to compile report from LLM."
        except Exception as e:
            logger.error(f"Failed to generate LLM report: {str(e)}. Using fallback compiler.")
            return IntelligenceReportCompiler._compile_fallback(trend_info, verifications, network_metrics)

    @staticmethod
    def _compile_fallback(trend: dict, verifications: list, net_metrics: dict) -> str:
        claim = trend.get("claim_cluster")
        growth = int(trend.get("growth_rate", 0) * 100)
        
        return f"""# Threat Intelligence Investigation Report

> [!CAUTION]
> **Subject Claim**: "{claim}"
> **Growth rate**: {growth}% | **Propagation Reach**: {trend.get("reach")} views
> **Networks Size**: {net_metrics.get("total_nodes", 0)} accounts | **Density Index**: {net_metrics.get("density", 0.0)}

---

## 1. Executive Summary
This narrative is propagating rapidly across platforms: {", ".join(trend.get("platforms", []))}.
It represents a high-risk information vector. The growth velocity is classified as **critical**, requiring active content tagging.

---

## 2. Key Claim Variations
- "Did you know that {claim.lower()}? Doctors don't want you to see this."
- "Visual proof of {claim.lower()} is spreading. Watch this before it gets deleted."

---

## 3. Propagation & Coordinated Bot Analysis
- **Total Accounts Connected**: {net_metrics.get("total_nodes", 0)}
- **Coordinated Linkages**: {net_metrics.get("total_edges", 0)}
- Coordinated bot activity has been flagged. The network shows centralized hubs distributing clips simultaneously.

---

## 4. Recommended Actions
1. **Apply content warning tags** stating "False/Manipulated context" on all matched video clips.
2. **Flag seed accounts** showing bot behavior for platform terms-of-service violations.
3. **Index fact checks** directly in RAG vector database to block search queries.
"""
