# dags/spark_ingest_dag.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
sys.path.append('/path/to/scripts')  # Adjust this path

from spark_mongo_ingest import ingest_all_csvs

default_args = {
    'owner': 'ashish',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

with DAG('spark_to_mongo_pipeline',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False) as dag:

    run_ingestion = PythonOperator(
        task_id='run_spark_mongo_ingestion',
        python_callable=ingest_all_csvs
    )

    run_ingestion
