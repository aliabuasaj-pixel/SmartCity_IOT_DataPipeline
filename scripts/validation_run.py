# File: SmartCity_IoT_DataPipeline/scripts/validation_run.py

import os
import glob
import pandas as pd
import json
from datetime import datetime

# -------------------------------
# إعداد المسارات
# -------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STAGING_DIR = os.path.join(BASE_DIR, "data", "staging", "json")
VALIDATED_DIR = os.path.join(BASE_DIR, "data", "validated", "json")
QUARANTINE_DIR = os.path.join(BASE_DIR, "data", "quarantine", "json")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# إنشاء المجلدات إذا لم تكن موجودة
os.makedirs(VALIDATED_DIR, exist_ok=True)
os.makedirs(QUARANTINE_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOGS_DIR, "validation.log")

# -------------------------------
# إعداد الدفعة (chunksize)
# -------------------------------
CHUNK_SIZE = 100_000

# -------------------------------
# تحميل قواعد التحقق من validation_rules.json
# -------------------------------
rules_path = os.path.join(BASE_DIR, "docs", "validation_rules.json")
if os.path.exists(rules_path):
    with open(rules_path, "r") as f:
        rules = json.load(f)
else:
    # إذا لم يكن الملف موجود، استخدم قواعد افتراضية
    rules = {
        "temperature": {"min": -50, "max": 60},
        "humidity": {"min": 0, "max": 100},
        "pollution_level": {"min": 0, "max": 500},
        "traffic": {"min": 0, "max": 5000},
        "power_usage": {"min": 0, "max": 1000}
    }

# -------------------------------
# دالة للتحقق من السجل
# -------------------------------
def is_valid(record):
    try:
        for field, limits in rules.items():
            if field not in record:
                return False
            value = record[field]
            if not (limits["min"] <= value <= limits["max"]):
                return False
        return True
    except:
        return False

# -------------------------------
# بدء التحقق من الملفات
# -------------------------------
json_files = glob.glob(os.path.join(STAGING_DIR, "*.jsonl"))

with open(LOG_FILE, "a") as log:
    log.write(f"\n\n=== Validation Run: {datetime.now()} ===\n")

for file_path in json_files:
    file_name = os.path.basename(file_path)
    validated_file_path = os.path.join(VALIDATED_DIR, file_name)
    quarantine_file_path = os.path.join(QUARANTINE_DIR, file_name)

    print(f"Processing {file_name} ...")
    total_records = 0
    validated_count = 0
    quarantine_count = 0

    for chunk in pd.read_json(file_path, lines=True, chunksize=CHUNK_SIZE):
        total_records += len(chunk)

        valid_chunk = chunk[chunk.apply(is_valid, axis=1)]
        invalid_chunk = chunk[~chunk.apply(is_valid, axis=1)]

        valid_chunk.to_json(validated_file_path, orient="records", lines=True, mode="a")
        invalid_chunk.to_json(quarantine_file_path, orient="records", lines=True, mode="a")

        validated_count += len(valid_chunk)
        quarantine_count += len(invalid_chunk)

    # سجل النتائج في log
    with open(LOG_FILE, "a") as log:
        log.write(f"{file_name}: total={total_records}, valid={validated_count}, invalid={quarantine_count}\n")

    print(f"✅ {file_name}: total={total_records}, valid={validated_count}, invalid={quarantine_count}")

print("\nValidation complete! Check logs/validation.log for details.")
