from quixstreams import Application
import json
import pandas as pd


list_of_topics = [
    "auth_events",
    "listen_events",
    "page_view_events",
    "status_change_events",
]

app = Application(
    broker_address="localhost:9094",
    loglevel="DEBUG",
    consumer_group="music_events_processor",
    auto_offset_reset="earliest",
)

data_dict = {k: [] for k in list_of_topics}

with app.get_consumer() as consumer:

    while len(data_dict["page_view_events"]) != 128378:
        consumer.subscribe(topics=list_of_topics)
        msg = consumer.poll()
        topic = msg.topic()
        data_dict[topic].append(json.loads(msg.value().decode("utf-8")))

        if not msg:
            continue

for topic, data in data_dict.items():
    df = pd.DataFrame(data)
    df.to_csv(f"data/{topic}.csv", index=False)
