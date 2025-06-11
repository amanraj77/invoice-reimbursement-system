from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ExpenseCategory(str, Enum):
    """Types of expenses"""
    FOOD = "food"
    TRAVEL = "travel"
    ACCOMMODATION = "accommodation"
    TRANSPORT = "transport"

class ReimbursementStatus(str, Enum):
    """Possible reimbursement statuses"""
    APPROVED = "approved"
    DECLINED = "declined"
    PARTIAL_APPROVED = "partial_approved"
    PENDING_REVIEW = "pending_review"

class InvoiceItem(BaseModel):
    """Individual item on an invoice"""
    description: str = "Unknown Item"
    quantity: int = 1
    unit_price: float = 0.0
    amount: float = 0.0

class InvoiceAnalysis(BaseModel):
    """Complete analysis of a single invoice"""
    invoice_id: str
    employee_name: str
    vendor_name: Optional[str] = "Unknown Vendor"
    date: Optional[str] = None
    amount: float
    category: ExpenseCategory
    items: List[InvoiceItem] = []
    status: ReimbursementStatus
    reimbursable_amount: float
    policy_violations: List[str] = []
    reasoning: str
    contains_alcohol: bool = False
    submission_date_valid: bool = True

class AnalysisResponse(BaseModel):
    """Response from invoice analysis"""
    analysis_results: List[InvoiceAnalysis]
    summary: Dict[str, Any]
    processing_time: float
    success: bool = True
    message: str = "Analysis completed successfully"

class ChatRequest(BaseModel):
    """Request for chat interface"""
    query: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Response from chat interface"""
    response: str
    sources: List[str] = []
    conversation_id: str
    success: bool = True
