from pymongo import MongoClient
import json

# 1️⃣ الاتصال بقاعدة البيانات
client = MongoClient("mongodb://localhost:27017")
db = client.smartcity

# 2️⃣ تجميع الاتجاهات الشهرية لاستهلاك الطاقة
pipeline = [
    {
        "$group": {
            "_id": {
                "month": {"$substr": ["$timestamp", 0, 7]}
            },
            "avgPowerUsage": {"$avg": "$power_usage"},
            "totalPowerUsage": {"$sum": "$power_usage"}
        }
    },
    {
        "$sort": {"_id.month": 1}
    }
]

# 3️⃣ تنفيذ التجميع
results = list(db.sensors.aggregate(pipeline))

# 4️⃣ حفظ النتائج في ملف JSON
output = [{"month": r["_id"]["month"], 
           "avgPowerUsage": r["avgPowerUsage"], 
           "totalPowerUsage": r["totalPowerUsage"]} for r in results]

output_path = "aggregations/power_usage_trends.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=4)

print("✅ تقرير 'Power Usage Trends' تم إنشاؤه بنجاح وحُفظ في", output_path)
