from pyspark.sql.session import SparkSession
from pyspark.sql.functions import col, concat_ws, md5
from schemas import listen_events_schema
from pyspark.sql import DataFrame
from configs import DB_TABLE_SONG_DIM, LISTEN_EVENTS_TOPIC, SPARK_MASTER_URL, APP_NAME
from util_functions import read_from_postgres, write_to_postgres, create_stream


spark = SparkSession.builder.appName(APP_NAME).master(SPARK_MASTER_URL).getOrCreate()


def process_batch(batch_df: DataFrame, batch_id: int) -> None:

    # check which ones are already in the DWH and then append the new ones to the DWH
    # 1. Read the Song Dim from DWH
    # 2. Antijoin DWH_Song_SKs with batch_Song_SKs
    # 3. Append the new rows to DWH

    main_dwh_df = read_from_postgres(spark, DB_TABLE_SONG_DIM)
    new_data = batch_df.exceptAll(main_dwh_df)
    write_to_postgres(new_data, DB_TABLE_SONG_DIM)

    # dwh_path = '/home/lupusruber/music_analytics/dummy_dwh'
    # main_dwh_df = read_from_main_dwh(dwh_path, spark)
    # write_new_files_to_dwh(new_data, dwh_path)


def song_dim_stream():

    listen_events = create_stream(
        spark=spark, topic=LISTEN_EVENTS_TOPIC, schema=listen_events_schema
    )

    song_artist_with_sk = listen_events.withColumn(
        "SongSK", md5(concat_ws("_", col("song"), col("artist")))
    )

    song_dim = (
        song_artist_with_sk.select("SongSK", "artist", "song")
        .dropDuplicates(["SongSK"])
        .coalesce(1)
    )

    song_dim_writer = (
        song_dim.writeStream.foreachBatch(process_batch)
        .option(
            "checkpointLocation",
            "/home/lupusruber/music_analytics/checkpoints/artist_dim_checkpoint",
        )
        .start()
    )

    return song_dim_writer


def main() -> None:

    song_dim = song_dim_stream()
    song_dim.awaitTermination()


if __name__ == "__main__":
    main()
