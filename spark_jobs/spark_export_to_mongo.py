from pyspark.sql import SparkSession

# إنشاء جلسة Spark مع تعطيل Native Hadoop Library على Windows
spark = SparkSession.builder \
    .appName("ExportToMongo") \
    .config("spark.mongodb.output.uri", "mongodb://127.0.0.1/smartcity.sensors") \
    .config("spark.hadoop.io.nativeio.NativeIO$Windows.access0", "false") \
    .getOrCreate()

# قراءة البيانات من مجلد validated
df = spark.read.parquet("data/validated")

# تصديرها إلى MongoDB داخل مجموعة sensors
df.write \
    .format("mongo") \
    .mode("overwrite") \
    .save()

spark.stop()
print("✅ تم تصدير البيانات إلى MongoDB (smartcity.sensors) بنجاح.")
