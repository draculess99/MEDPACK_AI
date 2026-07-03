import os
import requests
import json
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

if "current_tokens" not in st.session_state:
    st.session_state["current_tokens"] = 0

# Configure page
st.set_page_config(
    page_title="MedPack AI / MedAIM Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ports & Configs
LOCAL_MEDPACK_API_BASE_URL = os.environ.get("MEDPACK_LOCAL_API_BASE_URL", "http://127.0.0.1:5001")
REMOTE_MEDPACK_API_BASE_URL = os.environ.get("MEDPACK_REMOTE_API_BASE_URL", "")
DEFAULT_BACKEND_TARGET = os.environ.get("MEDPACK_BACKEND_TARGET", "Local Backend").strip()

# Apply modern premium styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

    /* Global Typography Override */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif !important;
    }
    
    /* Sleek Backgrounds and Cards */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 60%);
    }
    
    [data-testid="stSidebar"] {
        background-color: rgba(128, 128, 128, 0.25) !important;
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Premium Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white !important;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 12px 24px;
        font-weight: 600;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.5);
        border-color: rgba(255, 255, 255, 0.4);
        color: white !important;
    }
    
    /* Beautiful Metric Values */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        background: linear-gradient(90deg, #60a5fa 0%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Soften Metric Labels */
    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        font-weight: 500 !important;
        color: #94a3b8 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Modern Headers */
    h1, h2, h3 {
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    
    /* Add subtle glassmorphism to info/success/warning boxes */
    div[data-testid="stAlert"] {
        background-color: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
    }
    
    /* Clean up the dataframe borders */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# App Titles
st.title("📦 MedPack AI: Hospital Supply Shortage & Packing Priority System")
st.subheader("Forecasting hospital supply demand and converting shortage risk into packing and replenishment action.")

st.markdown("""
**Problem Statement:**
Hospital supply shortages are not just inventory problems — they are patient-flow and clinical operations problems. When demand rises faster than supplies can be packed, staged, and replenished, nurses lose time searching for critical items and patient care slows down. MedPack AI forecasts supply demand, identifies shortage risk, and prioritizes packing actions before the shortage reaches the bedside.
""")

# Sidebar Controls
with st.sidebar.container(border=True):
    st.subheader("🧭 Runtime Mode")

    backend_options = ["Local Backend", "Remote Backend"]
    default_backend_index = 0 if DEFAULT_BACKEND_TARGET not in backend_options else backend_options.index(DEFAULT_BACKEND_TARGET)
    backend_target = st.radio(
        "Backend target",
        backend_options,
        index=default_backend_index,
        help="Local Backend uses Flask on your Windows laptop. Remote Backend points to a deployed Railway/Render API URL."
    )

    if backend_target == "Remote Backend":
        remote_url_input = st.text_input(
            "Remote API URL",
            value=REMOTE_MEDPACK_API_BASE_URL,
            placeholder="https://your-medpack-backend.up.railway.app",
            help="Use this only after the backend is deployed. Leave blank to avoid accidental remote calls."
        ).strip().rstrip("/")
        MEDPACK_API_BASE_URL = remote_url_input or LOCAL_MEDPACK_API_BASE_URL
        if not remote_url_input:
            st.warning("Remote Backend selected but no remote URL is set. Falling back to local backend.")
    else:
        MEDPACK_API_BASE_URL = LOCAL_MEDPACK_API_BASE_URL

    agent_mode_label = st.radio(
        "Agent execution",
        ["Local AI Mode — zero tokens", "Remote LLM Mode — may use tokens"],
        index=0,
        help="Local mode is deterministic and free. Remote LLM mode only uses tokens if the backend has USE_LLM_AGENTS=true and a valid API key."
    )
    agent_mode = "remote" if agent_mode_label.startswith("Remote") else "local"

    if agent_mode == "local":
        st.success("Local AI Mode: no LLM/API tokens used.")
        selected_model = None
    else:
        st.warning("Remote LLM Mode selected. Tokens are only used if the backend is explicitly configured with USE_LLM_AGENTS=true and GEMINI_API_KEY.")
        selected_model = st.selectbox(
            "Select Remote Model",
            ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-3.1-flash-lite", "gemini-2.0-flash-exp"],
            index=2
        )

    # Render Token Meter
    token_gauge_placeholder = st.empty()

def render_token_gauge(tokens_val):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = tokens_val,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Tokens Used", 'font': {'size': 14, 'color': '#f8fafc'}},
        gauge = {
            'axis': {'range': [None, 1000], 'tickwidth': 1, 'tickcolor': "rgba(255,255,255,0.2)"},
            'bar': {'color': "#3b82f6"},
            'bgcolor': "rgba(255,255,255,0.02)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 250], 'color': "rgba(59, 130, 246, 0.1)"},
                {'range': [250, 750], 'color': "rgba(59, 130, 246, 0.3)"},
                {'range': [750, 1000], 'color': "rgba(59, 130, 246, 0.5)"}],
        }
    ))
    fig.update_layout(height=180, margin=dict(l=20, r=20, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "#f8fafc"})
    token_gauge_placeholder.plotly_chart(fig, use_container_width=True)

