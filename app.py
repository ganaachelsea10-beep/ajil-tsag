import streamlit as st
from datetime import date, datetime
import json
import os

st.set_page_config(page_title="Ажлын цаг & Цалин", layout="centered")

DATA_FILE = "ajilchnuud.json"

if "employees" not in st.session_state:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            st.session_state.employees = json.load(f)
    else:
        st.session_state.employees = {}

st.title("💼 Ажлын цаг бүртгэл & Цалин бодох")

tab1, tab2, tab3 = st.tabs(["📌 Цаг бүртгэх", "💰 Цалин бодох", "📜 Түүх"])

with tab1:
    name = st.text_input("👤 Ажилтны нэр", placeholder="Жишээ: Болд")
    
    col1, col2 = st.columns(2)
    with col1:
        selected_date = st.date_input("📅 Огноо", date.today())
    with col2:
        hourly_rate = st.number_input("💵 Цаг тутамд (₮)", value=5000, step=500, min_value=1000)
    
    col3, col4 = st.columns(2)
    with col3:
        start_time = st.time_input("🕒 Эхлэх цаг", datetime.strptime("08:00", "%H:%M").time())
    with col4:
        end_time = st.time_input("🕒 Дуусах цаг", datetime.strptime("17:00", "%H:%M").time())
    
    if st.button("✅ Бүртгэх", type="primary", use_container_width=True):
        if name.strip():
            start = datetime.combine(selected_date, start_time)
            end = datetime.combine(selected_date, end_time)
            hours = (end - start).total_seconds() / 3600
            if hours < 0: hours += 24
            salary = round(hours * hourly_rate)
            
            record = {
                "date": str(selected_date),
                "start": str(start_time),
                "end": str(end_time),
                "hours": round(hours, 2),
                "rate": hourly_rate,
                "salary": salary
            }
            
            if name not in st.session_state.employees:
                st.session_state.employees[name] = []
            st.session_state.employees[name].append(record)
            
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(st.session_state.employees, f, ensure_ascii=False, indent=2)
            
            st.success(f"**{name}** - {hours:.2f} цаг, **{salary:,}₮** бүртгэлээ!")
        else:
            st.error("Ажилтны нэрийг оруулна уу!")

with tab2:
    if st.session_state.employees:
        emp_name = st.selectbox("Ажилтан сонгох", list(st.session_state.employees.keys()))
        if st.button("💰 Цалин тооцоолох", type="primary", use_container_width=True):
            records = st.session_state.employees[emp_name]
            total_h = sum(r["hours"] for r in records)
            total_s = sum(r["salary"] for r in records)
            st.success(f"**{emp_name}**")
            st.metric("Нийт ажилласан цаг", f"{total_h:.2f} цаг")
            st.metric("Нийт цалин", f"{total_s:,} ₮")
    else:
        st.info("Эхлээд цаг бүртгээрэй")

with tab3:
    st.json(st.session_state.employees)
