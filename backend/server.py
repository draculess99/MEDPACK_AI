import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

from backend.model import load_model_and_predict
from backend.shortage_rules import calculate_shortage_risk
from backend.packing_optimizer import calculate_priority_and_pack_quantity
from backend.supply_memory import (
    load_supply_memory,
    update_supply_memory_after_actual,
    append_memory_event
)
from backend.agents.adk_agents import run_committee
from backend.packing_queue import build_packing_queue

app = Flask(__name__)
CORS(app)

PORT = int(os.environ.get("PORT", os.environ.get("MEDPACK_BACKEND_PORT", 5001)))

@app.route("/health", methods=["GET"])
def health():
    remote_enabled = str(os.environ.get("USE_LLM_AGENTS", "false")).strip().lower() in {"1", "true", "yes", "y", "on"}
    return jsonify({
        "status": "ok",
        "service": "MedPack AI backend",
        "default_agent_mode": os.environ.get("DEFAULT_AGENT_MODE", "local"),
        "remote_llm_enabled": remote_enabled,
        "gemini_key_present": bool(os.environ.get("GEMINI_API_KEY", "").strip()),
        "safe_default": "local_zero_token"
    })

@app.route("/api/data-sources", methods=["GET"])
def data_sources():
    path = "database/data_sources.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return jsonify(json.load(f))
    return jsonify({"error": "Data sources schema not found"}), 404

@app.route("/api/inventory", methods=["GET"])
def inventory():
    path = "database/inventory_state.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return jsonify(json.load(f))
    
    # Fallback to loading some from processed dataset
    processed_path = "database/processed/medpack_training_data.csv"
    if os.path.exists(processed_path):
        import pandas as pd
        df = pd.read_csv(processed_path)
        # return top 50 unique items/departments
        df_unique = df.drop_duplicates(subset=["item_name", "department"]).head(50)
        return jsonify(df_unique.to_dict(orient="records"))
        
    return jsonify([]), 200


@app.route("/api/packing-queue", methods=["GET", "POST"])
def packing_queue():
    """Return the top supplies to pack first using the live sidebar scenario.

    GET is kept for simple browser checks. POST is used by the Streamlit dashboard
    so department, sliders, hour/day, and season all affect the Top 5 queue.
    """
    if request.method == "POST":
        payload = request.json or {}
    else:
        payload = request.args.to_dict()

    limit = int(payload.get("limit", 5))
    max_records = int(payload.get("max_records", 50))
    department = payload.get("department", None)

    path = "database/inventory_state.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            inventory_records = json.load(f)
    else:
        inventory_records = inventory().get_json() or []

    if department:
        inventory_records = [rec for rec in inventory_records if rec.get("department") == department]

    queue = build_packing_queue(
        inventory_records,
        limit=limit,
        max_records=max_records,
        scenario=payload,
    )
    return jsonify({
        "department": department,
        "scenario_used": payload,
        "queue": queue,
    })

@app.route("/api/supply-memory", methods=["GET"])
def supply_memory():
    return jsonify(load_supply_memory())

@app.route("/api/supply-memory-events", methods=["GET"])
def supply_memory_events():
    path = "database/supply_memory_events.jsonl"
    if not os.path.exists(path):
        return jsonify([])
    
    events = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except Exception as e:
                    pass
    
    # Return last 10 events
    return jsonify(events[-10:])

@app.route("/api/predict-supply-demand", methods=["POST"])
def predict_supply_demand():
    telemetry = request.json or {}
    try:
        predicted_demand = load_model_and_predict(telemetry)
        
        # Load memory state
        memory_before = load_supply_memory()
        
        # Append forecast event
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "forecast",
            "item_name": telemetry.get("item_name", "Unknown"),
            "department": telemetry.get("department", "Unknown"),
            "telemetry_used": telemetry,
            "memory_before": memory_before,
            "forecast_result": {
                "predicted_24h_demand": round(predicted_demand, 2)
            }
        }
        append_memory_event(event)
        
        return jsonify({
            "predicted_24h_demand": round(predicted_demand, 2),
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/shortage-risk", methods=["POST"])
def shortage_risk():
    data = request.json or {}
    predicted_demand = data.get("predicted_24h_demand", 0.0)
    current_stock = data.get("current_stock", 0)
    
    result = calculate_shortage_risk(predicted_demand, current_stock)
    return jsonify(result)

@app.route("/api/packing-priority", methods=["POST"])
def packing_priority():
    data = request.json or {}
    item_name = data.get("item_name", "")
    department = data.get("department", "")
    shortage_result = data.get("shortage_result", {})
    telemetry = data.get("telemetry", {})
    
    result = calculate_priority_and_pack_quantity(
        item_name,
        department,
        shortage_result,
        telemetry
    )
    return jsonify(result)

@app.route("/api/update-supply-memory", methods=["POST"])
def update_supply_memory():
    data = request.json or {}
    item_name = data.get("item_name", "Unknown")
    department = data.get("department", "Unknown")
    predicted_demand = float(data.get("predicted_demand", 0.0))
    actual_usage = float(data.get("actual_usage", 0.0))
    
    new_memory = update_supply_memory_after_actual(
        predicted_demand,
        actual_usage,
        item_name,
        department
    )
    return jsonify(new_memory)

@app.route("/api/run-medpack-committee", methods=["POST"])
def run_medpack_committee():
    telemetry = request.json or {}
    
    # Run pipeline steps
    predicted_demand = load_model_and_predict(telemetry)
    
    shortage_result = calculate_shortage_risk(
        predicted_demand,
        telemetry.get("current_stock", 0)
    )
    
    priority_result = calculate_priority_and_pack_quantity(
        telemetry.get("item_name", ""),
        telemetry.get("department", ""),
        shortage_result,
        telemetry
    )
    
    memory_state = load_supply_memory()
    
    # Run ADK agent committee
    agent_mode = telemetry.get("agent_mode", os.environ.get("DEFAULT_AGENT_MODE", "local"))

    committee_result = run_committee(
        telemetry,
        {"predicted_24h_demand": predicted_demand},
        shortage_result,
        priority_result,
        memory_state,
        agent_mode=agent_mode
    )
    
    # Append forecast event
    event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "forecast",
        "item_name": telemetry.get("item_name", "Unknown"),
        "department": telemetry.get("department", "Unknown"),
        "telemetry_used": telemetry,
        "memory_before": memory_state,
        "forecast_result": {
            "predicted_24h_demand": round(predicted_demand, 2)
        }
    }
    append_memory_event(event)
    
    return jsonify({
        "telemetry": telemetry,
        "prediction": {"predicted_24h_demand": round(predicted_demand, 2)},
        "shortage_risk": shortage_result,
        "packing_priority": priority_result,
        "memory_state": memory_state,
        "committee": committee_result
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=os.environ.get("FLASK_DEBUG", "0") == "1")
