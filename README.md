# 🎉 Vendor Recommendation & Event Cost Estimation Bot

A local, logic-driven AI assistant for event planning and vendor selection. Built with Python and Streamlit — no cloud APIs, no paid tools.

---

## 🚀 Features

### 1. Vendor Recommendation System
- Select your event type (wedding, birthday, etc.)
- Enter your city and budget
- Get top 3 vendors ranked by:
  - Budget fit
  - Location match
  - Ratings
- Includes a personalized planning checklist
- Download results as a CSV

### 2. Event Cost Estimation & Negotiation Bot
- Pick services (venue, catering, photography, etc.)
- Choose number of guests and service quality (Basic / Premium / Luxe)
- Get estimated total cost based on mock price logic
- Enter vendor quote → Bot suggests counter-offer or accepts
- Simulated smart negotiation using logical thresholds

---

## 🧾 Files

| File | Description |
|------|-------------|
| `streamlit_app.py` | Main app (includes both Assignment 1 & 2 logic) |
| `final_vendor_data.csv` | Vendor database with 150 diverse, non-duplicate rows |
| `README.md` | You're reading it |

---

## 🛠️ Setup Instructions

### 1. Install Python (if not already installed)
Go to: https://www.python.org/downloads/

During installation, check ✅ **“Add Python to PATH”**.

---

### 2. Install Required Libraries

Open your terminal and run:

```bash
pip install streamlit pandas numpy

Place Files Together
project_folder/
├─ streamlit_app.py
├─ vendor_data.csv
└─ README.md

Run the App
streamlit run streamlit_app.py

🧠 Tech Stack
Python 3.10+

Streamlit

Pandas

Numpy

✨ Notes
All data and logic is local — no cloud keys, no OpenAI tokens.

Vendor data is mock-generated but realistic, sorted from lowest to highest price.

