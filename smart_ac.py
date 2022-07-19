#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from datetime import datetime
import time
import json
import config
import sqlite3

buffer = config.buffer

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(config.MQTT_TOPICS)

def on_message(client, userdata, msg):
    timestamp = datetime.now().replace(microsecond=0)
    json_string = json.loads(msg.payload.decode("utf-8"))
    json_string.update({"timestamp": str(timestamp)})
    buffer.get(msg.topic).append(json_string)

def add_to_db():
    db = sqlite3.connect("sqlite3.db")
    cursor = db.cursor()
    for mqtt_topic in buffer:
        if buffer[mqtt_topic]:

            ### CCS811 ###
            if mqtt_topic == config.CCS811_TOPIC:
                list = buffer[mqtt_topic]
                for item in list:
                    eco2 = item.get("eco2")
                    etvoc = item.get("etvoc")
                    timestamp = item.get("timestamp")
                    print(eco2 + " " + etvoc + " " + timestamp)
                    cursor.execute("CREATE TABLE IF NOT EXISTS " + config.CCS811_TOPIC + " (eco2 real, etvoc real, timestamp text)")
                    cursor.execute("INSERT INTO " + config.CCS811_TOPIC + " VALUES(?,?,?)",(eco2, etvoc, timestamp))

            ### BMP280 ###
            if mqtt_topic == config.BMP280_TOPIC:
                list = buffer[mqtt_topic]
                for item in list:
                    temp1 = item.get("temp1")
                    pressure = item.get("pressure")
                    timestamp = item.get("timestamp")
                    print(temp1 + " " + pressure + " " + timestamp)
                    cursor.execute("CREATE TABLE IF NOT EXISTS " + config.BMP280_TOPIC + " (temp1 real, pressure real, timestamp text)")
                    cursor.execute("INSERT INTO " + config.BMP280_TOPIC + " VALUES(?,?,?)",(temp1, pressure, timestamp))

            ### SCT013 ###
            if mqtt_topic == config.SCT013_TOPIC:
                list = buffer[mqtt_topic]
                for item in list:
                    amps = item.get("amps")
                    timestamp = item.get("timestamp")
                    print(amps + " " + timestamp)
                    cursor.execute("CREATE TABLE IF NOT EXISTS " + config.SCT013_TOPIC + " (amps real, timestamp text)")
                    cursor.execute("INSERT INTO " + config.SCT013_TOPIC + " VALUES(?,?)",(amps, timestamp))

            buffer[mqtt_topic] = []
    db.commit();
    db.close();

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
client.loop_start()

while True:
    add_to_db()
    time.sleep(1)
