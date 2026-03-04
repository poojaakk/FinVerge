from pydantic import BaseModel
from typing import Optional, Any, List

class Discrepancy(BaseModel):
    item: str
    type: str
    po_value: Optional[Any] = None
    invoice_value: Optional[Any] = None

class DiscrepancyResult(BaseModel):
    item_name: str
    issue_type: str
    issue_description: str
    status: str  # "APPROVED", "NEEDS_REVIEW", "REJECTED"
    explanation: str
    recommendation: str
    supporting_documents: List[str]

class VerificationSummary(BaseModel):
    total_items_checked: int
    items_approved: int
    items_need_review: int
    items_rejected: int
    overall_recommendation: str

class VerificationResponse(BaseModel):
    summary: VerificationSummary
    item_details: List[DiscrepancyResult]
    processing_notes: List[str]