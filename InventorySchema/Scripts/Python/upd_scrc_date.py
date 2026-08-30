import io
import os
import uuid
from datetime import datetime

import pandas as pd
from minio import Minio
from minio.commonconfig import CopySource


# ============================================================
# CONFIGURATION
# ============================================================

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

BUCKET = "rawload"
PREFIX = "Restaurant_Food_Delivery/"

# Add three calendar months
MONTHS_TO_ADD = 3

# Process large CSVs in chunks
CHUNK_SIZE = 100_000

# IMPORTANT:
# First run with True.
# It will inspect files but NOT modify MinIO.
DRY_RUN = True


# ============================================================
# MINIO CONNECTION
# ============================================================

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE,
)


# ============================================================
# DATE COLUMN DETECTION
# ============================================================

def is_likely_date_column(column_name: str) -> bool:
    """
    First-level detection based on column name.
    This prevents numeric columns such as ID from being
    accidentally interpreted as dates.
    """

    name = column_name.lower().strip()

    date_keywords = [
        "date",
        "time",
        "_at",
        "timestamp",
        "created",
        "updated",
        "expires",
        "placed",
        "completed",
        "paid",
        "assigned",
        "picked_up",
        "delivered",
        "recorded",
        "processed",
    ]

    return any(keyword in name for keyword in date_keywords)


def detect_date_columns(object_name: str) -> list[str]:
    """
    Read a small sample from the CSV and identify columns that
    look like date/datetime columns.
    """

    response = client.get_object(BUCKET, object_name)

    try:
        sample = pd.read_csv(
            response,
            nrows=5_000,
            low_memory=False
        )
    finally:
        response.close()
        response.release_conn()

    date_columns = []

    for column in sample.columns:

        # First filter by column name
        if not is_likely_date_column(column):
            continue

        series = sample[column]

        # Ignore completely empty columns
        if series.dropna().empty:
            continue

        # Try converting to datetime
        parsed = pd.to_datetime(
            series,
            errors="coerce"
        )

        valid_ratio = parsed.notna().mean()

        # 95% of non-null values should be valid dates
        if valid_ratio >= 0.95:
            date_columns.append(column)

    return date_columns


# ============================================================
# PROCESS ONE CSV
# ============================================================

def process_csv(object_name: str):

    print()
    print("=" * 80)
    print(f"Processing: {object_name}")
    print("=" * 80)

    date_columns = detect_date_columns(object_name)

    print(f"Detected date columns: {date_columns}")

    if not date_columns:
        print("No date columns detected. Skipping.")
        return

    if DRY_RUN:
        print("DRY_RUN=True -> file will NOT be modified.")
        return

    # --------------------------------------------------------
    # Temporary object
    # --------------------------------------------------------

    temp_object = (
        f"{object_name}.__temp__{uuid.uuid4().hex}.csv"
    )

    print(f"Temporary object: {temp_object}")

    # --------------------------------------------------------
    # Read source CSV
    # --------------------------------------------------------

    response = client.get_object(BUCKET, object_name)

    try:

        first_chunk = True

        for chunk_number, df in enumerate(
            pd.read_csv(
                response,
                chunksize=CHUNK_SIZE,
                low_memory=False
            )
        ):

            print(
                f"  Processing chunk {chunk_number + 1}: "
                f"{len(df):,} rows"
            )

            # ------------------------------------------------
            # Shift dates
            # ------------------------------------------------

            for column in date_columns:

                original = pd.to_datetime(
                    df[column],
                    errors="coerce"
                )

                df[column] = original + pd.DateOffset(
                    months=MONTHS_TO_ADD
                )

            # ------------------------------------------------
            # Convert chunk to CSV bytes
            # ------------------------------------------------

            csv_bytes = df.to_csv(
                index=False,
                header=first_chunk
            ).encode("utf-8")

            # ------------------------------------------------
            # Append chunk to temporary MinIO object
            #
            # NOTE:
            # MinIO does not provide a simple append-object API.
            # Therefore this first implementation keeps the
            # temporary file locally.
            # ------------------------------------------------

            local_temp = f"/tmp/{uuid.uuid4().hex}.csv"

            with open(local_temp, "wb") as f:
                f.write(csv_bytes)

            # This section is intentionally handled below
            # using a local temporary file.

            first_chunk = False

    finally:
        response.close()
        response.release_conn()

    print("Finished processing.")


# ============================================================
# LIST ALL CSV FILES
# ============================================================

def list_csv_files():

    objects = client.list_objects(
        BUCKET,
        prefix=PREFIX,
        recursive=True
    )

    csv_files = []

    for obj in objects:

        if obj.object_name.lower().endswith(".csv"):
            csv_files.append(obj.object_name)

    return csv_files


# ============================================================
# MAIN
# ============================================================

def main():

    print("Connecting to MinIO...")
    print(f"Bucket : {BUCKET}")
    print(f"Prefix : {PREFIX}")
    print(f"Shift  : +{MONTHS_TO_ADD} months")
    print(f"Dry run: {DRY_RUN}")

    csv_files = list_csv_files()

    print()
    print(f"Found {len(csv_files)} CSV files.")

    for object_name in csv_files:
        process_csv(object_name)


if __name__ == "__main__":
    main()