# enterprise-partner-governance-platform

Enterprise Partner Governance Platform agent scaffold for SharePoint, Office365,
Due Diligence, Contract Review, and Audit governance.

## Architecture

This project starts with a Governance Orchestrator built on AgentBase and
LangGraph. The graph is divided into deterministic agent nodes:

- Intake Agent: normalizes partner lifecycle tickets.
- DD Gate Agent: enforces `No DD Pass -> No Contract Review`.
- Contract Review Agent: prepares review rounds and mandatory department checks.
- SharePoint Agent: prepares official folder and permission actions.
- Audit Agent: emits audit events for every workflow transition.
- RBAC Agent: enforces role/action permission before workflow gates.
- AI Summary Agent: optionally summarizes blockers and next actions when an LLM is configured.

## Phase 1 Scope

Implemented foundation:

- Role-based access control with internal and external visibility rules.
- Partner ticket normalization.
- DD gate enforcement.
- DD rulebook and data source sync planning.
- Mandatory review matrix checks for initial trigger signals.
- Contract review round plan and reviewer task generation.
- Negotiation, Partner Portal Biz Gate, and Termination workflow planning.
- AI connector operation planning for DD, contract review, negotiation, risk scoring, and termination checklist.
- Dashboard snapshot generation for operational counters and review queues.
- Office365/Microsoft Graph connector planning for users, groups, mail, calendar, Teams, SharePoint, and OneDrive.
- Dry-run execution plan that orders all planned API operations and requires audit logging per step.
- Audit persistence planning for SharePoint `99_Audit_Trail` and Admin audit log append.
- SharePoint folder and permission action planning.
- Internal API contract registry for Admin, SharePoint, DD, Contract Review, and AI placeholders.
- Audit event generation across the deterministic workflow.

## Prerequisites

- Python 3.10+
- A GreenNode IAM Service Account

## Setup

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` for local development and configure credentials.
Do not commit `.env` or `.greennode.json`.

## Configure LLM

Set these values in `.env` when you want AI summaries or tool-calling:

```env
LLM_API_KEY=
LLM_BASE_URL=
LLM_MODEL=
```

Provider examples:

- GreenNode AIP: `LLM_BASE_URL=https://maas-llm-aiplatform-hcm.api.vngcloud.vn/v1`
- OpenAI: `LLM_BASE_URL=https://api.openai.com/v1`
- Ollama local: `LLM_BASE_URL=http://localhost:11434/v1`

## Configure Memory

Create memory later with `/agentbase-memory` and set:

```env
MEMORY_ID=
MEMORY_STRATEGY_ID=default
```

When `MEMORY_ID` is configured, requests must include:

```text
X-GreenNode-AgentBase-User-Id: test-user
X-GreenNode-AgentBase-Session-Id: test-session-1
```

## Run Locally

```powershell
python main.py
```

Test health:

```powershell
curl http://127.0.0.1:8080/health
```

Test an invocation:

```powershell
curl -X POST http://127.0.0.1:8080/invocations `
  -H "Content-Type: application/json" `
  -d "{\"ticket_id\":\"TCK-000001\",\"partner_name\":\"Haidilao\",\"tax_code\":\"123456789\",\"project_case\":\"DieuChinhPhi\",\"created_by\":\"biz.user\",\"dd_status\":\"Pass\",\"selected_departments\":[\"Legal\",\"FA\"],\"contract_signals\":[\"contains_payment_terms\"]}"
```

Run deterministic validation checks without starting the server:

```powershell
$env:PYTHONIOENCODING='utf-8'
$env:PYTHONUTF8='1'
python scripts\validate_governance_flow.py
```

## Deploy

Use `/agentbase-deploy` after local validation to build, push, and deploy to
AgentBase Runtime.
