import uuid
from sqlalchemy.future import select
from app.database.session import async_session
from app.models.result import AnalysisResult
from backend.ml.rag.vector_store import RAGVectorStore
import logging

logger = logging.getLogger(__name__)

class AgentMemory:
    """
    Manages long term agent memory:
    1. PostgreSQL: check previous verified reports
    2. Qdrant: semantic checking for previously checked claims
    """
    def __init__(self):
        try:
            self.vector_store = RAGVectorStore(collection_name="investigated_claims_memory")
        except Exception as e:
            logger.warning(f"Failed to connect to Qdrant memory collection: {str(e)}")
            self.vector_store = None

    async def recall_previous_investigation(self, claim: str) -> dict:
        """
        Scrapes historical investigations from database and vector memory.
        """
        # 1. Check Vector DB Memory
        if self.vector_store:
            try:
                hits = self.vector_store.search_evidence(claim, limit=1)
                if hits and hits[0]["score"] > 0.85:
                    logger.info(f"Memory hit in Qdrant for claim: '{claim[:30]}...'")
                    return {
                        "recalled": True,
                        "verdict": hits[0].get("verdict", "Uncertain"),
                        "evidence": hits[0]["text"],
                        "source": hits[0]["source"]
                    }
            except Exception as e:
                logger.error(f"Failed reading vector memory: {str(e)}")

        # 2. Check Postgres Database past results
        try:
            async with async_session() as db:
                # Query all analysis results
                stmt = select(AnalysisResult).order_index = AnalysisResult.id
                result = await db.execute(stmt)
                past_results = result.scalars().all()
                
                claim_lower = claim.lower()
                for past in past_results:
                    claims_list = past.extracted_claims or []
                    for c_item in claims_list:
                        title = c_item.get("title", "").lower()
                        # Simple keyword overlap or exact match
                        if claim_lower in title or title in claim_lower:
                            logger.info(f"Memory hit in PostgreSQL for claim: '{claim[:30]}...'")
                            return {
                                "recalled": True,
                                "verdict": c_item.get("rating"),
                                "evidence": c_item.get("analysis", "Verified in past report."),
                                "source": "Internal Historical Audit Database"
                            }
        except Exception as e:
            logger.error(f"Failed querying PostgreSQL audit history: {str(e)}")
            
        return {"recalled": False}

    def save_to_memory(self, claim: str, verdict: str, summary: str):
        """
        Saves a finalized investigation report to vector memory.
        """
        if self.vector_store:
            try:
                doc_id = f"mem_{uuid.uuid4().hex[:8]}"
                self.vector_store.index_document(
                    doc_id=doc_id,
                    text=summary,
                    metadata={
                        "claim": claim,
                        "verdict": verdict,
                        "source": "Agent Long-term Memory"
                    }
                )
                logger.info(f"Saved claim investigation to vector memory: {claim[:30]}...")
            except Exception as e:
                logger.error(f"Failed saving to vector memory: {str(e)}")