render_token_gauge(st.session_state["current_tokens"])

st.sidebar.caption(f"Backend API: `{MEDPACK_API_BASE_URL}`")

with st.sidebar.container(border=True):
    st.subheader("🏥 Supply Selection")
    # Options
    DEPARTMENTS = [
        "Emergency Department",
        "ICU",
        "Surgery",
        "Med-Surg",
        "Labor and Delivery",
        "Radiology",
        "Outpatient Clinic"
    ]

    ITEMS = {
        "IV Start Kit": "IV Supplies",
        "Syringe 10ml": "IV Supplies",
        "Nitrile Gloves Medium": "PPE",
        "Nitrile Gloves Large": "PPE",
        "Oxygen Mask": "Respiratory",
        "Wound Care Pack": "Wound Care",
        "Foley Catheter Kit": "Catheterization",
        "Blood Draw Kit": "Lab Supplies",
        "PPE Gown": "PPE",
        "Saline Flush": "IV Supplies",
        "Sterile Gauze": "Wound Care",
        "Surgical Tray": "Surgical Supplies",
        "Nasal Cannula": "Respiratory",
        "Patient Monitoring Leads": "Monitoring"
    }

    dept = st.selectbox("Department", DEPARTMENTS, index=0)
    item = st.selectbox("Supply Item", list(ITEMS.keys()), index=0)
    item_cat = ITEMS[item]
    st.markdown(f"**Category:** `{item_cat}`")

with st.sidebar.container(border=True):
    st.subheader("📊 Operational Metrics")
    current_stock = st.number_input("Current Stock", min_value=0, max_value=500, value=30)
    patient_volume = st.slider("Patient Volume", 1, 100, 15)
    acuity_level = st.slider("Acuity Level (1=Low, 4=Critical)", 1.0, 4.0, 2.5, step=0.1)
    procedure_count = st.slider("Procedure Count", 0, 50, 6)
    recent_usage_rate = st.slider("Recent Usage Rate (units/hr)", 0.0, 50.0, 8.5, step=0.5)

with st.sidebar.container(border=True):
    st.subheader("⏱️ Supply & Logistics")
    supplier_delay = st.slider("Supplier Delay (Days)", 0.0, 14.0, 2.5, step=0.5)
    reorder_point = st.number_input("Reorder Point", min_value=0, max_value=200, value=25)
    supplier_reliability = st.slider("Supplier Reliability Score", 0.0, 1.0, 0.9, step=0.05)
    pack_time = st.number_input("Pack Time (Minutes)", min_value=1.0, max_value=30.0, value=4.5, step=0.5)
    clinical_criticality = st.slider("Clinical Criticality (1-4)", 1, 4, 3)

