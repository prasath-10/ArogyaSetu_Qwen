"""Actual implementations of agent tools. Day 1: stubbed with mock data.
Replace with real DB / external API calls as the project progresses.
"""


def find_clinics(location: str, radius_km: float = 10) -> list[dict]:
    return [
        {"id": "clinic_001", "name": "Erode PHC", "distance_km": 3.2, "available": True},
        {"id": "clinic_002", "name": "Bhavani Govt Hospital", "distance_km": 7.8, "available": True},
    ]


def book_slot(clinic_id: str, patient_phone: str, preferred_time: str = "today") -> dict:
    return {
        "status": "confirmed",
        "clinic_id": clinic_id,
        "token": "#14",
        "time": preferred_time,
    }


def alert_emergency(patient_phone: str, location: str, symptom_summary: str) -> dict:
    return {
        "status": "dispatched",
        "ambulance_eta_min": 8,
        "doctor_paged": True,
        "location": location,
    }


TOOL_REGISTRY = {
    "find_clinics": find_clinics,
    "book_slot": book_slot,
    "alert_emergency": alert_emergency,
}
