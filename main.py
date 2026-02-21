import os
import json
import gspread
import asyncio
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from oauth2client.service_account import ServiceAccountCredentials

# --- Environment & State Management ---
load_dotenv()
processed_updates = set()
sent_alerts = set()

def get_data():
    """Accesses Google Sheets and returns a DataFrame for high-speed analysis."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    google_json_str = os.getenv("GOOGLE_CREDENTIALS")
    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    
    try:
        if google_json_str:
            creds_dict = json.loads(google_json_str)
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        
        gc = gspread.authorize(creds)
        data = gc.open_by_key(spreadsheet_id).worksheet("risk_alerts").get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        print(f"❌ Database Connectivity Error: {e}")
        return pd.DataFrame()

# --- PROACTIVE RISK MONITORING SYSTEM ---
async def check_vessel_risk(context: ContextTypes.DEFAULT_TYPE):
    global sent_alerts
    try:
        df = get_data()
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if df.empty or not chat_id: return

        # Identify all currently critical vessels
        critical_vessels = df[df['risk_level'] == 'CRITICAL']['vessel_id'].astype(str).tolist()
        new_alerts = [v for v in critical_vessels if v not in sent_alerts]

        if new_alerts:
            msg = f"🚨 *CRITICAL ALERT*: SmartPort AI detected {len(new_alerts)} new vessels requiring immediate attention."
            await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')
            sent_alerts.update(new_alerts)
        
        # Keep only active critical vessels in the notification memory
        sent_alerts = sent_alerts.intersection(set(critical_vessels))
    except Exception as e:
        print(f"Monitoring Loop Error: {e}")

# --- EXECUTIVE AI ANALYST (Immediate Reporting Mode) ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global processed_updates
    if not update.message or update.message.message_id in processed_updates: return
    processed_updates.add(update.message.message_id)

    try:
        ai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        df = get_data()
        
        if df.empty:
            await update.message.reply_text("❌ Error: Port operational data is currently unreachable.")
            return

        # 1. Local data aggregation
        counts = df['risk_level'].value_counts().to_dict()
        
        # 2. Senior Analyst System Instruction
        system_instruction = (
            "You are the SmartPort AI Senior Operations Analyst. "
            "TONE: High-level executive, professional, and technical. "
            "MANDATORY BEHAVIOR: Every response MUST start with an immediate status report. "
            "REPORT STRUCTURE: \n"
            "1. Categorical Breakdown with Emojis:\n"
            "   - 🔴 CRITICAL: [count]\n"
            "   - 🟡 WARNING: [count]\n"
            "   - 🟢 NORMAL: [count]\n"
            "2. Required Operational Recommendations:\n"
            "   - CRITICAL: Immediate intervention (reassign berth).\n"
            "   - WARNING: Monitor ETA and AIS stability closely.\n"
            "   - NORMAL: Routine operations.\n"
            "LANGUAGE: Default to English. However, if the user interacts in Spanish, "
            "seamlessly switch to professional Spanish. "
            "Do not list individual vessel IDs unless explicitly requested for deep-dive analysis."
        )

        context_payload = {
            "summary_counts": counts,
            "total_monitored": len(df)
        }

        completion = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Context Data: {context_payload}\nUser Input: {update.message.text}"}
            ]
        )
        await update.message.reply_text(completion.choices[0].message.content, parse_mode='Markdown')

    except Exception as e:
        print(f"AI Analyst Exception: {e}")

if __name__ == '__main__':
    print("🚢 SmartPort AI Bot - Senior Executive Mode Active")
    token = os.getenv("TELEGRAM_TOKEN")
    
    if token:
        app = ApplicationBuilder().token(token.strip()).build()
        
        # Background Monitoring (Every 60 seconds)
        if app.job_queue:
            app.job_queue.run_repeating(check_vessel_risk, interval=60, first=10)
        
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        app.run_polling(drop_pending_updates=True)