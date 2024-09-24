from configs import DB_TABLE_SESSION_FACT
from util_functions import write_to_postgres, read_from_postgres
from pyspark.sql import DataFrame

from pyspark.sql.functions import (
    col,
    year,
    month,
    dayofmonth,
    hour,
    minute,
    second,
    from_unixtime,
    concat_ws,
    md5,
    lit,
)


def session_fact_stream(spark, listen_events_stream):

    def process_batch_for_session_fact(batch_df: DataFrame, batch_id: int) -> None:
        
        unique = batch_df.dropDuplicates(['SessionSK'])

        session_fact_with_tss = (
            unique.withColumn("record_valid_from", col("ts"))
            .withColumn("record_valid_to", lit(None).cast("long"))
            .withColumn("is_record_valid", lit(1))
            .withColumn("session_duration", lit(0).cast("double"))
            .withColumn("primary_s_location", lit(None).cast("string"))
            .withColumn("session_start_ts", lit(None).cast('long'))
            .withColumn("session_end_ts", lit(None).cast('long'))
        )

        session_fact_with_cols = session_fact_with_tss.select(
            col("userId"),
            col("DateSK"),
            col("DateTimeSK"),
            col("session_start_ts"),
            col("session_end_ts"),
            col("level"),
            col("session_duration"),
            col("primary_s_location"),
            col("SessionSK"),
            col("record_valid_from"),
            col("record_valid_to"),
            col("is_record_valid"),
        )
        
        main_dwh_df = read_from_postgres(spark, DB_TABLE_SESSION_FACT)
        new_unique_records = session_fact_with_cols.join(
            main_dwh_df, on=["SessionSK"], how="left_anti"
        )
        write_to_postgres(new_unique_records, DB_TABLE_SESSION_FACT)
        

    session_fact_with_sks = (
        listen_events_stream.filter(col("duration").isNotNull())
        .withColumn("timestamp", from_unixtime(col("ts") / 1000).cast("timestamp"))
        .withColumn("year", year(col("timestamp")))
        .withColumn("month", month(col("timestamp")))
        .withColumn("day", dayofmonth(col("timestamp")))
        .withColumn("hour", hour(col("timestamp")))
        .withColumn("minute", minute(col("timestamp")))
        .withColumn("second", second(col("timestamp")))
        .withColumn(
            "DateTimeSK",
            md5(
                concat_ws(
                    "_",
                    col("year").cast("string"),
                    col("month").cast("string"),
                    col("day").cast("string"),
                    col("hour").cast("string"),
                    col("minute").cast("string"),
                    col("second").cast("string"),
                )
            ),
        )
        .withColumn(
            "DateSK",
            md5(
                concat_ws(
                    "_",
                    col("year").cast("string"),
                    col("month").cast("string"),
                    col("day").cast("string"),
                )
            ),
        )
        .withColumn(
            "SessionSK",
            md5(
                concat_ws(
                    "_", col("userId").cast("string"), col("sessionId").cast("string")
                )
            ),
        )
    )

    session_fact_writer = (
        session_fact_with_sks.writeStream.foreachBatch(process_batch_for_session_fact)
        .option(
            "checkpointLocation",
            "/home/lupusruber/music_analytics/checkpoints/session_fact_checkpoint",
        )
        .start()
    )

    return session_fact_writer
