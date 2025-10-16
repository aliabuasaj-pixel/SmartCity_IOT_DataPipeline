from pymongo import MongoClient
import json

# 1️⃣ الاتصال بقاعدة البيانات
client = MongoClient("mongodb://localhost:27017")
db = client.smartcity

# 2️⃣ تعريف معايير السجلات غير الصالحة (Invalid)
# يمكن أن تكون السجلات غير الصالحة مثلاً التي:
# - ليس لديها sensor_id
# - أو timestamp مفقود
# - أو قيم سالبة لمستشعرات معينة
pipeline = [
    {
        "$match": {
            "$or": [
                {"sensor_id": {"$exists": False}},
                {"timestamp": {"$exists": False}},
                {"pollution_level": {"$lt": 0}},
                {"temperature": {"$lt": -50}},
                {"power_usage": {"$lt": 0}}
            ]
        }
    },
    {
        "$group": {
            "_id": None,
            "invalidCount": {"$sum": 1}
        }
    }
]

# 3️⃣ تنفيذ التجميع
results = list(db.sensors.aggregate(pipeline))

# 4️⃣ تجهيز النتائج للحفظ
output = {
    "invalidRecords": results[0]["invalidCount"] if results else 0
}

# 5️⃣ حفظ النتائج في ملف JSON
output_path = "aggregations/invalid_records_count.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=4)

print("✅ تقرير 'Invalid Records Count' تم إنشاؤه بنجاح وحُفظ في", output_path)
