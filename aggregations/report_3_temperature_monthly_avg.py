from pymongo import MongoClient
import json

# 1️⃣ الاتصال بقاعدة البيانات
client = MongoClient("mongodb://localhost:27017")
db = client.smartcity

# 2️⃣ تجميع متوسط درجات الحرارة شهريًا
pipeline = [
    {
        "$group": {
            "_id": {
                "month": {"$substr": ["$timestamp", 0, 7]}
            },
            "avgTemperature": {"$avg": "$temperature"},
            "maxTemperature": {"$max": "$temperature"},
            "minTemperature": {"$min": "$temperature"}
        }
    },
    {
        "$sort": {"_id.month": 1}
    }
]

# 3️⃣ تنفيذ التجميع
results = list(db.sensors.aggregate(pipeline))

# 4️⃣ حفظ النتائج في ملف JSON
output = [{
    "month": r["_id"]["month"],
    "avgTemperature": r["avgTemperature"],
    "maxTemperature": r["maxTemperature"],
    "minTemperature": r["minTemperature"]
} for r in results]

output_path = "aggregations/temperature_monthly_avg.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=4)

print("✅ تقرير 'Temperature Monthly Average' تم إنشاؤه بنجاح وحُفظ في", output_path)
