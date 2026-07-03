import os
import json
from typing import Dict, Any

import requests


def _truthy(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _build_local_committee_texts(
    telemetry: Dict[str, Any],
    prediction_result: Dict[str, Any],
    shortage_result: Dict[str, Any],
    priority_result: Dict[str, Any],
    memory_state: Dict[str, Any],
) -> Dict[str, str]:
    """Build the deterministic, zero-token committee response."""
    item_name = telemetry.get("item_name", "Supply Item")
    department = telemetry.get("department", "Hospital Department")
    current_stock = telemetry.get("current_stock", 0)
    clinical_criticality = telemetry.get("clinical_criticality", 3)
    acuity_level = telemetry.get("acuity_level", "Medium")

    predicted_demand = prediction_result.get("predicted_24h_demand", 0.0)

    shortage_gap = shortage_result.get("shortage_gap", 0.0)
    coverage_ratio = shortage_result.get("coverage_ratio", 1.0)
    risk_level = shortage_result.get("risk_level", "Low")

    priority_score = priority_result.get("priority_score", 0.0)
    recommended_pack_quantity = priority_result.get("recommended_pack_quantity", 0)
    recommended_action = priority_result.get("recommended_action", "")

    trend = memory_state.get("trend_direction", "stable")
    rolling_avg = memory_state.get("rolling_usage_avg", 0.0)

    demand_agent_text = (
        f"[Demand Forecast Agent] I have analyzed the 24-hour demand projection for {item_name} in {department}. "
        f"The machine learning model predicts a demand of {predicted_demand:.1f} units. "
        f"Historical memory indicates a '{trend}' trend with a rolling usage average of {rolling_avg:.1f} units. "
        f"Given patient volume ({telemetry.get('patient_volume', 10)}) and acuity profile ({acuity_level}), "
        f"this demand forecast reflects active clinical consumption rates."
    )

    risk_agent_text = (
        f"[Inventory Risk Agent] Assessing risk for {item_name} with current stock of {current_stock} units. "
        f"The coverage ratio is {coverage_ratio * 100:.1f}%, resulting in a gap of {shortage_gap:.1f} units. "
        f"This places the department at a '{risk_level}' risk level. "
        f"If replenishments are delayed, the safety buffer could be depleted in about "
        f"{(current_stock / max(predicted_demand / 24.0, 0.1)):.1f} hours."
    )

    priority_agent_text = (
        f"[Packing Priority Agent] To resolve the shortage in {department}, the warehouse should act. "
        f"The packing optimizer calculated a priority score of {priority_score:.1f}. "
        f"I recommend packing and dispatching {recommended_pack_quantity} units. "
        f"At {telemetry.get('pack_time_minutes', 5.0)} minutes per pack, "
        f"this work takes approximately {(recommended_pack_quantity * telemetry.get('pack_time_minutes', 5.0)):.1f} minutes."
    )

    clinical_impacts = {
        1: "Low clinical impact. Minor delays in non-urgent supply item access.",
        2: "Moderate clinical impact. Potential minor delays in diagnostic or treatment steps.",
        3: "High clinical impact. Nurses may lose care time searching for supplies.",
        4: "Critical clinical impact. Direct patient-safety concern if supplies support emergency, surgery, or life-support workflows.",
    }
    impact_text = clinical_impacts.get(int(clinical_criticality), "Standard operational workflow impact.")

    clinical_agent_text = (
        f"[Clinical Safety Agent] Evaluating clinical safety for {item_name} (criticality: {clinical_criticality}/4). "
        f"A shortage in {department} combined with acuity '{acuity_level}' leads to: {impact_text} "
        f"Preventative replenishment keeps nurses at the bedside instead of hunting for supplies."
    )

    final_agent_text = (
        f"[Final Recommendation Agent] Action Plan for {item_name} in {department}: "
        f"1. Executive action: {recommended_action} "
        f"2. Stage the items in the department supply area. "
        f"3. {'Escalate to shift supervisor because of critical status.' if priority_result.get('escalation_required', False) else 'Log operation in standard shift inventory ledger.'} "
        f"4. Supplier delay is {telemetry.get('supplier_delay_days', 2.0)} days, so internal stock transfer should be considered before relying on delivery."
    )

    summary = (
        f"MedPack AI Committee consensus: {item_name} in {department} is under {risk_level} shortage risk. "
        f"With a priority score of {priority_score:.1f}, pack {recommended_pack_quantity} units. "
        f"Operational action: '{recommended_action}'"
    )

    return {
        "demand_forecast_agent": demand_agent_text,
        "inventory_risk_agent": risk_agent_text,
        "packing_priority_agent": priority_agent_text,
        "clinical_safety_agent": clinical_agent_text,
        "final_recommendation_agent": final_agent_text,
        "committee_summary": summary,
    }


def _try_remote_gemini_summary(
    telemetry: Dict[str, Any],
    prediction_result: Dict[str, Any],
    shortage_result: Dict[str, Any],
    priority_result: Dict[str, Any],
    memory_state: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Optional remote LLM path.

    This is intentionally gated by BOTH:
      1. user choosing remote mode from the UI/API, and
      2. USE_LLM_AGENTS=true plus GEMINI_API_KEY being present.

    Without both, no remote request is made and zero LLM tokens are used.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    model_name = telemetry.get("selected_model") or os.environ.get("GEMINI_MODEL", "gemini-1.5-flash").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set.")

    api_version = "v1alpha" if "exp" in model_name or "2.0" in model_name else "v1beta"
    url = (
        f"https://generativelanguage.googleapis.com/{api_version}/models/"
        f"{model_name}:generateContent?key={api_key}"
    )
    prompt = {
        "role": "MedPack AI remote LLM committee summarizer",
        "instruction": (
            "Create a concise hospital supply-chain decision summary. Do not invent facts. "
            "Use the provided ML prediction, shortage risk, packing priority, and memory state."
        ),
        "telemetry": telemetry,
        "prediction": prediction_result,
        "shortage_risk": shortage_result,
        "packing_priority": priority_result,
        "memory_state": memory_state,
    }
    payload = {
        "contents": [{"parts": [{"text": json.dumps(prompt, indent=2)}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 512},
    }

    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    text = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "")
        .strip()
    )
    if not text:
        raise RuntimeError("Remote LLM returned an empty response.")
    usage = data.get("usageMetadata", {}) or {}
    token_count = usage.get("totalTokenCount") or usage.get("total_tokens") or 0
    return {"text": text, "tokens_used": token_count, "model": model_name}


def run_committee(
    telemetry,
    prediction_result,
    shortage_result,
    priority_result,
    memory_state,
    agent_mode="local",
):
    """
    Execute the MedPack committee.

    Modes:
      - local: deterministic, zero-token, no remote API call.
      - remote: only attempts a Gemini call if USE_LLM_AGENTS=true and GEMINI_API_KEY exists.
    """
    requested_mode = str(agent_mode or telemetry.get("agent_mode", "local")).strip().lower()
    if requested_mode not in {"local", "remote"}:
        requested_mode = "local"

    local_texts = _build_local_committee_texts(
        telemetry, prediction_result, shortage_result, priority_result, memory_state
    )

    remote_enabled = _truthy(os.environ.get("USE_LLM_AGENTS", "false"))
    has_gemini_key = bool(os.environ.get("GEMINI_API_KEY", "").strip())
    actual_mode = "local"
    fallback_mode = True
    tokens_used = 0
    mode_note = "Local deterministic mode selected. No remote LLM call was made. Zero LLM tokens used."
    remote_model = None

    if requested_mode == "remote":
        if not remote_enabled:
            mode_note = (
                "Remote LLM Mode was selected in the UI, but USE_LLM_AGENTS is not true. "
                "For safety, MedPack used local deterministic agents and zero LLM tokens."
            )
        elif not has_gemini_key:
            mode_note = (
                "Remote LLM Mode was selected, but GEMINI_API_KEY is missing. "
                "MedPack used local deterministic agents and zero LLM tokens."
            )
        else:
            try:
                remote = _try_remote_gemini_summary(
                    telemetry, prediction_result, shortage_result, priority_result, memory_state
                )
                actual_mode = "remote"
                fallback_mode = False
                tokens_used = int(remote.get("tokens_used") or 0)
                remote_model = remote.get("model")
                local_texts["final_recommendation_agent"] = (
                    "[Remote LLM Committee Summary] " + remote["text"]
                )
                local_texts["committee_summary"] = remote["text"]
                mode_note = (
                    f"Remote LLM Mode used {remote_model}. Token usage reported by provider: {tokens_used}."
                )
            except Exception as exc:
                mode_note = (
                    "Remote LLM Mode was selected, but the remote call failed. "
                    f"MedPack fell back to local deterministic agents. Error: {exc}"
                )

    return {
        **local_texts,
        "requested_agent_mode": requested_mode,
        "actual_agent_mode": actual_mode,
        "remote_llm_enabled": remote_enabled,
        "remote_llm_key_present": has_gemini_key,
        "remote_model": remote_model,
        "tokens_used": tokens_used,
        "fallback_mode": fallback_mode,
        "mode_note": mode_note,
    }
