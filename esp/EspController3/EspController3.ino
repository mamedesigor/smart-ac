#include <PubSubClient.h>
#include "WiFi.h"
#include "config.h"

int ledPin = 32;
bool ledOn = false;
long ledTimer = 0;

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
char msg[100];

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
	mqttClient.setCallback(callback);
	mqttClient.setBufferSize(1024);
	while (!mqttClient.connected()) {
		if (mqttClient.connect(ESP_CONTROLLER_1_TOPIC)) {
			mqttClient.subscribe(IRRAW_TOPIC);
			mqttClient.publish(ESP_CONTROLLER_1_TOPIC, "WiFi and MQTT are up!");
			delay(100);
		} else {
			delay(2000);
		}
	}
}

void loop() {
	if (WiFi.status() != WL_CONNECTED || !mqttClient.connected()) reconnect();

	mqttClient.loop();

	long now = millis();
	if (now - sensorTimer > sensorDelay) {
		sensorTimer = now;
	}

	blinkLed();
}

void reconnect() {
	while (WiFi.status() != WL_CONNECTED){
		WiFi.reconnect();
		delay(500);
	}
	while (!mqttClient.connected()) {
		if (mqttClient.connect(ESP_CONTROLLER_1_TOPIC)) {
			mqttClient.subscribe(IRRAW_TOPIC);
			mqttClient.publish(ESP_CONTROLLER_1_TOPIC, "WiFi and MQTT are up!");
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
