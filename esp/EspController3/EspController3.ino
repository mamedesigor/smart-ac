#include <PubSubClient.h>
#include "WiFi.h"
#include "config.h"

int ledPin = 32;
bool ledOn = false;
long ledTimer = 0;
long ledEnabledTimer = 0;
bool ledEnabled = true;

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
char msg[100];

int mc38Pin = 34;

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
		if (mqttClient.connect(ESP_CONTROLLER_3_TOPIC)) {
			mqttClient.publish(ESP_CONTROLLER_3_TOPIC, "WiFi and MQTT are up!");
			delay(100);
		} else {
			delay(2000);
		}
	}

	//set up mc38
	pinMode(mc38Pin, INPUT);
	mqttClient.publish(ESP_CONTROLLER_3_TOPIC, "MC38 OK");
}

void loop() {
	if (WiFi.status() != WL_CONNECTED || !mqttClient.connected()) reconnect();

	mqttClient.loop();

	long now = millis();
	if (now - sensorTimer > sensorDelay) {

		//read mc38
		if(digitalRead(mc38Pin) == LOW) {
			sprintf(msg, "{\"door2\": \"closed\"}");
		} else {
			sprintf(msg, "{\"door2\": \"open\"}");
		}
		mqttClient.publish(MC38_2_TOPIC, msg);

		sensorTimer = now;
	}

	if(ledEnabled) blinkLed();
}

void reconnect() {
	while (WiFi.status() != WL_CONNECTED){
		WiFi.reconnect();
		delay(500);
	}
	while (!mqttClient.connected()) {
		if (mqttClient.connect(ESP_CONTROLLER_3_TOPIC)) {
			mqttClient.publish(ESP_CONTROLLER_3_TOPIC, "WiFi and MQTT are up!");
			delay(100);
		} else {
			delay(2000);
		}
	}
}

void blinkLed() {
	long now = millis();
	if (now - ledEnabledTimer > 20000) {
		ledEnabled = false;
		digitalWrite(ledPin, LOW);
	} else {
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
}
