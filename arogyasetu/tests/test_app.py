import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal, engine
from app.db.models import Base, Clinic
from app.agent.memory import session_memory


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    # Make sure we use SQLite or a separate db, but since CI has PG and local has PG, we can run Base.metadata.create_all
    Base.metadata.create_all(bind=engine)
    yield


def test_health_check():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "service": "arogya-agent"}


def test_db_setup_and_seed():
    db = SessionLocal()
    try:
        # Check if clinics were seeded
        clinics = db.query(Clinic).all()
        assert len(clinics) > 0
        assert any(c.city == "Erode" for c in clinics)
    finally:
        db.close()


def test_session_memory():
    session_id = "test-session-123"
    session_memory.clear_history(session_id)

    # Test blank history
    history = session_memory.get_history(session_id)
    assert history == []

    # Test add message
    session_memory.add_message(session_id, "user", "Hello")
    session_memory.add_message(session_id, "assistant", "Hi there")

    history = session_memory.get_history(session_id)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Hi there"

    session_memory.clear_history(session_id)
    assert session_memory.get_history(session_id) == []


def test_get_patient_case_endpoint():
    from app.db.models import DoctorCase
    import datetime

    db = SessionLocal()
    try:
        # Create a mock DoctorCase
        test_phone = "test-patient-phone-999"
        # Cleanup if exists
        db.query(DoctorCase).filter(DoctorCase.patient_phone == test_phone).delete()
        db.commit()

        # Try GET before case is reviewed (should return has_update=False)
        with TestClient(app) as client:
            response = client.get(f"/api/cases/patient/{test_phone}")
            assert response.status_code == 200
            assert response.json() == {"has_update": False}

            # Create case with status reviewed
            case = DoctorCase(
                patient_phone=test_phone,
                symptoms="Fever and dry cough",
                severity="critical",
                status="reviewed",
                doctor_notes="Take paracetamol and rest.",
                reviewed_at=datetime.datetime.utcnow(),
            )
            db.add(case)
            db.commit()
            db.refresh(case)

            response = client.get(f"/api/cases/patient/{test_phone}")
            assert response.status_code == 200
            data = response.json()
            assert data["has_update"] is True
            assert data["doctor_notes"] == "Take paracetamol and rest."
            assert data["status"] == "reviewed"
            assert data["case_id"] == str(case.id)

            # Cleanup
            db.delete(case)
            db.commit()
    finally:
        db.close()

