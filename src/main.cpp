#include <Arduino.h>

void setup() {
    Serial.begin(115200);
    Serial.println("ESP32 with PlatformIO is ready!");
}

void loop() {
    Serial.println("Hello, AVCR Project!");
    delay(1000);
}
