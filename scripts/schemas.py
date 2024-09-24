from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType,
    LongType,
    TimestampType,
)

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


date_dim_schema = StructType(
    [
        StructField("DateSK", StringType(), False),
        StructField("timestamp", TimestampType(), True),
        StructField("timestamp_unix", LongType(), True),
        StructField("year", IntegerType(), True),
        StructField("month", IntegerType(), True),
        StructField("day", IntegerType(), True),
    ]
)

date_time_dim_schema = StructType(
    [
        StructField("DateTimeSK", StringType(), False),
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
        StructField("LocationSK", StringType(), True),
        StructField("city", StringType(), True),
        StructField("zip", StringType(), True),
        StructField("state", StringType(), True),
        StructField("lon", DoubleType(), True),
        StructField("lat", DoubleType(), True),
    ]
)

user_dim_schema = StructType(
    [
        StructField("userId", LongType(), False),
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

# TO DO
event_fact_schema = StructType(
    [
        StructField("userId", LongType(), False),
        StructField("EventSK", StringType(), False),
        StructField("DateTimeSK", StringType(), False),
        StructField("DateSK", StringType(), False),
        StructField("LocationSK", StringType(), False),
        StructField("SongSK", StringType(), True),
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
        StructField("EventSK", StringType(), False),
        StructField("userId", LongType(), False),
        StructField("itemInSession", LongType(), False),
        StructField("sessionId", StringType(), False),
        StructField("userAgent", StringType(), True),
        StructField("page", StringType(), True),
        StructField("auth", StringType(), True),
        StructField("method", StringType(), True),
        StructField("status", StringType(), True),
        StructField("level", StringType(), True),
        StructField("is_listen_event", IntegerType(), True),
    ]
)

session_dim_schema = StructType(
    [
        StructField("SessionSK", StringType(), False),
        StructField("sessionId", LongType(), False),
        StructField("userId", LongType(), False),
    ]
)

event_session_bridge_schema = StructType(
    [
        StructField("SessionSK", StringType(), False),
        StructField("EventSK", StringType(), False),
    ]
)

session_fact_schema = StructType(
    [
        StructField("userId", LongType(), False),
        StructField("DateSK", StringType(), False),
        StructField("DateTimeSK", StringType(), False),
        StructField("session_start_ts", LongType(), False),
        StructField("session_end_ts", LongType(), True),
        StructField("level", StringType(), True),
        StructField("session_duration", DoubleType(), True),
        StructField("primary_s_location", StringType(), True),
        StructField("SessionSK", StringType(), False),
        StructField("record_valid_from", LongType(), True),
        StructField("record_valid_to", LongType(), True),
        StructField("is_record_valid", IntegerType(), True),
    ]
)
