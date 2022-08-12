#include <Arduino.h>
#include <IRremoteESP8266.h>
#include <IRsend.h>
#include <Wire.h>
#include <PubSubClient.h>
#include <Adafruit_BMP280.h>
#include "EmonLib.h"
#include "ccs811.h"
#include "WiFi.h"
#include "config.h"

const uint8_t IR_PULSE_MAX = 5;
const uint16_t kIrLed = 4;
IRsend irsend(kIrLed);

int ledPin = 32;
bool ledOn = false;
long ledTimer = 0;
long ledEnabledTimer = 0;
bool ledEnabled = true;

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
char msg[100];

EnergyMonitor sct013;
int sct013Pin = 34;
double sct013Calib = 4.928;
bool sct013FirstReading = false;
Adafruit_BMP280 bmp280;
bool bmp280Began = false;
CCS811 ccs811(-1);
long sensorTimer = 0;
int sensorDelay = 5000;

void setup() {
	//set up infra red
	irsend.begin();

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

	//set up i2c
	Wire.begin();
	mqttClient.publish(ESP_CONTROLLER_1_TOPIC, "Setup [I2C]: OK");
	delay(100);

	//set up ccs811
	ccs811.set_i2cdelay(50);
	if (ccs811.begin()) {
		mqttClient.publish(ESP_CONTROLLER_1_TOPIC, "Enable [CCS811]: OK");
	} else {
		mqttClient.publish(ESP_CONTROLLER_1_TOPIC, "Enable [CCS811]: FAILED");
	}
	delay(100);
	if (ccs811.start(CCS811_MODE_1SEC)) {
		mqttClient.publish(ESP_CONTROLLER_1_TOPIC, "Start [CCS811]: OK");
	} else {
		mqttClient.publish(ESP_CONTROLLER_1_TOPIC, "Start [CCS811]: FAILED");
	}
	delay(100);

	//set up bmp280
	if (bmp280.begin(0x76)) {
		bmp280Began = true;
		mqttClient.publish(ESP_CONTROLLER_1_TOPIC, "Begin [BMP280]: OK");
	} else {
		mqttClient.publish(ESP_CONTROLLER_1_TOPIC, "Begin [BMP280]: FAILED");
	}
	delay(100);

	//set up Energy Monitor (sct013)
	sct013.current(sct013Pin, sct013Calib);
}

void loop() {
	if (WiFi.status() != WL_CONNECTED || !mqttClient.connected()) reconnect();

	mqttClient.loop();

	long now = millis();
	if (now - sensorTimer > sensorDelay) {
		if(ccs811Read()) mqttClient.publish(CCS811_TOPIC, msg);
		if(bmp280Read()) mqttClient.publish(BMP280_TOPIC, msg);
		if(sct013Read()) mqttClient.publish(SCT013_TOPIC, msg);
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

bool bmp280Read() {
	if (bmp280Began) {
		float t = bmp280.readTemperature();
		float p = bmp280.readPressure() / 100.0f;
		sprintf(msg, "{\"temp1\": \"%.1f\", \"pressure\": \"%.1f\"}", t, p);
		return true;
	} else return false;
}

bool ccs811Read() {
	uint16_t eco2, tvoc, errstat, raw;
	ccs811.read(&eco2, &tvoc, &errstat, &raw);
	if ( errstat == CCS811_ERRSTAT_OK ) {
		sprintf(msg, "{\"eco2\": \"%hu\", \"tvoc\": \"%hu\"}", eco2, tvoc);
		return true;
	} else if ( errstat == CCS811_ERRSTAT_OK_NODATA ) {
		mqttClient.publish(ESP_CONTROLLER_1_TOPIC, "ccs811: waiting for (new) data");
	} else if ( errstat & CCS811_ERRSTAT_I2CFAIL ) {
		mqttClient.publish(ESP_CONTROLLER_1_TOPIC, "ccs811: I2C error");
	} else {
		sprintf(msg, "ccs811 error: %s", ccs811.errstat_str(errstat));
		mqttClient.publish(ESP_CONTROLLER_1_TOPIC, msg);
	}
	return false;
}

bool sct013Read() {
	if(sct013FirstReading) {
		double irms = sct013.calcIrms(1480);
		sprintf(msg, "{\"amps\": \"%g\"}", irms);
		return true;
	}
	sct013FirstReading = true;
	return false;
}

void callback(char* topic, byte* payload, unsigned int length) {
	if (String(topic) == IRRAW_TOPIC) {
		uint16_t irRawData[150];
		uint8_t irRawDataIndex = 0;
		char pulse[IR_PULSE_MAX];
		uint8_t pulseIndex = 0;
		for (int i = 0; i < length; i++) {
			char c = (char)payload[i];
			if(c != ';') {
				pulse[pulseIndex] = c;
				pulseIndex++;
				if(pulseIndex > IR_PULSE_MAX) {
					mqttClient.publish(ESP_CONTROLLER_1_TOPIC, "ERROR: ir pulse > 5 digits");
					return;
				}
			} else {
				pulseIndex = 0;
				irRawData[irRawDataIndex] = atoi(pulse);
				irRawDataIndex++;
				pulse[0] = pulse[1] = pulse[2] = pulse[3] = pulse[4] = '\0';
			}
		}
		sprintf(msg, "irraw received - size: %hu pulses: %hu", length, irRawDataIndex);
		mqttClient.publish(ESP_CONTROLLER_1_TOPIC, msg);
		irsend.sendRaw(irRawData, irRawDataIndex, 38);
	}
}
