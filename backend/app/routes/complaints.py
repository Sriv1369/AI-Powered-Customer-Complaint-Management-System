from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import datetime
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/complaints", tags=["complaints"])

def generate_complaint_code(db: Session) -> str:
    current_year = datetime.datetime.now().year
    # Count current complaints this year
    count = db.query(models.Complaint).filter(
        models.Complaint.complaint_code.like(f"CC-{current_year}-%")
    ).count()
    return f"CC-{current_year}-{(count + 1):04d}"

@router.post("", response_model=schemas.ComplaintResponse, status_code=status.HTTP_201_CREATED)
def create_complaint(complaint_in: schemas.ComplaintCreate, db: Session = Depends(get_db)):
    code = generate_complaint_code(db)
    
    db_complaint = models.Complaint(
        complaint_code=code,
        status=complaint_in.status or "Pending Triage",
        complaint_source=complaint_in.complaint_source,
        customer_name=complaint_in.customer_name,
        product_name=complaint_in.product_name,
        product_strength=complaint_in.product_strength,
        batch_number=complaint_in.batch_number,
        manufacturing_date=complaint_in.manufacturing_date,
        expiry_date=complaint_in.expiry_date,
        quantity_affected=complaint_in.quantity_affected,
        complaint_type=complaint_in.complaint_type,
        complaint_date=complaint_in.complaint_date,
        description=complaint_in.description,
        initial_severity=complaint_in.initial_severity,
        priority=complaint_in.priority
    )
    
    db.add(db_complaint)
    db.commit()
    db.refresh(db_complaint)
    
    # Log initial creation in AuditLog
    log = models.AuditLog(
        complaint_id=db_complaint.id,
        action="Create",
        changed_by="User",
        timestamp=datetime.datetime.utcnow()
    )
    db.add(log)
    db.commit()
    db.refresh(db_complaint)
    
    return db_complaint

@router.get("", response_model=List[schemas.ComplaintResponse])
def list_complaints(db: Session = Depends(get_db)):
    return db.query(models.Complaint).order_by(models.Complaint.created_at.desc()).all()

@router.get("/{complaint_id}", response_model=schemas.ComplaintResponse)
def get_complaint(complaint_id: int, db: Session = Depends(get_db)):
    db_complaint = db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()
    if not db_complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return db_complaint

@router.put("/{complaint_id}", response_model=schemas.ComplaintResponse)
def update_complaint(complaint_id: int, complaint_in: schemas.ComplaintUpdate, db: Session = Depends(get_db)):
    db_complaint = db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()
    if not db_complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    update_data = complaint_in.dict(exclude_unset=True)
    
    # Audit trail comparison
    audit_logs = []
    now = datetime.datetime.utcnow()
    
    for field, new_value in update_data.items():
        old_value = getattr(db_complaint, field)
        # Check if actually changed
        if str(old_value) != str(new_value) and new_value is not None:
            # Create audit log record
            log = models.AuditLog(
                complaint_id=db_complaint.id,
                action="Update Field",
                field_name=field,
                old_value=str(old_value) if old_value is not None else "",
                new_value=str(new_value),
                changed_by="User",
                timestamp=now
            )
            audit_logs.append(log)
            setattr(db_complaint, field, new_value)
            
    if audit_logs:
        db.add_all(audit_logs)
        db_complaint.updated_at = now
        db.commit()
        db.refresh(db_complaint)
        
    return db_complaint

@router.delete("/{complaint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_complaint(complaint_id: int, db: Session = Depends(get_db)):
    db_complaint = db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()
    if not db_complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    db.delete(db_complaint)
    db.commit()
    return None
