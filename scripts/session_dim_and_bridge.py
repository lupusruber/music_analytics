from configs import (
    DB_TABLE_SESSION_DIM,
    DB_TABLE_EVENT_SESSION_BRIDGE,
    CHECKPOINT_DIR_ROOT,
)
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, hash, concat_ws
from util_functions import read_from_bigquery_dwh, write_to_bigquery


def session_dim_bridge_stream(spark, page_view_stream):

    def process_batch_for_session_dim_bridge(
        batch_df: DataFrame, batch_id: int
    ) -> None:

        # check which ones are already in the DWH and then append the new ones to the DWH
        # 1. Read the Song Dim from DWH
        # 2. Antijoin DWH userId with batch userId
        # 3. Append the new rows to DWH

        session_dim = batch_df.select(
            col("SessionSK"),
            col("sessionId"),
            col("userId"),
        ).dropDuplicates(["SessionSK"])

        main_dwh_df = read_from_bigquery_dwh(spark, DB_TABLE_SESSION_DIM)

        new_unique_records = session_dim.join(
            main_dwh_df, on=["SessionSK"], how="left_anti"
        )

        write_to_bigquery(new_unique_records, DB_TABLE_SESSION_DIM)

        session_event_bridge = batch_df.select(
            col("SessionSK"),
            col("EventSK"),
        )

        main_dwh_df = read_from_bigquery_dwh(spark, DB_TABLE_EVENT_SESSION_BRIDGE)

        new_unique_records = session_event_bridge.join(
            main_dwh_df, on=["SessionSK", "EventSK"], how="left_anti"
        )

        write_to_bigquery(new_unique_records, DB_TABLE_EVENT_SESSION_BRIDGE)

    session_dim_bridge_with_sk = (
        page_view_stream.filter(col("userId").isNotNull())
        .withColumn(
            "EventSK",
            hash(concat_ws("_", col("sessionId"), col("itemInSession"))).cast("long"),
        )
        .withColumn(
            "SessionSK",
            hash(concat_ws("_", col("userId"), col("sessionId"))).cast("long"),
        )
    )

    session_dim_bridge_writer = (
        session_dim_bridge_with_sk.writeStream.foreachBatch(
            process_batch_for_session_dim_bridge
        )
        .option(
            "checkpointLocation",
            f"{CHECKPOINT_DIR_ROOT}/session_dim_bridge_checkpoint",
        )
        .start()
    )

    return session_dim_bridge_writer
