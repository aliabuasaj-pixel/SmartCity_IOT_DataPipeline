from pymongo import MongoClient
import json
from datetime import datetime

# 1️⃣ الاتصال بقاعدة البيانات
client = MongoClient("mongodb://localhost:27017")
db = client.smartcity

# 2️⃣ تحديد المصدر (البيانات الموثوقة)
source_collection = db.sensors  # أو validated_data حسب تسميتك

# 3️⃣ تحديد الشهر الحالي
current_month = datetime.now().strftime("%Y-%m")

# 4️⃣ التجميع لمعرفة أكثر المناطق تلوثًا
pipeline = [
    {
        "$project": {
            "region": 1,
            "pollution_level": 1,
            "month": {
                "$dateToString": {
                    "format": "%Y-%m",
                    "date": {"$toDate": "$timestamp"}
                }
            }
        }
    },
    {"$match": {"month": current_month}},
    {
        "$group": {
            "_id": "$region",
            "avgPollution": {"$avg": "$pollution_level"},
            "maxPollution": {"$max": "$pollution_level"},
            "alerts": {"$sum": {"$cond": [{"$gt": ["$pollution_level", 100]}, 1, 0]}}
        }
    },
    {"$sort": {"avgPollution": -1}},
    {"$limit": 5}
]

# 5️⃣ تنفيذ التجميع
results = list(source_collection.aggregate(pipeline))

# 6️⃣ حفظ النتائج في ملف JSON داخل مجلد aggregations
output_path = "aggregations/top_zones_pollution.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print(f"✅ تقرير 'Top Zones Pollution' تم إنشاؤه بنجاح وحُفظ في {output_path}")
