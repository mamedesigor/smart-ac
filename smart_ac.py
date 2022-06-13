#!/usr/bin/env python3

import paho.mqtt.client as mqtt

MQTT_TOPICS = []

with open("config.h", "r") as config:
    for line in config:
        splitted_line = line.split();
        for i, word in enumerate(splitted_line):
            if word == "SSID":
                SSID = splitted_line[i+1].replace('"', '')
            elif word == "PASSWORD":
                PASSWORD = splitted_line[i+1].replace('"', '')
            elif word == "MQTT_BROKER":
                MQTT_BROKER = splitted_line[i+1].replace('"', '')
            elif word == "MQTT_PORT":
                MQTT_PORT = int(splitted_line[i+1].replace('"', ''))
            elif word == "BMP280":
                BMP280 = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((BMP280, 0))
            elif word == "HTU21D":
                HTU21D = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((HTU21D, 0))
            elif word == "CCS811":
                CCS811 = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((CCS811, 0))
            elif word == "SDS011":
                SDS011 = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((SDS011, 0))
            elif word == "BH1750":
                BH1750 = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((BH1750, 0))
            elif word == "MICS6814":
                MICS6814 = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((MICS6814, 0))
            elif word == "SCT013_1":
                SCT013_1 = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((SCT013_1, 0))
            elif word == "SCT013_2":
                SCT013_2 = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((SCT013_2, 0))
            elif word == "REEDSWITCH":
                REEDSWITCH = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((REEDSWITCH, 0))
            elif word == "PIR":
                PIR = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((PIR, 0))
            elif word == "IR":
                IR = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((IR, 0))

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPICS)

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
