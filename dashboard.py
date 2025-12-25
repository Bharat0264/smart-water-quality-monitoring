import streamlit as st
import requests
import pandas as pd
import time

API_BASE_URL = "http://127.0.0.1:5000"
REFRESH_INTERVAL = 1800  # 30 minutes

st.set_page_config(
    page_title="Smart Water Quality Monitoring",
    layout="wide",
    page_icon="🚰"
)

# =========================
# HEADER
# =========================
st.title("🚰 Smart Water Quality Monitoring System")
st.caption("Real-time monitoring and ML-based water safety prediction")

st.divider()

# =========================
# LIVE SENSOR SECTION
# =========================
st.subheader("📡 Live Sensor Readings")

try:
    live = requests.get(f"{API_BASE_URL}/api/latest", timeout=5).json()

    if "ph" in live:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("pH", live["ph"])
        c2.metric("Turbidity (NTU)", live["turbidity"])
        c3.metric("Temperature (°C)", live["temperature"])
        c4.metric("Status", "🟢 SAFE" if live["prediction"] == "Safe" else "🔴 UNSAFE")

        st.caption(f"Last updated: {live['timestamp']}")
    else:
        st.info("No live data yet")

except:
    st.error("API not running")

st.divider()

# =========================
# HISTORY GRAPHS
# =========================
st.subheader("📊 Water Quality Trends")

try:
    history = requests.get(f"{API_BASE_URL}/api/history", timeout=5).json()
    df = pd.DataFrame(history)

    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        col1, col2 = st.columns(2)

        with col1:
            st.line_chart(df.set_index("timestamp")["ph"], height=300)
            st.caption("pH Variation Over Time")

        with col2:
            st.line_chart(df.set_index("timestamp")["turbidity"], height=300)
            st.caption("Turbidity Variation Over Time")

        col3, col4 = st.columns(2)

        with col3:
            st.line_chart(df.set_index("timestamp")["temperature"], height=300)
            st.caption("Temperature Variation Over Time")

        with col4:
            status_count = df["prediction"].value_counts()
            st.bar_chart(status_count, height=300)
            st.caption("Safe vs Unsafe Readings")

    else:
        st.warning("No historical data available")

except:
    st.error("Unable to load history data")

st.divider()

# =========================
# MANUAL TEST
# =========================
st.subheader("🧪 Manual Water Test")

with st.form("manual_test"):
    c1, c2, c3 = st.columns(3)
    ph = c1.number_input("pH", 0.0, 14.0, 7.0)
    turbidity = c2.number_input("Turbidity (NTU)", 0.0, value=2.0)
    temperature = c3.number_input("Temperature (°C)", value=25.0)
    submit = st.form_submit_button("Analyze")

if submit:
    payload = {
        "ph": ph,
        "turbidity": turbidity,
        "temperature": temperature
    }
    try:
        res = requests.post(f"{API_BASE_URL}/api/data", json=payload).json()
        if res["prediction"] == "Safe":
            st.success("✅ Water is SAFE")
        else:
            st.error("❌ Water is UNSAFE")
    except:
        st.error("API error")

st.caption("🔄 Auto-refresh every 30 minutes")
time.sleep(REFRESH_INTERVAL)
st.rerun()
