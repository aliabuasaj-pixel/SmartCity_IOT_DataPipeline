from pymongo import MongoClient
from datetime import datetime

# 1️⃣ الاتصال بقاعدة البيانات
client = MongoClient("mongodb://localhost:27017")
db = client.smartcity

# 2️⃣ تحديد مجموعة الـ MV والـ meta_state
mv_collection = db.mv_top5_temp_devices_monthly
meta_collection = db.mv_meta_state

# 3️⃣ الحصول على آخر نقطة تحديث (checkpoint) لتحديث تزايدي
meta = meta_collection.find_one({"mv": "mv_top5_temp_devices_monthly"})
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
            "temperature": 1,
            "month": {
                "$dateToString": {
                    "format": "%Y-%m",
                    "date": {"$toDate": "$timestamp"}  # تحويل Long إلى Date
                }
            }
        }
    },
    {
        "$group": {
            "_id": {"sensor_id": "$sensor_id", "month": "$month"},
            "avgTemperature": {"$avg": "$temperature"}
        }
    },
    {
        "$sort": {"_id.month": 1, "avgTemperature": -1}
    },
    {
        "$group": {
            "_id": "$_id.month",
            "topSensors": {
                "$push": {"sensor_id": "$_id.sensor_id", "avgTemperature": "$avgTemperature"}
            }
        }
    },
    {
        "$project": {
            "top5Sensors": {"$slice": ["$topSensors", 5]}
        }
    }
]

# 5️⃣ تشغيل التجميع وحفظ النتائج في الـ MV
results = list(db.sensors.aggregate(pipeline))
if results:
    # استخدام upsert لتجنب مشاكل المفتاح المكرر
    for r in results:
        mv_collection.update_one({"_id": r["_id"]}, {"$set": r}, upsert=True)

# 6️⃣ تحديث الـ meta_state
last_timestamp_doc = db.sensors.find().sort("timestamp", -1).limit(1)
last_timestamp_doc = list(db.sensors.find().sort("timestamp", -1).limit(1))
last_timestamp = last_timestamp_doc[0]["timestamp"] if last_timestamp_doc else None


meta_collection.update_one(
    {"mv": "mv_top5_temp_devices_monthly"},
    {"$set": {"last_timestamp": last_timestamp, "last_run": datetime.now()}},
    upsert=True
)

print("✅ MV 'mv_top5_temp_devices_monthly' updated successfully.")
