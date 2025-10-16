روع لوحة مؤشرات المدينة الذكية - Smart City Dashboard 🏙️
معلومات المجموعة 👥

الطلاب المشاركون:

علي أبو عساج

غادة الهبوب

شهد عبدالسلام

تحت إشراف المهندس: عمر أبو سند

وصف المشروع 📝

هذا المشروع يهدف إلى بناء لوحة مؤشرات Dashboard لمدينة ذكية باستخدام بيانات حساسات IoT. تعرض اللوحة معلومات وتحليلات حول:

إجمالي قراءات الحساسات اليومية

تنبيهات التلوث الشهرية

أفضل 5 أجهزة حرارة لكل شهر

اخترنا هذا المشروع لأنه يجمع بين تحليل البيانات، المعالجة التزايدية، وإنشاء Materialized Views (MV)، ويطبق عمليًا مفاهيم Big Data وApache Spark وMongoDB وStreamlit. كما يركز المشروع على جودة البيانات، التحقق Validation، والفهارس Indexing لتحسين الأداء.

وصف البيانات 📊
الجداول والمصادر:

sensors: البيانات الأولية لكل الحساسات

الحقول: sensor_id, timestamp, temperature, humidity, pollution_level, traffic, power_usage

عدد السجلات: حوالي 5,000,000

Materialized Views (MV):

mv_daily_readings_per_device: إجمالي القراءات اليومية لكل حساس

mv_monthly_pollution_alerts: تنبيهات التلوث الشهرية لكل شهر

mv_top5_temp_devices_monthly: أفضل 5 أجهزة حرارة لكل شهر

mv_meta_state: يحتوي على نقاط التحقق (checkpoints) وآخر وقت تحديث لكل MV

Logs: يتم تسجيل كل عمليات التشغيل والتحقق والتصدير هنا

Data Dictionary: موجود في docs/data_dictionary.md يوضح الحقول وأنواعها والقيود


هيكلية المجلدات 📂
SmartCity_IoT_DataPipeline/
├─ app/                 # واجهة المستخدم عبر Streamlit، يحتوي على app.py
├─ spark_jobs/          # سكريبتات Spark لمعالجة البيانات وإنشاء MV
├─ scripts/             # سكريبتات Python وJS لإنشاء Materialized Views والتحقق
├─ ingest_spark/        # ملفات ingest للبيانات عبر Spark (CSV كبير)
├─ ingest_json/         # ملفات ingest للبيانات بصيغة JSON/JSONL
├─ run_validation/      # سكريبتات التحقق من جودة البيانات (Validation)
├─ logs/                # ملفات السجلات التنفيذية
├─ docs/                # المستندات، دليل المشروع، قواعد التحقق، استراتيجية الفهرسة
├─ requirements.txt     # مكتبات Python المطلوبة

وصف المجلدات:

app/: يحتوي على واجهة المستخدم التي تعرض KPIs الثلاثة وتقارير MV، مع بطاقات مؤشرات وتاريخ آخر تحديث مأخوذ من mv_meta_state.

spark_jobs/: سكريبتات Spark لمعالجة البيانات الكبيرة وتحويلها من Raw → Staging → Validated → MV.

scripts/: سكريبتات Python وJS لإنشاء Materialized Views، تشغيل التحديث التزايدي، والتحقق من البيانات.

ingest_json/: قراءة ملفات JSON/JSONL على دفعات chunks/stream والكتابة إلى Staging.

run_validation/: تنفيذ بوابة الجودة Validation Gate، معالجة الأخطاء، تسجيل نتائج الرفض في Quarantine.

logs/: تسجيل كل عمليات التنفيذ، الأخطاء، مدة التشغيل، عدد السجلات المعالجة.

docs/: مستندات المشروع، Data Dictionary، استراتيجيات الفهرسة، Explain للفهارس.

requirements.txt: نسخة Python وSpark والمكتبات المستخدمة.

خطوات التنفيذ 🛠️
1️⃣ نطاق البيانات

اخترنا مشروع مدينة ذكية باستخدام حساسات IoT لعدم تكراره في المادة.

