from pyspark.sql.session import SparkSession

from configs import (
    SPARK_MASTER_URL,
    APP_NAME,
    PAGE_VIEW_EVENTS_TOPIC,
    LISTEN_EVENTS_TOPIC,
)

from song_dim import song_dim_stream
from location_dim import location_dim_stream
from date_and_date_time_dim import date_and_date_time_stream
from user_dim import user_dim_stream
from event_dim import event_dim_stream
from event_fact import event_fact_stream
from session_dim_and_bridge import session_dim_bridge_stream
from session_fact import session_fact_stream
from schemas import page_view_events_schema, listen_events_schema
from util_functions import create_stream


def main() -> None:

    spark = (
        SparkSession.builder.appName(APP_NAME).master(SPARK_MASTER_URL).getOrCreate()
    )

    page_view_events = create_stream(
        spark=spark, topic=PAGE_VIEW_EVENTS_TOPIC, schema=page_view_events_schema
    )

    listen_events = create_stream(
        spark=spark, topic=LISTEN_EVENTS_TOPIC, schema=listen_events_schema
    )

    song_dim = song_dim_stream(spark, listen_events)
    location_dim = location_dim_stream(spark, page_view_events)
    date_and_date_time_dim = date_and_date_time_stream(spark, page_view_events)
    user_dim = user_dim_stream(spark, listen_events)
    event_dim = event_dim_stream(spark, page_view_events)
    session_dim_bridge = session_dim_bridge_stream(spark, page_view_events)
    event_fact = event_fact_stream(spark, listen_events)
    session_fact = session_fact_stream(spark, listen_events)

    song_dim.awaitTermination()
    location_dim.awaitTermination()
    date_and_date_time_dim.awaitTermination()
    user_dim.awaitTermination()
    event_dim.awaitTermination()
    session_dim_bridge.awaitTermination()
    event_fact.awaitTermination()
    session_fact.awaitTermination()


if __name__ == "__main__":
    main()
