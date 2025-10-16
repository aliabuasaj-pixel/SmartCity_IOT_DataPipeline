from pymongo import MongoClient
from datetime import datetime

# 1️⃣ الاتصال بقاعدة البيانات
client = MongoClient("mongodb://localhost:27017")
db = client.smartcity

# 2️⃣ تحديد مجموعة الـ MV والـ meta_state
mv_collection = db.mv_monthly_pollution_alerts
meta_collection = db.mv_meta_state

# 3️⃣ الحصول على آخر نقطة تحديث (checkpoint) لتحديث تزايدي
meta = meta_collection.find_one({"mv": "mv_monthly_pollution_alerts"})
last_checkpoint = meta.get("last_timestamp") if meta else None

# 4️⃣ إنشاء التجميع Aggregation
pipeline = []

# خطوة لتصفية السجلات الجديدة فقط إذا وجد checkpoint
if last_checkpoint:
    pipeline.append({"$match": {"timestamp": {"$gt": last_checkpoint}}})

pipeline += [
    {
        "$project": {
            "region": 1,  # أو أي حقل يمثل المنطقة/الموقع
            "pollution_level": 1,
            "month": {
                "$dateToString": {
                    "format": "%Y-%m",
                    "date": {"$toDate": "$timestamp"}  # تحويل الـ Long إلى Date
                }
            }
        }
    },
    {
        "$match": {"pollution_level": {"$gt": 100}}  # مثال للتنبيه
    },
    {
        "$group": {
            "_id": {"region": "$region", "month": "$month"},
            "alertsCount": {"$sum": 1},
            "avgPollution": {"$avg": "$pollution_level"}
        }
    },
    {
        "$sort": {"_id.month": 1, "_id.region": 1}
    }
]

# 5️⃣ تشغيل التجميع وحفظ النتائج في الـ MV باستخدام upsert لكل سجل
results = list(db.sensors.aggregate(pipeline))
for doc in results:
    mv_collection.update_one(
        {"_id": doc["_id"]},  # المفتاح الفريد
        {"$set": doc},        # بيانات السجل
        upsert=True           # إدراج إذا غير موجود
    )

# 6️⃣ تحديث الـ meta_state
last_timestamp_doc = db.sensors.find().sort("timestamp", -1).limit(1)
last_timestamp = last_timestamp_doc[0]["timestamp"] if last_timestamp_doc.alive else None


meta_collection.update_one(
    {"mv": "mv_monthly_pollution_alerts"},
    {"$set": {"last_timestamp": last_timestamp, "last_run": datetime.now()}},
    upsert=True
)

print("✅ MV 'mv_monthly_pollution_alerts' updated successfully.")
