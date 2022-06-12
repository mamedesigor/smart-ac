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
            elif word == "TEMP1_TPC":
                TEMP1_TPC = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((TEMP1_TPC, 0))
            elif word == "TEMP2_TPC":
                TEMP2_TPC = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((TEMP2_TPC, 0))
            elif word == "CCS811":
                CCS811 = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((CCS811, 0))

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
