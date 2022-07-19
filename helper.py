#!/usr/bin/env python

import sys
import requests
import sqlite3
import time
import json
from datetime import datetime
import paho.mqtt.client as mqtt
import config

buffer = config.buffer

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(config.MQTT_TOPICS)

def on_message(client, userdata, msg):
    print(str(msg.payload.decode("utf-8")));

def mqtt_listener():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
    client.loop_forever()

def send_request():
    url = 'https://www.arcondicionado.cf/request'
    url2 = 'http://127.0.0.1:3031/request'
    timestamp = datetime.now().replace(microsecond=0)
    temp1_js = "temp1=39°C<br>" + str(timestamp)
    amps1_js = "amps1=12A<br>" + str(timestamp)
    temp2_js = "temp2=34°C<br>" + str(timestamp)
    amps2_js = "amps2=66A<br>" + str(timestamp)
    pressure_js = "pressure=900hPa<br>" + str(timestamp)
    humidity_js = "humidity=59%<br>" + str(timestamp)
    eco2_js = "eco2=555ppm<br>" + str(timestamp)
    tvoc_js = "tvoc=22pbm<br>" + str(timestamp)
    co_js = "co=10ppm<br>" + str(timestamp)
    no2_js = "no2=11ppm<br>" + str(timestamp)
    nh3_js = "nh3=15ppm<br>" + str(timestamp)
    presence1_js = "presence1=True<br>" + str(timestamp)
    presence2_js = "presence2=True<br>" + str(timestamp)
    pm25_js = "pm25=True<br>" + str(timestamp)
    pm10_js = "pm10=True<br>" + str(timestamp)
    door_js = "door=False<br>" + str(timestamp)
    luxes_js = "luxes=566lx<br>" + str(timestamp)
    instructions_js = "instructions=ON<br>" + str(timestamp)
    data = {"temp1": temp1_js, "amps1": amps1_js, "temp2": temp2_js, "amps2": amps2_js,
            "pressure": pressure_js, "humidity": humidity_js, "eco2": eco2_js, "tvoc": tvoc_js,
            "co": co_js, "no2": no2_js, "nh3": nh3_js, "presence1": presence1_js,
            "presence2": presence2_js, "pm25": pm25_js, "pm10": pm10_js, "door": door_js,
            "luxes": luxes_js, "instructions": instructions_js}
    requests.post(url, json = data)

def read_db():
    db = sqlite3.connect("sqlite3.db")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM ccs811")
    print(cursor.fetchall())
    db.close()

def timed_function(function):
    start_time = time.time()
    function()
    print("--- %s seconds ---" % (time.time() - start_time))

timed_function(mqtt_listener)
