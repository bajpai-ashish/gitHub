from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DateType, TimestampType


# ============================================================
# CONFIGURATION
# ============================================================

MINIO_ENDPOINT = "http://localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"

SOURCE_BUCKET = "rawload"
SOURCE_PREFIX = "Restaurant_Food_Delivery"

# IMPORTANT:
# Keep source untouched.
# Transformed files will go here.
TARGET_BUCKET = "rawload"
TARGET_PREFIX = "Restaurant_Food_Delivery_Test"

MONTHS_TO_ADD = 3

# First run should be True.
# DRY_RUN = True

# Now run should be False.
DRY_RUN = False


# ============================================================
# SPARK SESSION
# ============================================================

spark = (
    SparkSession.builder
    .appName("ShiftRestaurantDates")
    .config(
        "spark.hadoop.fs.s3a.endpoint",
        MINIO_ENDPOINT
    )
    .config(
        "spark.hadoop.fs.s3a.access.key",
        MINIO_ACCESS_KEY
    )
    .config(
        "spark.hadoop.fs.s3a.secret.key",
        MINIO_SECRET_KEY
    )
    .config(
        "spark.hadoop.fs.s3a.path.style.access",
        "true"
    )
    .config(
        "spark.hadoop.fs.s3a.connection.ssl.enabled",
        "false"
    )
    .getOrCreate()
)


# ============================================================
# FIND DATE/TIMESTAMP COLUMNS
# ============================================================

def get_date_columns(df):

    date_columns = []

    for field in df.schema.fields:

        if isinstance(
            field.dataType,
            (DateType, TimestampType)
        ):
            date_columns.append(
                (
                    field.name,
                    field.dataType.simpleString()
                )
            )

    return date_columns


# ============================================================
# PROCESS ONE CSV
# ============================================================

def process_csv(file_name):

    source_path = (
        f"s3a://{SOURCE_BUCKET}/"
        f"{SOURCE_PREFIX}/{file_name}"
    )

    target_path = (
        f"s3a://{TARGET_BUCKET}/"
        f"{TARGET_PREFIX}/{file_name}"
    )

    print()
    print("=" * 80)
    print(f"Processing: {file_name}")
    print("=" * 80)

    print(f"Source : {source_path}")

    # --------------------------------------------------------
    # Read CSV
    # --------------------------------------------------------

    df = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .option("timestampFormat", "yyyy-MM-dd HH:mm:ss")
        .csv(source_path)
    )

    # --------------------------------------------------------
    # Show schema
    # --------------------------------------------------------

    print("\nSchema:")
    df.printSchema()

    # --------------------------------------------------------
    # Find date/timestamp columns
    # --------------------------------------------------------

    date_columns = get_date_columns(df)

    print("\nDate/Timestamp columns:")

    if not date_columns:
        print("  None")

    for column_name, data_type in date_columns:
        print(
            f"  {column_name:<30} {data_type}"
        )

    # --------------------------------------------------------
    # Dry run
    # --------------------------------------------------------

    if DRY_RUN:

        print("\nDRY_RUN=True")
        print("No data will be modified.")

        return

    # --------------------------------------------------------
    # Add 3 months
    # --------------------------------------------------------

    for column_name, data_type in date_columns:
        print(
            f"Shifting {column_name} "
            f"({data_type}) by +{MONTHS_TO_ADD} months"
        )
        
        df = df.withColumn(
            column_name,
            F.add_months(
                F.col(column_name),
                MONTHS_TO_ADD
            )
        )

    # for column_name, data_type in date_columns:

        # print(
        #     f"Shifting {column_name} "
        #     f"by +{MONTHS_TO_ADD} months"
        # )

        # if data_type == "date":

        #     df = df.withColumn(
        #         column_name,
        #         F.add_months(
        #             F.col(column_name),
        #             MONTHS_TO_ADD
        #         )
        #     )

        # elif data_type == "timestamp":

        #     # Preserve the timestamp/time component.
        #     df = df.withColumn(
        #         column_name,
        #         F.to_timestamp(
        #             F.add_months(
        #                 F.to_date(F.col(column_name)),
        #                 MONTHS_TO_ADD
        #             )
        #             +
        #             (
        #                 F.col(column_name).cast("long")
        #                 - F.to_date(F.col(column_name))
        #                   .cast("timestamp")
        #                   .cast("long")
        #             )
        #         )
        #     )

    # --------------------------------------------------------
    # Write transformed CSV
    # --------------------------------------------------------

    print(f"\nWriting: {target_path}")

    (
        df.write
        .mode("overwrite")
        .option("header", "true")
        .csv(target_path)
    )

    print("Completed.")


# ============================================================
# LIST CSV FILES
# ============================================================

def get_csv_files():

    source_path = (
        f"s3a://{SOURCE_BUCKET}/"
        f"{SOURCE_PREFIX}/*.csv"
    )

    return source_path


# ============================================================
# MAIN
# ============================================================

try:

    csv_path = get_csv_files()

    # --------------------------------------------------------
    # For the first test, process all CSV files
    # --------------------------------------------------------

    df_files = (
        spark.read
        .format("binaryFile")
        .load(csv_path)
        .select("path")
    )

    files = [
        row.path
        for row in df_files.collect()
    ]

    print(f"Found {len(files)} CSV files.")

    for source_path in files:

        file_name = source_path.split("/")[-1]

        process_csv(file_name)
        # process_csv("order_status_history.csv")

finally:

    spark.stop()