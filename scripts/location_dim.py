from configs import DB_TABLE_LOCATION_DIM, CHECKPOINT_DIR_ROOT
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, concat_ws, hash
from util_functions import write_to_bigquery, read_from_bigquery_dwh


def location_dim_stream(spark, page_view_events):

    def process_batch_for_location_dim(batch_df: DataFrame, batch_id: int) -> None:

        main_dwh_df = read_from_bigquery_dwh(spark, DB_TABLE_LOCATION_DIM)
        new_unique_records = batch_df.join(
            main_dwh_df, on=["LocationSK"], how="left_anti"
        )
        write_to_bigquery(new_unique_records, DB_TABLE_LOCATION_DIM)

    locatiom_with_sk = page_view_events.withColumn(
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

    location_dim = locatiom_with_sk.select(
        "LocationSK", "city", "zip", "state", "lon", "lat"
    ).dropDuplicates(["LocationSK"])

    location_dim_writer = (
        location_dim.writeStream.foreachBatch(process_batch_for_location_dim)
        .option(
            "checkpointLocation",
            f"{CHECKPOINT_DIR_ROOT}/location_dim_checkpoint",
        )
        .start()
    )

    return location_dim_writer
