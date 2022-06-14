#!/usr/bin/env python3

MQTT_TOPICS = []

buffer = {}

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
            elif word == "BMP280_TOPIC":
                BMP280_TOPIC = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((BMP280_TOPIC, 0))
                buffer.update({BMP280_TOPIC: []})
            elif word == "HTU21D_TOPIC":
                HTU21D_TOPIC = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((HTU21D_TOPIC, 0))
                buffer.update({HTU21D_TOPIC: []})
            elif word == "CCS811_TOPIC":
                CCS811_TOPIC = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((CCS811_TOPIC, 0))
                buffer.update({CCS811_TOPIC: []})
            elif word == "SDS011_TOPIC":
                SDS011_TOPIC = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((SDS011_TOPIC, 0))
                buffer.update({SDS011_TOPIC: []})
            elif word == "BH1750_TOPIC":
                BH1750_TOPIC = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((BH1750_TOPIC, 0))
                buffer.update({BH1750_TOPIC: []})
            elif word == "MICS6814_TOPIC":
                MICS6814_TOPIC = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((MICS6814_TOPIC, 0))
                buffer.update({MICS6814_TOPIC: []})
            elif word == "SCT013_1_TOPIC":
                SCT013_1_TOPIC = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((SCT013_1_TOPIC, 0))
                buffer.update({SCT013_1_TOPIC: []})
            elif word == "SCT013_2_TOPIC":
                SCT013_2_TOPIC = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((SCT013_2_TOPIC, 0))
                buffer.update({SCT013_2_TOPIC: []})
            elif word == "REEDSWITCH_TOPIC":
                REEDSWITCH_TOPIC = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((REEDSWITCH_TOPIC, 0))
                buffer.update({REEDSWITCH_TOPIC: []})
            elif word == "PIR_TOPIC":
                PIR_TOPIC = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((PIR_TOPIC, 0))
                buffer.update({PIR_TOPIC: []})
            elif word == "IR_TOPIC":
                IR_TOPIC = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((IR_TOPIC, 0))
                buffer.update({IR_TOPIC: []})
