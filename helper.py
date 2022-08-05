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
    timestamp = datetime.now().replace(microsecond=0)
    temp1_js = "temp1=55°C<br>" + str(timestamp)
    amps_js = "amps=12A<br>" + str(timestamp)
    temp2_js = "temp2=69°C<br>" + str(timestamp)
    pressure_js = "pressure=900hPa<br>" + str(timestamp)
    humidity_js = "humidity=59%<br>" + str(timestamp)
    eco2_js = "eco2=555ppm<br>" + str(timestamp)
    tvoc_js = "tvoc=22pbm<br>" + str(timestamp)
    motion1_js = "motion1=True<br>" + str(timestamp)
    motion2_js = "motion2=True<br>" + str(timestamp)
    pm25_js = "pm25=True<br>" + str(timestamp)
    pm10_js = "pm10=True<br>" + str(timestamp)
    door1_js = "door1=False<br>" + str(timestamp)
    door2_js = "door2=False<br>" + str(timestamp)
    luxes_js = "luxes=566lx<br>" + str(timestamp)
    instructions_js = "instructions=ON<br>" + str(timestamp)
    data = {
            "temp1": temp1_js,
            "amps": amps_js,
            "temp2": temp2_js,
            "pressure": pressure_js,
            "humidity": humidity_js,
            "eco2": eco2_js,
            "tvoc": tvoc_js,
            "motion1": motion1_js,
            "motion2": motion2_js,
            "pm25": pm25_js,
            "pm10": pm10_js,
            "door1": door1_js,
            "door2": door2_js,
            "luxes": luxes_js,
            "instructions": instructions_js
            }
    requests.post(url, json = data)

def read_db():
    db = sqlite3.connect("sqlite3.db")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM bmp280")
    print(cursor.fetchall())
    db.close()

def timed_function(function):
    start_time = time.time()
    function()
    print("--- %s seconds ---" % (time.time() - start_time))

timed_function(send_request)
