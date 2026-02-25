import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =====================================================================
# 1. PAGE CONFIGURATION
# =====================================================================
st.set_page_config(
    page_title="SmartPort AI | Control Center",
    page_icon="⚓",
    layout="wide"
)

# Custom CSS for UI consistency across the Suite
st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #3e4259;
    }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 2. HEADER & KPI SECTION
# =====================================================================
st.title("⚓ SmartPort Operations AI")
st.markdown("Real-time terminal monitoring, congestion analysis, and predictive logistics.")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Active Vessels", "14", "+2 Today")
col2.metric("Port Congestion", "LOW", "Optimal", delta_color="normal")
col3.metric("Avg. Clearance Time", "3.8h", "-0.4h")
col4.metric("Pending Containers", "842", "High Load")

# =====================================================================
# 3. OPERATIONAL ANALYTICS
# =====================================================================
st.subheader("Terminal Occupancy & Flow Trends")

# Mock data for visualization
chart_data = pd.DataFrame({
    'Hour': list(range(24)),
    'Occupancy %': [45, 42, 40, 38, 45, 55, 70, 85, 90, 88, 85, 80, 75, 70, 72, 75, 80, 85, 82, 78, 70, 60, 50, 48]
})

fig = px.area(
    chart_data, 
    x='Hour', 
    y='Occupancy %', 
    template="plotly_dark",
    color_discrete_sequence=['#00d4ff']
)

fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor='#3e4259'),
    margin=dict(l=10, r=10, t=30, b=10),
    height=400
)

st.plotly_chart(fig, use_container_width=True)

# =====================================================================
# 4. ACTION CENTER (Sidebar) - SHIP-SPECIFIC
# =====================================================================
st.sidebar.title("⚓ Port Command")

# Bot Config
TOKEN = "8528957593:AAFe92KmsIT2Lmw2qW6JJvpW69H3MPCXY9k"
CHAT_ID = "8460877081"

# 1. Select the Area
target_terminal = st.sidebar.selectbox("Terminal Area:", ["Terminal A", "Terminal B", "Dry Dock 1"])

# 2. Select the Specific Vessel (This makes it real!)
vessel_id = st.sidebar.text_input("Vessel ID / Container ID:", value="Vessel-742")

# 3. Select the Specific Action
operation_order = st.sidebar.selectbox("Action Order:", [
    "Emergency Berth Reassignment", 
    "Priority Unloading", 
    "Hold in Anchorage Area",
    "Customs Inspection Hold"
])

if st.sidebar.button("Execute & Notify Telegram"):
    # The message now includes the SPECIFIC SHIP
    message = (
        f"🚨 *OPERATIONAL COMMAND*\n\n"
        f"🚢 *Vessel:* {vessel_id}\n"
        f"📍 *Location:* {target_terminal}\n"
        f"⚙️ *Action:* {operation_order}\n"
        f"✅ *Status:* Confirmed by Ops"
    )
    
    # Send to Telegram
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)
    st.toast(f"Order sent for {vessel_id}")