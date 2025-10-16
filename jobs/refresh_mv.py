import pymongo
from datetime import datetime

# الاتصال بقاعدة البيانات
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["smartcity"]

# قائمة الـ Materialized Views لتحديثها
views = [
    "mv_daily_readings_per_device",
    "mv_monthly_pollution_alerts",
    "mv_top5_temp_devices_monthly"
]

# سجل الحالة العامة
meta = db.mv_meta_state

for mv in views:
    start_time = datetime.now()
    status = "success"
    last_error = None
    docs_affected = 0

    try:
        # محاكاة التحديث التزايدي (merge)
        result = db[mv].update_many({}, {"$set": {"last_refresh": datetime.now()}})
        docs_affected = result.modified_count

    except Exception as e:
        status = "error"
        last_error = str(e)

    # حفظ نتيجة التشغيل في meta_state
    meta.insert_one({
        "mv": mv,
        "start": start_time,
        "end": datetime.now(),
        "status": status,
        "last_error": last_error,
        "docs_affected": docs_affected,
        "duration": (datetime.now() - start_time).total_seconds()
    })

print("✅ Materialized Views refresh completed.")
