import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    complaint_code = Column(String(50), unique=True, index=True)  # e.g., CC-2026-0001
    status = Column(String(50), default="Pending Triage")  # Pending Triage, Under Investigation, Resolved

    # 1. Origin & Customer Details
    complaint_source = Column(String(100), nullable=True)  # Email, Customer Portal, Phone Call, Letter, Regulatory Agency
    customer_name = Column(String(150), nullable=True)

    # 2. Product & Batch Identification
    product_name = Column(String(150), nullable=True)
    product_strength = Column(String(50), nullable=True)  # e.g., 500mg, IP/BP
    batch_number = Column(String(100), nullable=True)
    manufacturing_date = Column(String(50), nullable=True)
    expiry_date = Column(String(50), nullable=True)
    quantity_affected = Column(String(50), nullable=True)  # e.g., "15 kg" or "100 bottles"

    # 3. Complaint Details
    complaint_type = Column(String(100), nullable=True)  # Packaging Integrity, Contamination, Efficacy / Substandard, Adverse Event, Other
    complaint_date = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)

    # 4. Initial Assessment & Priority
    initial_severity = Column(String(50), nullable=True)  # Critical, Major, Minor
    priority = Column(String(50), nullable=True)  # High, Medium, Low

    # 5. AI Co-Pilot Risk Assessment & Quality Analysis
    completeness_status = Column(String(50), nullable=True)  # Complete, Incomplete
    completeness_feedback = Column(Text, nullable=True)
    root_cause_recommendation = Column(Text, nullable=True)
    capa_recommendation = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    risk_classification_reasoning = Column(Text, nullable=True)
    next_action = Column(String(250), nullable=True)
    risk_assessment_details = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    logs = relationship("AuditLog", back_populates="complaint", cascade="all, delete-orphan", order_by="desc(AuditLog.timestamp)")

    def to_dict(self):
        return {
            "id": self.id,
            "complaint_code": self.complaint_code,
            "status": self.status,
            "complaint_source": self.complaint_source or "",
            "customer_name": self.customer_name or "",
            "product_name": self.product_name or "",
            "product_strength": self.product_strength or "",
            "batch_number": self.batch_number or "",
            "manufacturing_date": self.manufacturing_date or "",
            "expiry_date": self.expiry_date or "",
            "quantity_affected": self.quantity_affected or "",
            "complaint_type": self.complaint_type or "",
            "complaint_date": self.complaint_date or "",
            "description": self.description or "",
            "initial_severity": self.initial_severity or "",
            "priority": self.priority or "",
            "completeness_status": self.completeness_status or "",
            "completeness_feedback": self.completeness_feedback or "",
            "root_cause_recommendation": self.root_cause_recommendation or "",
            "capa_recommendation": self.capa_recommendation or "",
            "summary": self.summary or "",
            "risk_classification_reasoning": self.risk_classification_reasoning or "",
            "next_action": self.next_action or "",
            "risk_assessment_details": self.risk_assessment_details or "",
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "logs": [log.to_dict() for log in self.logs]
        }


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"))
    action = Column(String(100))  # "Create", "Update Field", "AI Extract", "Sign Record"
    field_name = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    changed_by = Column(String(100), default="User")  # "User", "AI Copilot"
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship
    complaint = relationship("Complaint", back_populates="logs")

    def to_dict(self):
        return {
            "id": self.id,
            "complaint_id": self.complaint_id,
            "action": self.action,
            "field_name": self.field_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "changed_by": self.changed_by,
            "timestamp": self.timestamp
        }
