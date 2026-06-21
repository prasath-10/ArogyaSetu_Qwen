# Architecture

This document will hold the full architecture diagram and explanation, required for hackathon submission.

## Components

- **WhatsApp Business Cloud API** — entry/exit point for all patient communication
- **FastAPI backend** — hosted on Alibaba Cloud ECS, receives webhook events
- **Agent Orchestrator** — manages the Qwen Cloud tool-calling loop
- **Qwen Cloud** — LLM for language understanding, triage reasoning, and multilingual replies
- **Tools** — `find_clinics`, `book_slot`, `alert_emergency`
- **PostgreSQL (Alibaba RDS)** — stores clinics, appointments, patient records
- **Redis** — stores short-term conversation/session memory

## Diagram

*(Add exported PNG/SVG diagram here before submission — e.g. `architecture.png`)*

## Data flow

1. Patient sends a WhatsApp message
2. Meta delivers it to our FastAPI webhook
3. Orchestrator builds the message history and calls Qwen Cloud
4. Qwen decides whether to call a tool (find_clinics / book_slot / alert_emergency) or reply directly
5. Tool results are fed back to Qwen, which produces the final natural-language reply
6. Reply is sent back to the patient via WhatsApp Cloud API
7. Moderate/critical cases are also written to the doctor review queue
