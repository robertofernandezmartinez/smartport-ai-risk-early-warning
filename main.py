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

# --- Configuration & Global Cache ---
load_dotenv()
cached_df = pd.DataFrame()
processed_updates = set()
sent_alerts = set()

def get_data_from_sheets():
    """Fetches data from Google Sheets."""
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
        print(f"❌ Connection Error: {e}")
        return pd.DataFrame()

async def generate_executive_report(df, user_query="Provide an updated status report."):
    """Uses AI to generate the immediate status report with counts and protocols."""
    ai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    counts = df['risk_level'].value_counts().to_dict()
    
    system_instruction = (
        "You are the SmartPort AI Senior Operations Analyst. "
        "MANDATORY: Your response must ALWAYS start with a 'PORT STATUS REPORT'.\n"
        "1. Categorical Breakdown (Use Emojis): 🔴 CRITICAL, 🟡 WARNING, 🟢 NORMAL.\n"
        "2. Operational Protocols: \n"
        "   - CRITICAL: Immediate intervention (reassign berth).\n"
        "   - WARNING: Monitor ETA and AIS stability closely.\n"
        "   - NORMAL: Routine operations.\n"
        "Language: English by default, Spanish if the user speaks Spanish. "
        "Be concise, professional, and do not list IDs unless asked."
    )

    context_payload = {"summary_counts": counts, "total_vessels": len(df)}
    
    completion = ai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Context: {context_payload}\nQuery: {user_query}"}
        ]
    )
    return completion.choices[0].message.content

# --- BACKGROUND MONITORING & PROACTIVE REPORT ---
async def refresh_data_and_alert(context: ContextTypes.DEFAULT_TYPE):
    global cached_df, sent_alerts
    print("🔄 Syncing with Google Sheets...")
    new_df = get_data_from_sheets()
    
    if not new_df.empty:
        cached_df = new_df
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        # Identify new critical risks
        critical_vessels = cached_df[cached_df['risk_level'] == 'CRITICAL']['vessel_id'].astype(str).tolist()
        new_alerts = [v for v in critical_vessels if v not in sent_alerts]

        if new_alerts and chat_id:
            # INSTEAD OF A SIMPLE TEXT, WE SEND THE FULL AI REPORT IMMEDIATELY
            report = await generate_executive_report(cached_df, user_query="NEW CRITICAL VESSELS DETECTED. Send full status report.")
            header = f"🚨 *CRITICAL UPDATE*: {len(new_alerts)} new vessels in danger!\n\n"
            await context.bot.send_message(chat_id=chat_id, text=header + report, parse_mode='Markdown')
            sent_alerts.update(new_alerts)
        
        sent_alerts = sent_alerts.intersection(set(critical_vessels))

# --- INSTANT MESSAGE HANDLING ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global processed_updates, cached_df
    if not update.message or update.message.message_id in processed_updates: return
    processed_updates.add(update.message.message_id)

    if cached_df.empty:
        await update.message.reply_text("⏳ Syncing data... please wait a few seconds.")
        return

    report = await generate_executive_report(cached_df, user_query=update.message.text)
    await update.message.reply_text(report, parse_mode='Markdown')

if __name__ == '__main__':
    print("🚢 SmartPort AI Bot - Proactive Analyst Mode")
    token = os.getenv("TELEGRAM_TOKEN")
    
    if token:
        app = ApplicationBuilder().token(token.strip()).build()
        
        if app.job_queue:
            # Every 60 seconds it checks for changes and sends a full report if criticals are found
            app.job_queue.run_repeating(refresh_data_and_alert, interval=60, first=1)
        
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        app.run_polling(drop_pending_updates=True)