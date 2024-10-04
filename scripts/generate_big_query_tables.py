from pyspark.sql import SparkSession
import os
from configs import (
    table_name_with_schema_dict,
    PATH_TO_GOOGLE_APPLICATION_CREDENTIALS,
    TEMP_GCS_BUCKET,
    PROJECT_ID,
    DATASET_ID,
)


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = PATH_TO_GOOGLE_APPLICATION_CREDENTIALS

os.environ["PYSPARK_SUBMIT_ARGS"] = (
    "--packages "
    "org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.0,"
    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,"
    "org.postgresql:postgresql:42.5.0,"
    "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.28.0,"
    "com.google.cloud.bigdataoss:gcs-connector:hadoop3-2.2.5 "
    "pyspark-shell"
)

spark = (
    SparkSession.builder.appName("BigQueryWrite")
    .config("spark.hadoop.google.cloud.auth.service.account.enable", "true")
    .config(
        "spark.hadoop.google.cloud.auth.service.account.json.keyfile",
        PATH_TO_GOOGLE_APPLICATION_CREDENTIALS,
    )
    .config("fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
    .config("fs.gs.auth.service.account.enable", "true")
    .config(
        "fs.gs.auth.service.account.json.keyfile",
        PATH_TO_GOOGLE_APPLICATION_CREDENTIALS,
    )
    .config("temporaryGcsBucket", TEMP_GCS_BUCKET)
    .getOrCreate()
)


for table_id, schema in table_name_with_schema_dict.items():

    df = spark.createDataFrame(
        [],
        schema=schema,
    )

    df.write.format("bigquery").option("writeMethod", "direct").option(
        "table", f"{PROJECT_ID}:{DATASET_ID}.{table_id}"
    ).save()