with st.sidebar.container(border=True):
    st.subheader("📅 Time Context")
    hour = st.slider("Hour of Day", 0, 23, 12)
    day_of_week = st.slider("Day of Week (0=Mon, 6=Sun)", 0, 6, 2)
    season = st.selectbox("Season", ["Spring", "Summer", "Autumn", "Winter"], index=1)

# Build Telemetry Dict
telemetry = {
    "department": dept,
    "item_name": item,
    "item_category": item_cat,
    "current_stock": int(current_stock),
    "patient_volume": int(patient_volume),
    "acuity_level": float(acuity_level),
    "procedure_count": int(procedure_count),
    "recent_usage_rate": float(recent_usage_rate),
    "supplier_delay_days": float(supplier_delay),
    "day_of_week": int(day_of_week),
    "hour": int(hour),
    "season": season,
    "reorder_point": int(reorder_point),
    "unit_cost": 15.0, # default unit cost
    "supplier_reliability_score": float(supplier_reliability),
    "pack_time_minutes": float(pack_time),
    "clinical_criticality": int(clinical_criticality),
    "agent_mode": agent_mode,
    "selected_model": selected_model
}

# Main Layout Columns
st.sidebar.markdown("---")
show_sys_panels = st.sidebar.checkbox("Show Right-Hand Side Panels", value=False)

if show_sys_panels:
    col1, col2 = st.columns([2, 1])
else:
    col1 = st.container()
    col2 = None

