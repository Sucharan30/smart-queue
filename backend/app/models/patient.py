import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Index, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Patient(Base):
    __tablename__ = "patients"
    __table_args__ = (
        Index("ix_patient_phone_name", "phone_number", "full_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    full_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    phone_number: Mapped[str] = mapped_column(String(25), nullable=False, index=True)
    preferred_language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    tokens = relationship("QueueToken", back_populates="patient")
