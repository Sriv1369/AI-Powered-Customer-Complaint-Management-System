from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
import datetime
from .database import Base

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    complaint_code = Column(String(50), unique=True, index=True) # e.g. CC-2026-0001
    status = Column(String(50), default="Pending Triage") # Pending Triage, Under Investigation, Resolved
    
    # 1. Origin & Customer Details
    complaint_source = Column(String(100), nullable=True) # e.g., Email, Portal, Phone
    customer_name = Column(String(150), nullable=True)
    
    # 2. Product & Batch Identification
    product_name = Column(String(150), nullable=True)
    product_strength = Column(String(50), nullable=True) # e.g., 500mg
    batch_number = Column(String(100), nullable=True)
    manufacturing_date = Column(String(50), nullable=True)
    expiry_date = Column(String(50), nullable=True)
    quantity_affected = Column(String(50), nullable=True) # e.g., "10 kg" or "100 bottles"
    
    # 3. Complaint Details
    complaint_type = Column(String(100), nullable=True) # e.g., Packaging, Efficacy, Contamination
    complaint_date = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    
    # 4. Initial Assessment & Priority
    initial_severity = Column(String(50), nullable=True) # Critical, Major, Minor
    priority = Column(String(50), nullable=True) # High, Medium, Low
    
    # AI Extractions & Insights (Bonus features)
    completeness_status = Column(String(50), nullable=True) # Complete, Incomplete
    completeness_feedback = Column(Text, nullable=True)
    root_cause_recommendation = Column(Text, nullable=True)
    capa_recommendation = Column(Text, nullable=True)
    risk_classification_reasoning = Column(Text, nullable=True)
    next_action = Column(String(200), nullable=True)
    risk_assessment_details = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    logs = relationship("AuditLog", back_populates="complaint", cascade="all, delete-orphan")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"))
    action = Column(String(100)) # "Create", "Update Field", "AI Extract"
    field_name = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    changed_by = Column(String(100), default="User") # "User", "AI Copilot"
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship
    complaint = relationship("Complaint", back_populates="logs")
