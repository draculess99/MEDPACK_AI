# MedPack AI: Hospital Supply Shortage Prediction & Packing Priority System

**MedPack AI** is a healthcare logistics project that predicts hospital supply demand and converts shortage risk into warehouse packing action before the shortage reaches the bedside.

It combines a **Streamlit dashboard**, **Flask API**, **XGBoost/fallback machine-learning model**, **deterministic shortage rules**, **packing optimization**, **JSON memory**, and a five-agent **ADK-style decision committee**.

> SafeStaff AI focused on people: ER wait-time risk and nurse staffing support. MedPack AI focuses on supplies: predicting what the hospital will run short of and telling the warehouse what to pack first.

---

## Project Story

Hospitals do not only fail from a lack of nurses. They also fail when critical supplies are not packed, staged, replenished, or escalated fast enough.

When an emergency department, ICU, surgery floor, or labor and delivery unit starts consuming supplies faster than the warehouse can respond, nurses lose time searching for IV kits, oxygen masks, PPE gowns, saline flushes, catheters, monitoring leads, and wound-care packs. That delay becomes a patient-flow problem.

MedPack AI turns this operational chain into a decision-support system:

```text
Hospital telemetry → 24h demand forecast → shortage-risk rules → packing-priority optimizer → agent committee recommendation → JSON memory feedback
```

The result is a practical logistics app for a hospital supply room or warehouse team: **what item is at risk, where it is needed, how urgent it is, how much to pack, and whether to escalate.**

---

## Core Features

- **24-hour supply demand forecasting** using XGBoost, with RandomForest/deterministic fallback support.
- **Shortage-risk classification** into `Low`, `Medium`, `High`, and `Critical`.
- **Packing-priority optimizer** that weighs shortage gap, clinical criticality, patient acuity, department importance, supplier delay, usage rate, and pack time.
- **Top 5 Supplies to Pack First** queue now powered by the same backend ML/rules/optimizer pipeline as the main decision flow.
- **Five-agent committee** for demand, inventory risk, packing priority, clinical safety, and final recommendation.
- **Transparent JSON memory** that logs prediction deltas, rolling usage averages, trend direction, and event history.
- **No PHI design**: only operational signals are used; no names, patient IDs, MRNs, diagnoses, or individual patient records are stored.
- **Deployment-ready backend/frontend split** for Railway, Render, or similar platforms.

---

## App Architecture

```text
frontend/dashboard.py
        │
        ▼
backend/server.py  ────────────────┐
        │                           │
        ├── backend/model.py         │  ML demand forecast
        ├── backend/shortage_rules.py│  deterministic safety thresholds
        ├── backend/packing_optimizer.py
        ├── backend/packing_queue.py │  real top-5 packing queue
        ├── backend/supply_memory.py │  JSON memory + audit trail
        └── backend/agents/adk_agents.py
```

---

## How the Decision Pipeline Works

### 1. Machine Learning Forecast

`backend/model.py` predicts `actual_usage_next_24h` from operational telemetry:

- department
- item name/category
- current stock
- patient volume
- acuity level
- procedure count
- recent usage rate
- supplier delay
- day/hour/season
- reorder point
- supplier reliability
- clinical criticality
- pack time

The project prefers XGBoost. If XGBoost is unavailable, it falls back safely.

### 2. Shortage-Risk Rules

`backend/shortage_rules.py` compares forecasted demand against current stock.

Risk is calculated from:

- `shortage_gap = predicted_24h_demand - current_stock`
- `coverage_ratio = current_stock / predicted_24h_demand`

The rules intentionally use conservative thresholds. Either a large shortage gap or a weak coverage ratio can elevate the risk level.

### 3. Packing Optimizer

`backend/packing_optimizer.py` turns risk into action:

- priority score
- recommended pack quantity
- escalation flag
- plain-English warehouse instruction

### 4. Agentic Committee

`backend/agents/adk_agents.py` simulates a practical ADK-style agent committee:

1. Demand Forecast Agent
2. Inventory Risk Agent
3. Packing Priority Agent
4. Clinical Safety Agent
5. Final Recommendation Agent

The default implementation is deterministic and zero-token-cost, so the app can run without a paid LLM key.

### 5. Memory Feedback Loop

`backend/supply_memory.py` stores state in:

```text
database/supply_memory_state.json
database/supply_memory_events.jsonl
```

This allows the app to track actual usage after the forecast and update rolling memory over time.

---

## How to Run Locally

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the local orchestrator

```bash
python app.py
```

### 3. Open the app

```text
Dashboard: http://127.0.0.1:8502
Backend:   http://127.0.0.1:5001/health
```

