#include <Wire.h>
#include <PubSubClient.h>
#include "ccs811.h"
#include "WiFi.h"
#include "config.h"

const char* topic = "ccs811";

long before = 0;

char msg[20];

CCS811 ccs811(-1);
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

void setup() {
  Serial.begin(115200);

  //connect to wifi
  WiFi.begin(SSID, PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi..");
  }
  Serial.println("Connected to WiFi!");

  //set up mqtt server
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  while (!mqttClient.connected()) {
    Serial.println("Connecting to MQTT...");
    mqttClient.connect("mqtt connected!");
    delay(2000);
  }

  //setup i2c
  Serial.print("Setup: I2C ");
  Wire.begin();
  Serial.println("OK");

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

void loop() {
  mqttClient.loop();

  if (five_seconds_delay()) {
    //dtostrf(i, 6, 2, msg);
    uint16_t eco2, etvoc, errstat, raw;
    ccs811.read(&eco2, &etvoc, &errstat, &raw);
    Serial.print("CCS811: ");
    if ( errstat == CCS811_ERRSTAT_OK ) {
      Serial.print("eco2=");  Serial.print(eco2);  Serial.print(" ppm  ");
      Serial.print("etvoc="); Serial.print(etvoc); Serial.print(" ppb  ");
    } else if ( errstat == CCS811_ERRSTAT_OK_NODATA ) {
      Serial.print("waiting for (new) data");
    } else if ( errstat & CCS811_ERRSTAT_I2CFAIL ) {
      Serial.print("I2C error");
    } else {
      Serial.print( "error: " );
      Serial.print( ccs811.errstat_str(errstat) );
    }
    Serial.println();

    sprintf(msg, "eco2=%dppm etvoc=%d", eco2, etvoc);
    mqttClient.publish(topic, msg);
  }
}

bool five_seconds_delay() {
  long now = millis();
  if (now - before > 5000) {
    before = now;
    return true;
  } return false;
}
