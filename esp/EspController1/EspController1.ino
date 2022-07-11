#include <Wire.h>
#include <PubSubClient.h>
#include "ccs811.h"
#include "WiFi.h"
#include "config.h"

long lastMqttReconnectAttempt = 0;
long timer = 0;

CCS811 ccs811(-1);
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
char ccs811Reading[40];

void setup() {
	Serial.begin(115200);
	setupWifi();
	setupMqtt();
	setupI2c();
	setupCcs811();
}

void loop() {
	//reconnect to wifi
	while (WiFi.status() != WL_CONNECTED) {
		Serial.println("Reconnecting to WiFi..");
		delay(500);
		WiFi.reconnect();
	}

	//reconnect to mqtt server
	if (!mqttClient.connected()) {
		long now = millis();
		if (now - lastMqttReconnectAttempt > 2000) {
			lastMqttReconnectAttempt = now;
			if (mqttReconnect()) {
				lastMqttReconnectAttempt = 0;
			}
		}
	} else {
		mqttClient.loop();

		if (fiveSecondsDelay()) {
			if(ccs811Read()) mqttClient.publish(CCS811_TOPIC, ccs811Reading);
		}
	}
}

void setupWifi() {
	WiFi.begin(SSID, PASSWORD);
	while (WiFi.status() != WL_CONNECTED) {
		delay(500);
		Serial.println("Connecting to WiFi..");
	}
	Serial.println("Connected to WiFi!");
}

void setupMqtt() {
	mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
	//mqttClient.setCallback(callback);
}

void setupI2c() {
	Serial.print("Setup: I2C ");
	Wire.begin();
	Serial.println("OK");
}

void setupCcs811() {
	//enable CCS811
	bool ok;
	Serial.print("Setup: CCS811 ");
	ccs811.set_i2cdelay(50);
	ok = ccs811.begin();
	if (ok) Serial.println("OK"); else Serial.println("FAILED");

	//start CCS811
	Serial.print("Setup: CCS811 start ");
	ok = ccs811.start(CCS811_MODE_1SEC);
	if (ok) Serial.println("OK"); else Serial.println("FAILED");

	//CCS811 version
	Serial.print("CCS811 library version: "); Serial.println(CCS811_VERSION);
}

boolean mqttReconnect() {
	Serial.println("Connecting to MQTT...");
	if (mqttClient.connect("EspController1")) {
		//mqttClient.subscribe("topics");
		Serial.println("MQTT connected!");
	}
	return mqttClient.connected();
}

bool fiveSecondsDelay() {
	long now = millis();
	if (now - timer > 5000) {
		timer = now;
		return true;
	} return false;
}

bool ccs811Read() {
	uint16_t eco2, etvoc, errstat, raw;
	ccs811.read(&eco2, &etvoc, &errstat, &raw);
	Serial.print("CCS811: ");
	if ( errstat == CCS811_ERRSTAT_OK ) {
		Serial.print("eco2=");  Serial.print(eco2);  Serial.print(" ppm  ");
		Serial.print("etvoc="); Serial.print(etvoc); Serial.print(" ppb  ");
		Serial.println();
		sprintf(ccs811Reading, "{\"eco2\": \"%hu\", \"etvoc\": \"%hu\"}", eco2, etvoc);
		return true;
	} else if ( errstat == CCS811_ERRSTAT_OK_NODATA ) {
		Serial.print("waiting for (new) data");
	} else if ( errstat & CCS811_ERRSTAT_I2CFAIL ) {
		Serial.print("I2C error");
	} else {
		Serial.print( "error: " );
		Serial.print( ccs811.errstat_str(errstat) );
	}
	Serial.println();
	return false;
}
