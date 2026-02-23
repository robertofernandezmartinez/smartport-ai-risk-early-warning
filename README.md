# 🚢 SmartPort AI: Real-Time Maritime Risk Monitoring
### *Predictive Intelligence for Port Operations & Vessel Delay Prevention*

**SmartPort AI** is an end-to-end maritime risk intelligence system designed to predict, monitor, and act on vessel delays in congested port environments. It transforms raw AIS (Automatic Identification System) movement data into **actionable operational alerts**, identifying vessels at risk of exceeding the critical 120-minute berthing delay window.

The system delivers insights via a cloud-based audit trail and a **Senior AI Analyst** on Telegram, optimized for high-speed executive reporting.

> **Data Source:** [Container Ship Tracking Dataset (Kaggle)](https://www.kaggle.com/datasets/bobaaayoung/container-ship-data-collection)

---

## 🎯 Project Purpose & Business Logic
Port operations rely on tight berthing windows. Delays beyond **120 minutes** have cascading economic impacts on the entire global supply chain. 

SmartPort AI answers the critical operational question: 
> *"Which vessels are likely to exceed the 120-minute delay threshold, and what is the prioritized operational response?"*

---

## 🏗️ Architecture Overview

The ecosystem is organized into a four-layer technical structure:

### 1. ML Prediction Engine (`01_Scripts` & `04_Models`)
* **Feature Engineering:** Processes speed stability, heading variance, and historical congestion.
* **Inference:** An **XGBoost** model trained to classify delay probability with high precision.
* **Models:** Stored in `.pkl` format for immediate deployment and retraining.

### 2. Data Lifecycle Management (`02_Data`)
* **Raw & Working:** Full data pipeline from the original `tracking_db.csv` to balanced datasets for model training.
* **Outputs:** Automated generation of `risk_alerts.csv` for local auditing and verification.

### 3. Cloud Command Center (Google Sheets)
* **Single Source of Truth:** Cloud-based repository for immediate operational visibility.
* **Data Integrity:** Every prediction includes a unique **SHA-256 hash** (`prediction_id`) for total traceability.

### 4. Proactive AI Assistant (`telegram_bot.py`)
* **Asynchronous Caching:** Background syncing every 60s ensures **zero-latency** responses to user queries.
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

* **`01_Scripts/`**: Utility scripts for data cleaning and training.
* **`02_Data/`**: Full dataset hierarchy (Raw, Working, Validation).
* **`03_Notebooks/`**: End-to-end development pipeline (EDA, Modeling).
* **`04_Models/`**: Serialized `.pkl` files for the model and pipelines.
* **`05_Outputs/`**: Prediction results and exported risk alerts.
* **`docs/`**: Technical documentation and legacy workflow backups.
* **`telegram_bot.py`**: The core AI Analyst engine for Telegram.
* **`logs_builder_sheets.py`**: Main synchronization engine for Cloud Operational Logs.
* **`Procfile`**: Configuration for deployment on Railway.
* **`requirements.txt`**: Optimized system dependencies.

---

## 🛠️ Tech Stack

* **ML:** Python, XGBoost, Scikit-learn, Pandas.
* **Cloud & API:** Google Sheets API (`gspread`), OpenAI API (**GPT-4o-mini**).
* **Interface:** Telegram Bot API (`python-telegram-bot` with `job-queue`).
* **Security:** SHA-256 Hashing, Environment Variables (`.env`).