# TravelAutomation
A small script automation for flight booking

# ✈️ Flight Script Generator

This is a Streamlit app to generate:
- ✈️ Flight Blocking Scripts  
- 🧾 EMD Issuance Scripts  
- 📊 Excel/CSV Booking Summaries  
...with optional OCR-based fare extraction from screenshots.

---

## 🔧 Features

- Upload and parse 2 or 4 flight segments.
- Upload a screenshot to extract **basic** and **total fare** using OCR.
- Auto-calculate EMD based on fare and commission.
- Select airline to auto-fill commission rates.
- Generate Excel/CSV summaries.
- Download results or copy scripts directly.

---

## 📁 Project Structure

├── booking_app.py              # Main Streamlit application
├── priceReading.py            # Contains OCR logic using Tesseract
├── emd_calculator.py          # EMD calculation logic
├── flight_commissions.csv     # Mapping of airline → commission + flight code
├── requirements.txt           # Python dependencies


---

## 🚀 Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/your-username/flight-script-generator.git
cd TravelCode

pip install -r requirements.txt

brew install tesseract

streamlit run booking_app.py
