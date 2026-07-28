from datetime import datetime
from pyspark.sql import SparkSession

# -------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------
LOCAL_WAREHOUSE_PATH = "/data/data_files/iceberg/WideWorldImportersDW"
MSSQL_JAR = "C:/data/spark/jars/mssql-jdbc-12.6.5.jre11.jar"

# Cloudflare R2 Credentials (Fill these in!)
R2_AID="Variable"
R2_AK="Variable"
R2_SAK="Variable"
R2_BUCKET_NAME = "wide-world-importers-dw"

# If using Cloudflare R2 Data Catalog (REST API):
R2_TKN = ""
R2_CATALOG_URI = f"https://{R2_AID}.r2.cloudflarestorage.com/iceberg"

# -------------------------------------------------------------
# BUILD SPARK SESSION WITH BOTH CATALOGS
# -------------------------------------------------------------
spark = (
    SparkSession.builder.appName("Local to Cloudflare R2 Iceberg Migration")
    # Add Iceberg runtime and AWS bundles for S3A support
    .config(
        "spark.jars.packages",
        "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.1,org.apache.iceberg:iceberg-aws-bundle:1.6.1",
    )
    .config(
        "spark.sql.extensions",
        "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
    )
    # ---------------------------------------------------------
    # CATALOG 1: Local Hadoop Catalog ('reporting')
    # ---------------------------------------------------------
    .config(
        "spark.sql.catalog.reporting",
        "org.apache.iceberg.spark.SparkCatalog",
    )
    .config(
        "spark.sql.catalog.reporting.catalog-impl",
        "org.apache.iceberg.hadoop.HadoopCatalog",
    )
    .config(
        "spark.sql.catalog.reporting.warehouse",
        f"file:///{LOCAL_WAREHOUSE_PATH}",
    )
    # ---------------------------------------------------------
    # CATALOG 2: Cloudflare R2 Catalog ('r2_catalog')
    # Using HadoopCatalog on S3A (or REST catalog)
    # ---------------------------------------------------------
    .config(
        "spark.sql.catalog.r2_catalog",
        "org.apache.iceberg.spark.SparkCatalog",
    )
    .config(
        "spark.sql.catalog.r2_catalog.catalog-impl",
        "org.apache.iceberg.hadoop.HadoopCatalog",
    )
    .config(
        "spark.sql.catalog.r2_catalog.warehouse",
        f"s3a://{R2_BUCKET_NAME}/iceberg",
    )
    # Hadoop S3A Connector Settings for Cloudflare R2
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .config(
        "spark.hadoop.fs.s3a.endpoint",
        f"https://{R2_AID}.r2.cloudflarestorage.com",
    )
    .config("spark.hadoop.fs.s3a.access.key", R2_AK)
    .config("spark.hadoop.fs.s3a.secret.key", R2_SAK)
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .getOrCreate()
)

print("✅ Spark Session initialized successfully!")

# -------------------------------------------------------------
# MIGRATION LOOP
# -------------------------------------------------------------
# Fetch all namespaces from local 'reporting' catalog
namespaces = spark.sql("SHOW NAMESPACES IN reporting").collect()

for ns in namespaces:
    ns_name = ns["namespace"]

    # Skip 'integration' namespace as requested
    if ns_name.lower() == "integration":
        print(f"⏩ Skipping namespace: '{ns_name}'")
        continue

    print(f"\n📁 Processing Namespace: '{ns_name}'...")

    # Create namespace in Cloudflare R2 catalog if it doesn't exist
    spark.sql(f"CREATE NAMESPACE IF NOT EXISTS r2_catalog.{ns_name}")

    # Get all tables in this namespace
    tables = spark.sql(f"SHOW TABLES IN reporting.{ns_name}").collect()

    for tbl in tables:
        tbl_name = tbl["tableName"]
        source_table = f"reporting.{ns_name}.{tbl_name}"
        target_table = f"r2_catalog.{ns_name}.{tbl_name}"

        print(f"  └── 🚚 Transferring table '{source_table}' -> '{target_table}'...")

        # Read local table
        df = spark.table(source_table)

        # Write to Cloudflare R2 as Iceberg table
        df.writeTo(target_table).using("iceberg").createOrReplace()

        print(f"      ✅ Successfully written {df.count()} rows to {target_table}")

print("\n🎉 Migration completed successfully!")