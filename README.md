# 🚢 SmartPort AI: Real-Time Maritime Risk Monitoring
### *Predictive Intelligence for Port Operations & Vessel Delay Prevention*

**SmartPort AI** es un sistema de inteligencia de riesgo marítimo diseñado para predecir, monitorear y actuar sobre los retrasos de buques en entornos portuarios congestionados. Transforma datos brutos de movimiento AIS en **alertas operacionales accionables**, identificando buques en riesgo de superar la ventana crítica de 120 minutos de retraso.

El sistema entrega insights a través de un registro en la nube y un **Analista Senior de IA** en Telegram, optimizado para reportes ejecutivos de alta velocidad.

> **Fuente de Datos:** [Container Ship Tracking Dataset (Kaggle)](https://www.kaggle.com/datasets/bobaaayoung/container-ship-data-collection)

---

## 🎯 Propósito del Proyecto y Lógica de Negocio
Las operaciones portuarias dependen de ventanas de atraque estrictas. Los retrasos superiores a **120 minutos** generan impactos económicos en cascada en toda la cadena de suministro.

SmartPort AI responde a la pregunta operativa crítica:
> *"¿Qué buques es probable que superen el umbral de retraso de 120 minutos y cuál es la respuesta operativa priorizada?"*

---

## 🏗️ Resumen de la Arquitectura

El ecosistema se organiza en una estructura técnica de cuatro capas:

### 1. Motor de Predicción ML (`01_Scripts` & `04_Models`)
* **Feature Engineering:** Procesa estabilidad de velocidad y varianza de rumbo.
* **Inferencia:** Modelo **XGBoost** entrenado para clasificar la probabilidad de retraso.
* **Modelos:** Almacenados en formato `.pkl` para ejecución inmediata.

### 2. Gestión de Datos (`02_Data`)
* **Raw & Working:** Ciclo completo de vida del dato, desde el `tracking_db.csv` original hasta los datasets balanceados para entrenamiento.
* **Outputs:** Generación de `risk_alerts.csv` para auditoría local.

### 3. Centro de Control en la Nube (Google Sheets)
* **Single Source of Truth:** Repositorio en la nube para visibilidad operativa inmediata.
* **Integridad:** Cada predicción incluye un hash SHA-256 único para trazabilidad total.

### 4. Asistente de IA Proactivo (`telegram_bot.py`)
* **Asynchronous Caching:** Sincronización en segundo plano cada 60s para respuestas instantáneas.
* **Executive Reporting:** Notificaciones automáticas con desgloses por categoría (🔴/🟡/🟢) y protocolos de acción.

---

## 🚦 Clasificación de Riesgo y Matriz de Decisión

| Nivel de Riesgo | Rango de Score | Significado Operativo | Acción Sugerida |
| :--- | :--- | :--- | :--- |
| **🔴 CRITICAL** | > 0.80 | Alta probabilidad de retraso >120 min | Intervención inmediata (reasignar atraque) |
| **🟡 WARNING** | 0.50 – 0.80 | Riesgo elevado | Monitorear ETA y estabilidad de AIS |
| **🟢 NORMAL** | < 0.50 | Bajo riesgo | Operaciones de rutina |

---

## 📂 Estructura del Repositorio

* **`01_Scripts/`**: Scripts de ejecución, limpieza y logs.
* **`02_Data/`**: Datasets (Raw, Working, Validation).
* **`03_Notebooks/`**: Pipeline completo de desarrollo (EDA, Feature Engineering, Modeling).
* **`04_Models/`**: Archivos `.pkl` del modelo entrenado y pipelines.
* **`05_Outputs/`**: Resultados de predicciones y alertas.
* **`docs/`**: Documentación técnica y backups de workflows (n8n).
* **`telegram_bot.py`**: El motor del Analista de IA para Telegram.
* **`ai_notifier.py`**: Script de sincronización de alertas críticas.
* **`Procfile`**: Configuración para despliegue en Railway.
* **`requirements.txt`**: Dependencias optimizadas del sistema.

---

## 🛠️ Tech Stack

* **ML:** Python, XGBoost, Scikit-learn, Pandas.
* **Cloud:** Google Sheets API (`gspread`), OpenAI API (**GPT-4o-mini**).
* **Interface:** Telegram Bot API (`python-telegram-bot` con `job-queue`).
* **Seguridad:** Hashing SHA-256, Variables de entorno (`.env`).