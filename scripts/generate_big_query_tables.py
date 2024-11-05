from pyspark.sql import SparkSession
from configs import (
    table_name_with_schema_dict,
    # PATH_TO_GOOGLE_APPLICATION_CREDENTIALS,
    TEMP_GCS_BUCKET,
    PROJECT_ID,
    DATASET_ID,
)


spark = (
    SparkSession.builder.appName("BigQueryWrite")
    .config("spark.hadoop.google.cloud.auth.service.account.enable", "true")
    # .config(
    #     "spark.hadoop.google.cloud.auth.service.account.json.keyfile",
    #     PATH_TO_GOOGLE_APPLICATION_CREDENTIALS,
    # )
    .config("fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
    .config("fs.gs.auth.service.account.enable", "true")
    # .config(
    #     "fs.gs.auth.service.account.json.keyfile",
    #     PATH_TO_GOOGLE_APPLICATION_CREDENTIALS,
    # )
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

    print(f"Created table {table_id}")
