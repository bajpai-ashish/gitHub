from pyspark.sql import SparkSession

LOCAL_WAREHOUSE_PATH = "/data/data_files/iceberg/iceberg_warehouse"
CATALOG_NAME = "local"

spark = SparkSession.builder \
    .appName("Iceberg Setup") \
    .config(f"spark.sql.catalog.{CATALOG_NAME}", "org.apache.iceberg.spark.SparkCatalog") \
    .config(f"spark.sql.catalog.{CATALOG_NAME}.catalog-impl", "org.apache.iceberg.hadoop.HadoopCatalog") \
    .config(f"spark.sql.catalog.{CATALOG_NAME}.warehouse", f"file:///{LOCAL_WAREHOUSE_PATH}") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .getOrCreate()

print("Spark session started with Iceberg support.")

df_orc = spark.sql("SELECT DepartmentID,Name,GroupName,to_date(ModifiedDate,'M/d/yyyy') ModifiedDate FROM orc.`C:/data/data_files/orc/HumanResources/Department`")
df_orc.show(10,truncate=False)
df_csv = spark.sql("SELECT * FROM csv.`C:/data/data_files/tmp/HumanResources_Department.csv`")
df_csv.show(10,truncate=False)