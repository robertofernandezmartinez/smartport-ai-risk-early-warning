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

# 1. Environment Loading
load_dotenv()

processed_updates = set()
sent_alerts = set()

def get_data():
    """Accesses Google Sheets and returns a list of dicts."""
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
        return gc.open_by_key(spreadsheet_id).worksheet("risk_alerts").get_all_records()
    except Exception as e:
        print(f"❌ Connectivity Error: {e}")
        return []

# --- RISK MONITORING SYSTEM (Alertas Proactivas) ---
async def check_vessel_risk(context: ContextTypes.DEFAULT_TYPE):
    global sent_alerts
    try:
        data = get_data()
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not data or not chat_id: return

        current_high_risks = set()
        new_alerts = []

        for vessel in data:
            v_id = str(vessel.get('vessel_id', '')).strip()
            risk = str(vessel.get('risk_level', '')).strip()
            if risk == 'CRITICAL':
                current_high_risks.add(v_id)
                if v_id not in sent_alerts:
                    new_alerts.append(v_id)
                    sent_alerts.add(v_id)
        
        if new_alerts:
            msg = f"🚨 *CRITICAL RISK*: SmartPort AI detectó {len(new_alerts)} nuevos buques críticos."
            await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')
        
        sent_alerts = sent_alerts.intersection(current_high_risks)
    except Exception as e:
        print(f"Monitoring Error: {e}")

# --- AI LOGISTICS ANALYST (Respuestas Inteligentes) ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global processed_updates
    if not update.message or update.message.message_id in processed_updates: return
    processed_updates.add(update.message.message_id)

    try:
        ai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        raw_data = get_data()
        df = pd.DataFrame(raw_data)

        # 1. Resumen de conteo para la IA (Quick Status)
        summary_stats = df['risk_level'].value_counts().to_dict()
        
        # 2. Prompt del Sistema Refinado
        system_instruction = (
            "Eres un Analista de Operaciones Portuarias de alto nivel. "
            "Tu prioridad es dar un RESUMEN EJECUTIVO. "
            "NUNCA listes todos los IDs de los barcos a menos que el usuario lo pida específicamente. "
            "Estructura tu respuesta así: \n"
            "1. Resumen numérico por categoría (Critical, Warning, Normal).\n"
            "2. Análisis rápido de la situación.\n"
            "3. Recomendación breve.\n"
            "Responde de forma concisa y profesional en español."
        )
        
        # Le enviamos solo el resumen y las primeras filas, no las 600
        context_data = f"Conteos de Riesgo: {summary_stats}. Muestra de datos: {df.head(5).to_dict()}"

        completion = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Contexto: {context_data}\nPregunta: {update.message.text}"}
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
        # Nota: He quitado el delete_webhook manual para evitar conflictos con asyncio
        if app.job_queue:
            app.job_queue.run_repeating(check_vessel_risk, interval=60, first=10)
        
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        app.run_polling(drop_pending_updates=True)