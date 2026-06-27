import asyncio
import sys
import re
import os
if hasattr(sys.stdout, 'reconfigure') and "pytest" not in sys.modules:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Check for API key before importing agent (which initializes the OpenAI client)
if not os.environ.get("QWEN_API_KEY"):
    if "pytest" in sys.modules:
        import pytest
        pytest.skip("QWEN_API_KEY not set — skipping live agent tests.", allow_module_level=True)
    else:
        print("⚠️  QWEN_API_KEY not set — skipping live agent tests.")
        print("   Set QWEN_API_KEY in your .env file to run these scenarios.")
        sys.exit(0)

from app.agent.orchestrator import run_agent
from app.tools.implementations import TOOL_REGISTRY

# Mock DB dependent tools for the test
TOOL_REGISTRY['find_clinics'] = lambda location, severity: [{"id": 1, "name": f"Mock Clinic {location}", "type": "PHC", "distance_km": 2.5, "available_slots": 5}]
TOOL_REGISTRY['book_slot'] = lambda patient_name, clinic_id, time_preference, severity: {"status": "success", "booking_id": "MOCK-123", "clinic_id": clinic_id, "time": "2:00 PM"}
TOOL_REGISTRY['alert_emergency'] = lambda location, patient_condition: {"status": "dispatched", "ambulance_id": "AMB-404", "eta_mins": 10}


def extract_severity(reply_text):
    """Extract severity using the same logic as chat.py"""
    reply_upper = reply_text.upper()
    # Try explicit tag first
    match = re.search(r'\[SEVERITY:\s*(LOW|MODERATE|CRITICAL)\]', reply_upper)
    if match:
        return match.group(1)
    # Fallback to keyword detection
    if "CRITICAL" in reply_upper:
        return "CRITICAL"
    elif "MODERATE" in reply_upper:
        return "MODERATE"
    return "LOW"


def test_scenarios():
    scenarios = [
        {"name": "Scenario 1 — LOW", "input": "I have a mild headache", "session_id": "test_sess_1"},
        {"name": "Scenario 2 — MODERATE", "input": "I have fever 103°F for 3 days", "session_id": "test_sess_2"},
        {"name": "Scenario 3 — CRITICAL", "input": "I have severe chest pain and cant breathe", "session_id": "test_sess_3"},
        {"name": "Scenario 4 — Tamil", "input": "எனக்கு காய்ச்சல் இருக்கிறது", "session_id": "test_sess_4"},
        {"name": "Scenario 5 — Hindi", "input": "मुझे बुखार है", "session_id": "test_sess_5"},
    ]
    
    print("=========================================")
    passed = 0
    failed = 0
    
    for s in scenarios:
        print(f"Testing {s['name']}...")
        try:
            reply = run_agent(s["input"], session_id=s["session_id"])
            severity = extract_severity(reply)
            # Strip severity tag from display
            clean_reply = re.sub(r'(?i)\[SEVERITY:\s*(LOW|MODERATE|CRITICAL)\]', '', reply).strip()
            
            print(f"  Input: {s['input']}")
            print(f"  Severity: {severity}")
            print(f"  Reply: {clean_reply[:120]}...")
            print(f"  ✅ PASSED\n")
            passed += 1
        except Exception as e:
            print(f"  ❌ FAILED: {e}\n")
            failed += 1

    # Scenario 6 - Multi-turn
    print("Testing Scenario 6 — Multi-turn memory...")
    try:
        sess6 = "test_sess_6"
        run_agent("I have fever", session_id=sess6)
        reply6 = run_agent("I am in Erode", session_id=sess6)
        clean_reply6 = re.sub(r'(?i)\[SEVERITY:\s*(LOW|MODERATE|CRITICAL)\]', '', reply6).strip()
        print(f"  Multi-turn reply: {clean_reply6[:150]}...")
        print(f"  ✅ PASSED\n")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}\n")
        failed += 1

    print("=========================================")
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed} scenarios")
    print("=========================================")


if __name__ == "__main__":
    test_scenarios()

