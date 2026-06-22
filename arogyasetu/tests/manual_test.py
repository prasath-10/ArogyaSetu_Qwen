"""Manual test script — run the agent from the command line without WhatsApp.

Usage:
    python tests/manual_test.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.agent.orchestrator import run_agent
from app.agent.memory import session_memory

if __name__ == "__main__":
    print("Arogya Agent — manual test (type 'quit' to exit)\n")

    # Clear previous history for manual-test-session to start fresh
    session_id = "manual-test-session"
    session_memory.clear_history(session_id)

    while True:
        try:
            msg = input("Patient: ")
        except (KeyboardInterrupt, EOFError):
            break
        if msg.lower() == "quit":
            break
        if not msg.strip():
            continue

        # run_agent automatically fetches history from memory.py based on session_id
        reply = run_agent(msg, session_id=session_id)
        print(f"ArogyaBot: {reply}\n")
