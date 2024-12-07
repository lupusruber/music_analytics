from quixstreams import Application
import json
import pandas as pd


list_of_topics = [
    "listen_events_2",
]

app = Application(
    broker_address="localhost:9094",
    loglevel="DEBUG",
    auto_offset_reset="earliest",
)


with app.get_producer() as producer:

    # producer.produce(topic='listen_events')

    df = pd.read_csv("/home/lupusruber/music_analytics/data/listen_events.csv")
    columns = df.columns.tolist()

    for item in df.itertuples(index=False, name=None):
        data_dict = {k: v for (k, v) in zip(columns, item)}
        producer.produce(topic=list_of_topics[0], value=json.dumps(data_dict))
