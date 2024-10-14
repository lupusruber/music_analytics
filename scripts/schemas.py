from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType,
    LongType,
    TimestampType,
)

# RAW TABLES SCHEMAS

auth_events_schema = StructType(
    [
        StructField("ts", LongType(), True),
        StructField("sessionId", LongType(), True),
        StructField("level", StringType(), True),
        StructField("itemInSession", LongType(), True),
        StructField("city", StringType(), True),
        StructField("zip", StringType(), True),
        StructField("state", StringType(), True),
        StructField("userAgent", StringType(), True),
        StructField("lon", DoubleType(), True),
        StructField("lat", DoubleType(), True),
        StructField("userId", LongType(), True),
        StructField("lastName", StringType(), True),
        StructField("firstName", StringType(), True),
        StructField("gender", StringType(), True),
        StructField("registration", LongType(), True),
        StructField("success", StringType(), True),
    ]
)

page_view_events_schema = StructType(
    [
        StructField("ts", LongType(), True),
        StructField("sessionId", LongType(), True),
        StructField("page", StringType(), True),
        StructField("auth", StringType(), True),
        StructField("method", StringType(), True),
        StructField("status", IntegerType(), True),
        StructField("level", StringType(), True),
        StructField("itemInSession", LongType(), True),
        StructField("city", StringType(), True),
        StructField("zip", StringType(), True),
        StructField("state", StringType(), True),
        StructField("userAgent", StringType(), True),
        StructField("lon", DoubleType(), True),
        StructField("lat", DoubleType(), True),
        StructField("userId", LongType(), True),
        StructField("lastName", StringType(), True),
        StructField("firstName", StringType(), True),
        StructField("gender", StringType(), True),
        StructField("registration", LongType(), True),
        StructField("artist", StringType(), True),
        StructField("song", StringType(), True),
        StructField("duration", DoubleType(), True),
    ]
)

listen_events_schema = StructType(
    [
        StructField("artist", StringType(), True),
        StructField("song", StringType(), True),
        StructField("duration", DoubleType(), True),
        StructField("ts", LongType(), True),
        StructField("sessionId", LongType(), True),
        StructField("auth", StringType(), True),
        StructField("level", StringType(), True),
        StructField("itemInSession", LongType(), True),
        StructField("city", StringType(), True),
        StructField("zip", StringType(), True),
        StructField("state", StringType(), True),
        StructField("userAgent", StringType(), True),
        StructField("lon", DoubleType(), True),
        StructField("lat", DoubleType(), True),
        StructField("userId", LongType(), True),
        StructField("lastName", StringType(), True),
        StructField("firstName", StringType(), True),
        StructField("gender", StringType(), True),
        StructField("registration", LongType(), True),
    ]
)

status_change_events_schema = StructType(
    [
        StructField("ts", LongType(), True),
        StructField("sessionId", LongType(), True),
        StructField("auth", StringType(), True),
        StructField("level", StringType(), True),
        StructField("itemInSession", LongType(), True),
        StructField("city", StringType(), True),
        StructField("zip", StringType(), True),
        StructField("state", StringType(), True),
        StructField("userAgent", StringType(), True),
        StructField("lon", DoubleType(), True),
        StructField("lat", DoubleType(), True),
        StructField("userId", LongType(), True),
        StructField("lastName", StringType(), True),
        StructField("firstName", StringType(), True),
        StructField("gender", StringType(), True),
        StructField("registration", LongType(), True),
    ]
)

# DWH MODEL SCHEMAS

date_dim_schema = StructType(
    [
        StructField("DateSK", LongType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("timestamp_unix", LongType(), True),
        StructField("year", IntegerType(), True),
        StructField("month", IntegerType(), True),
        StructField("day", IntegerType(), True),
    ]
)

date_time_dim_schema = StructType(
    [
        StructField("DateTimeSK", LongType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("timestamp_unix", LongType(), True),
        StructField("year", IntegerType(), True),
        StructField("month", IntegerType(), True),
        StructField("day", IntegerType(), True),
        StructField("hour", IntegerType(), True),
        StructField("minute", IntegerType(), True),
        StructField("second", IntegerType(), True),
    ]
)

location_dim_schema = StructType(
    [
        StructField("LocationSK", LongType(), True),
        StructField("city", StringType(), True),
        StructField("zip", StringType(), True),
        StructField("state", StringType(), True),
        StructField("lon", DoubleType(), True),
        StructField("lat", DoubleType(), True),
    ]
)

user_dim_schema = StructType(
    [
        StructField("userId", LongType(), True),
        StructField("firstName", StringType(), True),
        StructField("lastName", StringType(), True),
        StructField("gender", StringType(), True),
        StructField("registration_ts", LongType(), True),
        StructField("registration_city", StringType(), True),
        StructField("registration_zip", StringType(), True),
        StructField("registration_state", StringType(), True),
        StructField("registration_lon", DoubleType(), True),
        StructField("registration_lat", DoubleType(), True),
    ]
)

event_fact_schema = StructType(
    [
        StructField("userId", LongType(), True),
        StructField("EventSK", LongType(), True),
        StructField("DateTimeSK", LongType(), True),
        StructField("DateSK", LongType(), True),
        StructField("LocationSK", LongType(), True),
        StructField("SongSK", LongType(), True),
        StructField("timestamp", LongType(), True),
        StructField("level", StringType(), True),
        StructField("duration", DoubleType(), True),
        StructField("is_moving", IntegerType(), True),
        StructField("consecutive_no_song", IntegerType(), True),
        StructField("is_first_listen_event", IntegerType(), True),
        StructField("is_last_listen_event", IntegerType(), True),
        StructField("is_song_skipped", IntegerType(), True),
        StructField("next_listen_event_time_gap", IntegerType(), True),
        StructField("record_valid_from", LongType(), True),
        StructField("record_valid_to", LongType(), True),
        StructField("is_record_valid", IntegerType(), True),
    ]
)

event_dim_schema = StructType(
    [
        StructField("EventSK", LongType(), True),
        StructField("userId", LongType(), True),
        StructField("itemInSession", LongType(), True),
        StructField("sessionId", LongType(), True),
        StructField("userAgent", StringType(), True),
        StructField("page", StringType(), True),
        StructField("auth", StringType(), True),
        StructField("method", StringType(), True),
        StructField("status", IntegerType(), True),
        StructField("level", StringType(), True),
        StructField("is_listen_event", IntegerType(), True),
    ]
)

session_dim_schema = StructType(
    [
        StructField("SessionSK", LongType(), True),
        StructField("sessionId", LongType(), True),
        StructField("userId", LongType(), True),
    ]
)

event_session_bridge_schema = StructType(
    [
        StructField("SessionSK", LongType(), True),
        StructField("EventSK", LongType(), True),
    ]
)

session_fact_schema = StructType(
    [
        StructField("userId", LongType(), True),
        StructField("DateSK", LongType(), True),
        StructField("DateTimeSK", LongType(), True),
        StructField("session_start_ts", LongType(), True),
        StructField("session_end_ts", LongType(), True),
        StructField("level", StringType(), True),
        StructField("session_duration", DoubleType(), True),
        StructField("primary_s_location", LongType(), True),
        StructField("SessionSK", LongType(), True),
        StructField("record_valid_from", LongType(), True),
        StructField("record_valid_to", LongType(), True),
        StructField("is_record_valid", IntegerType(), True),
    ]
)

song_dim_schema = StructType(
    [
        StructField("SongSK", LongType(), True),
        StructField("artist", StringType(), True),
        StructField("song", StringType(), True),
    ]
)
