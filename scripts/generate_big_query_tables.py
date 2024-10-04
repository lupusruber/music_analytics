from pyspark.sql import SparkSession
import os
from configs import table_name_with_schema_dict, PATH_TO_GOOGLE_APPLICATION_CREDENTIALS

project_id = "music-analytics-project"
region = "us-central1"
cluster_name = "dataproc-cluster"

dataset_id = "music_analytics"

temp_gcs_bucket = "music_analytics_bucket"


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
    .getOrCreate()
)

spark.conf.set("temporaryGcsBucket", temp_gcs_bucket)

for table_id, schema in table_name_with_schema_dict.items():

    df = spark.createDataFrame(
        [],
        schema=schema,
    )

    df.write.format("bigquery").option("writeMethod", "direct").option(
        "table", f"{project_id}:{dataset_id}.{table_id}"
    ).save()
