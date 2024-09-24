from configs import DB_TABLE_EVENT_DIM
from util_functions import read_from_postgres, write_to_postgres
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, md5, concat_ws, when
import pyspark.sql.functions as F


def event_dim_stream(spark, page_view_stream):

    def process_batch_for_event_dim(batch_df: DataFrame, batch_id: int) -> None:

        # check which ones are already in the DWH and then append the new ones to the DWH
        # 1. Read the Song Dim from DWH
        # 2. Antijoin DWH_userId with batch_userId
        # 3. Append the new rows to DWH

        event_dim_with_dwh_columns = batch_df.select(
            col("EventSK"),
            col("userId"),
            col("itemInSession"),
            col("sessionId"),
            col("userAgent"),
            col("page"),
            col("auth"),
            col("method"),
            col("status"),
            col("level"),
            col("is_listen_event"),
        )

        main_dwh_df = read_from_postgres(spark, DB_TABLE_EVENT_DIM)
        new_unique_records = event_dim_with_dwh_columns.join(
            main_dwh_df, on=["EventSK"], how="left_anti"
        )
        write_to_postgres(new_unique_records, DB_TABLE_EVENT_DIM)

    event_dim_with_sk = page_view_stream.withColumn(
        "EventSK", md5(concat_ws("_", col("sessionId"), col("itemInSession")))
    ).withColumn("is_listen_event", when(col("song").isNotNull(), 1).otherwise(0))

    event_dim_writer = (
        event_dim_with_sk.writeStream.foreachBatch(process_batch_for_event_dim)
        .option(
            "checkpointLocation",
            "/home/lupusruber/music_analytics/checkpoints/event_dim_checkpoint",
        )
        .start()
    )

    return event_dim_writer
