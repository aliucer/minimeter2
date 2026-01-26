"""Pydantic schemas for API requests, responses, and data validation."""
from typing import Optional, List
from datetime import date
from pydantic import BaseModel


# ============================================================
# REQUEST SCHEMAS
# ============================================================

class CustomerCreate(BaseModel):
    """Create a new customer."""
    name: str


class UtilityAccountCreate(BaseModel):
    """Create a new utility account."""
    customer_id: int
    provider: str


class IngestRunRequest(BaseModel):
    """Request to run an ingestion job."""
    customer_id: int
    utility_account_id: int
    job_type: str


# ============================================================
# RESPONSE SCHEMAS
# ============================================================

class HealthResponse(BaseModel):
    ok: bool


class CustomerResponse(BaseModel):
    id: int
    name: str
    created_at: str


class UtilityAccountResponse(BaseModel):
    id: int
    customer_id: int
    provider: str
    created_at: str


class JobResponse(BaseModel):
    """Response for job creation."""
    job_id: int
    status: str
    message: Optional[str] = None


class BillResult(BaseModel):
    """Extracted bill data."""
    billing_period_start: str
    billing_period_end: str
    total_amount: float
    json_payload: str


class AgentResultResponse(BaseModel):
    """Response for agent result query."""
    job_id: int
    status: str
    result: Optional[BillResult] = None
    error: Optional[str] = None
    message: Optional[str] = None


# ============================================================
# DATA SCHEMAS (for LLM extraction)
# ============================================================

class LineItem(BaseModel):
    """Single line item from a bill."""
    name: str
    amount: float


class BillNormalized(BaseModel):
    """Normalized bill data extracted by LLM."""
    billing_period_start: date
    billing_period_end: date
    total_amount: float
    line_items: List[LineItem]
