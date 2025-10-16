import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime

# 1️⃣ الاتصال بقاعدة البيانات MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.smartcity

# 2️⃣ جلب بيانات الـ Materialized Views
daily_readings = pd.DataFrame(list(db.mv_daily_readings_per_device.find()))
monthly_pollution = pd.DataFrame(list(db.mv_monthly_pollution_alerts.find()))
top_temp_devices = pd.DataFrame(list(db.mv_top5_temp_devices_monthly.find()))

# 3️⃣ معالجة البيانات لتكون جاهزة للعرض
# Daily Readings: مجموع القراءة اليومية لكل الحساسات
total_daily_readings = daily_readings['total_readings'].sum() if not daily_readings.empty else 0

# Monthly Pollution Alerts: مجموع التنبيهات
total_monthly_alerts = monthly_pollution['alertsCount'].sum() if not monthly_pollution.empty else 0

# Top 5 Temp Devices: عرض آخر شهر فقط
top_sensors_display = "N/A"
if not top_temp_devices.empty:
    # ترتيب حسب _id (الشهر)
    top_temp_devices = top_temp_devices.sort_values(by="_id", ascending=False)
    latest_month = top_temp_devices.iloc[0]
    top_sensors_display = ", ".join([sensor['sensor_id'] for sensor in latest_month['top5Sensors']])

# 4️⃣ جلب آخر تحديث من mv_meta_state
meta_state = db.mv_meta_state.find_one(sort=[("start", -1)])
last_update = meta_state['end'] if meta_state else None

# 5️⃣ عرض البيانات في Streamlit
st.title("Smart City Dashboard 🌆")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Daily Readings",
    total_daily_readings
)

col2.metric(
    "Monthly Pollution Alerts",
    total_monthly_alerts
)

col3.metric(
    "Top 5 Temp Devices (Monthly)",
    top_sensors_display
)

st.markdown(f"**Last Update:** {last_update}" if last_update else "**Last Update:** N/A")
