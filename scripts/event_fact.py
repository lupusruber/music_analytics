from configs import DB_TABLE_EVENT_FACT, CHECKPOINT_DIR_ROOT
from util_functions import write_to_bigquery
from pyspark.sql import DataFrame
from pyspark.sql.window import Window

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
    hash,
    lag,
    lead,
    when,
    unix_timestamp,
    lit,
)

def event_fact_stream(spark, listen_events_stream):

    def process_batch_for_event_fact(batch_df: DataFrame, batch_id: int) -> None:

        user_window = Window.partitionBy("userId").orderBy("timestamp")

        event_fact_with_added_cols = (
            batch_df.withColumn("record_valid_from", col("ts"))
            .withColumn("record_valid_to", lit(None).cast("long"))
            .withColumn("is_record_valid", lit(1))
            .withColumn("consecutive_no_song", lit(0))
            .withColumn(
                "is_moving",
                when(
                    (lag(col("lat")).over(user_window) == col("lat"))
                    | (lag(col("lon")).over(user_window) == col("lon")),
                    0,
                ).otherwise(1),
            )
            .withColumn(
                "consecutive_no_song",
                when(
                    lag(col("artist")).over(user_window) == col("artist"),
                    col("consecutive_no_song") + 1,
                ).otherwise(0),
            )
            .withColumn(
                "is_first_listen_event",
                when(lag(col("timestamp")).over(user_window).isNull(), 1).otherwise(0),
            )
            .withColumn(
                "is_last_listen_event",
                when(lead(col("timestamp")).over(user_window).isNull(), 1).otherwise(0),
            )
            .withColumn(
                "next_listen_event_time_gap",
                unix_timestamp(lead(col("timestamp")).over(user_window))
                - unix_timestamp(col("timestamp")),
            )
            .withColumn(
                "is_song_skipped", when(col("duration") < lit(30), 1).otherwise(0)
            )
        )

        event_fact_with_added_cols = event_fact_with_added_cols.select(
            col("userId"),
            col("EventSK"),
            col("DateTimeSK"),
            col("DateSK"),
            col("LocationSK"),
            col("SongSK"),
            col("ts").alias("timestamp"),
            col("level"),
            col("duration"),
            col("is_moving"),
            col("consecutive_no_song"),
            col("is_first_listen_event"),
            col("is_last_listen_event"),
            col("is_song_skipped"),
            col("next_listen_event_time_gap"),
            col("record_valid_from"),
            col("record_valid_to"),
            col("is_record_valid"),
        )

        write_to_bigquery(event_fact_with_added_cols, DB_TABLE_EVENT_FACT)

    event_fact_with_sks = (
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
            hash(
                concat_ws(
                    "_",
                    col("year").cast("string"),
                    col("month").cast("string"),
                    col("day").cast("string"),
                    col("hour").cast("string"),
                    col("minute").cast("string"),
                    col("second").cast("string"),
                )
            ).cast('long'),
        )
        .withColumn(
            "DateSK",
            hash(
                concat_ws(
                    "_",
                    col("year").cast("string"),
                    col("month").cast("string"),
                    col("day").cast("string"),
                )
            ).cast('long'),
        )
        .withColumn(
            "LocationSK",
            hash(
                concat_ws(
                    "_",
                    col("city").cast("string"),
                    col("zip").cast("string"),
                    col("state").cast("string"),
                    col("lon").cast("string"),
                    col("lat").cast("string"),
                )
            ).cast('long'),
        )
        .withColumn("SongSK", hash(concat_ws("_", col("song"), col("artist"))).cast('long'))
        .withColumn(
            "EventSK", hash(concat_ws("_", col("sessionId"), col("itemInSession"))).cast('long')
        )
    )

    event_fact_writer = (
        event_fact_with_sks.writeStream.foreachBatch(process_batch_for_event_fact)
        .option(
            "checkpointLocation",
            f"{CHECKPOINT_DIR_ROOT}/event_fact_checkpoint",
        )
        .start()
    )

    return event_fact_writer
