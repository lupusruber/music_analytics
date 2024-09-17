import os


os.environ["PYSPARK_SUBMIT_ARGS"] = (
    "--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.0,"
    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,"
    "org.postgresql:postgresql:42.5.0 pyspark-shell"
)


LIST_OF_TOPICS = [
    "auth_events",
    "listen_events",
    "page_view_events",
    "status_change_events",
]
LISTEN_EVENTS_TOPIC = LIST_OF_TOPICS[1]


BOOTSTRAP_SERVERS = "localhost:9094"
TOPICS_STRING = ",".join(LIST_OF_TOPICS)
SPARK_MASTER_URL = "local[*]"  # "spark://localhost:7077"

APP_NAME = "KafkaStreaming"

DB_NAME = "dwh"
DB_URL = f"jdbc:postgresql://localhost:5432/{DB_NAME}"
DB_TABLE_SONG_DIM = "SongDim"
DB_PROPERTIES = {"user": "root", "password": "root", "driver": "org.postgresql.Driver"}
