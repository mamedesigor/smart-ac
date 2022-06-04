#!/usr/bin/env python3
MQQT_TOPICS = []
with open("config.h", "r") as config:
    for line in config:
        splitted_line = line.split();
        for i, word in enumerate(splitted_line):
            if word == "SSID":
                SSID = splitted_line[i+1].replace('"', '')
            elif word == "PASSWORD":
                PASSWORD = splitted_line[i+1].replace('"', '')
            elif word == "MQQT_BROKER":
                MQQT_BROKER = splitted_line[i+1].replace('"', '')
            elif word == "MQQT_PORT":
                MQQT_PORT = splitted_line[i+1].replace('"', '')
            elif word == "TEMP1_TPC":
                TEMP1_TPC = splitted_line[i+1].replace('"', '')
                MQQT_TOPICS.append(TEMP1_TPC)
            elif word == "TEMP2_TPC":
                TEMP2_TPC = splitted_line[i+1].replace('"', '')
                MQQT_TOPICS.append(TEMP2_TPC)
