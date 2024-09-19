from pyspark.sql.session import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    LongType,
    IntegerType
)


import os

os.environ["PYSPARK_SUBMIT_ARGS"] = (
    "--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.0,"
    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,"
    "org.postgresql:postgresql:42.5.0 pyspark-shell"
)

session_fact_schema = StructType(
    [
        StructField("userId", LongType(), False),
        StructField("DateSK", StringType(), False),
        StructField("DateTimeSK", StringType(), False),
        StructField("session_start_ts", LongType(), False),
        StructField("session_end_ts", LongType(), False),
        StructField("level", StringType(), False),
        StructField("session_duration", DoubleType(), True),
        StructField("primary_s_location", StringType(), False),
        StructField("SessionSK", StringType(), False),
    ]
)


spark = SparkSession.builder.appName("KafkaStreaming").master("local[*]").getOrCreate()
DB_TABLE = "SessionFact"
DB_URL = f"jdbc:postgresql://localhost:5432/dwh"
DB_PROPERTIES = {
    "user": "root",
    "password": "root",
    "driver": "org.postgresql.Driver",
}

df = (
    spark.read.option("header", "true")
    .schema(session_fact_schema)
    .csv("/home/lupusruber/music_analytics/SongDimHeader.csv")
)
df.write.jdbc(url=DB_URL, table=DB_TABLE, mode="overwrite", properties=DB_PROPERTIES)
spark.stop()
