import uuid
from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("analysis_jobs.id", ondelete="CASCADE"), unique=True, nullable=False)
    transcript: Mapped[dict] = mapped_column(JSON, nullable=False)  # JSON representation of timecoded transcript segments
    ocr_text: Mapped[dict] = mapped_column(JSON, nullable=False)  # JSON representation of frame-by-frame text
    caption_text: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_claims: Mapped[dict] = mapped_column(JSON, nullable=False)  # JSON representation of claims analysis
    llm_reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    fact_check_sources: Mapped[dict] = mapped_column(JSON, nullable=False)  # JSON representation of source links/citations
    final_report: Mapped[dict] = mapped_column(JSON, nullable=False)  # Aggregated report for fast retrieval

    # Relationships
    job = relationship("AnalysisJob", back_populates="result")
