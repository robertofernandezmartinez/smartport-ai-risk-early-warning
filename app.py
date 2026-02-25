import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests

# =====================================================================
# 1. DATABASE CONNECTION (Google Sheets)
# =====================================================================
def load_data():
    # Use your existing Spreadsheet ID
    SHEET_ID = "1aTJLlg4YNT77v1PLQccKl8ZCADBJN0U8kncTBvf43P0"
    
    # Credentials setup (Ensure your json file is in the repo)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    
    # Open the sheet and get data
    sheet = client.open_by_key(SHEET_ID).sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# Load real data from your Sheets
df = load_data()

# =====================================================================
# 2. MAIN INTERFACE
# =====================================================================
st.title("⚓ SmartPort AI | Command Center")

# Metrics based on real data
total_vessels = len(df)
critical_risks = len(df[df['risk_level'] == 'CRITICAL'])

col1, col2, col3 = st.columns(3)
col1.metric("Monitored Vessels", total_vessels)
col2.metric("Critical Alerts", critical_risks, delta_color="inverse")
col3.metric("System Status", "Live", "Connected")

st.markdown("---")

# Layout: Risk Table & Tactical Sidebar
col_main, col_side = st.columns([2, 1])

with col_main:
    st.subheader("Live Risk Monitor (From Sheets)")
    # Show only the most relevant columns for the operator
    display_df = df[['vessel_id', 'risk_score', 'risk_level', 'recommended_action']]
    st.dataframe(display_df, use_container_width=True, hide_index=True)

with col_side:
    st.subheader("🕹️ Operational Action")
    
    # SELECTOR: Real Vessel IDs from your Sheets
    selected_vessel = st.selectbox("Target Vessel:", df['vessel_id'].unique())
    
    # Get the recommended action from Sheets for that specific vessel
    rec_action = df[df['vessel_id'] == selected_vessel]['recommended_action'].values[0]
    st.caption(f"Suggested: {rec_action}")
    
    # Action to execute
    final_order = st.selectbox("Order to Dispatch:", [
        "Immediate Berth Reassignment",
        "Priority Inspection",
        "AIS Protocol Resync",
        "Manual Review Confirmed"
    ])
    
    if st.button("Execute & Notify Telegram"):
        # RECUERDA: Pega tu TOKEN e ID reales aquí
        TOKEN = "YOUR_TELEGRAM_TOKEN"
        CHAT_ID = "YOUR_CHAT_ID"
        
        msg = (
            f"🚨 *COMMAND EXECUTED*\n\n"
            f"🚢 *Vessel:* {selected_vessel}\n"
            f"⚙️ *Order:* {final_order}\n"
            f"📋 *Ref Action:* {rec_action}\n"
            f"✅ *Status:* Sent to Terminal Ops"
        )
        
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
        st.success(f"Notification sent for {selected_vessel}")

st.sidebar.markdown("---")
st.sidebar.info("SmartPort Suite | Data-Driven Decisions")