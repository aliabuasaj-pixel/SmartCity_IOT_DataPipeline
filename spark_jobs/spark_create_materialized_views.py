from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, count, col

# إنشاء جلسة Spark
spark = SparkSession.builder \
    .appName("MaterializedViews") \
    .config("spark.mongodb.input.uri", "mongodb://127.0.0.1/smartcity.sensors") \
    .config("spark.mongodb.output.uri", "mongodb://127.0.0.1/smartcity") \
    .getOrCreate()

# قراءة البيانات من MongoDB
df = spark.read.format("mongo").load()

# عرض أول صف للتأكد من الاتصال
df.show(1)

# إنشاء عرض لمتوسط القراءة لكل نوع حساس
avg_df = df.groupBy("sensor_type").agg(avg("reading_value").alias("avg_value"))
avg_df.write.format("mongo").mode("overwrite").option("collection", "avg_sensor_readings").save()

# إنشاء عرض لعدد القراءات حسب المنطقة
region_df = df.groupBy("region").agg(count("*").alias("count"))
region_df.write.format("mongo").mode("overwrite").option("collection", "region_stats").save()

# كشف القيم غير الطبيعية (تجاوز حد معين)
anomalies_df = df.filter(col("reading_value") > 90)
anomalies_df.write.format("mongo").mode("overwrite").option("collection", "anomalies").save()

spark.stop()
print("✅ تم إنشاء الـ Materialized Views في MongoDB بنجاح.")
