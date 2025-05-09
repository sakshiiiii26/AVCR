import random
import requests
import time
import json

# Flask server URL (replace with your actual backend URL)
server_url = "http://localhost:5000/api/sensor-data"

def generate_sensor_data():
    """Generate random mock sensor data to simulate ESP32 readings."""
    # Simulate sensor data
    temperature = random.uniform(20.0, 30.0)  # Temperature between 20 and 30 °C
    humidity = random.uniform(30.0, 60.0)    # Humidity between 30 and 60 %
    mq2 = random.randint(100, 500)           # MQ2 sensor value
    mq4 = random.randint(100, 500)           # MQ4 sensor value
    mq6 = random.randint(100, 500)           # MQ6 sensor value
    mq9 = random.randint(100, 500)           # MQ9 sensor value
    mq131 = random.randint(100, 500)         # MQ131 sensor value
    distance = random.randint(0, 100)        # LIDAR distance between 0-100 cm

    # Return the simulated sensor data as a dictionary
    return {
        "temperature": temperature,
        "humidity": humidity,
        "o2": mq131 * 0.1,   # Estimating O2
        "co2": mq6 * 0.3,    # Estimating CO2
        "co": mq9 * 0.5,     # Estimating CO
        "ch4": mq4 * 0.4,    # Estimating Methane (CH4)
        "propane": mq6 * 0.6, # Estimating Propane
        "smoke": mq2 * 0.5,  # Estimating Smoke
        "distance": distance
    }

def send_sensor_data_to_server(data):
    """Send sensor data to the Flask server via HTTP POST request."""
    print("Sending data to server...")
    headers = {"Content-Type": "application/json"}
    response = requests.post(server_url, data=json.dumps(data), headers=headers)

    print("Response status:", response.status_code)
    print("Response body:", response.text)

    if response.status_code not in (200, 201):
        print(f"❌ Error sending data: {response.status_code}")
    else:
        print("✅ Data sent successfully!")



def simulate():
    """Simulate sending sensor data every 5 seconds."""
    while True:
        sensor_data = generate_sensor_data()
        print("Simulated sensor data:", sensor_data)
        send_sensor_data_to_server(sensor_data)
        time.sleep(5)  # Delay for 5 seconds before sending next data

if __name__ == "__main__":
    simulate()
