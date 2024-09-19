from configs import DB_TABLE_USER_DIM
from util_functions import read_from_postgres, write_to_postgres
from pyspark.sql import DataFrame
from pyspark.sql.functions import col
import pyspark.sql.functions as F


def user_dim_stream(spark, listen_events_stream):

    def process_batch_for_user_dim(batch_df: DataFrame, batch_id: int) -> None:

        # check which ones are already in the DWH and then append the new ones to the DWH
        # 1. Read the Song Dim from DWH
        # 2. Antijoin DWH_userId with batch_userId
        # 3. Append the new rows to DWH

        user_dim_with_dwh_columns = batch_df.select(
            col("userId"),
            col("firstName"),
            col("lastName"),
            col("gender"),
            col("registration").alias("registration_ts"),
            col("city").alias("registration_city"),
            col("zip").alias("registration_zip"),
            col("state").alias("registration_state"),
            col("lon").alias("registration_lon"),
            col("lat").alias("registration_lat"),
        )

        main_dwh_df = read_from_postgres(spark, DB_TABLE_USER_DIM)
        new_unique_records = user_dim_with_dwh_columns.join(
            main_dwh_df, on=["userId"], how="left_anti"
        )
        write_to_postgres(new_unique_records, DB_TABLE_USER_DIM)

    listen_events_stream_with_watermark = listen_events_stream.withColumn(
        "event_time", F.from_unixtime(F.col("ts") / 1000).cast("timestamp")
    ).withWatermark("event_time", "2 minutes")

    user_dim = listen_events_stream_with_watermark.groupBy("userId").agg(
        F.min("event_time").alias("earliest_ts"),
        F.first("city").alias("city"),
        F.first("zip").alias("zip"),
        F.first("state").alias("state"),
        F.first("userAgent").alias("userAgent"),
        F.first("lon").alias("lon"),
        F.first("lat").alias("lat"),
        F.first("lastName").alias("lastName"),
        F.first("firstName").alias("firstName"),
        F.first("gender").alias("gender"),
        F.first("registration").alias("registration"),
    )

    user_dim_writer = (
        user_dim.writeStream.foreachBatch(process_batch_for_user_dim)
        .outputMode("update")
        .option(
            "checkpointLocation",
            "/home/lupusruber/music_analytics/checkpoints/user_dim_checkpoint",
        )
        .start()
    )

    return user_dim_writer
