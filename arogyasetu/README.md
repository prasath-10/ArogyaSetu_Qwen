ArogyaSetu is a production-grade, autonomous healthcare-access agent built on Qwen Cloud and deployed on Alibaba Cloud infrastructure. It is designed to triage patient symptoms over WhatsApp, route moderate cases to nearby clinics, escalate critical cases to emergency services, and keep a licensed doctor in the loop at every decision point — bringing reliable healthcare access to rural patients who don't have one nearby.

Built for the **Global AI Hackathon with Qwen Cloud** — Track 4: Autopilot Agent.

## Technical Architecture Overview

ArogyaSetu implements a single-agent, tool-calling orchestration pipeline backed by Qwen Cloud's reasoning models. The system utilizes Qwen Cloud's OpenAI-compatible function-calling API, a FastAPI stateless webhook runtime, and a persistent PostgreSQL + Redis memory layer to deliver grounded, language-aware, and safety-reviewed triage decisions.

```
                         [ Patient WhatsApp Message ]
                                     │
                                     ▼
                       [ WhatsApp Cloud API Webhook ]
                                     │
                                     ▼
                    [ Redis Session Memory Load ]
                                     │
                                     ▼
                       [ FastAPI Agent Orchestrator ]
                                     │
                                     ▼
                         [ Qwen Cloud Reasoning ]
                              (qwen-max)
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           ▼                         ▼                         ▼
      find_clinics()             book_slot()           alert_emergency()
   (clinic lookup tool)      (appointment tool)        (emergency escalation)
           │                         │                         │
           └─────────────────────────┼─────────────────────────┘
                                     │
                                     ▼
                  [ PostgreSQL — Alibaba RDS persistent store ]
                                     │
                                     ▼
                      [ Redis Session Memory Sync ]
                                     │
                                     ▼
                       [ Reply Sent via WhatsApp ]
                                     │
                                     ▼
                     [ Doctor Review Dashboard Queue ]
```

## Core Features and Capabilities

- **Multilingual symptom triage**: Understands and replies in Tamil, Hindi, and English — patients message in their own language, no translation step required from them.
- **Three-tier severity routing**: Classifies every message as low / moderate / critical and routes accordingly — self-care guidance, same-day clinic booking, or immediate emergency escalation.
- **Tool-calling agent loop**: Qwen Cloud function-calling drives `find_clinics`, `book_slot`, and `alert_emergency` — the model decides which tool to invoke and when, rather than following a fixed script.
- **Human-in-the-loop safety**: The agent never gives a final diagnosis or prescribes medication. Every moderate or critical case is pushed to a doctor review queue before treatment proceeds.
- **Persistent memory**: PostgreSQL stores clinics, appointments, and patient history; Redis holds short-term conversation context across a session.
- **WhatsApp-native delivery**: No app download required — works on any phone with WhatsApp, which is critical for rural reach.
- **FastAPI REST backend**: Webhook-driven architecture with a `/health` endpoint and auto-generated Swagger docs.
- **Alibaba Cloud deployment**: Containerized backend deployed on Alibaba Cloud ECS with PostgreSQL on Alibaba RDS.

## Agent Persona and Tool Design

ArogyaSetu uses a single reasoning agent (rather than multiple sequential agents) with three specialized tools it can call as needed:

- **ArogyaBot (system persona)**: A calm, warm triage assistant. Replies in the patient's language, keeps messages short for WhatsApp, and never sounds robotic or clinical.
- **`find_clinics`**: Looks up nearby clinics or hospitals given a patient's location and search radius.
- **`book_slot`**: Books a same-day or next-day appointment slot at a given clinic for a patient.
- **`alert_emergency`**: Bypasses normal booking and immediately dispatches emergency services plus an on-call doctor page, used only for critical symptoms (chest pain, breathlessness, severe bleeding, loss of consciousness, stroke signs).

## Documentation Index

Detailed design specs and guides are organized within the `docs/` directory:

- **Architecture and data flow**: [`docs/architecture.md`](docs/architecture.md) — component breakdown, message flow, and diagram notes.
- **Deployment guide**: `docs/deployment.md` *(added at deployment step)* — Alibaba Cloud ECS + RDS setup and deployment proof.

## Quick Start & Installation

### Local Developer Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/arogyasetu.git
cd arogyasetu

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# edit .env and add your QWEN_API_KEY
```

### CLI Test Execution (no WhatsApp required)

```bash
# Launch the interactive manual test shell
python tests/manual_test.py
```

```
Arogya Agent — manual test (type 'quit' to exit)

