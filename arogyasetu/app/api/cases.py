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
    # Collected during critical triage conversation
    patient_name: str | None = None
    patient_age: int | None = None
    location_detail: str | None = None

    class Config:
        from_attributes = True


class ReviewRequest(BaseModel):
    case_id: int
    doctor_notes: str
    status: str = "reviewed"


# ── Endpoints ────────────────────────────────────────────────────────

@router.get("/cases", response_model=list[CaseOut])
def list_cases(status: str | None = None, db: Session = Depends(get_db)):
    """Return doctor cases, optionally filtered by status.

    If status is omitted the endpoint returns only pending cases (backwards-compatible).
    Pass status=all to retrieve every case.
    """
    query = db.query(DoctorCase)
    if status and status != "all":
        query = query.filter(DoctorCase.status == status)
    elif not status:
        query = query.filter(DoctorCase.status == "pending")
    cases = query.order_by(DoctorCase.created_at.desc()).all()
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


@router.get("/cases/patient/{session_id}")
def get_patient_case(session_id: str, db: Session = Depends(get_db)):
    """Look up a DoctorCase for a patient session, checking for doctor reviews."""
    case = (
        db.query(DoctorCase)
        .filter(DoctorCase.patient_phone == session_id)
        .order_by(DoctorCase.created_at.desc())
        .first()
    )

    if case and case.status in ("reviewed", "resolved") and case.doctor_notes:
        return {
            "has_update": True,
            "doctor_notes": case.doctor_notes,
            "status": case.status,
            "reviewed_at": case.reviewed_at.isoformat() if case.reviewed_at else None,
            "case_id": str(case.id),
        }

    return {"has_update": False}
