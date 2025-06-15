
Autonomous Vehicle for Calamity Rescue (AVCR)

AI for Safer and Smarter Inclusive Bharat

AVCR is an AI-powered rescue vehicle designed to assist during natural disasters and industrial accidents. It uses real-time sensor data and machine learning to detect hazards, assess survivability, and support rapid rescue operations—especially in rural and disaster-prone areas.

Problem Statement

Rescue operations in India are often delayed and risky due to poor visibility, gas leaks, debris, and lack of real-time information—especially in remote areas. AVCR solves this by offering an intelligent, autonomous, and affordable solution to locate survivors and detect danger zones early.

Solution

AVCR is a modular ground vehicle powered by Jetson Nano and integrated with:

ESP32 for wireless sensor communication

Gas & temperature sensors (MQ2, MQ4, MQ6, MQ131, DHT22)

LIDAR for obstacle avoidance and area mapping

ML models for anomaly detection & survivability prediction

Flask API for real-time data handling and decision-making

Tech Stack

Hardware: Jetson Nano, ESP32, LIDAR, MQ Sensors, DHT22
Languages: Python, C++
Frameworks: Flask, Scikit-learn, NumPy, Pandas
Protocols: LoRa / Serial / Wi-Fi (for ESP32 to Jetson)
ML Models: Random Forest (survivability), Isolation Forest (anomaly detection)

Features

Real-time gas, temperature, and distance monitoring

Survivability prediction of detected individuals

Hazard classification using AI

Remote control and data display through web dashboard

Works in offline mode (Edge AI)

How to Run

Clone the repo:
git clone https://github.com/sakshiiiii26/AVCR.git
cd AVCR

Install dependencies:
pip install -r requirements.txt

Run Flask backend:
python app.py

Access local server:
http://localhost:5000

Project Structure

AVCR/
├── models/
│ └── survivability_model.pkl
├── sensors/
│ └── sensor_readings.py
├── app.py
├── utils.py
├── templates/
│ └── index.html
├── static/
├── requirements.txt
└── README.md

Future Scope

Integrate drone-based aerial scans

Multi-agent swarm rescue system

AI voice assistance for remote responders

Integration with government disaster portals

Team

Sakshi Sharma – ML & Backend Development

Umang Sharma - IoT & hardware
