"""Manual test script — run the agent from the command line without WhatsApp.

Usage:
    python tests/manual_test.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.agent.orchestrator import run_agent

if __name__ == "__main__":
    print("Arogya Agent — manual test (type 'quit' to exit)\n")
    history = []
    while True:
        msg = input("Patient: ")
        if msg.lower() == "quit":
            break
        reply = run_agent(msg, conversation_history=history)
        print(f"ArogyaBot: {reply}\n")
        history.append({"role": "user", "content": msg})
        history.append({"role": "assistant", "content": reply})