Patient: I have had a fever of 103°F and a cough for 3 days
ArogyaBot: That sounds uncomfortable — let's get you seen today...
```

### FastAPI Web Server Execution

```bash
# Launch the API server locally
uvicorn app.main:app --reload --port 8000
```

- Health check: `http://localhost:8000/health`
- Interactive Swagger UI: `http://localhost:8000/docs`

### Connecting WhatsApp

Point your WhatsApp webhook URL (e.g. via ngrok during local dev) to:

```
POST https://<your-domain>/api/webhook
```

Use the same `WHATSAPP_VERIFY_TOKEN` value in both `.env` and the Meta App dashboard.

## Production Deployment Workflow

ArogyaSetu is containerized and deployed to Alibaba Cloud:

```bash
# Build the container image
docker build -t arogyasetu-agent:latest .

# Tag and push to your Alibaba Container Registry instance
docker tag arogyasetu-agent:latest registry.cn-hangzhou.aliyuncs.com/<namespace>/arogyasetu-agent:latest
docker push registry.cn-hangzhou.aliyuncs.com/<namespace>/arogyasetu-agent:latest
```

**Provision on Alibaba Cloud ECS**: Deploy the pushed container on an ECS instance, with PostgreSQL provisioned via Alibaba Cloud RDS and connection secrets managed via environment variables (or Alibaba Cloud KMS for production-grade secret management).

## System Observability and Verification

Run the test suite to verify pipeline integrity:

```bash
pytest tests/ -v
```

## Project Structure

```
arogyasetu/
├── app/
│   ├── main.py                  # FastAPI entrypoint
│   ├── config.py                # Settings (env vars)
│   ├── agent/
│   │   ├── orchestrator.py      # Core agent loop (tool-calling)
│   │   ├── qwen_client.py       # Qwen Cloud API wrapper
│   │   └── prompts.py           # System prompt / triage instructions
│   ├── tools/
│   │   ├── schemas.py           # Tool definitions (JSON schema for Qwen)
│   │   └── implementations.py   # Actual tool logic (DB calls, etc.)
│   ├── api/
│   │   └── whatsapp.py          # WhatsApp webhook routes
│   └── db/                      # DB models
├── docs/
│   └── architecture.md
├── tests/
│   └── manual_test.py
├── .env.example
├── requirements.txt
├── LICENSE
└── README.md
```

## Hackathon Submissions & Demos

This section will list system validation runs and screenshots showcasing the working state of the agent, its memory, deployment, and safety guardrails, to be completed before submission.

### 1. System Architecture
*(Add architecture diagram screenshot here)* — high-level overview of the agent orchestration pipeline showing how the orchestrator, Qwen Cloud, and the three tools cooperate.

### 2. Conversation Trace
*(Add screenshot here)* — a real WhatsApp conversation showing triage in action across the three severity tiers (low, moderate, critical).

### 3. Persistent Memory
*(Add screenshot here)* — demonstrating the PostgreSQL appointment record and Redis session memory across a multi-turn conversation.

### 4. Alibaba Cloud Deployment
*(Add screenshot/recording here)* — confirms the FastAPI service is containerized and running on Alibaba Cloud ECS, with a linked code file proving use of Alibaba Cloud services.

### 5. Safety Guardrails
*(Add screenshot here)* — showcases the human-in-the-loop doctor review queue and the agent's refusal to diagnose or prescribe.

### 6. Demo Video
*(Add YouTube/Vimeo link here)* — ~3 minute walkthrough of the full patient-to-appointment flow.

## Roadmap

- [x] Day 1 — Repo scaffold, Qwen agent loop, stubbed tools, manual CLI test
- [ ] Day 2 — Real PostgreSQL models for clinics/appointments, Redis session memory
- [ ] Day 3 — WhatsApp end-to-end integration, multilingual testing (Tamil/Hindi/English)
- [ ] Day 4 — Emergency escalation flow, doctor review dashboard
- [ ] Day 5 — Deploy to Alibaba Cloud, record deployment proof
- [ ] Day 6 — Architecture diagram, demo video, polish README
- [ ] Day 7 — Submission (Devpost, repo, video, blog post)

## Safety Note

This agent is a **triage and routing assistant**, not a diagnostic tool. It never provides a final diagnosis or prescribes medication — every moderate or critical case is reviewed by a licensed human doctor before treatment proceeds.

## License

MIT License

Copyright (c) 2026 ArogyaSetu Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
