from pyspark.sql import DataFrame
from pyspark.sql.functions import from_json
from configs import BOOTSTRAP_SERVERS, DB_URL, DB_PROPERTIES, PROJECT_ID, DATASET_ID


def create_stream(spark, topic, schema):

    return (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", BOOTSTRAP_SERVERS)
        .option("subscribe", topic)
        .option("startingOffsets", "earliest")
        .load()
        .selectExpr("CAST(value as STRING) as value")
        .select(from_json("value", schema).alias("data"))
        .select("data.*")
    )


def read_from_postgres(spark, table: str):
    return spark.read.jdbc(url=DB_URL, table=table, properties=DB_PROPERTIES)


def write_to_postgres(df: DataFrame, table: str):
    df.write.mode("append").jdbc(url=DB_URL, table=table, properties=DB_PROPERTIES)


def read_from_dummy_dwh(file_path, spark):
    return spark.read.option("header", "true").csv(file_path)


def write_new_files_to_dummy_dwh(df: DataFrame, file_path: str):
    return df.write.mode("append").csv(file_path)


def write_to_bigquery(spark_data_frame: DataFrame, table_id: str, mode: str = "append"):

    (
        spark_data_frame.write.mode(mode)
        .format("bigquery")
        .option("table", f"{PROJECT_ID}:{DATASET_ID}.{table_id}")
        .save()
    )


def read_from_bigquery_dwh(spark, table_id: str) -> DataFrame:

    return (
        spark.read.format("bigquery")
        .option("table", f"{PROJECT_ID}:{DATASET_ID}.{table_id}")
        .load()
    )
