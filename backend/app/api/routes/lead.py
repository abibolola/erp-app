from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.lead import LeadCreate, LeadOut, LeadUpdate
from app.models.lead import Lead
from app.models.user import User
from app.core.permissions import requires_permission
from app.core.security import get_current_user

router = APIRouter(prefix="/leads", tags=["Leads"])

@router.post("/", response_model=LeadOut)
@requires_permission("create_lead")
def create_lead(
    lead: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_lead = Lead(**lead.dict(), created_by_id=current_user.id)
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    return new_lead

@router.get("/", response_model=list[LeadOut])
@requires_permission("view_crm")
def get_leads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Lead).filter(Lead.created_by_id == current_user.id).all()

@router.get("/{lead_id}", response_model=LeadOut)
@requires_permission("view_crm")
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.created_by_id == current_user.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.put("/{lead_id}", response_model=LeadOut)
@requires_permission("edit_crm")
def update_lead(
    lead_id: int,
    lead_update: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.created_by_id == current_user.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    for key, value in lead_update.dict(exclude_unset=True).items():
        setattr(lead, key, value)

    db.commit()
    db.refresh(lead)
    return lead
