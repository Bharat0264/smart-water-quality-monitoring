import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:5000/api/data"

st.set_page_config(page_title="Water Quality Monitoring", layout="centered")

st.title("💧 Smart Water Quality Monitoring & Prediction System")
st.subheader("AI-based Real-Time Water Safety Assessment")

st.markdown("""
This system monitors **pH**, **turbidity**, and **temperature**  
and predicts whether water is **Safe or Unsafe** using Machine Learning.
""")

st.divider()

# ---------------- LIVE READINGS ----------------
st.header("📡 Live Water Sample Readings")

try:
    response = requests.get(API_URL, timeout=3)
    if response.status_code == 200 and len(response.json()) > 0:
        latest = response.json()[0]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("pH", latest["ph"])
        col2.metric("Turbidity (NTU)", latest["turbidity"])
        col3.metric("Temperature (°C)", latest["temperature"])
        col4.metric("Status", latest["prediction"])
    else:
        st.info("No live data available.")
except:
    st.error("Flask API not reachable.")

st.divider()

# ---------------- PREDICTION ----------------
st.header("🔍 Analyze New Water Sample")

c1, c2, c3 = st.columns(3)
with c1:
    ph = st.number_input("pH", 0.0, 14.0, 7.0, step=0.1)
with c2:
    turbidity = st.number_input("Turbidity (NTU)", 0.0, 100.0, 2.0, step=0.1)
with c3:
    temperature = st.number_input("Temperature (°C)", -5.0, 100.0, 25.0, step=0.1)

if st.button("🧠 Predict Water Quality"):
    payload = {
        "ph": ph,
        "turbidity": turbidity,
        "temperature": temperature
    }

    try:
        res = requests.post(API_URL, json=payload, timeout=5)
        result = res.json()
        pred = result["prediction"]

        if pred == "Safe":
            st.success("✅ Water Quality is SAFE")
        else:
            st.error("❌ Water Quality is UNSAFE")
    except:
        st.error("Prediction failed.")

st.divider()

# ---------------- HISTORY ----------------
st.header("📊 Recent Readings")

try:
    hist = requests.get(API_URL).json()
    df = pd.DataFrame(hist)
    st.dataframe(df)
except:
    st.info("No data available.")

st.divider()

st.header("ℹ️ Safe Water Standards")
st.markdown("""
- **pH:** 6.5 – 8.5  
- **Turbidity:** ≤ 5 NTU  
- **Temperature:** 10 – 30 °C  
""")

st.caption("Minor Project – Smart Water Quality Monitoring System")
