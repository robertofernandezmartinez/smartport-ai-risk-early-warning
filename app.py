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
# 4. ACTION CENTER (Sidebar) - UPDATED
# =====================================================================
import requests

st.sidebar.title("⚓ Port Command")

# Bot Configuration (Fill these in)
TOKEN = "YOUR_TELEGRAM_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

target_terminal = st.sidebar.selectbox("Select Terminal:", [
    "Terminal A (North)", 
    "Terminal B (South)", 
    "Dry Dock 1"
])

# Action mapping based on your alert logic
operation_order = st.sidebar.selectbox("Action Order:", [
    "Reassign Berth (Emergency)", 
    "Prioritize AIS Data Sync", 
    "Standard Flow Optimization"
])

if st.sidebar.button("Execute & Notify Telegram"):
    # Professional message construction
    message = (
        f"⚓ *SMARTPORT COMMAND LOG*\n\n"
        f"📍 *Target:* {target_terminal}\n"
        f"⚙️ *Action:* {operation_order}\n"
        f"✅ *Status:* Executed via Dashboard\n"
        f"👤 *Operator:* Admin"
    )
    
    # Real-time Telegram API request
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": message, 
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            # Fixed: global toast notification
            st.toast("Telegram Alert Dispatched!") 
            st.sidebar.success("Command Sent Successfully!")
        else:
            st.sidebar.error("Telegram API Error")
    except Exception as e:
        st.sidebar.error(f"Connection Error: {e}")

st.sidebar.markdown("---")
st.sidebar.caption("SmartPort AI v1.0 | Operational Intelligence")