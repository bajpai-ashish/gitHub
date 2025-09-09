# scripts/spark_mongo_ingest.py

from pyspark.sql import SparkSession
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

def ingest_all_csvs():
    spark = SparkSession.builder.getOrCreate()
    dfs = {}

    for dirname, _, filenames in os.walk('/kaggle/input'):
        for filename in filenames:
            csv_file_path = os.path.join(dirname, filename)
            df = spark.read.csv(csv_file_path, header=True, inferSchema=True)
            key_name = os.path.splitext(filename)[0]
            dfs[key_name] = df

    uri = "mongodb+srv://ashishbajpai:YourNewPassword@z4jnpy6.mongodb.net/"
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client['kaggleDB']

    for collection_name, df in dfs.items():
        records = [row.asDict() for row in df.collect()]
        if records:
            db[collection_name].insert_many(records)
            print(f"Inserted {len(records)} into '{collection_name}'")
        else:
            print(f"No data in '{collection_name}'")
