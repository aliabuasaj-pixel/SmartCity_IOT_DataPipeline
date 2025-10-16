🏙️ مشروع لوحة مؤشرات المدينة الذكية - Smart City Dashboard
👨‍💻 معلومات المجموعة

الطلاب المشاركون:

علي أبو عساج

غادة الهبوب

شهد عبدالسلام

تحت إشراف المهندس: عمر أبو سند

📝 وصف المشروع

هذا المشروع يهدف إلى بناء لوحة مؤشرات Dashboard لمدينة ذكية باستخدام بيانات حساسات IoT.

تُظهر اللوحة معلومات حول:

📊 إجمالي قراءات الحساسات اليومية

🌫️ تنبيهات التلوث الشهرية

🌡️ أفضل 5 أجهزة حرارة لكل شهر

اخترنا هذا المشروع لأنه يجمع بين تحليل البيانات، المعالجة التزايدية، وإنشاء Materialized Views (MV)، ويطبق عمليًا مفاهيم Big Data، Spark، MongoDB وStreamlit.

🗃️ وصف البيانات
الجداول والمصادر:

sensors: البيانات الأولية لكل الحساسات

الحقول: sensor_id, timestamp, temperature, humidity, pollution_level, traffic, power_usage

عدد السجلات: 5,000,000+

Materialized Views (MV):

mv_daily_readings_per_device: إجمالي القراءات اليومية لكل حساس

mv_monthly_pollution_alerts: تنبيهات التلوث الشهرية

mv_top5_temp_devices_monthly: أفضل 5 أجهزة حرارة لكل شهر

mv_meta_state: يحتوي على نقاط التحقق (checkpoints) وآخر وقت تحديث لكل MV

📄 ملفات توثيق البيانات:

docs/data_dictionary.md

docs/validation_rules.json

docs/md.strategy_index

🗂️ هيكلية المجلدات
SmartCity_IoT_DataPipeline/
├─ app/                 # واجهة Streamlit
│   └─ app.py
├─ spark_jobs/          # مهام Spark لمعالجة البيانات
│   └─ spark_ingest.py
├─ scripts/             # سكريبتات إنشاء MV والتحقق من البيانات
│   ├─ create_mv_daily_readings.py
│   ├─ create_mv_monthly_pollution_alerts.py
│   ├─ create_mv_top5_temp_devices_monthly.py
│   ├─ generate_json_data.py
│   ├─ validation_run.py
│   └─ ...
├─ ingest_spark/        # ملفات ingest عبر Spark
├─ ingest_json/         # ملفات ingest بصيغة JSON
├─ run_validation/      # سكريبتات للتحقق من صحة البيانات
├─ aggregations/        # التقارير التحليلية الخمسة
├─ logs/                # ملفات السجلات التنفيذية
├─ docs/                # مستندات ودليل المشروع
├─ requirements.txt     # مكتبات Python المطلوبة
└─ README.md            # هذا الملف

![هيكل المشروع](docs/screenshots/structure_of_project.png)



🧩 مراحل التنفيذ
1️⃣ إدخال البيانات (Ingestion)
إدخال JSON

السكريبت scripts/ingest_json.py يقرأ الملفات بصيغة JSON أو JSONL على شكل دفعات (chunks) ويكتب الملفات إلى مجلد staging.

الحد الأدنى لكل ملف: 500,000 سجل.

2️⃣ بوابة التحقق من البيانات (Validation Gate + Quarantine)

السكريبت scripts/validation_run.py يتحقق من البيانات بناءً على القواعد في:
docs/validation_rules.json

البيانات الصحيحة → تنتقل إلى data/validated/

البيانات الفاسدة أو غير المطابقة → تنتقل إلى data/quarantine/

يتم تسجيل جميع التفاصيل في logs/validation.log

3️⃣ الفهارس وشرح التنفيذ (Indexing + Explain)

لإنشاء فهارس على MongoDB لتسريع الاستعلامات على مجموعات البيانات الكبيرة.

الفهارس المستخدمة:

_id لكل MV → لتسريع القراءة/الكتابة.

فهرس مركب (Compound Index) على sensor_id + day للمقاييس اليومية.

فهارس اختيارية حسب الحقول الأكثر استخدامًا في الاستعلامات.

نتائج Explain ExecutionStats محفوظة في:
docs/explain_*

![نتائج MongoDB](docs/screenshots/mongodb_results.png)


4️⃣ Aggregations / التقارير

تم تنفيذ 5 تقارير تجميعية (Aggregation Reports) لتحليل البيانات الكبيرة:

Daily Readings per Device 📈

إجمالي القراءات اليومية لكل حساس

Monthly Pollution Alerts 🌫️

عدد التنبيهات لكل شهر، مع متوسط القيم

Top 5 Temp Devices (Monthly) 🌡️

أعلى 5 أجهزة حرارة لكل شهر

Invalid Records Count ❌

عدد السجلات غير الصالحة لكل حقل رئيسي

Power Usage Monthly Avg ⚡

متوسط استهلاك الطاقة لكل جهاز شهريًا

كل تقرير موجود في aggregations/ مع سكريبت مستقل لتشغيله.

5️⃣ Materialized Views (MV) + التحديث التزايدي

تم إنشاء 3 عروض مادية (MV) باستخدام MongoDB وميزة $merge للتحديث التزايدي.

النقاط الرئيسية:

mv_daily_readings_per_device → _id = {sensor, day}

mv_monthly_pollution_alerts → _id = {month}

mv_top5_temp_devices_monthly → _id = {month}

كل MV يحتوي على checkpoint و Safety Window لمعالجة البيانات المتأخرة دون فقدان.

تحديث العروض المادية يتم عبر:
jobs/refresh_mv.py

![نجاح إنشاء MV يومي](docs/screenshots/mv_daily_readings_success.png)

![نجاح إنشاء MV التلوث الشهري](docs/screenshots/mv_pollution_success.png)

![نجاح إنشاء MV أفضل 5 أجهزة حرارة](docs/screenshots/mv_top5_success.png)




سجلات التشغيل محفوظة في مجلد logs/

6️⃣ لوحة المؤشرات (Dashboard)

التطبيق التفاعلي في: app/app.py باستخدام Streamlit.

تعرض 3 بطاقات KPIs:

إجمالي القراءات اليومية لكل حساس

تنبيهات التلوث الشهرية

أفضل 5 أجهزة حرارة

تعرض أيضًا آخر وقت تحديث مأخوذ من mv_meta_state.

![لوحة المؤشرات](docs/screenshots/dashboard_view.png)


متطلبات التشغيل ⚙️

Python: 3.11+

Apache Spark: 3.4+

MongoDB: 8+

المكتبات: موجودة في requirements.txt، تشمل:

streamlit

pandas

pymongo

plotly

datetime
