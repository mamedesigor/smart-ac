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
            elif word == "SCT013_TOPIC":
                SCT013_TOPIC = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((SCT013_TOPIC, 0))
                buffer.update({SCT013_TOPIC: []})
            elif word == "MC38_1_TOPIC":
                MC38_1_TOPIC = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((MC38_1_TOPIC, 0))
                buffer.update({MC38_1_TOPIC: []})
            elif word == "MC38_2_TOPIC":
                MC38_2_TOPIC = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((MC38_2_TOPIC, 0))
                buffer.update({MC38_2_TOPIC: []})
            elif word == "HCSR501_1_TOPIC":
                HCSR501_1_TOPIC = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((HCSR501_1_TOPIC, 0))
                buffer.update({HCSR501_1_TOPIC: []})
            elif word == "HCSR501_2_TOPIC":
                HCSR501_2_TOPIC = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((HCSR501_2_TOPIC, 0))
                buffer.update({HCSR501_2_TOPIC: []})
            elif word == "INSTRUCTIONS_TOPIC":
                INSTRUCTIONS_TOPIC = splitted_line[i+1].replace('"', '')
                MQTT_TOPICS.append((INSTRUCTIONS_TOPIC, 0))
                buffer.update({INSTRUCTIONS_TOPIC: []})
            elif word == "ESP_CONTROLLER_1_TOPIC":
                ESP_CONTROLLER_1_TOPIC = splitted_line[i+1].replace('"', '')
            elif word == "ESP_CONTROLLER_2_TOPIC":
                ESP_CONTROLLER_2_TOPIC = splitted_line[i+1].replace('"', '')
            elif word == "ESP_CONTROLLER_3_TOPIC":
                ESP_CONTROLLER_3_TOPIC = splitted_line[i+1].replace('"', '')
            elif word == "RPI_TOPIC":
                RPI_TOPIC = splitted_line[i+1].replace('"', '')
            elif word == "IRRAW_TOPIC":
                IRRAW_TOPIC = splitted_line[i+1].replace('"', '')
            elif word == "IRRAW_CODE":
                IRRAW_CODE = splitted_line[i+1].replace('"', '')
