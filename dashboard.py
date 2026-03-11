import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="AI SOC Dashboard", layout="wide")

# ------------------------------------------------
# Auto refresh every 3 seconds
# ------------------------------------------------

st_autorefresh(interval=3000, key="dashboardrefresh")

st.title("🛡️ AI Intrusion Detection Dashboard")

API_STATS = "http://127.0.0.1:5000/stats"

# ------------------------------------------------
# Fetch API stats
# ------------------------------------------------

try:
    r = requests.get(API_STATS)
    data = r.json()
except:
    st.error("API server not running")
    st.stop()

total = data.get("total_packets", 0)
attacks = data.get("attacks", 0)
normal = data.get("normal", 0)
report = data.get("last_report", "No incidents yet")

# ------------------------------------------------
# Risk Score Calculation
# ------------------------------------------------

risk = 0

if total > 0:
    risk = attacks / total

if risk < 0.1:
    status = "🟢 SAFE"
elif risk < 0.3:
    status = "🟡 SUSPICIOUS ACTIVITY"
else:
    status = "🔴 UNDER ATTACK"

# ------------------------------------------------
# Network Status
# ------------------------------------------------

st.subheader("Network Security Status")

colA, colB = st.columns(2)

colA.metric("Security Status", status)
colB.metric("Network Risk Score", round(risk, 2))

st.divider()

# ------------------------------------------------
# Core Metrics
# ------------------------------------------------

col1, col2, col3 = st.columns(3)

col1.metric("Total Packets Analyzed", total)
col2.metric("Normal Traffic", normal)
col3.metric("Detected Attacks", attacks)

st.divider()

# ------------------------------------------------
# Traffic Distribution
# ------------------------------------------------

st.subheader("Traffic Distribution")

chart_data = pd.DataFrame({
    "Traffic Type": ["Normal", "Attack"],
    "Count": [normal, attacks]
})

st.bar_chart(chart_data.set_index("Traffic Type"))

st.divider()

# ------------------------------------------------
# Latest AI Investigation
# ------------------------------------------------

st.subheader("Latest AI Investigation")

if report != "No incidents yet":
    st.warning(report)
else:
    st.info("No incidents detected yet.")

st.divider()

# ------------------------------------------------
# Download Report
# ------------------------------------------------

st.subheader("Incident Report")

if report != "No incidents yet":

    st.download_button(
        label="Download Investigation Report",
        data=report,
        file_name="SOC_Incident_Report.txt",
        mime="text/plain"
    )

else:
    st.info("A report will be available when an attack is detected.")