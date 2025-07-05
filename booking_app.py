# booking_app.py

import streamlit as st
from datetime import datetime
import pandas as pd
from emd_calculator import calculate_emd_value
import base64
from openpyxl import Workbook
from openpyxl.utils import get_column_letter


st.set_page_config(page_title="Flight Script Generator", layout="centered")
st.title("✈️ Flight Blocking + EMD Script Generator")

# === Airline dropdown (outside form) ===
try:
    df = pd.read_csv("flight_commissions.csv")
    flight_codes = list(df["Airline"].unique()) + ["Other (Manual Entry)"]
except Exception as e:
    st.error("❌ Failed to load flight_commissions.csv")
    st.stop()

selected_airline = st.selectbox("Select Airline", flight_codes)

if selected_airline == "Other (Manual Entry)":
    flight_code = st.text_input("Enter Flight Code Manually")
    basic_commission = st.number_input("Enter Basic Commission", value=0.0)
    overall_commission = st.number_input("Enter Overall Commission", value=0.0)
else:
    row = df[df["Airline"] == selected_airline].iloc[0]
    flight_code = row["FlightCode"]
    basic_commission = row["BasicCommission"]
    overall_commission = row["OverallCommission"]
    st.markdown(f"✈️ Flight Code: `{flight_code}`")
    st.markdown(f"📊 Basic: `{basic_commission}` | Overall: `{overall_commission}`")

# === Form Starts ===
with st.form("flight_form"):
    st.subheader("Flight Inputs")

    flight_text = st.text_area(
        "Enter 2 or 4 Flight Lines (one per line)",
        "EK 543 21JAN MAADXB AK1 0345 0635 TU\nEK 201 22JAN DXBMAA AK1 0325 0835 TU",
        height=150
    )

    uploaded_image = st.file_uploader("Upload Screenshot for Fare OCR (PNG, JPG)", type=["png", "jpg", "jpeg"])
    use_ocr = st.checkbox("📷 Use screenshot to extract fare values")

    basic_fare = overall_fare = 0
    if use_ocr and uploaded_image is not None:
        try:
            from priceReading import get_prices_from_ocr
            basic_fare, overall_fare, ocr_text = get_prices_from_ocr(uploaded_image)
            st.success(f"OCR ✅ Basic Fare = ₹{basic_fare}, Total Fare = ₹{overall_fare}")
        except Exception as e:
            st.error(f"❌ OCR Failed: {e}")

    if overall_fare > 0:
        price = st.number_input("💰 Price per Passenger (from screenshot)", value=overall_fare)
    else:
        price = st.number_input("💰 Price per Passenger (Manual Entry)", value=0)

    passenger_count = st.number_input("Number of Passengers", min_value=1, value=158)
    baggage_pieces = st.number_input("Check-in Bags (pieces)", min_value=1, value=2)
    checkin_weight = st.number_input("Check-in Bag Weight (kg)", value=23)
    handcarry_weight = st.number_input("Hand-carry Bag Weight (kg)", value=7)
    pnr = st.text_input("PNR Number", "ABCD123")

    auto_calc = st.checkbox("Auto-calculate EMD from fare and commission")
    if auto_calc and basic_fare > 0 and overall_fare > 0:
        emd_value = calculate_emd_value(basic_fare, overall_fare, basic_commission, overall_commission, passenger_count)
        st.success(f"✅ Auto-calculated EMD: INR {emd_value}")
    else:
        emd_value = 0

    company_name = st.selectbox(
        "Select Company",
        ["WIPRO LTD", "TATA CONSULTANCY SERVICES", "INFOSYS LTD", "CAPGEMINI LTD", "CTS LTD"],
        index=1
    )

    submitted = st.form_submit_button("Generate Scripts")

if submitted:
    flight_lines = [line.strip() for line in flight_text.strip().split("\n") if line.strip()]

    if len(flight_lines) not in [2, 4]:
        st.error("❌ Please enter exactly 2 or 4 flight lines.")
        st.stop()

    def format_date(date_str):
        return datetime.strptime(date_str + "25", "%d%b%y").strftime("%d-%b-%y")

    def format_time(time_str):
        return datetime.strptime(time_str, "%H%M").strftime("%I:%M %p")

    updated_flights = [line.replace("AK1", str(passenger_count)) for line in flight_lines]
    blocking_script = updated_flights + [
        f"NP.Baggage Allowance//{baggage_pieces}piece {checkin_weight}KG each//{handcarry_weight}KG for Handcarry",
        f"NP.Price per adult display// INR {price}.00",
        f"NP.PNR CONTROL OWN  *****{pnr}*****",
        f"NP.TKPZ{basic_commission}/Z{overall_commission}/DTDAD/EB PNR *****{pnr}*****",
        "P.MAAT* MYXCEL TOURS AND TRAVELS 8122586619 REF RESERVATION"
    ]

    start_date = flight_lines[0].split()[2]
    return_date = flight_lines[-1].split()[2]
    now = datetime.now()
    today_str = now.strftime("%d%b").upper()
    current_time = now.strftime("%H%M")
    flight_timestamp = f"{flight_code}{today_str}{current_time}"

    emd_script = [
        f"NP.//{pnr}//{start_date}//{return_date}//{flight_timestamp}//INR {emd_value}.00",
        f"NP.{pnr}//EMD STATUS ACTIVE",
        f"NP.{pnr}//{company_name}",
        "NP.VIEWPRINTNET",
        "P.MAAT*MYXCEL TOURS AND TRAVELS 8122586619 REF RESERVATION",
        "T.T*",
        "R.K",
        "*R"
    ]

    excel_data = [["No of Pax", "Origin", "Route", "Dept. Date", "Dept. Time", "Flight No", "Arr. Date", "Arr. Time", "PNR", "EMD Status"]]

    for i, line in enumerate(flight_lines):
        parts = line.split()
        if len(parts) < 7:
            st.error(f"❌ Flight line {i+1} is malformed: '{line}'")
            st.stop()

        route = parts[3][:3] + "-" + parts[3][3:]
        dept_date = format_date(parts[2])
        arr_date = dept_date
        dept_time = format_time(parts[5])
        arr_time = format_time(parts[6])
        flight_no = f"{parts[0]} {parts[1]}"

        row = [
            passenger_count if i == 0 else "",
            parts[3][:3],
            route,
            dept_date,
            dept_time,
            flight_no,
            arr_date,
            arr_time,
            pnr if i == 0 else "",
            "Issued" if i == 0 else ""
        ]
        excel_data.append(row)

    # Convert to DataFrame
    headers = excel_data[0]
    data_rows = excel_data[1:]
    df_summary = pd.DataFrame(data_rows, columns=headers)

# Save to CSV
    csv_file = f"{pnr}_booking_summary.csv"
    df_summary.to_csv(csv_file, index=False)

        # Show blocking script
    st.subheader("✈️ BLOCKING SCRIPT")
    st.code("\n".join(blocking_script))

    # Show EMD script
    st.subheader("🧾 EMD ISSUING SCRIPT")
    st.code("\n".join(emd_script))

    # Download button
    with open(csv_file, "rb") as f:
        st.download_button("📥 Download Excel Summary", f, file_name=csv_file)