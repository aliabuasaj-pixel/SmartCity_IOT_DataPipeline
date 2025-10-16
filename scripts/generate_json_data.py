# File: SmartCity_IoT_DataPipeline/scripts/generate_json_data.py

import json
import random
from datetime import datetime, timedelta
import os

# -------------------------------
# إعداد المسارات بطريقة آمنة
# -------------------------------
# احصل على المسار المطلق لمجلد المشروع الرئيسي
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# المسار النهائي لمجلد حفظ البيانات
RAW_JSON_DIR = os.path.join(BASE_DIR, "data", "raw", "json")

# إنشاء المجلد إذا لم يكن موجودًا
os.makedirs(RAW_JSON_DIR, exist_ok=True)

# -------------------------------
# إعداد المتغيرات
# -------------------------------
NUM_FILES = 2              # عدد الملفات التي تريد توليدها
RECORDS_PER_FILE = 500_000 # عدد السجلات لكل ملف

# الحقول التي سنستخدمها لكل سجل
SENSOR_TYPES = ["temperature", "humidity", "pollution", "traffic", "power_usage"]

# -------------------------------
# دالة لتوليد سجل واحد
# -------------------------------
def generate_record():
    return {
        "sensor_id": f"sensor_{random.randint(1,1000)}",
        "timestamp": (datetime.now() - timedelta(minutes=random.randint(0, 60*24*30))).isoformat(),
        "temperature": round(random.uniform(-10, 40), 2),
        "humidity": round(random.uniform(20, 90), 2),
        "pollution_level": round(random.uniform(0, 500), 2),
        "traffic": random.randint(0, 1000),
        "power_usage": round(random.uniform(0, 100), 2)
    }

# -------------------------------
# توليد الملفات
# -------------------------------
for file_idx in range(1, NUM_FILES + 1):
    filename = os.path.join(RAW_JSON_DIR, f"sensors_{file_idx:02d}.jsonl")
    print(f"Generating {filename} ...")
    
    with open(filename, "w") as f:
        for _ in range(RECORDS_PER_FILE):
            record = generate_record()
            f.write(json.dumps(record) + "\n")
    
    print(f"{filename} generated successfully!")
