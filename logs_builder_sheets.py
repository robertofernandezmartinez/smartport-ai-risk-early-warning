# =========================================================
# SMARTPORT AI NOTIFIER (BALANCED DASHBOARD SYNC)
# =========================================================
import pandas as pd
import gspread
import hashlib
import os
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURATION ---
PROJECT_PATH = '/Users/rober/smartport-ai-risk-early-warning'
CSV_SOURCE = os.path.join(PROJECT_PATH, '05_Outputs/risk_alerts.csv')
CREDENTIALS_FILE = os.path.join(PROJECT_PATH, "credentials.json")
SPREADSHEET_ID = "1aTJLlg4YNT77v1PLQccKl8ZCADBJN0U8kncTBvf43P0"

def sync_balanced_dashboard():
    """
    Reads the latest risk alerts and synchronizes them with the Google Sheets Dashboard.
    """
    print("Connecting to Google Sheets...")
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds).open_by_key(SPREADSHEET_ID).worksheet("risk_alerts")
    except Exception as e:
        print(f"✘ Connection Error: {e}")
        return

    if not os.path.exists(CSV_SOURCE):
        print(f"✘ Error: {CSV_SOURCE} not found. Please run the execution script first.")
        return
        
    df = pd.read_csv(CSV_SOURCE)
    
    # Balancing the dashboard view
    df_sync = pd.concat([
        df[df['risk_level'] == 'CRITICAL'].head(100),
        df[df['risk_level'] == 'WARNING'].head(400),
        df[df['risk_level'] == 'NORMAL'].head(100)
    ]).fillna("N/A")

    rows = []
    for _, r in df_sync.iterrows():
        raw_id = f"{r['vessel_id']}_{r['timestamp']}"
        p_id = hashlib.sha256(raw_id.encode()).hexdigest()[:12]
        
        rows.append([
            p_id,                             
            str(r['timestamp']),              
            str(r['vessel_id']),              
            float(round(r['risk_score'], 3)), 
            str(r['risk_level']),             
            str(r['recommended_action']),     
            "Pending Review"                  
        ])

    print(f"Uploading {len(rows)} records to Dashboard...")
    client.clear()
    
    headers = [
        "prediction_id", 
        "timestamp_prediction", 
        "vessel_id", 
        "risk_score", 
        "risk_level", 
        "recommended_action", 
        "status"
    ]
    
    client.insert_row(headers, 1)
    if rows:
        client.append_rows(rows)
        print("✅ Sync Complete: SmartPort AI Operational Logs updated.")
    else:
        print("⚠ Warning: No data available for sync.")

if __name__ == "__main__":
    sync_balanced_dashboard()