with col1:
    st.header("🔮 Prediction & Logistics Actions")
    
    # Buttons
    run_forecast = st.button("🔮 Predict 24-Hour Supply Demand")
    run_committee_btn = st.button("🤖 Run MedPack Committee Decision")
    
    if run_forecast or run_committee_btn:
        # Call Backend
        try:
            res = requests.post(f"{MEDPACK_API_BASE_URL}/api/run-medpack-committee", json=telemetry)
            if res.status_code == 200:
                result = res.json()
                
                prediction = result["prediction"]
                shortage = result["shortage_risk"]
                priority = result["packing_priority"]
                committee = result["committee"]
                
                # Render Metrics
                st.markdown("### 📊 Live Analytics Output")
                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                
                with m_col1:
                    st.metric(
                        label="Forecasted 24h Demand",
                        value=f"{prediction['predicted_24h_demand']:.1f} units"
                    )
                with m_col2:
                    st.metric(
                        label="Shortage Gap",
                        value=f"{shortage['shortage_gap']:.1f} units",
                        delta=f"Stock: {current_stock}"
                    )
                with m_col3:
                    st.metric(
                        label="Coverage Ratio",
                        value=f"{shortage['coverage_ratio'] * 100:.1f}%"
                    )
                with m_col4:
                    risk_color = "red" if shortage["risk_level"] == "Critical" else "orange" if shortage["risk_level"] == "High" else "yellow" if shortage["risk_level"] == "Medium" else "green"
                    st.markdown(f"<div style='text-align: center;'><span class='metric-label'>Risk Level</span><br><span style='color: {risk_color}; font-size: 1.8rem; font-weight: bold;'>{shortage['risk_level']}</span></div>", unsafe_allow_html=True)
                
                # Shortage & Packing Panels
                st.info(f"**Shortage Logic Explanation:** {shortage['reasoning']}")
                
                # Packing Priority Panel
                st.markdown("---")
                st.markdown("### 📦 Warehouse Packing Instructions")
                p_col1, p_col2 = st.columns(2)
                with p_col1:
                    st.metric("Priority Score", f"{priority['priority_score']:.1f} / 100")
                with p_col2:
                    st.metric("Recommended Pack Quantity", f"{priority['recommended_pack_quantity']} units")
                
                if priority["escalation_required"]:
                    st.error(f"⚠️ **Escalation Triggered!** {priority['recommended_action']}")
                else:
                    st.success(f"✅ **Action Ready:** {priority['recommended_action']}")
                st.caption(priority["reasoning"])
                
                # Committee Panel
                if run_committee_btn:
                    st.markdown("---")
                    st.header("🤖 Agentic Committee Panel")
                    
                    with st.expander("👤 Demand Forecast Agent Insights", expanded=True):
                        st.write(committee["demand_forecast_agent"])
                    with st.expander("👤 Inventory Risk Agent Insights", expanded=True):
                        st.write(committee["inventory_risk_agent"])
                    with st.expander("👤 Packing Priority Agent Insights", expanded=True):
                        st.write(committee["packing_priority_agent"])
                    with st.expander("👤 Clinical Safety Agent Insights", expanded=True):
                        st.write(committee["clinical_safety_agent"])
                    with st.expander("👤 Final Recommendation Agent Insights", expanded=True):
                        st.write(committee["final_recommendation_agent"])
                        
                    st.markdown("#### 📝 Committee Consensus Summary")
                    st.success(committee["committee_summary"])
                    mode_actual = committee.get("actual_agent_mode", "local")
                    tokens_used = committee.get("tokens_used", 0)
                    st.session_state["current_tokens"] = tokens_used
                    render_token_gauge(tokens_used)
                    
                    mode_note = committee.get("mode_note", "")
                    if mode_actual == "remote":
                        st.warning(f"Remote LLM mode used. Tokens reported: {tokens_used}")
                    else:
                        st.info(f"Local AI mode used. Tokens reported: {tokens_used}")
                    st.caption(mode_note)
            else:
                st.error(f"Backend API returned error code {res.status_code}: {res.text}")
        except Exception as e:
            st.error(f"Failed to connect to backend server at {MEDPACK_API_BASE_URL}. Ensure server is running. Error: {e}")

    # Top 5 Supplies Table
    st.markdown("---")
    st.header("📋 Top 5 Supplies to Pack First")
    st.caption(
        "This queue uses the live sidebar scenario. Department changes the supply universe; "
        "the sliders, hour/day, and season change risk, pack quantity, priority score, and ranking."
    )
    try:
        queue_payload = dict(telemetry)
        queue_payload.update({"limit": 5, "max_records": 75})
        queue_res = requests.post(
            f"{MEDPACK_API_BASE_URL}/api/packing-queue",
            json=queue_payload,
            timeout=30,
        )
        if queue_res.status_code == 200:
            queue_response = queue_res.json()
            queue_data = queue_response.get("queue", queue_response if isinstance(queue_response, list) else [])
            if queue_data:
                df_queue = pd.DataFrame(queue_data)
                display_cols = [
                    "item_name",
                    "item_category",
                    "department",
                    "current_stock",
                    "predicted_24h_demand",
                    "shortage_gap",
                    "risk_level",
                    "recommended_pack_quantity",
                    "priority_score",
                    "scenario_pressure_score",
                    "escalation_required",
                ]
                available_cols = [c for c in display_cols if c in df_queue.columns]
                st.dataframe(df_queue[available_cols], use_container_width=True)
                with st.expander("Why did the Top 5 change?", expanded=False):
                    st.write(
                        "The table was recalculated using the current sidebar inputs: "
                        f"department={dept}, patient_volume={patient_volume}, acuity={acuity_level}, "
                        f"procedure_count={procedure_count}, recent_usage_rate={recent_usage_rate}, "
                        f"supplier_delay={supplier_delay}, season={season}, hour={hour}, day={day_of_week}."
                    )
                    if "pressure_note" in df_queue.columns:
                        st.dataframe(df_queue[["item_name", "pressure_note"]], use_container_width=True)
            else:
                st.write("No inventory records found for this department.")
        else:
            st.error(f"Failed to load live packing queue from API: {queue_res.status_code} - {queue_res.text}")
    except Exception as e:
        st.write(f"Cannot load live queue: {e}")

