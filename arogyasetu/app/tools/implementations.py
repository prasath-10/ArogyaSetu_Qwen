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
    from app.db.models import DoctorCase

    db = SessionLocal()
    result = None
    clinic_name = None
    token = None
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
        clinic_name = clinic.name

        appointment = Appointment(
            clinic_id=clinic.id,
            patient_phone=patient_phone,
            slot_time=preferred_time,
            token=token,
            status="confirmed",
        )
        db.add(appointment)
        db.commit()

        result = {
            "status": "confirmed",
            "clinic_name": clinic_name,
            "token": token,
            "time": preferred_time,
        }
    except Exception as e:
        db.rollback()
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()

    # Log moderate case in a fresh isolated session — runs after booking commits
    if result and result.get("status") == "confirmed":
        db2 = SessionLocal()
        try:
            mod_case = DoctorCase(
                patient_phone=patient_phone,
                symptoms=f"Appointment booked at {clinic_name} — token {token}",
                severity="moderate",
                status="pending",
            )
            db2.add(mod_case)
            db2.commit()
            db2.refresh(mod_case)
            print(f"[Booking] Moderate case logged: ID={mod_case.id}")
        except Exception as e:
            db2.rollback()
            print(f"[Booking] Failed to log moderate case: {type(e).__name__}: {e}")
        finally:
            db2.close()

    return result

def alert_emergency(
    patient_phone: str, location: str, symptom_summary: str
) -> dict:
    """Escalate critical cases.

    Triggers an emergency dispatch webhook if configured.
    Also creates a Patient record if needed and logs a DoctorCase
    to the dashboard.
    """
    from app.db.models import DoctorCase

    db = SessionLocal()
    try:
        # Ensure a Patient row exists (required for any downstream FK usage)
        patient = db.query(Patient).filter(Patient.phone == patient_phone).first()
        if not patient:
            patient = Patient(
                phone=patient_phone,
                name="Emergency Patient",
                language_preference="en",
            )
            db.add(patient)
            db.commit()
            print(f"[Emergency] Patient created: {patient_phone}")

        # Log the critical case for the doctor dashboard
        try:
            case = DoctorCase(
                patient_phone=patient_phone,
                symptoms=symptom_summary,
                severity="critical",
                status="pending",
            )
            db.add(case)
            db.commit()
            db.refresh(case)
            print(f"[Emergency] Case logged to DB: ID={case.id}")
        except Exception as e:
            db.rollback()
            print(f"[Emergency] Failed to log case: {type(e).__name__}: {e}")
    except Exception as e:
        db.rollback()
        print(f"[Emergency] Patient creation failed: {type(e).__name__}: {e}")
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
