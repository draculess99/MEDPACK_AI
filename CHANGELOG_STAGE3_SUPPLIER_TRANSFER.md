# MedPack AI Stage 3 — Supplier + Transfer Intelligence

Stage 3 moves MedPack AI from shortage detection into shortage resolution.

## Added

- Internal transfer recommendations between departments.
- Supplier delay and backup-vendor risk scoring.
- Substitute-item rules and availability checks.
- Full Stage 3 control-tower action plan.
- New Stage 3 dashboard panel.
- New Stage 3 reference-data tab for vendors and substitute rules.
- Groq narrative context now includes Stage 3 facts when Groq mode is selected.

## New backend modules

- `backend/transfer_optimizer.py`
- `backend/supplier_risk.py`
- `backend/substitution_engine.py`
- `backend/stage3_action_plan.py`

## New data files

- `database/vendor_state.json`
- `database/substitution_rules.json`

## New endpoints

- `GET /api/stage3-reference-data`
- `POST /api/transfer-recommendation`
- `POST /api/supplier-risk`
- `POST /api/substitute-options`
- `POST /api/stage3-action-plan`

## What Stage 3 answers

Stage 1: What do we have and is it safe?
Stage 2: Are we truly short after using usable stock?
Stage 3: How do we fix the shortage before it hits the bedside?

## Safety note

Substitution rules are demo-only. In a real hospital, substitute rules would require approval from clinical governance, pharmacy/materials management, infection control, and local policy owners.