---

## Deployment

MedPack AI should be deployed as two services.

### Backend service

Start command:

```bash
./start_backend.sh
```

Health check:

```text
/health
```

### Frontend service

Start command:

```bash
./start_frontend.sh
```

Required frontend environment variable:

```text
MEDPACK_API_BASE_URL=https://YOUR-BACKEND-DOMAIN
```

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for the full Railway/Render-style guide.

---

## API Endpoints

| Endpoint | Method | Purpose |
|---|---:|---|
| `/health` | GET | Backend health check |
| `/api/inventory` | GET | Current inventory snapshot |
| `/api/packing-queue?limit=5` | GET | Ranked supplies to pack first |
| `/api/predict-supply-demand` | POST | 24h demand forecast |
| `/api/shortage-risk` | POST | Risk classification |
| `/api/packing-priority` | POST | Packing recommendation |
| `/api/run-medpack-committee` | POST | Full committee pipeline |
| `/api/supply-memory` | GET | Current memory state |
| `/api/update-supply-memory` | POST | Update memory from actual usage |
| `/api/supply-memory-events` | GET | Recent audit events |

---

## Data Design

The app can run with fully synthetic no-PHI operational data. It can also ingest a Kaggle hospital supply-chain CSV if placed here:

```text
database/raw/kaggle_hospital_supply_chain.csv
```

If fields are missing, the loader maps what it can and synthesizes the operational variables needed for the simulation.

---

## No-PHI Guardrail

MedPack AI is designed as an operational simulation and decision-support system. It does **not** require or generate:

- patient names
- patient IDs
- medical record numbers
- diagnoses
- addresses
- phone numbers
- individual medical histories

It only uses high-level operational signals such as patient volume, acuity level, procedure count, department, stock level, and usage rate.

---

## Testing

```bash
pytest
```

The tests cover:

- data generation/loading
- model prediction
- shortage rules
- packing optimizer
- supply memory
- Flask API health checks

---

## Competition/Portfolio Pitch

**MedPack AI predicts hospital supply shortages and tells the warehouse what to pack first.**

It is built for the real gap between hospital operations and supply-chain execution. The system does not stop at a prediction. It turns the forecast into a risk tier, the risk tier into a packing quantity, and the packing quantity into a plain-English operational recommendation reviewed by an agentic committee.

This is where the project becomes more than a dashboard: it is a decision bridge between clinical demand and warehouse action.

---

## Suggested Project Title

**MedPack AI: Predicting Hospital Supply Shortages and Prioritizing Warehouse Packing Before Bedside Risk**

## Windows 11 Quick Start

Use the Windows launchers included at the project root.

**One-click local run:**

```bat
RUN_ME.bat
```

This installs dependencies, prepares the data/model if needed, starts the Flask backend, and starts the Streamlit dashboard.

Local URLs:

```text
Backend health check: http://127.0.0.1:5001/health
Dashboard:            http://127.0.0.1:8502
```

**Debug mode with separate windows:**

```bat
RUN_BACKEND.bat
RUN_FRONTEND.bat
```

**Run tests:**

```bat
RUN_TESTS.bat
```

The `.sh` files are kept only for Linux/macOS or cloud deployment environments. On Windows 11, use the `.bat` or `.ps1` files.

## Local vs Remote Switch

The Streamlit left sidebar now includes two runtime controls:

1. **Backend target**
   - `Local Backend` uses `http://127.0.0.1:5001` on your Windows 11 laptop.
   - `Remote Backend` lets you paste a deployed Railway/Render backend URL.

2. **Agent execution**
   - `Local AI Mode — zero tokens` is the safe default. It uses XGBoost, shortage rules, packing optimization, JSON memory, and deterministic local committee agents.
   - `Remote LLM Mode — may use tokens` only makes a remote LLM call if the backend has both `USE_LLM_AGENTS=true` and `GEMINI_API_KEY` configured.

Safe default:

```env
DEFAULT_AGENT_MODE=local
USE_LLM_AGENTS=false
```

That means you can demo the project locally without burning Gemini/OpenAI tokens.

## Sidebar-Responsive Top 5 Queue

The **Top 5 Supplies to Pack First** table is driven by the Flask backend endpoint:

```text
POST /api/packing-queue
```

The Streamlit frontend sends the active sidebar values to the backend. Department changes the supply universe, while the operational sliders, hour/day, and season change shortage risk, pack quantity, priority score, and the order of the queue.

This remains a local, zero-token expert-system flow unless Remote LLM Mode is explicitly enabled and configured.
"# MEDPACK_AI" 
