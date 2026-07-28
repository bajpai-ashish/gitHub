import os
import sys

# -------------------------------------------------------------
# 1. FORCE DRIVER CLASSPATH BEFORE PYSPARK IMPORTS
# -------------------------------------------------------------
# Adjust this path if your Iceberg JAR is in a different directory
ICEBERG_JAR_PATH = (
    "C:/data/spark/jars/iceberg-spark-runtime-4.0_2.13-1.10.0.jar"
)

os.environ["PYSPARK_SUBMIT_ARGS"] = (
    f'--conf spark.driver.extraClassPath="{ICEBERG_JAR_PATH}" pyspark-shell'
)
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession

# -------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------
LOCAL_WAREHOUSE_PATH = "C:/data/data_files/iceberg/WideWorldImportersDW"

# Cloudflare R2 Credentials
R2_AID=""
R2_AK=""
R2_SAK=""
R2_BUCKET_NAME = "wide-world-importers-dw"

# Target Namespace
TARGET_NAMESPACE = "integration"

# -------------------------------------------------------------
# BUILD SPARK SESSION
# -------------------------------------------------------------
print("⚡ Initializing PySpark Session...")

spark = (
    SparkSession.builder.appName(
        "Transfer Integration Namespace to Cloudflare R2"
    )
    .config(
        "spark.sql.extensions",
        "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
    )
    # ---------------------------------------------------------
    # CATALOG 1: Local Hadoop Catalog ('reporting')
    # ---------------------------------------------------------
    .config(
        "spark.sql.catalog.reporting", "org.apache.iceberg.spark.SparkCatalog"
    )
    .config(
        "spark.sql.catalog.reporting.catalog-impl",
        "org.apache.iceberg.hadoop.HadoopCatalog",
    )
    .config(
        "spark.sql.catalog.reporting.warehouse",
        f"file:///{LOCAL_WAREHOUSE_PATH.lstrip('/')}",
    )
    # ---------------------------------------------------------
    # CATALOG 2: Cloudflare R2 Catalog ('r2_catalog')
    # ---------------------------------------------------------
    .config(
        "spark.sql.catalog.r2_catalog", "org.apache.iceberg.spark.SparkCatalog"
    )
    .config(
        "spark.sql.catalog.r2_catalog.catalog-impl",
        "org.apache.iceberg.hadoop.HadoopCatalog",
    )
    .config(
        "spark.sql.catalog.r2_catalog.warehouse",
        f"s3a://{R2_BUCKET_NAME}/iceberg",
    )
    # Hadoop S3A Connector Configuration for Cloudflare R2
    .config(
        "spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem"
    )
    .config(
        "spark.hadoop.fs.s3a.endpoint",
        f"https://{R2_AID}.r2.cloudflarestorage.com",
    )
    .config("spark.hadoop.fs.s3a.access.key", R2_AK)
    .config("spark.hadoop.fs.s3a.secret.key", R2_SAK)
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .getOrCreate()
)

print("✅ Spark initialized cleanly!\n")

# -------------------------------------------------------------
# TRANSFER 'INTEGRATION' TABLES
# -------------------------------------------------------------
try:
    # 1. Ensure target namespace exists on Cloudflare R2
    print(
        f"📁 Creating namespace 'r2_catalog.{TARGET_NAMESPACE}' if not present..."
    )
    spark.sql(f"CREATE NAMESPACE IF NOT EXISTS r2_catalog.{TARGET_NAMESPACE}")

    # 2. Fetch all tables from local integration namespace
    tables = spark.sql(
        f"SHOW TABLES IN reporting.{TARGET_NAMESPACE}"
    ).collect()

    if not tables:
        print(f"⚠️ No tables found in reporting.{TARGET_NAMESPACE}")
        sys.exit(0)

    print(
        f"📌 Found {len(tables)} table(s) in 'reporting.{TARGET_NAMESPACE}':"
    )
    for tbl in tables:
        print(f"  • {tbl['tableName']}")

    print("\n" + "=" * 60)
    print(f"🚀 Transferring '{TARGET_NAMESPACE}' tables to Cloudflare R2...")
    print("=" * 60 + "\n")

    # 3. Loop through tables and write to R2
    for tbl in tables:
        tbl_name = tbl["tableName"]
        source_table = f"reporting.{TARGET_NAMESPACE}.{tbl_name}"
        target_table = f"r2_catalog.{TARGET_NAMESPACE}.{tbl_name}"

        print(
            f"🚚 Copying '{source_table}' -> '{target_table}'...",
            end="",
            flush=True,
        )

        df = spark.table(source_table)
        df.writeTo(target_table).using("iceberg").createOrReplace()

        print(f" ✅ DONE ({df.count()} rows)")

    print(
        f"\n🎉 Successfully transferred all '{TARGET_NAMESPACE}' tables to Cloudflare R2!"
    )

except Exception as e:
    print(f"\n❌ Error during transfer: {e}")

finally:
    spark.stop()