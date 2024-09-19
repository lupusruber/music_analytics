import os


# Spark Jars
os.environ["PYSPARK_SUBMIT_ARGS"] = (
    "--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.0,"
    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,"
    "org.postgresql:postgresql:42.5.0 pyspark-shell"
)

# Spark Settings
SPARK_MASTER_URL = "local[*]"  # later "spark://localhost:7077"
APP_NAME = "KafkaStreaming"

# Kafka Topics
LIST_OF_TOPICS = [
    "auth_events",
    "listen_events",
    "page_view_events",
    "status_change_events",
]
AUTH_EVENTS_TOPIC = LIST_OF_TOPICS[0]
LISTEN_EVENTS_TOPIC = LIST_OF_TOPICS[1]
PAGE_VIEW_EVENTS_TOPIC = LIST_OF_TOPICS[2]
STATUS_CHANGE_EVENTS_TOPIC = LIST_OF_TOPICS[3]
TOPICS_STRING = ",".join(LIST_OF_TOPICS)

# Kafka Connection
KAFKA_BROKER_URL = "localhost"
KAFKA_BROKER_PORT = "9094"
BOOTSTRAP_SERVERS = f"{KAFKA_BROKER_URL}:{KAFKA_BROKER_PORT}"

# DWH Connection
DB_URL = "localhost"
DB_PORT = "5432"
DB_NAME = "dwh"
DB_ENGINE = "jdbc"
DB_TYPE = "postgresql"
DB_URL = f"{DB_ENGINE}:{DB_TYPE}://{DB_URL}:{DB_PORT}/{DB_NAME}"

# DWH Credentials
DB_USER = "root"
DB_PASSWORD = "root"
DB_PROPERTIES = {
    "user": DB_USER,
    "password": DB_PASSWORD,
    "driver": "org.postgresql.Driver",
}

# DWH Tables
DB_TABLE_SONG_DIM = "SongDim"
DB_TABLE_USER_DIM = "UserDim"
DB_TABLE_DATE_DIM = "DateDim"
DB_TABLE_EVENT_DIM = "EventDim"
DB_TABLE_SESSION_DIM = "SessionDim"
DB_TABLE_LOCATION_DIM = "LocationDim"
DB_TABLE_DATE_TIME_DIM = "DateTimeDim"

DB_TABLE_EVENT_FACT = "EventFact"
DB_TABLE_SESSION_FACT = "SessionFact"

DB_TABLE_EVENT_SESSION_BRIDGE = "EventSessionBridge"
