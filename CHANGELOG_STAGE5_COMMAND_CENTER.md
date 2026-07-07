# Stage 5 - Agentic Command Center

Stage 5 is the final MedPack AI control-tower layer. It wraps Stages 1-4 into a single operational command packet.

## Added

- `backend/stage5_command_center.py`
  - Builds final command-center decision packet.
  - Produces priority code, command status, response window, owner, escalation owner, action cards, handoff packet, audit checklist, and agent briefing.

- `database/escalation_playbooks.json`
  - Editable playbook for risk levels, response times, owners, escalation owners, and cadence.

## New API endpoints

- `GET /api/stage5-reference-data`
- `POST /api/stage5-command-center`

## Dashboard additions

- `🧭 Stage 5: Agentic Command Center`
- `🧭 Stage 5 Standalone Agentic Command Center`
- `🧭 Stage 5 Playbook`
- New committee expander: `Stage 5 Command Center Agent Insights`

## What Stage 5 does

Stage 5 converts the previous layers into an action-oriented hospital command view:

1. Stage 1: item traceability / tasks / compliance context
2. Stage 2: usable stock and true shortage gap
3. Stage 3: transfer, supplier, substitute, escalation choices
4. Stage 4: cost, waste, ROI, executive value
5. Stage 5: owner-based command plan and handoff queue

## Example output

```text
Priority: P1
Command Status: ORANGE - Act this shift
Primary Owner: Supply Tech Lead
Escalation Owner: Charge Nurse
Response Window: 30 minutes
Commander Decision: Approve Stage 3 action path and complete transfer/order tasks.
```

## Safety

Stage 5 is deterministic and local by default. It does not require Groq/Gemini and does not change the no-freeze committee path. If Groq is selected, Groq only rewrites the wording; the Stage 5 facts remain locally calculated.
