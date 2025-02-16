#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <DHT.h>
#include <TF_Tiny_Lidar.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Server URL (replace with your ngrok URL)
const char* serverUrl = "http://abcd1234.ngrok.io/api/sensor-data";

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
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi");

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
        int mq2Value = analogRead(MQ2_PIN);
        int mq4Value = analogRead(MQ4_PIN);
        int mq6Value = analogRead(MQ6_PIN);
        int mq9Value = analogRead(MQ9_PIN);
        int mq131Value = analogRead(MQ131_PIN);
        float distance = lidar.getDistance();

        // Create JSON payload
        String payload = "{";
        payload += "\"temperature\": " + String(temperature) + ",";
        payload += "\"humidity\": " + String(humidity) + ",";
        payload += "\"mq2\": " + String(mq2Value) + ",";
        payload += "\"mq4\": " + String(mq4Value) + ",";
        payload += "\"mq6\": " + String(mq6Value) + ",";
        payload += "\"mq9\": " + String(mq9Value) + ",";
        payload += "\"mq131\": " + String(mq131Value) + ",";
        payload += "\"distance\": " + String(distance);
        payload += "}";

        // Send HTTP POST request
        HTTPClient http;
        http.begin(serverUrl);
        http.addHeader("Content-Type", "application/json");
        int httpResponseCode = http.POST(payload);

        if (httpResponseCode > 0) {
            Serial.println("Data sent to server");
        } else {
            Serial.println("Error sending data");
        }
        http.end();
    }
    delay(5000); // Send data every 5 seconds
}