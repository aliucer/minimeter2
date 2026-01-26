"""SQLAlchemy ORM Models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON
from .database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class UtilityAccount(Base):
    __tablename__ = "utility_accounts"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    provider = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id = Column(Integer, primary_key=True)
    utility_account_id = Column(Integer, ForeignKey("utility_accounts.id"), nullable=False)
    job_type = Column(String, nullable=False)
    status = Column(String, default="pending")
    error_message = Column(String, nullable=True)
    attempt_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("ingestion_jobs.id"), nullable=False)
    utility_account_id = Column(Integer, ForeignKey("utility_accounts.id"), nullable=False)
    gcs_path = Column(String, nullable=False)
    artifact_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class NormalizedBillSQL(Base):
    __tablename__ = "normalized_bills_sql"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    utility_account_id = Column(Integer, ForeignKey("utility_accounts.id"), nullable=False)
    billing_period_start = Column(String, nullable=False)  # Stored as string ISO date
    billing_period_end = Column(String, nullable=False)
    total_amount = Column(Float, nullable=False)
    json_payload = Column(String, nullable=False)  # JSON stored as string or JSON type
    created_at = Column(DateTime, default=datetime.utcnow)
