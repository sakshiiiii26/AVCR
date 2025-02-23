#  1. Anomaly Detection (Isolation Forest)
import pandas as pd
from sklearn.ensemble import IsolationForest

# Load the sensor dataset
df = pd.read_csv("sensor_data.csv")  # Replace with your actual dataset

# Selecting relevant sensor features
features = ["o2", "co2", "co", "ch4", "propane", "smoke", "temperature", "humidity"]
X = df[features]

# Train Isolation Forest model
model = IsolationForest(contamination=0.05)  # 5% data as anomalies
model.fit(X)

# Predict anomalies (1 = normal, -1 = anomaly)
df["anomaly"] = model.predict(X)

# Save the model
import joblib
joblib.dump(model, "anomaly_detector.pkl")

print("Anomaly detection model trained and saved!")

# 2. Time-Series Prediction (LSTM)
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

# Load and preprocess data
df = pd.read_csv("sensor_data.csv")
features = ["o2", "co2", "co", "ch4", "propane", "smoke", "temperature", "humidity"]
scaler = MinMaxScaler()
df_scaled = scaler.fit_transform(df[features])

# Prepare input sequences
X, y = [], []
sequence_length = 10  # Use past 10 readings to predict the next one

for i in range(len(df_scaled) - sequence_length):
    X.append(df_scaled[i : i + sequence_length])
    y.append(df_scaled[i + sequence_length])

X, y = np.array(X), np.array(y)

# Build LSTM model
model = Sequential([
    LSTM(50, activation="relu", return_sequences=True, input_shape=(sequence_length, len(features))),
    LSTM(50, activation="relu"),
    Dense(len(features))
])

model.compile(optimizer="adam", loss="mse")
model.fit(X, y, epochs=20, batch_size=16, verbose=1)

# Save model
model.save("gas_prediction_model.h5")
print("Time-series prediction model trained and saved!")

#  3. Danger Level Classification (XGBoost)
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

# Load dataset
df = pd.read_csv("sensor_data.csv")

# Define thresholds for safety levels
def classify_danger(row):
    if row["co"] > 50 or row["ch4"] > 200 or row["propane"] > 150 or row["smoke"] > 80:
        return "Danger"
    elif row["co"] > 30 or row["ch4"] > 100 or row["propane"] > 80 or row["smoke"] > 50:
        return "Warning"
    else:
        return "Safe"

df["danger_level"] = df.apply(classify_danger, axis=1)

# Encode labels
le = LabelEncoder()
df["danger_level"] = le.fit_transform(df["danger_level"])

# Train-test split
X = df[["o2", "co2", "co", "ch4", "propane", "smoke", "temperature", "humidity"]]
y = df["danger_level"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train XGBoost model
model = xgb.XGBClassifier()
model.fit(X_train, y_train)

# Save the model
joblib.dump(model, "danger_classifier.pkl")
joblib.dump(le, "label_encoder.pkl")

print("Danger level classification model trained and saved!")
