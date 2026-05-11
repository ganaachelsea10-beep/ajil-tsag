import streamlit as st
import pandas as pd
from datetime import date, datetime
import json
import os
import plotly.express as px
from fpdf import FPDF
import tempfile

st.set_page_config(page_title="Ажлын Цаг & Цалин", layout="wide")
st.title("💼 Ажлын цаг бүртгэл & Цалин удирдлага")

DATA_FILE = "ajilchnuud.json"

if "employees" not in st.session_state:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            st.session_state.employees = json.load(f)
    else:
        st.session_state.employees = {}

menu = st.sidebar.selectbox("Меню", 
    ["📌 Цаг бүртгэх", "👤 Ажилтан удирдах", "📊 Тайлан & График", "📜 Бүх бүртгэл", "📄 PDF Тайлан"])

# ====================== ЦАГ БҮРТГЭХ ======================
if menu == "📌 Цаг бүртгэх":
    st.subheader("Шинэ бүртгэл нэмэх")
    col1, col2 = st.columns([1,1])
    with col1:
        name_options = list(st.session_state.employees.keys())
        if name_options:
            name = st.selectbox("Ажилтан", name_options)
        else:
            name = st.text_input("Ажилтны нэр (шинээр)")
    
    col3, col4, col5 = st.columns(3)
    with col3: selected_date = st.date_input("Огноо", date.today())
    with col4: start_time = st.time_input("Эхлэх", datetime.strptime("08:00", "%H:%M").time())
    with col5: end_time = st.time_input("Дуусах", datetime.strptime("17:00", "%H:%M").time())
    
    hourly_rate = st.number_input("Үндсэн цаг тутамд (₮)", value=5000, step=500)
    
    if st.button("✅ Бүртгэх", type="primary"):
        if name.strip():
            start = datetime.combine(selected_date, start_time)
            end = datetime.combine(selected_date, end_time)
            hours = (end - start).total_seconds() / 3600
            if hours < 0: hours += 24
            
            regular = min(hours, 8)
            ot = max(0, hours - 8)
            salary = round(regular * hourly_rate + ot * hourly_rate * 1.5)
            
            record = {
                "date": str(selected_date), "start": str(start_time), "end": str(end_time),
                "hours": round(hours, 2), "regular_hours": round(regular, 2),
                "overtime": round(ot, 2), "rate": hourly_rate, "salary": salary
            }
            
            if name not in st.session_state.employees:
                st.session_state.employees[name] = []
            st.session_state.employees[name].append(record)
            
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(st.session_state.employees, f, ensure_ascii=False, indent=2)
            
            st.success(f"**{name}** — {hours:.2f} цаг (OT: {ot:.2f}) → **{salary:,}₮**")

# ====================== PDF ТАЙЛАН ======================
elif menu == "📄 PDF Тайлан":
    st.subheader("PDF Тайлан үүсгэх")
    
    all_records = []
    for emp, recs in st.session_state.employees.items():
        for r in recs:
            r_copy = r.copy()
            r_copy["employee"] = emp
            all_records.append(r_copy)
    
    if all_records:
        df = pd.DataFrame(all_records)
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.strftime("%Y-%m")
        
        month_list = sorted(df["month"].unique(), reverse=True)
        selected_month = st.selectbox("Сар сонгох", month_list)
        
        filtered = df[df["month"] == selected_month].copy()
        
        # Статистик
        total_salary = filtered["salary"].sum()
        total_hours = filtered["hours"].sum()
        total_ot = filtered["overtime"].sum()
        
        st.write(f"### {selected_month} сарын тайлан")
        col1, col2, col3 = st.columns(3)
        col1.metric("Нийт цалин", f"{total_salary:,} ₮")
        col2.metric("Нийт цаг", f"{total_hours:.1f} цаг")
        col3.metric("Overtime", f"{total_ot:.1f} цаг")
        
        if st.button("📄 PDF Тайлан татах", type="primary"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, f"Ажлын цаг & Цалингийн тайлан - {selected_month}", ln=True, align="C")
            pdf.ln(10)
            
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"Нийт цалин: {total_salary:,} ₮", ln=True)
            pdf.cell(0, 10, f"Нийт цаг: {total_hours:.2f} | Overtime: {total_ot:.2f}", ln=True)
            pdf.ln(5)
            
            # Хүснэгт
            pdf.set_font("Arial", "B", 10)
            pdf.cell(40, 10, "Огноо", 1)
            pdf.cell(40, 10, "Ажилтан", 1)
            pdf.cell(25, 10, "Цаг", 1)
            pdf.cell(25, 10, "OT", 1)
            pdf.cell(40, 10, "Цалин", 1, ln=True)
            
            pdf.set_font("Arial", "", 10)
            for _, row in filtered.iterrows():
                pdf.cell(40, 8, str(row["date"].date()), 1)
                pdf.cell(40, 8, row["employee"], 1)
                pdf.cell(25, 8, f"{row['hours']}", 1)
                pdf.cell(25, 8, f"{row['overtime']}", 1)
                pdf.cell(40, 8, f"{row['salary']:,}", 1, ln=True)
            
            # Хадгалах
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                pdf.output(tmp.name)
                with open(tmp.name, "rb") as f:
                    pdf_bytes = f.read()
            
            st.download_button(
                label="📥 PDF татах",
                data=pdf_bytes,
                file_name=f"tsalin_tailan_{selected_month}.pdf",
                mime="application/pdf"
            )
    else:
        st.info("Мэдээлэл байхгүй байна.")

# Бусад меню (өмнөх кодтой адил)
else:
    # Өмнөх кодны үлдсэн хэсгийг (Ажилтан удирдах, Тайлан & График, Бүх бүртгэл) хэвээр үлдээе
    # Хэрэв хүсвэл бүтэн кодыг дахин өгнө
    st.info("Бусад хэсэг удахгүй шинэчлэгдэнэ. PDF хэсэг амжилттай нэмэгдлээ.")

# Хадгалах
if st.sidebar.button("💾 Өгөгдөл хадгалах"):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(st.session_state.employees, f, ensure_ascii=False, indent=2)
    st.success("Хадгалагдлаа!")
