from configs import DB_TABLE_SONG_DIM, CHECKPOINT_DIR_ROOT
from util_functions import read_from_bigquery_dwh, write_to_bigquery
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, concat_ws, hash


def song_dim_stream(spark, listen_events_stream):

    def process_batch_for_song_dim(batch_df: DataFrame, batch_id: int) -> None:

        # Check which ones are already in the DWH and then append the new ones to the DWH
        # 1. Read the Song Dim from DWH
        # 2. Antijoin DWH_Song_SKs with batch_Song_SKs
        # 3. Append the new rows to DWH

        main_dwh_df = read_from_bigquery_dwh(spark, DB_TABLE_SONG_DIM)
        new_unique_records = batch_df.join(main_dwh_df, on=["SongSK"], how="left_anti")
        write_to_bigquery(new_unique_records, DB_TABLE_SONG_DIM)

    song_artist_with_sk = listen_events_stream.withColumn(
        "SongSK", hash(concat_ws("_", col("song"), col("artist"))).cast("long")
    )

    song_dim = song_artist_with_sk.select("SongSK", "artist", "song").dropDuplicates(
        ["SongSK"]
    )

    song_dim_writer = (
        song_dim.writeStream.foreachBatch(process_batch_for_song_dim)
        .option(
            "checkpointLocation",
            f"{CHECKPOINT_DIR_ROOT}/artist_dim_checkpoint",
        )
        .start()
    )

    return song_dim_writer
