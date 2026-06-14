import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Billing & Plan tracking
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    subscription_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    billing_plan: Mapped[str] = mapped_column(String(50), default="free", nullable=False)  # free, pro, team, enterprise
    billing_status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    
    # Usage limits
    monthly_analyses_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    monthly_analyses_limit: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    api_calls_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    jobs = relationship("AnalysisJob", back_populates="user", cascade="all, delete-orphan")
