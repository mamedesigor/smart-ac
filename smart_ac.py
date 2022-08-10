#!/usr/bin/env python3

from threading import Thread
import paho.mqtt.client as mqtt
from datetime import datetime
import time
import json
import config
import sqlite3
import requests
import board
import adafruit_bh1750


buffer = config.buffer

last_measurements = {}

def log(msg):
    print("["+ str(datetime.now().replace(microsecond=0)) + "] " + msg)

def on_connect(client, userdata, flags, rc):
    log("Connected with result code " + str(rc))
    client.subscribe(config.MQTT_TOPICS)

def on_message(client, userdata, msg):
    timestamp = datetime.now().replace(microsecond=0)
    json_string = json.loads(msg.payload.decode("utf-8"))
    json_string.update({"timestamp": str(timestamp)})
    buffer.get(msg.topic).append(json_string)

def start_bh1750():
    while True:
        time.sleep(5)
        reading = '{"luxes": "' + str("%.2f"%bh1750.lux) + '"}'
        client.publish(config.BH1750_TOPIC, reading)

def send_post_request():
    url = 'https://www.arcondicionado.cf/request'
    if len(last_measurements) > 0:
        try:
            requests.post(url, json = last_measurements, timeout = 5)
            log("---------------- post request sent ----------------")
            log(str(last_measurements))
        except:
            log("An exception occurred when sending post request")
        last_measurements.clear()

