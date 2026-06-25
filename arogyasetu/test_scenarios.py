import asyncio
import sys
sys.stdout.reconfigure(encoding='utf-8')
from app.agent.orchestrator import run_agent
from app.tools.implementations import TOOL_REGISTRY

# Mock DB dependent tools for the test
TOOL_REGISTRY['find_clinics'] = lambda location, severity: [{"id": 1, "name": f"Mock Clinic {location}", "type": "PHC", "distance_km": 2.5, "available_slots": 5}]
TOOL_REGISTRY['book_slot'] = lambda patient_name, clinic_id, time_preference, severity: {"status": "success", "booking_id": "MOCK-123", "clinic_id": clinic_id, "time": "2:00 PM"}
TOOL_REGISTRY['alert_emergency'] = lambda location, patient_condition: {"status": "dispatched", "ambulance_id": "AMB-404", "eta_mins": 10}

def test_scenarios():
    scenarios = [
        {"name": "Scenario 1 — LOW", "input": "I have a mild headache", "session_id": "test_sess_1"},
        {"name": "Scenario 2 — MODERATE", "input": "I have fever 103°F for 3 days", "session_id": "test_sess_2"},
        {"name": "Scenario 3 — CRITICAL", "input": "I have severe chest pain and cant breathe", "session_id": "test_sess_3"},
        {"name": "Scenario 4 — Tamil", "input": "எனக்கு காய்ச்சல் இருக்கிறது", "session_id": "test_sess_4"},
        {"name": "Scenario 5 — Hindi", "input": "मुझे बुखार है", "session_id": "test_sess_5"},
    ]
    
    print("=========================================")
    for s in scenarios:
        print(f"Testing {s['name']}...")
        reply = run_agent(s["input"], session_id=s["session_id"])
        
        reply_upper = reply.upper()
        severity = "LOW"
        if "CRITICAL" in reply_upper: severity = "CRITICAL"
        elif "MODERATE" in reply_upper: severity = "MODERATE"
        
        print(f"Input: {s['input']}")
        print(f"Severity Evaluated: {severity}")
        print(f"Reply Preview: {reply[:100]}...\n")

    # Scenario 6 - Multi-turn
    print("Testing Scenario 6 — Multi-turn memory...")
    sess6 = "test_sess_6"
    run_agent("I have fever", session_id=sess6)
    reply6 = run_agent("I am in Erode", session_id=sess6)
    print(f"Multi-turn reply preview: {reply6[:150]}...")
    print("=========================================")

if __name__ == "__main__":
    test_scenarios()
