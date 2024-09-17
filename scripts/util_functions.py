from pyspark.sql import DataFrame
from pyspark.sql.functions import from_json
from configs import BOOTSTRAP_SERVERS, DB_URL, DB_PROPERTIES


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


def read_from_main_dwh(file_path, spark):
    return spark.read.option("header", "true").csv(file_path)


def write_new_files_to_dwh(df: DataFrame, file_path: str):
    return df.write.mode("append").csv(file_path)
