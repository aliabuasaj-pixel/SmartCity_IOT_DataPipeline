from pymongo import MongoClient
import json

# 1️⃣ الاتصال بقاعدة البيانات
client = MongoClient("mongodb://localhost:27017")
db = client.smartcity

# 2️⃣ تجميع أوقات الذروة لحركة المرور
pipeline = [
    {
        "$match": {"sensor_type": "traffic"}
    },
    {
        "$project": {
            "hour": {"$hour": {"$toDate": "$timestamp"}},
            "traffic_flow": 1
        }
    },
    {
        "$group": {
            "_id": "$hour",
            "avgFlow": {"$avg": "$traffic_flow"},
            "maxFlow": {"$max": "$traffic_flow"}
        }
    },
    {
        "$sort": {"avgFlow": -1}
    },
    {
        "$limit": 10  # نعرض فقط أكثر 10 ساعات ازدحاماً
    }
]

# 3️⃣ تنفيذ التجميع
results = list(db.sensors.aggregate(pipeline))

# 4️⃣ حفظ النتائج في ملف JSON
output = [{
    "hour": r["_id"],
    "avgFlow": r["avgFlow"],
    "maxFlow": r["maxFlow"]
} for r in results]

output_path = "aggregations/traffic_peak_hours.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=4)

print("✅ تقرير 'Traffic Peak Hours' تم إنشاؤه بنجاح وحُفظ في", output_path)
