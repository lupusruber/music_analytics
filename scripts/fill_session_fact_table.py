from util_functions import read_from_bigquery_dwh, write_to_bigquery
from pyspark.sql import SparkSession
from configs import (
    TEMP_GCS_BUCKET,
    APP_NAME,
    DB_TABLE_EVENT_FACT,
    DB_TABLE_EVENT_SESSION_BRIDGE,
    DB_TABLE_SESSION_FACT,
)
from pyspark.sql import functions as F


spark = (
    SparkSession.builder.appName(APP_NAME)
    .config("spark.hadoop.google.cloud.auth.service.account.enable", "true")
    .config("fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
    .config("fs.gs.auth.service.account.enable", "true")
    .config(
        "spark.history.fs.update.interval", "10s"
    )
    .config("temporaryGcsBucket", TEMP_GCS_BUCKET)
    .getOrCreate()
)


event_fact = (
    read_from_bigquery_dwh(spark, DB_TABLE_EVENT_FACT)
    .filter(F.col("is_record_valid") == F.lit(1))
    .select(
        F.col("EventSK"),
        F.col("LocationSK"),
        F.col("timestamp"),
        F.col("level"),
        F.col("duration"),
        F.col("DateSK"),
        F.col("userId"),
        F.col("DateTimeSK"),
    )
)
bridge = read_from_bigquery_dwh(spark, DB_TABLE_EVENT_SESSION_BRIDGE)
event_fact_with_session_sk = event_fact.join(bridge, on="EventSK", how="inner")


# Step 1: Perform the group by and aggregate functions
# Step 2: Create a DataFrame for the new session records with the additional columns
new_session_records = (
    event_fact_with_session_sk.groupBy("SessionSK")
    .agg(
        F.min("timestamp").alias("session_start_ts"),
        F.max("timestamp").alias("session_end_ts"),
        F.sum("duration").alias("session_duration"),
        F.mode("LocationSK").alias("primary_s_location"),
        F.mode("userId").alias("userId"),
        F.mode("level").alias("level"),
        F.mode("DateSK").alias("DateSK"),
        F.mode("DateTimeSK").alias("DateTimeSK"),
    )
    .withColumn("record_valid_from", F.current_timestamp().cast("long"))
    .withColumn("record_valid_to", F.lit(None).cast("long"))
    .withColumn("is_record_valid", F.lit(1))
    .alias("new")
)


existing_session_fact = (
    read_from_bigquery_dwh(spark, DB_TABLE_SESSION_FACT)
    .filter(F.col("is_record_valid") == F.lit(1))
    .alias("existing")
)


records_to_close = (
    existing_session_fact.join(new_session_records, on="SessionSK", how="inner")
    .filter(F.col("existing.record_valid_from") > F.col("new.record_valid_from"))
    .select(
        "existing.*",  # Select all columns from the existing session
        F.col("new.record_valid_from").alias("new_record_valid_from"),
    )
)


# Step 3: Update the existing records' record_valid_to to match new_record_valid_from and mark them as closed
closed_session_records = (
    records_to_close.withColumn("record_valid_to", F.col("new_record_valid_from"))
    .withColumn("is_record_valid", F.lit(0))
    .drop("new_record_valid_from")
)  # Drop the temporary column after use

closed_session_records = closed_session_records.select(
        F.col("userId"),
        F.col("DateSK"),
        F.col("DateTimeSK"),
        F.col("session_start_ts"),
        F.col("session_end_ts"),
        F.col("level"),
        F.col("session_duration"),
        F.col("primary_s_location"),
        F.col("SessionSK"),
        F.col("record_valid_from"),
        F.col("record_valid_to"),
        F.col("is_record_valid"),
)

new_session_records = new_session_records.select(
        F.col("userId"),
        F.col("DateSK"),
        F.col("DateTimeSK"),
        F.col("session_start_ts"),
        F.col("session_end_ts"),
        F.col("level"),
        F.col("session_duration"),
        F.col("primary_s_location"),
        F.col("SessionSK"),
        F.col("record_valid_from"),
        F.col("record_valid_to"),
        F.col("is_record_valid"),
)

new_session_records.show(2)


# Step 4: Combine the closed records with the new session records
final_records = closed_session_records.union(new_session_records)

final_records_selected_cols = final_records.select(
        F.col("userId"),
        F.col("DateSK"),
        F.col("DateTimeSK"),
        F.col("session_start_ts"),
        F.col("session_end_ts"),
        F.col("level"),
        F.col("session_duration"),
        F.col("primary_s_location"),
        F.col("SessionSK"),
        F.col("record_valid_from"),
        F.col("record_valid_to"),
        F.col("is_record_valid"),
)


# Write the final records back to BigQuery
write_to_bigquery(
    final_records_selected_cols, DB_TABLE_SESSION_FACT, mode="append"
)  # Use 'append' if needed instead
