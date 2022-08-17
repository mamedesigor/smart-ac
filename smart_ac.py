#!/usr/bin/env python3

from gpiozero import MotionSensor
from threading import Thread
import paho.mqtt.client as mqtt
from datetime import datetime
import time
import json
import config
import sqlite3
import requests
import board
import serial
import adafruit_bh1750
import shutil
from os.path import exists


buffer = config.buffer

last_measurements = {}

last_backup = datetime.now()

loop_time = 3

controller_data = {}

def log(msg):
    print("["+ str(datetime.now().replace(microsecond=0)) + "] " + msg)

def deserialize_datetime(dt):
    line = dt.split()
    date = line[0].split('-')
    time = line[1].split(':')

    year = int(date[0])
    month = int(date[1])
    day = int(date[2])
    hour = int(time[0])
    minute = int(time[1])
    second = int(time[2])
    return datetime(year, month, day, hour, minute, second)

def controller_update():
    instructions_delay = 3600
    poweroff_maybe = False
    poweroff = False
    now = datetime.now()

    # verify if last instruction was more than 1h ago
    if "instructions_poweroff_timestamp" in controller_data:
        instructions_poweroff_timestamp = deserialize_datetime(controller_data.get("instructions_poweroff_timestamp"))
        instructions_timer = (now - instructions_poweroff_timestamp).total_seconds()
        if instructions_timer > instructions_delay:
            poweroff_maybe = True
    else:
        poweroff_maybe = True

    if(poweroff_maybe):
        # door1 open more than 3 minutes
        if "door1_closed_timestamp" in controller_data:
            door1_closed_timestamp = deserialize_datetime(controller_data.get("door1_closed_timestamp"))
            door1_closed_timer = (now - door1_closed_timestamp).total_seconds()
            if door1_closed_timer > 180:
                poweroff_ac("door1 open " + str(door1_closed_timer))
                poweroff = True

        # door2 open more than 3 minutes
        if "door2_closed_timestamp" in controller_data and not poweroff:
            door2_closed_timestamp = deserialize_datetime(controller_data.get("door2_closed_timestamp"))
            door2_closed_timer = (now - door2_closed_timestamp).total_seconds()
            if door2_closed_timer > 180:
                poweroff_ac("door2 open " + str(door2_closed_timer))
                poweroff = True

        # no motion detected in 1 hour
        if "motion2_timestamp" in controller_data and not poweroff:
            motion2_timestamp = deserialize_datetime(controller_data.get("motion2_timestamp"))
            motion2_timer = (now - motion2_timestamp).total_seconds()
            if motion2_timer > 3600:
                poweroff_ac("motion2")
                poweroff = True

        # ac on between 11:30 and 12:30
        if not poweroff:
            time1130 = datetime(now.year, now.month, now.day, 11, 30)
            time1230 = datetime(now.year, now.month, now.day, 12, 30)
            if now > time1130 and now < time1230:
                poweroff_ac(">1130 <1230")
                poweroff = True

        # ac on past 17:30
        if not poweroff:
            time1730 = datetime(now.year, now.month, now.day, 17, 30)
            if now > time1730:
                poweroff_ac(">1730")

def poweroff_ac(msg):
    client.publish(config.IRRAW_TOPIC, config.IRRAW_CODE)
    client.publish(config.INSTRUCTIONS_TOPIC, '{"instructions": "POWEROFF"}')
    log("poweroff ac " + str(msg))

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

def start_sds011():
    while True:
        data = []
        for index in range(0,10):
            datum = sds011.read()
            data.append(datum)

        pmtwofive = int.from_bytes(b''.join(data[2:4]), byteorder='little') / 10
        pmten = int.from_bytes(b''.join(data[4:6]), byteorder='little') / 10
        reading = '{"pm10": "' + str(pmten) + '", "pm25": "' + str(pmtwofive) + '"}'
        client.publish(config.SDS011_TOPIC, reading)
        time.sleep(10)

def start_hcsr501_2():
    while True:
        hcsr501_2.wait_for_motion()
        reading = '{"motion2": "detected"}'
        client.publish(config.HCSR501_2_TOPIC, reading)
        hcsr501_2.wait_for_no_motion()

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
                    if door1 == "closed":
                        controller_data.update({"door1_closed_timestamp": timestamp})

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
                    if door2 == "closed":
                        controller_data.update({"door2_closed_timestamp": timestamp})

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
                    controller_data.update({"motion2_timestamp": timestamp})

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

            ### INSTRUCTIONS ###
            if mqtt_topic == config.INSTRUCTIONS_TOPIC:
                list = buffer[mqtt_topic]
                for item in list:
                    timestamp = item.get("timestamp")
                    instructions = item.get("instructions")
                    last_measurements.update({"instructions": "instructions=" + instructions + "<br>" + timestamp})
                    cursor.execute("CREATE TABLE IF NOT EXISTS " + config.INSTRUCTIONS_TOPIC + " (instructions text, timestamp text)")
                    cursor.execute("INSERT INTO " + config.INSTRUCTIONS_TOPIC + " VALUES(?,?)",(instructions, timestamp))
                    log(mqtt_topic + " added to db instructions: POWEROFF")
                    controller_data.update({"instructions_poweroff_timestamp": timestamp})

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

sds011 = serial.Serial('/dev/ttyUSB0')
sds011_thread = Thread(target=start_sds011)
sds011_thread.start()

hcsr501_2 = MotionSensor(4)
hcsr501_2_thread = Thread(target=start_hcsr501_2)
hcsr501_2_thread.start()

while True:
    add_to_db()
    controller_update()
    send_post_request()
    time.sleep(loop_time)

    #perform backup hourly
    now = datetime.now()
    backup_timer = (now - last_backup).total_seconds()
    if backup_timer > 3600 and not exists("sqlite3bkp.db"):
        shutil.copyfile("sqlite3.db", "sqlite3bkp.db")
        log("[BACKUP] " + str(backup_timer))
        last_backup = now
