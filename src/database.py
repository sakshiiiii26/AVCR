from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS
import joblib
import numpy as np

app = Flask(__name__)
CORS(app)

# SQLite database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensor_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Float, nullable=True)
    o2 = db.Column(db.Float, nullable=True)      # Oxygen
    co2 = db.Column(db.Float, nullable=True)     # Carbon Dioxide
    co = db.Column(db.Float, nullable=True)      # Carbon Monoxide
    ch4 = db.Column(db.Float, nullable=True)     # Methane
    propane = db.Column(db.Float, nullable=True) # Propane
    smoke = db.Column(db.Float, nullable=True)   # Smoke
    distance = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Load ML models
anomaly_model = joblib.load("anomaly_detector.pkl")
danger_model = joblib.load("danger_classifier.pkl")
label_encoder = joblib.load("label_encoder.pkl")
# Route to receive sensor data (POST)
@app.route('/api/sensor-data', methods=['POST'])
def receive_sensor_data():
    try:
        data = request.get_json()

        # Predict anomaly
        features = np.array([[data['o2'], data['co2'], data['co'], data['ch4'], data['propane'], data['smoke'], data['temperature'], data['humidity']]])
        is_anomaly = anomaly_model.predict(features)[0]  # 1 = normal, -1 = anomaly

        # Predict danger level
        danger_level = danger_model.predict(features)[0]
        danger_level = label_encoder.inverse_transform([danger_level])[0]  # Convert to label (Safe, Warning, Danger)

        # Save data to database
        new_data = SensorData(
            temperature=data.get('temperature'),  # Using `.get()` to prevent crashes
            humidity=data.get('humidity'),
            o2=data.get('o2'),
            co2=data.get('co2'),
            co=data.get('co'),
            ch4=data.get('ch4'),
            propane=data.get('propane'),
            smoke=data.get('smoke'),
            distance=data.get('distance')
        )
        db.session.add(new_data)
        db.session.commit()
        return jsonify({"status": "success", "message": "Data stored successfully!"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# Route to fetch all sensor data (GET)
@app.route('/api/sensor-data', methods=['GET'])
def get_sensor_data():
    data = SensorData.query.order_by(SensorData.timestamp.desc()).limit(20).all()  # Fetch last 20 entries
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
        "timestamp": d.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for d in data]
    return jsonify(result)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
