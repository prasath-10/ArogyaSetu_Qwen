"""Tool schemas exposed to Qwen for function calling."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "find_clinics",
            "description": "Find nearby clinics or hospitals given a patient location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City or area name, e.g. 'Erode'"},
                    "radius_km": {"type": "number", "description": "Search radius in kilometers"},
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_slot",
            "description": "Book an appointment slot at a clinic for a patient.",
            "parameters": {
                "type": "object",
                "properties": {
                    "clinic_id": {"type": "string"},
                    "patient_phone": {"type": "string"},
                    "preferred_time": {"type": "string", "description": "ISO timestamp or 'today'/'tomorrow' + time"},
                },
                "required": ["clinic_id", "patient_phone"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "alert_emergency",
            "description": "Escalate to emergency services (ambulance + on-call doctor) for critical symptoms.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_phone": {
                        "type": "string",
                        "description": "Patient's WhatsApp phone number.",
                    },
                    "location": {
                        "type": "string",
                        "description": "Patient's location or nearest landmark. Use 'Unknown — follow up required' if not provided.",
                    },
                    "symptom_summary": {
                        "type": "string",
                        "description": "Compact clinical summary including symptoms, onset time, and any collected patient details.",
                    },
                    "patient_name": {
                        "type": "string",
                        "description": "Patient's name as collected during the conversation. Optional.",
                    },
                    "patient_age": {
                        "type": "integer",
                        "description": "Patient's age in years as collected during the conversation. Optional.",
                    },
                    "location_detail": {
                        "type": "string",
                        "description": "Verbatim location or landmark text provided by the patient. Optional — supplements the 'location' field.",
                    },
                },
                "required": ["patient_phone", "location", "symptom_summary"],
            },
        },
    },
]
