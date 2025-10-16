from pymongo import MongoClient
from datetime import datetime

# 1️⃣ الاتصال بقاعدة البيانات
client = MongoClient("mongodb://localhost:27017")
db = client.smartcity

# 2️⃣ تحديد مجموعة الـ MV
mv_collection = db.mv_daily_readings_per_device
meta_collection = db.mv_meta_state

# 3️⃣ الحصول على آخر نقطة تحديث (checkpoint) لتحديث تزايدي
meta = meta_collection.find_one({"mv": "mv_daily_readings_per_device"})
last_checkpoint = meta.get("last_timestamp") if meta else None

# 4️⃣ إنشاء التجميع Aggregation
pipeline = []

# خطوة لتصفية السجلات الجديدة فقط إذا وجد checkpoint
if last_checkpoint:
    pipeline.append({"$match": {"timestamp": {"$gt": last_checkpoint}}})

pipeline += [
    {
        "$project": {
            "sensor_id": 1,
            # تحويل timestamp من رقم طويل إلى نوع Date قبل استخدام $dateToString
            "date": {"$dateToString": {"format": "%Y-%m-%d", "date": {"$toDate": "$timestamp"}}}
        }
    },
    {
        "$group": {
            "_id": {"sensor": "$sensor_id", "day": "$date"},
            "total_readings": {"$sum": 1}
        }
    }
]

# 5️⃣ تشغيل التجميع وحفظ النتائج في الـ MV
results = list(db.sensors.aggregate(pipeline))
if results:
    mv_collection.insert_many(results)

# 6️⃣ تحديث الـ meta_state
last_timestamp = db.sensors.find().sort("timestamp", -1).limit(1)[0]["timestamp"]
meta_collection.update_one(
    {"mv": "mv_daily_readings_per_device"},
    {"$set": {"last_timestamp": last_timestamp, "last_run": datetime.now()}},
    upsert=True
)
print("✅ MV 'mv_daily_readings_per_device' updated successfully.")
