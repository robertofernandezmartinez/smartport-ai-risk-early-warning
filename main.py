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
    """Hard-fetch from Google Sheets."""
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

# --- BACKGROUND REFRESH (The Secret to Speed) ---
async def refresh_data_cache(context: ContextTypes.DEFAULT_TYPE):
    """Background task to keep data fresh without blocking user interaction."""
    global cached_df, sent_alerts
    print("🔄 Refreshing Dashboard Cache...")
    new_df = get_data_from_sheets()
    
    if not new_df.empty:
        cached_df = new_df
        
        # Proactive Critical Alerts
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        critical_vessels = cached_df[cached_df['risk_level'] == 'CRITICAL']['vessel_id'].astype(str).tolist()
        new_alerts = [v for v in critical_vessels if v not in sent_alerts]

        if new_alerts and chat_id:
            msg = f"🚨 *CRITICAL ALERT*: SmartPort AI detected {len(new_alerts)} new high-risk vessels."
            await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')
            sent_alerts.update(new_alerts)
        
        sent_alerts = sent_alerts.intersection(set(critical_vessels))

# --- INSTANT AI ANALYST ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global processed_updates, cached_df
    if not update.message or update.message.message_id in processed_updates: return
    processed_updates.add(update.message.message_id)

    # 1. Immediate Response from Cache (Zero Latency)
    if cached_df.empty:
        await update.message.reply_text("⏳ System initializing. Data is being synchronized, please wait 5 seconds...")
        return

    try:
        ai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        counts = cached_df['risk_level'].value_counts().to_dict()
        
        system_instruction = (
            "You are the SmartPort AI Senior Operations Analyst. "
            "MANDATORY: Provide an IMMEDIATE EXECUTIVE REPORT with these exact sections:\n"
            "1. Status with Emojis: 🔴 CRITICAL, 🟡 WARNING, 🟢 NORMAL.\n"
            "2. Operational Protocols: CRITICAL (Immediate intervention), WARNING (Monitor ETA), NORMAL (Routine).\n"
            "Tone: Executive, Professional. Language: English default, Spanish if prompted."
        )

        context_payload = {"summary_counts": counts, "total_vessels": len(cached_df)}

        completion = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Context: {context_payload}\nQuery: {update.message.text}"}
            ]
        )
        await update.message.reply_text(completion.choices[0].message.content, parse_mode='Markdown')

    except Exception as e:
        print(f"AI Error: {e}")

if __name__ == '__main__':
    print("🚢 SmartPort AI Bot - Ultra-Fast Executive Mode")
    token = os.getenv("TELEGRAM_TOKEN")
    
    if token:
        app = ApplicationBuilder().token(token.strip()).build()
        
        # This task runs every 60s and fills the 'cached_df'
        if app.job_queue:
            app.job_queue.run_repeating(refresh_data_cache, interval=60, first=1)
        
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        app.run_polling(drop_pending_updates=True)