if col2 is not None:
    with col2:
        st.header("🧭 Runtime Status")
        try:
            health_res = requests.get(f"{MEDPACK_API_BASE_URL}/health", timeout=5)
            if health_res.status_code == 200:
                health = health_res.json()
                st.json({
                    "backend_target": backend_target,
                    "api_base_url": MEDPACK_API_BASE_URL,
                    "selected_agent_mode": agent_mode,
                    "remote_llm_enabled_on_backend": health.get("remote_llm_enabled"),
                    "gemini_key_present_on_backend": health.get("gemini_key_present"),
                    "safe_default": health.get("safe_default"),
                })
            else:
                st.warning("Backend health check did not return OK.")
        except Exception as e:
            st.warning(f"Backend health check unavailable: {e}")

        st.header("💾 Transparent Memory")
        try:
            mem_res = requests.get(f"{MEDPACK_API_BASE_URL}/api/supply-memory")
            if mem_res.status_code == 200:
                memory_state = mem_res.json()
                st.markdown("### 🧠 Current Rolling State")
                st.json(memory_state)
            else:
                st.write("Error loading memory state.")
        except Exception as e:
            st.write(f"Memory unavailable: {e}")
            
        st.markdown("### 📥 Log Feedback & Update Memory")
        feedback_usage = st.number_input("Actual Usage next 24 Hours", min_value=0.0, value=12.0, step=1.0)
        update_mem_btn = st.button("🔄 Update Memory with Actual Usage")
        
        if update_mem_btn:
            try:
                update_res = requests.post(f"{MEDPACK_API_BASE_URL}/api/update-supply-memory", json={
                    "item_name": item,
                    "department": dept,
                    "predicted_demand": recent_usage_rate * 1.2,
                    "actual_usage": feedback_usage
                })
                if update_res.status_code == 200:
                    st.success("Memory updated successfully! Page will reflect new rolling averages and delta metrics.")
                    st.json(update_res.json())
                else:
                    st.error("Failed to update memory.")
            except Exception as e:
                st.error(f"Error updating memory: {e}")
                
        st.markdown("### 📜 Recent Event Logs (supply_memory_events.jsonl)")
        try:
            events_res = requests.get(f"{MEDPACK_API_BASE_URL}/api/supply-memory-events")
            if events_res.status_code == 200:
                st.json(events_res.json())
        except Exception as e:
            st.write(f"Logs unavailable: {e}")

# Data sources section
st.markdown("---")
st.header("🗃️ Data Source Transparency")
try:
    sources_res = requests.get(f"{MEDPACK_API_BASE_URL}/api/data-sources")
    if sources_res.status_code == 200:
        data_sources = sources_res.json()
        st.json(data_sources)
        
        # Check Kaggle vs Synthetic
        raw_exists = os.path.exists("database/raw/kaggle_hospital_supply_chain.csv")
        if raw_exists:
            st.success("✅ Primary Kaggle source detected at `database/raw/kaggle_hospital_supply_chain.csv`")
        else:
            st.warning("⚠️ Kaggle source not found. Relying on synthesized, PHI-free operational simulation records.")
except Exception as e:
    st.write(f"Data sources descriptor unavailable: {e}")

# Architecture Section
st.markdown("---")
st.header("🏗️ System Architecture & Workflow")
st.markdown("""
1. **Machine Learning Pipeline:** An XGBoost Regressor model predicts `actual_usage_next_24h` based on real-time operational telemetry (volumetrics, recent run rates, acuity).
2. **Deterministic Rules Engine:** Translates predicted demand & current stock levels into structured safety thresholds (`Low`, `Medium`, `High`, `Critical` risk levels).
3. **Logistics Packing Optimizer:** Integrates risk status with clinical significance, department priorities, and packaging speed constraints to compute a prioritized scoring vector.
4. **Agentic Advisory Committee:** A 5-agent advisory committee reviews the metrics. The left-sidebar switch controls local zero-token mode vs optional remote LLM mode.
5. **Stateful Feedback Loop:** Transparently updates standard memory structures and writes JSONL telemetry logs for auditing and dashboard validation.
""")
