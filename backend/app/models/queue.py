import uuid
from datetime import datetime, date
from sqlalchemy import (
    String,
    Text,
    Integer,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
    func,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class QueueCounter(Base):
    __tablename__ = "queue_counters"
    __table_args__ = (
        UniqueConstraint("clinic_id", "department_id", "token_date", name="uq_clinic_dept_date_counter"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    clinic_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("clinics.id", ondelete="CASCADE"), nullable=False
    )
    department_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("departments.id", ondelete="CASCADE"), nullable=False
    )
    token_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    last_sequence_number: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class QueueToken(Base):
    __tablename__ = "queue_tokens"
    __table_args__ = (
        UniqueConstraint("clinic_id", "department_id", "token_date", "sequence_number", name="uq_token_dept_date_seq"),
        UniqueConstraint("clinic_id", "department_id", "token_date", "token_number", name="uq_token_dept_date_number"),
        Index("ix_token_queue_lookup", "clinic_id", "department_id", "token_date", "status"),
        Index("ix_token_patient", "patient_id"),
        Index("ix_token_doctor", "doctor_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    clinic_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("clinics.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    department_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("doctors.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("patients.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    token_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    token_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    registration_source: Mapped[str] = mapped_column(String(20), nullable=False)  # STAFF, WEB, WHATSAPP
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="WAITING")
    registration_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    called_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    consultation_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    clinic = relationship("Clinic", back_populates="tokens")
    department = relationship("Department", back_populates="tokens")
    doctor = relationship("Doctor", back_populates="tokens")
    patient = relationship("Patient", back_populates="tokens")
    events = relationship("QueueEvent", back_populates="token", cascade="all, delete-orphan", order_by="QueueEvent.created_at.asc()")
    notification_logs = relationship("NotificationLog", back_populates="token", cascade="all, delete-orphan")


class QueueEvent(Base):
    __tablename__ = "queue_events"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    token_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("queue_tokens.id", ondelete="CASCADE"), nullable=False, index=True
    )
    previous_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    new_status: Mapped[str] = mapped_column(String(30), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., TOKEN_CREATED
    event_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_by: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationships
    token = relationship("QueueToken", back_populates="events")


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    token_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("queue_tokens.id", ondelete="CASCADE"), nullable=False, index=True
    )
    channel: Mapped[str] = mapped_column(String(30), nullable=False)  # WHATSAPP, SMS
    message_type: Mapped[str] = mapped_column(String(50), nullable=False)  # TOKEN_CONFIRMATION
    delivery_status: Mapped[str] = mapped_column(String(30), nullable=False, default="LOGGED")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    token = relationship("QueueToken", back_populates="notification_logs")
