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

# --- AUTOMATIC RISK MONITORING (Alertas Proactivas) ---
async def check_vessel_risk(context: ContextTypes.DEFAULT_TYPE):
    global sent_alerts
    try:
        df = get_data()
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if df.empty or not chat_id: return

        critical_vessels = df[df['risk_level'] == 'CRITICAL']['vessel_id'].astype(str).tolist()
        new_alerts = [v for v in critical_vessels if v not in sent_alerts]

        if new_alerts:
            msg = f"🚨 *NUEVA ALERTA CRÍTICA*: Se han detectado {len(new_alerts)} buques adicionales en riesgo máximo."
            await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')
            sent_alerts.update(new_alerts)
        
        sent_alerts = sent_alerts.intersection(set(critical_vessels))
    except Exception as e:
        print(f"Monitoring Error: {e}")

# --- EXECUTIVE AI ANALYST (Informe Inmediato) ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global processed_updates
    if not update.message or update.message.message_id in processed_updates: return
    processed_updates.add(update.message.message_id)

    try:
        ai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        df = get_data()
        
        if df.empty:
            await update.message.reply_text("❌ Error: No se pudo acceder a los datos en tiempo real.")
            return

        # 1. Procesamiento local de estadísticas
        counts = df['risk_level'].value_counts().to_dict()
        
        # 2. Instrucciones Estrictas para el Informe Inmediato
        system_instruction = (
            "Eres el SmartPort AI Senior Analyst. Tu respuesta DEBE ser un informe ejecutivo inmediato. "
            "TONO: Altamente profesional y directo. "
            "ESTRUCTURA OBLIGATORIA: \n"
            "1. Conteo por Niveles con Emojis:\n"
            "   - 🔴 CRITICAL: [conteo]\n"
            "   - 🟡 WARNING: [conteo]\n"
            "   - 🟢 NORMAL: [conteo]\n"
            "2. Recomendaciones de Acción por Nivel:\n"
            "   - CRITICAL: Immediate intervention (reassign berth).\n"
            "   - WARNING: Monitor ETA and AIS stability closely.\n"
            "   - NORMAL: Routine operations.\n"
            "IDIOMA: Por defecto inglés, pero cambia a español si el usuario te habla en ese idioma. "
            "No listes IDs de barcos a menos que se te pregunte específicamente por uno."
        )

        context_brief = {
            "summary_counts": counts,
            "total_vessels": len(df)
        }

        completion = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Context: {context_brief}\nQuery: {update.message.text}"}
            ]
        )
        await update.message.reply_text(completion.choices[0].message.content, parse_mode='Markdown')

    except Exception as e:
        print(f"AI Assistant Error: {e}")

if __name__ == '__main__':
    print("🚢 SmartPort AI Bot - Running in Executive Mode...")
    token = os.getenv("TELEGRAM_TOKEN")
    
    if token:
        app = ApplicationBuilder().token(token.strip()).build()
        
        if app.job_queue:
            # Monitorización cada 60 segundos
            app.job_queue.run_repeating(check_vessel_risk, interval=60, first=10)
        
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        app.run_polling(drop_pending_updates=True)