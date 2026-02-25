# 🚢 SmartPort AI: Real-Time Maritime Risk Monitoring
### *Predictive Intelligence for Port Operations & Vessel Delay Prevention*

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_svg)](https://smartport-ai-risk-early-warning.streamlit.app/)

**SmartPort AI** is an end-to-end maritime risk intelligence system designed to predict, monitor, and act on vessel delays in congested port environments. It transforms raw AIS (Automatic Identification System) movement data into **actionable operational alerts**, identifying vessels at risk of exceeding the critical 120-minute berthing delay window.

The system delivers insights via a **Cloud Command Center (Streamlit)** and a **Senior AI Analyst on Telegram**, optimized for high-speed executive reporting and real-time tactical dispatch.

> **Data Source:** [Container Ship Tracking Dataset (Kaggle)](https://www.kaggle.com/datasets/bobaaayoung/container-ship-data-collection)

---

## 🌐 Live Command Center
**Access the real-time dashboard here:** [https://smartport-ai-risk-early-warning.streamlit.app/](https://smartport-ai-risk-early-warning.streamlit.app/)

---

## 🎯 Project Purpose & Business Logic
Port operations rely on tight berthing windows. Delays beyond **120 minutes** have cascading economic impacts on the entire global supply chain. 

SmartPort AI answers the critical operational question: 
> *"Which vessels are likely to exceed the 120-minute delay threshold, and what is the prioritized operational response?"*

---

## 🏗️ Architecture Overview

The ecosystem is organized into a robust, autonomous ML structure:

### 1. Autonomous ML Engine (`04_Models`)
* **Encapsulated Pipeline:** Feature engineering (vessel dynamics, time intervals) is baked directly into the Scikit-Learn pipeline object (`.pkl`). 
* **Zero-Friction Ingestion:** The model safely accepts raw, unformatted AIS data, dynamically handling missing values and type casting.
* **Inference:** A calibrated **XGBoost** model classifies delay probability with high precision.

### 2. Operational Command Center (`app.py`)
* **Streamlit Cloud Dashboard:** A real-time web interface for port authorities to visualize risk levels.
* **Bidirectional Integration:** Reads live data from Google Sheets and triggers tactical notifications via Telegram.
* **Enterprise Security:** Fully powered by **Streamlit Secrets (TOML)** to manage encrypted API credentials for Google Cloud and Telegram.

### 3. Cloud Database (Google Sheets)
* **Single Source of Truth:** Cloud-based repository (via `gspread`) for immediate operational visibility.
* **Data Integrity:** Every prediction includes a unique **SHA-256 hash** for total traceability.

### 4. Proactive AI Assistant (`telegram_bot.py`)
* **Asynchronous Caching:** Background syncing ensures **zero-latency** responses to user queries.
* **Executive Reporting:** Automatic push notifications with categorical breakdowns (🔴/🟡/🟢) and direct action protocols.

---

## 🚦 Risk Classification & Decision Matrix

| Risk Level | Score Range | Operational Meaning | Suggested Action |
| :--- | :--- | :--- | :--- |
| **🔴 CRITICAL** | > 0.80 | High likelihood of >120 min delay | Immediate intervention (reassign berth) |
| **🟡 WARNING** | 0.50 – 0.80 | Elevated risk | Monitor ETA and AIS stability closely |
| **🟢 NORMAL** | < 0.50 | Low risk | Routine operations |

---

## 📂 Repository Structure

* **`app.py`**: The main Cloud Command Center (Streamlit Dashboard).
* **`01_Scripts/`**: Utility scripts for data cleaning and training.
* **`02_Data/`**: Full dataset hierarchy (Raw, Working, Validation).
* **`03_Notebooks/`**: End-to-end development pipeline (EDA, Modeling).
* **`04_Models/`**: Serialized `.pkl` files for the model and pipelines.
* **`05_Outputs/`**: Prediction results and exported risk alerts.
* **`telegram_bot.py`**: The core AI Analyst engine for Telegram.
* **`logs_builder_sheets.py`**: Main synchronization engine for Cloud Operational Logs.
* **`requirements.txt`**: Optimized system dependencies.

---

## 🛠️ Tech Stack

* **ML & Analytics:** Python, XGBoost, Scikit-learn, Pandas.
* **Web Dashboard:** Streamlit, Plotly.
* **Cloud & API:** Google Sheets API (`gspread`), OpenAI API (**GPT-4o-mini**).
* **Interface:** Telegram Bot API (`python-telegram-bot`).
* **Security:** SHA-256 Hashing, Streamlit Secrets (TOML), Environment Variables.

---

## ⚙️ Deployment & Secrets Management

This project uses **Streamlit Secrets** for secure cloud deployment. To run locally, ensure you have a `.streamlit/secrets.toml` file with:
* `TELEGRAM_TOKEN` & `TELEGRAM_CHAT_ID`
* `[gcp_service_account]` credentials block for Google Cloud.

---
*Developed as part of the SmartPort AI Automation Project - 2026*