# 🚢 SmartPort AI: Real-Time Maritime Risk Monitoring
### *Predictive Intelligence for Port Operations & Vessel Delay Prevention*

**SmartPort AI** is an end-to-end maritime risk intelligence system designed to predict, monitor, and act on vessel delays in congested port environments. It transforms raw AIS (Automatic Identification System) movement data into **actionable operational alerts**, identifying vessels at risk of exceeding the critical 120-minute berthing delay window.

Insights are delivered via a cloud-based audit trail and a **Senior AI Analyst** on Telegram, optimized for high-speed executive reporting.

> **Data Source:** [Container Ship Tracking Dataset (Kaggle)](https://www.kaggle.com/datasets/bobaaayoung/container-ship-data-collection)

---

## 🎯 Project Purpose & Business Logic
Port operations rely on tight berthing windows. Delays beyond **120 minutes** have cascading economic impacts on the entire supply chain. 

SmartPort AI answers the critical operational question: 
> *"Which vessels are likely to exceed the 120-minute delay threshold, and what is the prioritized operational response?"*

### Core Objectives
* **Predict** vessel delays exceeding 120 minutes using an XGBoost classification engine.
* **Categorize Risk** automatically into a standardized three-tier matrix.
* **Notify Operators** in real-time via proactive cloud-to-mobile synchronization.
* **Executive Insights** provided by a GPT-4o-mini powered analyst with bilingual support.

---

## 🏗️ Architecture Overview

SmartPort AI is built as a high-performance three-layer ecosystem:



### 1. ML Prediction Engine (XGBoost)
* **Feature Engineering:** Processes movement-based features such as speed stability and heading variance.
* **Inference:** Runs an **XGBoost** model trained to classify delay probability with high precision.
* **Output:** Generates a `risk_score` (0-1) and a recommended action per vessel.

### 2. Cloud Audit & Operational Dashboard (Google Sheets)
* **Single Source of Truth:** Uses Google Sheets as a lightweight cloud data warehouse for auditability.
* **Data Integrity:** Every prediction is logged with a unique **SHA-256 hash** (`prediction_id`), ensuring full traceability and preventing duplicates.

### 3. Command & Control: Proactive AI Bot
* **Asynchronous Caching:** Implements a background `job_queue` that syncs with the cloud every 60s, ensuring **zero-latency** responses.
* **Proactive Executive Reporting:** Automatically pushes a full status report (categorical counts + emojis) whenever a new **CRITICAL** risk is detected.
* **Smart Analysis:** Powered by **OpenAI GPT-4o-mini**, allowing natural language queries and automated protocol recommendations.

---

## 🚦 Risk Classification & Decision Matrix

| Risk Level | Score Range | Operational Meaning | Suggested Action |
| :--- | :--- | :--- | :--- |
| **🔴 CRITICAL** | > 0.80 | High likelihood of >120 min delay | Immediate intervention (reassign berth) |
| **🟡 WARNING** | 0.50 – 0.80 | Elevated risk | Monitor ETA and AIS stability closely |
| **🟢 NORMAL** | < 0.50 | Low risk | Routine operations |

---

## 📊 Dashboard Schema

| Column | Description |
| :--- | :--- |
| `prediction_id` | Unique SHA-256 hash for full traceability. |
| `timestamp` | Exact execution time of the ML inference. |
| `vessel_id` | Unique identifier for the vessel (AIS). |
| `risk_score` | Model confidence (0.0 to 1.0). |
| `risk_level` | Categorization (CRITICAL / WARNING / NORMAL). |
| `action` | Automated operational recommendation. |

---

## 🛠️ Tech Stack

* **Machine Learning:** Python, XGBoost, Scikit-learn, Pandas.
* **Cloud & API:** Google Sheets API (`gspread`), OpenAI API (**GPT-4o-mini**).
* **Interface:** Telegram Bot API (`python-telegram-bot` with `job-queue`).
* **Performance:** Asynchronous background caching and multithreading.
* **Security:** SHA-256 Hashing, Environment Variables (`.env`).

---

## 🚀 Key AI Features
* **Immediate Status Report:** Every interaction starts with a real-time categorical breakdown.
* **Bilingual Support:** Automatically detects and responds in English or Spanish.
* **Operational Protocols:** Direct mapping of AI predictions to specific port authority actions.