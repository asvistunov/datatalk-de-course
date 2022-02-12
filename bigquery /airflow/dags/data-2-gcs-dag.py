import os
import logging

from airflow import DAG
from airflow.utils.dates import days_ago


from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator, BigQueryInsertJobOperator
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")

path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'trips_data_all')

default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="data_2_gcs_dag",
    schedule_interval="@daily",
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    tags=['dtc-de'],
) as dag:

    gcs_2_gcs_task = move_files = GCSToGCSOperator(
        task_id='gcs_2_gcs_task',
        source_bucket=BUCKET,
        source_object="raw/yellow_tripdata*.csv",
        destination_object="yellow/yellow_tripdata",
        destination_bucket=BUCKET,
        move_object=False
    )

    gcs_2_bq_ext_task = BigQueryCreateExternalTableOperator(
        task_id="bigquery_external_table_task",
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": "external_yellow_trip_table",
            },
            "externalDataConfiguration": {
                "autodetect": True,
                "sourceFormat": "CSV",
                "sourceUris": [f"gs://{BUCKET}/yellow/*"],
            },
        },
    )

    CREATE_PART_TBL_QUERY = f"""CREATE OR REPLACE TABLE {BIGQUERY_DATASET}.yellow_tripdata_partitoned_clustered
        PARTITION BY DATE(tpep_pickup_datetime)
        CLUSTER BY VendorID AS
        SELECT * FROM {BIGQUERY_DATASET}.external_yellow_trip_table"""

    bq_ext_2_part_task = BigQueryInsertJobOperator(
        task_id='bq_ext_2_part_task',
        configuration={
            "query": {
                "query": CREATE_PART_TBL_QUERY,
                "useLegacySql": False,
            }
        }

    )

    gcs_2_gcs_task >> gcs_2_bq_ext_task >> bq_ext_2_part_task