from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Schema for Audit Log
class AuditLogBase(BaseModel):
    action: str
    field_name: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_by: str
    timestamp: datetime

    class Config:
        from_attributes = True

class AuditLogResponse(AuditLogBase):
    id: int
    complaint_id: int

# Schema for Complaint Fields
class ComplaintFields(BaseModel):
    complaint_source: Optional[str] = ""
    customer_name: Optional[str] = ""
    product_name: Optional[str] = ""
    product_strength: Optional[str] = ""
    batch_number: Optional[str] = ""
    manufacturing_date: Optional[str] = ""
    expiry_date: Optional[str] = ""
    quantity_affected: Optional[str] = ""
    complaint_type: Optional[str] = ""
    complaint_date: Optional[str] = ""
    description: Optional[str] = ""
    initial_severity: Optional[str] = ""
    priority: Optional[str] = ""
    next_action: Optional[str] = ""
    risk_assessment_details: Optional[str] = ""

# Schema for Complaint Creation/Update
class ComplaintCreate(ComplaintFields):
    status: Optional[str] = "Pending Triage"

class ComplaintUpdate(BaseModel):
    status: Optional[str] = None
    complaint_source: Optional[str] = None
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    product_strength: Optional[str] = None
    batch_number: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    quantity_affected: Optional[str] = None
    complaint_type: Optional[str] = None
    complaint_date: Optional[str] = None
    description: Optional[str] = None
    initial_severity: Optional[str] = None
    priority: Optional[str] = None
    
    # AI fields
    completeness_status: Optional[str] = None
    completeness_feedback: Optional[str] = None
    root_cause_recommendation: Optional[str] = None
    summary: Optional[str] = None
    risk_classification_reasoning: Optional[str] = None
    next_action: Optional[str] = None
    risk_assessment_details: Optional[str] = None

# Schema for Complaint Response
class ComplaintResponse(BaseModel):
    id: int
    complaint_code: str
    status: str
    complaint_source: Optional[str] = ""
    customer_name: Optional[str] = ""
    product_name: Optional[str] = ""
    product_strength: Optional[str] = ""
    batch_number: Optional[str] = ""
    manufacturing_date: Optional[str] = ""
    expiry_date: Optional[str] = ""
    quantity_affected: Optional[str] = ""
    complaint_type: Optional[str] = ""
    complaint_date: Optional[str] = ""
    description: Optional[str] = ""
    initial_severity: Optional[str] = ""
    priority: Optional[str] = ""
    
    completeness_status: Optional[str] = None
    completeness_feedback: Optional[str] = None
    root_cause_recommendation: Optional[str] = None
    summary: Optional[str] = None
    risk_classification_reasoning: Optional[str] = None
    next_action: Optional[str] = None
    risk_assessment_details: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    logs: List[AuditLogResponse] = []

    class Config:
        from_attributes = True

# Schema for AI Text/File Extraction request
class ExtractionRequest(BaseModel):
    text: str

# Schema for AI Chat request
class ChatRequest(BaseModel):
    message: str
    chat_history: List[dict] = [] # list of {"role": "user"|"assistant", "content": "..."}
    current_fields: ComplaintFields

# Schema for AI Assessment Request
class AssessmentRequest(BaseModel):
    fields: ComplaintFields
    assessment_type: str # "completeness" | "root_cause" | "capa" | "risk" | "duplicate" | "summary"
