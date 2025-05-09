#include <Arduino.h>
#include <Wire.h>
#include "DHT.h"

// --- PIN Definitions ---
#define DHTPIN 4
#define DHTTYPE DHT22

#define MQ2_PIN 34
#define MQ4_PIN 35
#define MQ6_PIN 32
#define MQ9_PIN 33
#define MQ131_PIN 25

#define LIDAR_SDA 21
#define LIDAR_SCL 22

// --- DHT22 Setup ---
DHT dht(DHTPIN, DHTTYPE);

// --- Setup ---
void setup() {
  Serial.begin(115200);
  dht.begin();

  Wire.begin(LIDAR_SDA, LIDAR_SCL);  // I2C for LIDAR
  Serial.println("AVCR Sensor Integration Initialized.");
}

// --- Read Distance from TF-LC02 LIDAR (Simple Raw Read) ---
int readLidarDistance() {
  Wire.beginTransmission(0x10); // Default I2C address of TF-LC02
  Wire.write(0x00);             // Distance register
  Wire.endTransmission();
  Wire.requestFrom(0x10, 2);
  if (Wire.available() == 2) {
    int high = Wire.read();
    int low = Wire.read();
    return (high << 8) + low;
  }
  return -1; // Error
}

// --- Loop ---
void loop() {
  // --- DHT22 Readings ---
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // --- Gas Sensor Readings ---
  int mq2 = analogRead(MQ2_PIN);
  int mq4 = analogRead(MQ4_PIN);
  int mq6 = analogRead(MQ6_PIN);
  int mq9 = analogRead(MQ9_PIN);
  int mq131 = analogRead(MQ131_PIN);

  // --- LIDAR Readings ---
  int distance = readLidarDistance();

  // --- Print All Values ---
  Serial.println("==== Sensor Readings ====");
  Serial.print("Temp: "); Serial.print(temperature); Serial.println(" *C");
  Serial.print("Humidity: "); Serial.print(humidity); Serial.println(" %");
  Serial.print("MQ2: "); Serial.println(mq2);
  Serial.print("MQ4: "); Serial.println(mq4);
  Serial.print("MQ6: "); Serial.println(mq6);
  Serial.print("MQ9: "); Serial.println(mq9);
  Serial.print("MQ131: "); Serial.println(mq131);
  Serial.print("LIDAR Distance: "); Serial.print(distance); Serial.println(" cm");
  Serial.println("=========================");

  delay(2000);  // 2 seconds between readings
}
