from configs import DB_TABLE_DATE_DIM, DB_TABLE_DATE_TIME_DIM, CHECKPOINT_DIR_ROOT
from util_functions import read_from_bigquery_dwh, write_to_bigquery
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, concat_ws, hash
from pyspark.sql.functions import (
    col,
    year,
    month,
    dayofmonth,
    hour,
    minute,
    second,
    from_unixtime,
)


def date_and_date_time_stream(spark, page_view_events):

    def process_batch_for_date_date_time_dim(
        batch_df: DataFrame, batch_id: int
    ) -> None:

        date_dim_from_dwh = read_from_bigquery_dwh(spark, DB_TABLE_DATE_DIM)
        new_date_data = batch_df.dropDuplicates(["DateSK"]).select(
            "DateSK", "year", "month", "day"
        )
        new_date_data_unique = new_date_data.join(
            date_dim_from_dwh, on=["DateSK"], how="left_anti"
        )
        write_to_bigquery(new_date_data_unique, DB_TABLE_DATE_DIM)

        date_time_dim_from_dwh = read_from_bigquery_dwh(spark, DB_TABLE_DATE_TIME_DIM)
        new_date_time_data = batch_df.select(
            "DateTimeSK",
            "year",
            "month",
            "day",
            "hour",
            "minute",
            "second",
        ).dropDuplicates(["DateTimeSK"])
        new_date_time_data_unique = new_date_time_data.join(
            date_time_dim_from_dwh, on=["DateTimeSK"], how="left_anti"
        )
        write_to_bigquery(new_date_time_data_unique, DB_TABLE_DATE_TIME_DIM)

    only_ts = (
        page_view_events.select("ts")
        .dropDuplicates(["ts"])
        .withColumn("timestamp", from_unixtime(col("ts") / 1000).cast("timestamp"))
        .select(
            year("timestamp").alias("year"),
            month("timestamp").alias("month"),
            dayofmonth("timestamp").alias("day"),
            hour("timestamp").alias("hour"),
            minute("timestamp").alias("minute"),
            second("timestamp").alias("second"),
        )
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
    )

    date_date_time_writer = (
        only_ts.writeStream.foreachBatch(process_batch_for_date_date_time_dim)
        .option(
            "checkpointLocation",
            f"{CHECKPOINT_DIR_ROOT}/date_and_date_time_dims_checkpoint",
        )
        .start()
    )

    return date_date_time_writer
