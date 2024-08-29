from quixstreams import Application
from pprint import pprint
import json
import  pandas as pd

app = Application(
        broker_address="localhost:9092",
        loglevel="DEBUG",
        consumer_group="music_events_processor",
        auto_offset_reset="earliest",
    )

with app.get_consumer() as consumer:
    msgs = []
    while len(msgs) < 100000:

        consumer.subscribe(topics=["listen_events"])
        msg = consumer.poll(1)
        #breakpoint()
        if msg == None:
            break
        msgs.append(json.loads(msg.value().decode('utf-8')))
        
df = pd.DataFrame(msgs)
df.to_csv('events.csv')
