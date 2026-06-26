from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import datetime

from app.db.database import get_db
from app.db.models import DoctorCase

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────

class CaseOut(BaseModel):
    id: int
    patient_phone: str
    symptoms: str
    severity: str
    created_at: datetime.datetime | None = None
    reviewed_at: datetime.datetime | None = None
    doctor_notes: str | None = None
    status: str

    class Config:
        from_attributes = True


class ReviewRequest(BaseModel):
    case_id: int
    doctor_notes: str
    status: str = "reviewed"


# ── Endpoints ────────────────────────────────────────────────────────

@router.get("/cases", response_model=list[CaseOut])
def list_pending_cases(db: Session = Depends(get_db)):
    """Return all doctor cases with status 'pending'."""
    cases = (
        db.query(DoctorCase)
        .filter(DoctorCase.status == "pending")
        .order_by(DoctorCase.created_at.desc())
        .all()
    )
    return cases


@router.post("/cases/review", response_model=CaseOut)
def review_case(payload: ReviewRequest, db: Session = Depends(get_db)):
    """Doctor submits a review for an existing case."""
    case = db.query(DoctorCase).filter(DoctorCase.id == payload.case_id).first()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if payload.status not in ("reviewed", "resolved"):
        raise HTTPException(
            status_code=422,
            detail="status must be 'reviewed' or 'resolved'",
        )

    case.doctor_notes = payload.doctor_notes
    case.status = payload.status
    case.reviewed_at = datetime.datetime.utcnow()

    db.commit()
    db.refresh(case)
    return case
