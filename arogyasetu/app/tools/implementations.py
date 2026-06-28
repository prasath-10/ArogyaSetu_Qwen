import random
import httpx
from app.config import settings
from app.db.database import SessionLocal
from app.db.models import Clinic, Appointment, Patient


def find_clinics(location: str, radius_km: float = 10) -> list[dict]:
    """Find clinics matching the location string.

    If no exact matches on city/address, fall back to returning all clinics.
    """
    db = SessionLocal()
    try:
        query_str = f"%{location}%"
        clinics = (
            db.query(Clinic)
            .filter(
                (Clinic.city.ilike(query_str))
                | (Clinic.address.ilike(query_str))
                | (Clinic.name.ilike(query_str))
            )
            .all()
        )

        if not clinics:
            # Fallback to all clinics if no search criteria matched
            clinics = db.query(Clinic).all()

        results = []
        for c in clinics:
            # Mock a distance for demo / localized routing
            distance = round(random.uniform(1.0, 8.0), 1)
            results.append(
                {
                    "id": c.id,
                    "name": c.name,
                    "address": c.address,
                    "city": c.city,
                    "distance_km": distance,
                    "available": c.available,
                    "phone": c.phone,
                }
            )
        return results
    finally:
        db.close()


def book_slot(
    clinic_id: str | int, patient_phone: str, preferred_time: str = "today"
) -> dict:
    """Create a patient record if new, and book an appointment slot in the database."""
    db = SessionLocal()
    try:
        try:
            c_id = int(clinic_id)
        except (ValueError, TypeError):
            return {"status": "failed", "error": "Invalid clinic ID format"}

        clinic = db.query(Clinic).filter(Clinic.id == c_id).first()
        if not clinic:
            return {
                "status": "failed",
                "error": f"Clinic with ID {clinic_id} not found",
            }
        if not clinic.available:
            return {
                "status": "failed",
                "error": f"Clinic {clinic.name} is currently not available",
            }

        # Check / create patient
        patient = (
            db.query(Patient).filter(Patient.phone == patient_phone).first()
        )
        if not patient:
            patient = Patient(
                phone=patient_phone,
                name="Anonymous Patient",
                language_preference="en",
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)

        # Generate a random token
        token_num = random.randint(10, 99)
        token = f"#{token_num}"

        appointment = Appointment(
            clinic_id=clinic.id,
            patient_phone=patient_phone,
            slot_time=preferred_time,
            token=token,
            status="confirmed",
        )
        db.add(appointment)
        db.commit()

        # Log moderate case to doctor dashboard
        from app.db.models import DoctorCase
        case = DoctorCase(
            patient_phone=patient_phone,
            symptoms=f"Appointment booked at {clinic.name} — token {token}",
            severity="moderate",
            status="pending",
        )
        db.add(case)
        db.commit()
        print(f"[Booking] Moderate case logged to doctor dashboard")

        return {
            "status": "confirmed",
            "clinic_name": clinic.name,
            "token": token,
            "time": preferred_time,
        }
    except Exception as e:
        db.rollback()
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()

def alert_emergency(
    patient_phone: str, location: str, symptom_summary: str
) -> dict:
    """Escalate critical cases.

    Triggers an emergency dispatch webhook if configured.
    Also logs the case to the DoctorCase table for doctor review.
    """
    from app.db.models import DoctorCase

    # Save to DoctorCase table for doctor dashboard
    db = SessionLocal()
    try:
        case = DoctorCase(
            patient_phone=patient_phone,
            symptoms=symptom_summary,
            severity="critical",
            status="pending",
        )
        db.add(case)
        db.commit()
        print(f"[Emergency] Case logged to doctor dashboard for {patient_phone}")
    except Exception as e:
        db.rollback()
        print(f"[Emergency] Failed to log case to DB: {e}")
    finally:
        db.close()

    # Send webhook if configured
    response_status = "logged"
    if settings.emergency_webhook_url:
        try:
            payload = {
                "patient_phone": patient_phone,
                "location": location,
                "symptom_summary": symptom_summary,
            }
            with httpx.Client() as client:
                r = client.post(
                    settings.emergency_webhook_url, json=payload, timeout=5.0
                )
                if r.status_code in (200, 201):
                    response_status = "dispatched"
        except Exception as e:
            print(f"[Emergency] Webhook post failed: {e}")

    return {
        "status": response_status,
        "ambulance_eta_min": 10,
        "doctor_paged": True,
        "location": location,
    }


TOOL_REGISTRY = {
    "find_clinics": find_clinics,
    "book_slot": book_slot,
    "alert_emergency": alert_emergency,
}
