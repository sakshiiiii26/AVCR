#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include <TFmini.h>   // If using standard TFmini library

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Server URL (replace with your backend URL)
const char* serverUrl = "http://your-server-ip:5000/api/sensor-data";

// Sensor pins
#define DHTPIN 4
#define MQ2_PIN 34
#define MQ4_PIN 35
#define MQ6_PIN 32
#define MQ9_PIN 33
#define MQ131_PIN 25
#define LIDAR_SDA 21
#define LIDAR_SCL 22

// Initialize DHT22
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// Initialize TF-LC02 Lidar
TF_Tiny_Lidar lidar;

void setup() {
    Serial.begin(115200);

    // Connect to WiFi
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi...");
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
    }
    Serial.println("\nConnected to WiFi");

    // Initialize sensors
    dht.begin();
    Wire.begin(LIDAR_SDA, LIDAR_SCL);
    lidar.begin();
}

void loop() {
    if (WiFi.status() == WL_CONNECTED) {
        // Read sensor data
        float temperature = dht.readTemperature();
        float humidity = dht.readHumidity();
        int mq2Raw = analogRead(MQ2_PIN);
        int mq4Raw = analogRead(MQ4_PIN);
        int mq6Raw = analogRead(MQ6_PIN);
        int mq9Raw = analogRead(MQ9_PIN);
        int mq131Raw = analogRead(MQ131_PIN);
        float distance = lidar.getDistance();

        //  Check for valid sensor readings
        if (isnan(temperature) || isnan(humidity)) {
            Serial.println("❌ Failed to read from DHT sensor!");
            return;
        }

        // Estimate gas concentrations using calibration coefficients
        float o2 = mq131Raw * 0.1;   // O2 estimation
        float co2 = mq6Raw * 0.3;   // CO2 estimation
        float co = mq9Raw * 0.5;    // CO estimation
        float ch4 = mq4Raw * 0.4;   // Methane estimation
        float propane = mq6Raw * 0.6; // Propane estimation
        float smoke = mq2Raw * 0.5; // Smoke estimation

        // Create JSON payload
        StaticJsonDocument<256> jsonDoc;
        jsonDoc["temperature"] = temperature;
        jsonDoc["humidity"] = humidity;
        jsonDoc["o2"] = o2;
        jsonDoc["co2"] = co2;
        jsonDoc["co"] = co;
        jsonDoc["ch4"] = ch4;
        jsonDoc["propane"] = propane;
        jsonDoc["smoke"] = smoke;
        jsonDoc["distance"] = distance;

        String payload;
        serializeJson(jsonDoc, payload);

        // Send HTTP POST request
        HTTPClient http;
        http.begin(serverUrl);
        http.addHeader("Content-Type", "application/json");
        int httpResponseCode = http.POST(payload);

        if (httpResponseCode > 0) {
            Serial.println("✅ Data sent to server: " + payload);
        } else {
            Serial.println("❌ Error sending data. HTTP Code: " + String(httpResponseCode));
        }
        http.end();
    } else {
        Serial.println("⚠️ WiFi not connected. Retrying...");
        WiFi.begin(ssid, password);
    }

    delay(5000); // Send data every 5 seconds
}
