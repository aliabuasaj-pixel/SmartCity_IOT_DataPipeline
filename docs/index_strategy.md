# Index Strategy for SmartCity IoT Pipeline

## 1. Compound Index (sensor_id + timestamp)
- **Reason:** Optimize queries filtering by sensor and sorting by recent readings.
- **Query Type:** 
  ```js
  db.sensors.find({ sensor_id: "A1001" }).sort({ timestamp: -1 })

# Index Strategy for SmartCity IoT Pipeline

في هذا المشروع، نعتمد على بيانات حساسات المدينة الذكية (Smart City IoT)،
ولذلك قمنا بتصميم مجموعة فهارس تساعد في تسريع الاستعلامات الأكثر شيوعًا
في لوحات المراقبة وتحليل البيانات.

---

## 1. Compound Index (sensor_id + timestamp)
- **النوع:** فهرس مركب (Compound)
- **السبب:** أغلب الاستعلامات تعتمد على البحث عن قياسات حساس معين بترتيب زمني.
- **كيف يخدمنا:** هذا الفهرس يجعل البحث عن أحدث قراءة لكل حساس أسرع بكثير.
- **الاستعلام الذي يخدمه:**
  ```js
  db.sensors.find({ sensor_id: "sensor_1" }).sort({ timestamp: -1 })

## 2. Single Index (pollution_level)
- **Type:** Single Field Index
- **Reason:** Needed for queries/reports on the most polluted areas.
- **How it helps:** Speeds up sorting and ranking by pollution level.
- **Example Query:** 
```js
db.sensors.find().sort({ pollution_level: -1 })

## 3. Compound Index (traffic + power_usage)
- **Reason:** Optimize queries/reports that filter or sort by traffic and power consumption together.
- **Query Type:** 
```js
db.sensors.find({ traffic: { $gt: 500 } }).sort({ power_usage: -1 })