def add_to_db():
    db = sqlite3.connect("sqlite3.db")
    cursor = db.cursor()
    for mqtt_topic in buffer:
        if buffer[mqtt_topic]:

            ### CCS811 ###
            if mqtt_topic == config.CCS811_TOPIC:
                list = buffer[mqtt_topic]
                for item in list:
                    timestamp = item.get("timestamp")
                    eco2 = item.get("eco2")
                    last_measurements.update({"eco2": "eco2=" + eco2 + "ppm<br>" + timestamp})
                    tvoc = item.get("tvoc")
                    last_measurements.update({"tvoc": "tvoc=" + tvoc + "ppm<br>" + timestamp})
                    cursor.execute("CREATE TABLE IF NOT EXISTS " + config.CCS811_TOPIC + " (eco2 real, tvoc real, timestamp text)")
                    cursor.execute("INSERT INTO " + config.CCS811_TOPIC + " VALUES(?,?,?)",(eco2, tvoc, timestamp))
                    log(mqtt_topic + " added to db eco2: " + eco2 + " tvoc: " + tvoc)

            ### BMP280 ###
            if mqtt_topic == config.BMP280_TOPIC:
                list = buffer[mqtt_topic]
                for item in list:
                    timestamp = item.get("timestamp")
                    temp1 = item.get("temp1")
                    last_measurements.update({"temp1": "temp1=" + temp1 + "ºC<br>" + timestamp})
                    pressure = item.get("pressure")
                    last_measurements.update({"pressure": "pressure=" + pressure + "hPa<br>" + timestamp})
                    cursor.execute("CREATE TABLE IF NOT EXISTS " + config.BMP280_TOPIC + " (temp1 real, pressure real, timestamp text)")
                    cursor.execute("INSERT INTO " + config.BMP280_TOPIC + " VALUES(?,?,?)",(temp1, pressure, timestamp))
                    log(mqtt_topic + " added to db temp1: " + temp1 + " pressure: " + pressure)

            ### SCT013 ###
            if mqtt_topic == config.SCT013_TOPIC:
                list = buffer[mqtt_topic]
                for item in list:
                    timestamp = item.get("timestamp")
                    amps = item.get("amps")
                    last_measurements.update({"amps": "amps=" + amps + "A<br>" + timestamp})
                    cursor.execute("CREATE TABLE IF NOT EXISTS " + config.SCT013_TOPIC + " (amps real, timestamp text)")
                    cursor.execute("INSERT INTO " + config.SCT013_TOPIC + " VALUES(?,?)",(amps, timestamp))
                    log(mqtt_topic + " added to db amps: " + amps)

            ### HCSR501_1 ###
            if mqtt_topic == config.HCSR501_1_TOPIC:
                list = buffer[mqtt_topic]
                for item in list:
                    timestamp = item.get("timestamp")
                    motion1 = item.get("motion1")
                    last_measurements.update({"motion1": "motion1=" + motion1 + "<br>" + timestamp})
                    cursor.execute("CREATE TABLE IF NOT EXISTS " + config.HCSR501_1_TOPIC + " (motion1 text, timestamp text)")
                    cursor.execute("INSERT INTO " + config.HCSR501_1_TOPIC + " VALUES(?,?)",(motion1, timestamp))
                    log(mqtt_topic + " added to db motion1: " + motion1)

            ### MC38_1 ###
            if mqtt_topic == config.MC38_1_TOPIC:
                list = buffer[mqtt_topic]
                for item in list:
                    timestamp = item.get("timestamp")
                    door1 = item.get("door1")
                    last_measurements.update({"door1": "door1=" + door1 + "<br>" + timestamp})
                    cursor.execute("CREATE TABLE IF NOT EXISTS " + config.MC38_1_TOPIC + " (door1 text, timestamp text)")
                    cursor.execute("INSERT INTO " + config.MC38_1_TOPIC + " VALUES(?,?)",(door1, timestamp))
                    log(mqtt_topic + " added to db door1: " + door1)

            ### HTU21D ###
            if mqtt_topic == config.HTU21D_TOPIC:
                list = buffer[mqtt_topic]
                for item in list:
                    timestamp = item.get("timestamp")
                    temp2 = item.get("temp2")
                    last_measurements.update({"temp2": "temp2=" + temp2 + "ºC<br>" + timestamp})
                    humidity = item.get("humidity")
                    last_measurements.update({"humidity": "humidity=" + humidity + "%RH<br>" + timestamp})
                    cursor.execute("CREATE TABLE IF NOT EXISTS " + config.HTU21D_TOPIC + " (temp2 real, humidity real, timestamp text)")
                    cursor.execute("INSERT INTO " + config.HTU21D_TOPIC + " VALUES(?,?,?)",(temp2, humidity, timestamp))
                    log(mqtt_topic + " added to db temp2: " + temp2 + " humidity: " + humidity)

            ### MC38_2 ###
            if mqtt_topic == config.MC38_2_TOPIC:
                list = buffer[mqtt_topic]
                for item in list:
                    timestamp = item.get("timestamp")
                    door2 = item.get("door2")
                    last_measurements.update({"door2": "door2=" + door2 + "<br>" + timestamp})
                    cursor.execute("CREATE TABLE IF NOT EXISTS " + config.MC38_2_TOPIC + " (door2 text, timestamp text)")
                    cursor.execute("INSERT INTO " + config.MC38_2_TOPIC + " VALUES(?,?)",(door2, timestamp))
                    log(mqtt_topic + " added to db door2: " + door2)

            ### SDS011 ###
            if mqtt_topic == config.SDS011_TOPIC:
                list = buffer[mqtt_topic]
                for item in list:
                    timestamp = item.get("timestamp")
                    pm10 = item.get("pm10")
                    last_measurements.update({"pm10": "pm10=" + pm10 + "µg/m³<br>" + timestamp})
                    pm25 = item.get("pm25")
                    last_measurements.update({"pm25": "pm25=" + pm25 + "µg/m³<br>" + timestamp})
                    cursor.execute("CREATE TABLE IF NOT EXISTS " + config.SDS011_TOPIC + " (pm10 real, pm25 real, timestamp text)")
                    cursor.execute("INSERT INTO " + config.SDS011_TOPIC + " VALUES(?,?,?)",(pm10, pm25, timestamp))
                    log(mqtt_topic + " added to db pm10: " + pm10 + " pm25: " + pm25)

            ### HCSR501_2 ###
            if mqtt_topic == config.HCSR501_2_TOPIC:
                list = buffer[mqtt_topic]
                for item in list:
                    timestamp = item.get("timestamp")
                    motion2 = item.get("motion2")
                    last_measurements.update({"motion2": "motion2=" + motion2 + "<br>" + timestamp})
                    cursor.execute("CREATE TABLE IF NOT EXISTS " + config.HCSR501_2_TOPIC + " (motion2 text, timestamp text)")
                    cursor.execute("INSERT INTO " + config.HCSR501_2_TOPIC + " VALUES(?,?)",(motion2, timestamp))
                    log(mqtt_topic + " added to db motion2: " + motion2)

            ### BH1750 ###
            if mqtt_topic == config.BH1750_TOPIC:
                list = buffer[mqtt_topic]
                for item in list:
                    timestamp = item.get("timestamp")
                    luxes = item.get("luxes")
                    last_measurements.update({"luxes": "luxes=" + luxes + "lx<br>" + timestamp})
                    cursor.execute("CREATE TABLE IF NOT EXISTS " + config.BH1750_TOPIC + " (luxes real, timestamp text)")
                    cursor.execute("INSERT INTO " + config.BH1750_TOPIC + " VALUES(?,?)",(luxes, timestamp))
                    log(mqtt_topic + " added to db luxes: " + luxes)

            buffer[mqtt_topic].clear()
    db.commit();
    db.close();

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
client.loop_start()

i2c = board.I2C()
bh1750 = adafruit_bh1750.BH1750(i2c)

bh1750_thread = Thread(target=start_bh1750)
bh1750_thread.start()

while True:
    add_to_db()
    send_post_request()
    time.sleep(3)
