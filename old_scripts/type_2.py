from configs import DB_TABLE_EVENT_FACT
from util_functions import write_to_postgres, read_from_postgres
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
    md5,
    lag,
    lead,
    when,
    unix_timestamp,
    lit,
)


def event_fact_stream(spark, listen_events_stream):

    def process_batch_for_event_fact(batch_df: DataFrame, batch_id: int) -> None:

        existing_records_df = read_from_postgres(spark, DB_TABLE_EVENT_FACT)

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

        event_fact_with_existing_records = event_fact_with_added_cols.alias("new").join(
            existing_records_df.alias("existing"), on="EventSK", how="left"
        )

        updated_existing_records = (
            event_fact_with_existing_records.filter(
                col("existing.EventSK").isNotNull()
            )  # Only for matching records
            .withColumn(
                "existing.record_valid_to",
                when(
                    col("new.ts") > col("existing.record_valid_from"), col("new.ts")
                ).cast("long"),
            )
            .withColumn(
                "existing.is_record_valid", lit(0)
            )  # Mark old record as invalid
            .select("existing.*")
        )

        new_records = event_fact_with_added_cols.alias("new").join(
            existing_records_df.alias("existing"), on="EventSK", how="left_anti"
        )

        final_event_fact_df = updated_existing_records.unionByName(new_records)

        write_to_postgres(final_event_fact_df, DB_TABLE_EVENT_FACT)

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
            "LocationSK",
            md5(
                concat_ws(
                    "_",
                    col("city").cast("string"),
                    col("zip").cast("string"),
                    col("state").cast("string"),
                    col("lon").cast("string"),
                    col("lat").cast("string"),
                )
            ),
        )
        .withColumn("SongSK", md5(concat_ws("_", col("song"), col("artist"))))
        .withColumn(
            "EventSK", md5(concat_ws("_", col("sessionId"), col("itemInSession")))
        )
    )

    event_fact_writer = (
        event_fact_with_sks.writeStream.foreachBatch(process_batch_for_event_fact)
        .option(
            "checkpointLocation",
            "/home/lupusruber/music_analytics/checkpoints/event_fact_checkpoint",
        )
        .start()
    )

    return event_fact_writer
