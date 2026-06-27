"""Quick e2e test script for the doctor cases flow."""
import sys, io, json
from urllib.request import urlopen, Request

def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    # Step 4-5: Check pending cases
    print("=" * 60)
    print("STEP 4-5: GET /api/cases (pending)")
    print("=" * 60)
    r = urlopen("http://localhost:8000/api/cases")
    cases = json.loads(r.read())
    print(f"Pending cases: {len(cases)}")
    for c in cases:
        print(f"  Case #{c['id']}: phone={c['patient_phone']}, severity={c['severity']}, status={c['status']}")
        print(f"    symptoms: {c['symptoms'][:80]}")

    if not cases:
        print("ERROR: No pending cases found!")
        sys.exit(1)

    case_id = cases[0]["id"]
    print(f"\nUsing case #{case_id} for review test.")

    # Step 6-7: Submit doctor review
    print("\n" + "=" * 60)
    print("STEP 6-7: POST /api/cases/review (mark as reviewed)")
    print("=" * 60)
    payload = json.dumps({
        "case_id": case_id,
        "doctor_notes": "Patient shows signs of acute cardiac distress. Ambulance dispatched. ECG and troponin test required on arrival.",
        "status": "reviewed",
    }).encode()
    req = Request(
        "http://localhost:8000/api/cases/review",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    r = urlopen(req)
    reviewed = json.loads(r.read())
    print(f"Review response status: {r.status}")
    print(f"  Case #{reviewed['id']}: status={reviewed['status']}, reviewed_at={reviewed['reviewed_at']}")
    print(f"  doctor_notes: {reviewed['doctor_notes']}")

    # Step 8: Confirm case is gone from pending
    print("\n" + "=" * 60)
    print("STEP 8: GET /api/cases (pending) — case should be gone")
    print("=" * 60)
    r = urlopen("http://localhost:8000/api/cases")
    remaining = json.loads(r.read())
    remaining_ids = [c["id"] for c in remaining]
    print(f"Pending cases: {len(remaining)}")
    if case_id in remaining_ids:
        print(f"FAIL: Case #{case_id} is still in pending list!")
        sys.exit(1)
    else:
        print(f"PASS: Case #{case_id} is no longer in pending list.")

    print("\n" + "=" * 60)
    print("ALL E2E TESTS PASSED ✓")
    print("=" * 60)


if __name__ == "__main__":
    main()

