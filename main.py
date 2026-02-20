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

# --- Environment & State ---
load_dotenv()
processed_updates = set()
sent_alerts = set()

def get_data():
    """Accesses Google Sheets and returns a DataFrame for analysis."""
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
        print(f"❌ Connectivity Error: {e}")
        return pd.DataFrame()

# --- AUTOMATIC RISK MONITORING ---
async def check_vessel_risk(context: ContextTypes.DEFAULT_TYPE):
    global sent_alerts
    try:
        df = get_data()
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if df.empty or not chat_id: return

        critical_vessels = df[df['risk_level'] == 'CRITICAL']['vessel_id'].astype(str).tolist()
        new_alerts = [v for v in critical_vessels if v not in sent_alerts]

        if new_alerts:
            msg = f"🚨 *CRITICAL UPDATE*: {len(new_alerts)} new vessels reached critical risk levels."
            await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')
            sent_alerts.update(new_alerts)
        
        # Keep only currently critical vessels in memory
        sent_alerts = sent_alerts.intersection(set(critical_vessels))
    except Exception as e:
        print(f"Monitoring Error: {e}")

# --- EXECUTIVE AI ANALYST ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global processed_updates
    if not update.message or update.message.message_id in processed_updates: return
    processed_updates.add(update.message.message_id)

    try:
        ai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        df = get_data()
        
        if df.empty:
            await update.message.reply_text("Unable to access live port data.")
            return

        # 1. Local Pre-processing (The "Técnico" part)
        counts = df['risk_level'].value_counts().to_dict()
        top_critical = df[df['risk_level'] == 'CRITICAL'].head(5).to_dict(orient='records')

        # 2. Advanced System Instruction
        system_instruction = (
            "You are the SmartPort AI Senior Analyst. "
            "TONE: Professional, direct, and technical. "
            "BEHAVIOR: Always start with a brief categorical count (Critical, Warning, Normal) "
            "even if the user just greets you. This is your 'Automatic Status Report'. "
            "LANGUAGE: Default is English, but if the user speaks in Spanish, switch fluently. "
            "TECHNICAL CAPACITY: You have access to detailed risk scores and recommended actions. "
            "Avoid long lists of IDs unless specifically asked for details on a ship."
        )

        context_brief = {
            "summary_counts": counts,
            "sample_critical_details": top_critical,
            "total_vessels_monitored": len(df)
        }

        completion = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Context: {context_brief}\nUser Query: {update.message.text}"}
            ]
        )
        await update.message.reply_text(completion.choices[0].message.content, parse_mode='Markdown')

    except Exception as e:
        print(f"AI Assistant Error: {e}")

if __name__ == '__main__':
    print("🚢 SmartPort AI Bot - Running in Senior Analyst Mode...")
    token = os.getenv("TELEGRAM_TOKEN")
    
    if token:
        app = ApplicationBuilder().token(token.strip()).build()
        
        if app.job_queue:
            app.job_queue.run_repeating(check_vessel_risk, interval=60, first=10)
        
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        app.run_polling(drop_pending_updates=True)