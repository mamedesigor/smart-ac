#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from datetime import datetime
import time
import json
import config

buffer = config.buffer

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(config.MQTT_TOPICS)

def on_message(client, userdata, msg):
    timestamp = datetime.now().replace(microsecond=0)
    json_string = json.loads(msg.payload.decode("utf-8"))
    json_string.update({"timestamp": str(timestamp)})
    buffer.get(msg.topic).append(json_string)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
client.loop_forever()
