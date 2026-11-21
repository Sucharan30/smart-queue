import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, UniqueConstraint, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Department(Base):
    __tablename__ = "departments"
    __table_args__ = (
        UniqueConstraint("clinic_id", "code", name="uq_clinic_department_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    clinic_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("clinics.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    clinic = relationship("Clinic", back_populates="departments")
    doctors = relationship("Doctor", back_populates="department", cascade="all, delete-orphan")
    tokens = relationship("QueueToken", back_populates="department")
