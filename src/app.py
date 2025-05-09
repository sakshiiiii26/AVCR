from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS
import joblib
import numpy as np
import tensorflow as tf
import csv
import os
import pandas as pd
from flask_socketio import SocketIO
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*") 
CORS(app)

# SQLite database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensor_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# CSV file setup
CSV_FILE = "sensor_data.csv"

# Create CSV file with headers if it doesn't exist
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "o2", "co2", "co", "ch4", "propane", "smoke", "temperature", "humidity", "anomaly", "danger_level"])

# Database Model
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Float, nullable=True)
    o2 = db.Column(db.Float, nullable=True)      
    co2 = db.Column(db.Float, nullable=True)     
    co = db.Column(db.Float, nullable=True)      
    ch4 = db.Column(db.Float, nullable=True)     
    propane = db.Column(db.Float, nullable=True) 
    smoke = db.Column(db.Float, nullable=True)   
    distance = db.Column(db.Float, nullable=True)
    anomaly = db.Column(db.Integer, nullable=True)  
    danger_level = db.Column(db.String(10), nullable=True)  
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Load ML models
# Load ML models with correct paths
anomaly_model = joblib.load("src/anomaly_detector.pkl")
danger_model = joblib.load("src/danger_classifier.pkl")
label_encoder = joblib.load("src/label_encoder.pkl")
scaler = joblib.load("src/scaler.pkl")  # Load the MinMaxScaler
gas_prediction_model = tf.keras.models.load_model("src/gas_prediction_model.h5", compile=False)# Load LSTM Model
print("🚀 App is using the updated .h5 model file")


# Define sensor features
FEATURES = ["o2", "co2", "co", "ch4", "propane", "smoke", "temperature", "humidity"]

# Route to receive sensor data (POST)
@app.route('/api/sensor-data', methods=['POST'])
def receive_sensor_data():
    try:
        data = request.get_json()
        print("📥 Received sensor data:", data)
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        # Prepare feature array for ML models
        features = np.array([[data.get(f, 0) for f in FEATURES]])

        # Predict anomaly
        is_anomaly = int(anomaly_model.predict(features)[0])  

        # Predict danger level
        try:
            danger_level = danger_model.predict(features)[0]
            danger_level = label_encoder.inverse_transform([danger_level])[0]
        except ValueError:
            danger_level = "Unknown"

        # Save data to database
        new_data = SensorData(
            temperature=data.get('temperature', 0),
            humidity=data.get('humidity', 0),
            o2=data.get('o2', 0),
            co2=data.get('co2', 0),
            co=data.get('co', 0),
            ch4=data.get('ch4', 0),
            propane=data.get('propane', 0),
            smoke=data.get('smoke', 0),
            distance=data.get('distance', 0),
            anomaly=is_anomaly,
            danger_level=danger_level
        )
        db.session.add(new_data)
        db.session.commit()

        # Append to CSV file
        try:
            with open(CSV_FILE, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    timestamp,
                    data.get("o2", 0),
                    data.get("co2", 0),
                    data.get("co", 0),
                    data.get("ch4", 0),
                    data.get("propane", 0),
                    data.get("smoke", 0),
                    data.get("temperature", 0),
                    data.get("humidity", 0),
                    is_anomaly,
                    danger_level
                ])
        except Exception as csv_error:
            print("Warning: Could not write to CSV!", csv_error)

        return jsonify({
            "status": "success",
            "message": "Data stored successfully!",
            "anomaly": is_anomaly,
            "danger_level": danger_level
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 400

# Route to fetch last 20 sensor data records (GET)
@app.route('/api/sensor-data', methods=['GET'])
def get_sensor_data():
    data = SensorData.query.order_by(SensorData.id.desc()).limit(20).all()
    result = [{
        "id": d.id,
        "temperature": d.temperature,
        "humidity": d.humidity,
        "o2": d.o2,
        "co2": d.co2,
        "co": d.co,
        "ch4": d.ch4,
        "propane": d.propane,
        "smoke": d.smoke,
        "distance": d.distance,
        "anomaly": d.anomaly,
        "danger_level": d.danger_level,
        "timestamp": d.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for d in data]
    return jsonify(result)

# Route to download the sensor data CSV file
@app.route('/api/download-csv', methods=['GET'])
def download_csv():
    return send_file(CSV_FILE, as_attachment=True, mimetype="text/csv")

# Route to predict gas levels using LSTM Model
# @app.route('/api/predict-gas', methods=['GET'])
# def predict_gas():
#     try:
#         # Read the latest 10 rows from the CSV file
#         df = pd.read_csv(CSV_FILE)

#         if len(df) < 10:
#             return jsonify({"error": "Not enough data for prediction. Need at least 10 readings."}), 400

#         # Select the last 10 readings
#         last_10 = df.iloc[-10:][FEATURES].values

#         # Scale input data
#         input_scaled = scaler.transform(last_10)

#         # Reshape for LSTM (batch_size=1, timesteps=10, features=8)
#         input_scaled = input_scaled.reshape(1, 10, len(FEATURES))

#         # Predict future gas levels
#         prediction = gas_prediction_model.predict(input_scaled)

#         # Convert back to original scale
#         prediction_unscaled = scaler.inverse_transform(prediction)

#         return jsonify({"predicted_values": prediction_unscaled.tolist()})

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400




@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        # Prepare features for ML models
        features = np.array([[data.get(f, 0) for f in FEATURES]])

        # Predict anomaly
        is_anomaly = int(anomaly_model.predict(features)[0])

        # Predict danger level
        try:
            danger_level = danger_model.predict(features)[0]
            danger_level = label_encoder.inverse_transform([danger_level])[0]
        except ValueError:
            danger_level = "Unknown"

        # Predict future gas levels using LSTM
        features_scaled = scaler.transform(features)
        features_scaled = features_scaled.reshape(1, 1, len(FEATURES))  # Reshape for LSTM
        future_gas_prediction = gas_prediction_model.predict(features_scaled)
        predicted_values = scaler.inverse_transform(future_gas_prediction)

        return jsonify({
            "anomaly": is_anomaly,
            "danger_level": danger_level,
            "predicted_values": predicted_values.tolist()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