الهدف: تحليل قراءات الحساسات اليومية، التلوث، واستهلاك الطاقة والحرارة.

البيانات الأولية محفوظة في Raw، ثم تتم معالجتها إلى Staging وValidated.

2️⃣ مدخلات البيانات (Raw → Staging) 📥

المسار المستخدم: ingest_json/ لقراءة ملفات JSON/JSONL باستخدام سكريبت Python على دفعات (chunks/stream) والكتابة إلى Staging.

الحد الأدنى لكل ملف: 500,000 سجل، مع الاحتفاظ بالبنية والحقول الصحيحة.

تم إعداد Data Dictionary في docs/data_dictionary.md لتوضيح كل حقل، نوع البيانات، والقيود.

تم تجاهل مسار Spark/CSV الكبير لتجنب التعارض مع المتطلبات.

3️⃣ بوابة الجودة - Validation Gate ✅

أولًا تمر البيانات من Raw → Staging بدون فهارس إضافية.

يتم التحقق من صحة البيانات عبر run_validation/validation_run.py، باستخدام قواعد موجودة في docs/validation_rules.json.

السجلات غير المطابقة تُرسل إلى Quarantine، مع تسجيل السبب في logs/validation.log.

تم استخدام Chunks لمعالجة البيانات الكبيرة بكفاءة.

4️⃣ الفهارس + Explain 📌

تم إنشاء 3 فهارس على الأقل لكل MV، مع التركيز على فهرس مركب Composite Index.

أنواع الفهارس المستخدمة: Single, Compound, Partial، لتسريع الاستعلامات حسب التقرير.

استراتيجية الفهرسة موثقة في docs/index_strategy.md مع شرح سبب اختيار كل فهرس.

تم الاحتفاظ بلقطات executionStats (Explain) لثلاثة استعلامات رئيسية قبل وبعد الفهرسة.

5️⃣ Aggregations / التقارير 📈

تم إنشاء 5 تقارير رئيسية على الأقل:

Daily Readings per Device: إجمالي القراءات اليومية لكل حساس.

Monthly Pollution Alerts: متوسط التنبيهات الشهرية لكل منطقة.

Top 5 Temp Devices (Monthly): أفضل 5 أجهزة حرارة لكل شهر.

Invalid Records Count: عدد السجلات غير الصحيحة لكل حقل حساس.

Power Usage Monthly Avg: متوسط استهلاك الطاقة لكل شهر لكل حساس.

كل تقرير موجود في مجلد aggregations/، مع سكريبت مستقل للتشغيل.

6️⃣ Materialized Views (MV) 🔄

تم إنشاء ≥ 3 MV لتسريع الاستعلامات:

mv_daily_readings_per_device

mv_monthly_pollution_alerts

mv_top5_temp_devices_monthly

المفاتيح المستخدمة:

MV اليومية → _id = {sensor, day}

MV التنبيهات → _id = {month}

MV أفضل أجهزة الحرارة → _id = {month}

التحديث التزايدي Incremental Update: فقط السجلات الجديدة بعد آخر checkpoint.

Checkpoint و Safety Window: لضمان عدم فقدان أي بيانات عند التحديث التزايدي.

Logs التشغيل: يتم تسجيل errors, duration, start, end لكل MV في مجلد logs/.

7️⃣ لوحة المؤشرات - Dashboard 🖥️

واجهة Streamlit تعرض KPIs الثلاثة الأساسية:

إجمالي القراءات اليومية لكل حساس

التنبيهات الشهرية للتلوث

أفضل 5 أجهزة حرارة لكل شهر

تعرض أيضًا آخر وقت تحديث مأخوذ من mv_meta_state.

تدعم التصفية حسب تاريخ، نوع الحساس، والمنطقة.

المخطط المعماري 🏗️
flowchart LR
    Raw --> Staging --> Validated --> MV --> Dashboard


Raw: البيانات الأولية من الحساسات

Staging: مرحلة التحضير والكتابة إلى مجلد مؤقت

Validated: بعد التحقق من جودة البيانات

MV: Materialized Views لتسريع الاستعلامات

Dashboard: عرض البيانات عبر Streamlit

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
