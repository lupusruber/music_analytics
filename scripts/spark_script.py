from pyspark.sql.session import SparkSession
from pyspark.sql.functions import col, from_json, concat_ws, md5
from schemas import (
    listen_events_schema,
    auth_events_schema,
    page_view_events_schema,
    status_change_events_schema,
)


import os

os.environ["PYSPARK_SUBMIT_ARGS"] = (
    "--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0 pyspark-shell"
)


LIST_OF_TOPICS = [
    "auth_events",
    "listen_events",
    "page_view_events",
    "status_change_events",
]


BOOTSTRAP_SERVERS = "localhost:9094"
TOPICS_STRING = ",".join(LIST_OF_TOPICS)
SPARK_MASTER_URL = "spark://localhost:7077"


spark = SparkSession.builder.appName("KafkaStreaming").master("local[*]").getOrCreate()


def create_stream(topic, schema):
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


def main() -> None:

    listen_events = create_stream(topic=LIST_OF_TOPICS[1], schema=listen_events_schema)

    song_dim_with_sk = listen_events.withColumn(
        "SongSK", md5(concat_ws("_", col("song"), col("artist")))
    )

    selected_columns = (
        song_dim_with_sk.select("SongSK", "artist", "song")
        .dropDuplicates(["SongSK"])
        .coalesce(1)
    )

    song_and_artist_dim = (
        selected_columns.writeStream.outputMode("append")
        .format("csv")
        .option("path", "/home/lupusruber/music_analytics/data/artist_dim")
        .option(
            "checkpointLocation",
            "/home/lupusruber/music_analytics/checkpoints/artist_dim_checkpoint",
        )
        .option("header", "true")
        .start()
    )

    song_and_artist_dim.awaitTermination()


if __name__ == "__main__":
    main()
