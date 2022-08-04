#include <PubSubClient.h>
#include <Wire.h>
#include <HTU2xD_SHT2x_Si70xx.h>
#include "WiFi.h"
#include "config.h"

int ledPin = 32;
bool ledOn = false;
long ledTimer = 0;

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
char msg[100];

int hcsr501Pin = 35;

int mc38Pin = 33;

HTU2xD_SHT2x_SI70xx htu21d(HTU2xD_SENSOR, HUMD_12BIT_TEMP_14BIT);
bool temperatureWasRead = false;
float temperatureValue, compensatedHumidityValue;

long sensorTimer = 0;
int sensorDelay = 5000;

void setup() {
	//set up led indicator
	pinMode(ledPin, OUTPUT);

	//wifi
	delay(2000);
	WiFi.begin(SSID, PASSWORD);
	while (WiFi.status() != WL_CONNECTED) delay(500);

	//set up mqtt
	mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
	while (!mqttClient.connected()) {
		if (mqttClient.connect(ESP_CONTROLLER_2_TOPIC)) {
			mqttClient.publish(ESP_CONTROLLER_2_TOPIC, "WiFi and MQTT are up!");
			delay(100);
		} else {
			delay(2000);
		}
	}

	//set up hcsr501
	pinMode(hcsr501Pin, INPUT);
	mqttClient.publish(ESP_CONTROLLER_2_TOPIC, "HCSR501 OK");

	//set up mc38
	pinMode(mc38Pin, INPUT);
	mqttClient.publish(ESP_CONTROLLER_2_TOPIC, "MC38 OK");

	//set up htu21d
	while (htu21d.begin() != true) {
		mqttClient.publish(ESP_CONTROLLER_2_TOPIC, "HTU21D not connected, fail or VDD < +2.25v");
		delay(5000);
	}
	mqttClient.publish(ESP_CONTROLLER_2_TOPIC, "HTU21D OK");
}

void loop() {
	if (WiFi.status() != WL_CONNECTED || !mqttClient.connected()) reconnect();

	mqttClient.loop();

	long now = millis();
	if (now - sensorTimer > sensorDelay - 500) {

		//read temperature
		if(!temperatureWasRead) {
			temperatureWasRead = true;
			temperatureValue = htu21d.readTemperature();

			if (temperatureValue == HTU2XD_SHT2X_SI70XX_ERROR) {
				mqttClient.publish(ESP_CONTROLLER_2_TOPIC, "[htu21d] error reading temperature");

				if (htu21d.voltageStatus() == false) {
					mqttClient.publish(ESP_CONTROLLER_2_TOPIC, "[htu21d] power FAIL, VDD < +2.25v");
				}

				htu21d.softReset();
				htu21d.setHeater(false);
				htu21d.setResolution(HUMD_12BIT_TEMP_14BIT);
			}
		}

		if (now - sensorTimer > sensorDelay) {

			//read humidity
			temperatureWasRead = false;
			if (temperatureValue != HTU2XD_SHT2X_SI70XX_ERROR) {
				compensatedHumidityValue = htu21d.getCompensatedHumidity(temperatureValue);

				if (compensatedHumidityValue == HTU2XD_SHT2X_SI70XX_ERROR) {
					mqttClient.publish(ESP_CONTROLLER_2_TOPIC, "[htu21d] error reading humidity");

					if (htu21d.voltageStatus() == false) {
						mqttClient.publish(ESP_CONTROLLER_2_TOPIC, "[htu21d] power FAIL, VDD < +2.25v");
					}
				} else {

					//publish htu21d data
					sprintf(msg, "{\"temp2\": \"%.1f\", \"humidity\": \"%.1f\"}", temperatureValue, compensatedHumidityValue);
					mqttClient.publish(HTU21D_TOPIC, msg);
				}
			}

			//read hcsr501
			if(digitalRead(hcsr501Pin) == LOW) {
				sprintf(msg, "{\"motion1\": \"not detected\"}");
			} else {
				sprintf(msg, "{\"motion1\": \"detected\"}");
			}
			mqttClient.publish(HCSR501_1_TOPIC, msg);

			//read mc38
			if(digitalRead(mc38Pin) == LOW) {
				sprintf(msg, "{\"door1\": \"closed\"}");
			} else {
				sprintf(msg, "{\"door1\": \"open\"}");
			}
			mqttClient.publish(MC38_1_TOPIC, msg);

			sensorTimer = now;
		}
	}

	blinkLed();
}

void reconnect() {
	while (WiFi.status() != WL_CONNECTED){
		WiFi.reconnect();
		delay(500);
	}
	while (!mqttClient.connected()) {
		if (mqttClient.connect(ESP_CONTROLLER_2_TOPIC)) {
			mqttClient.publish(ESP_CONTROLLER_2_TOPIC, "WiFi and MQTT are up!");
			delay(100);
		} else {
			delay(2000);
		}
	}
}

void blinkLed() {
	long now = millis();
	if(!ledOn) {
		if (now - ledTimer > 1000) {
			ledTimer = now;
			digitalWrite(ledPin, HIGH);
			ledOn = true;
		}
	} else {
		if (now - ledTimer > 50) {
			ledTimer = now;
			digitalWrite(ledPin, LOW);
			ledOn = false;
		}
	}
}
