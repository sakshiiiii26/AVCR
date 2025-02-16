from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensor_data.db'
db = SQLAlchemy(app)

# Database model
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    mq2 = db.Column(db.Float)
    mq4 = db.Column(db.Float)
    mq6 = db.Column(db.Float)
    mq9 = db.Column(db.Float)
    mq131 = db.Column(db.Float)
    distance = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Route to receive sensor data
@app.route('/api/sensor-data', methods=['POST'])
def receive_sensor_data():
    data = request.get_json()
    new_data = SensorData(
        temperature=data['temperature'],
        humidity=data['humidity'],
        mq2=data['mq2'],
        mq4=data['mq4'],
        mq6=data['mq6'],
        mq9=data['mq9'],
        mq131=data['mq131'],
        distance=data['distance']
    )
    db.session.add(new_data)
    db.session.commit()
    return jsonify({"status": "success"})

# Route to fetch all sensor data
@app.route('/api/sensor-data', methods=['GET'])
def get_sensor_data():
    data = SensorData.query.all()
    result = [{
        "id": d.id,
        "temperature": d.temperature,
        "humidity": d.humidity,
        "mq2": d.mq2,
        "mq4": d.mq4,
        "mq6": d.mq6,
        "mq9": d.mq9,
        "mq131": d.mq131,
        "distance": d.distance,
        "timestamp": d.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for d in data]
    return jsonify(result)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)