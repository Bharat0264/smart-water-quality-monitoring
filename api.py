from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import joblib
import os

app = Flask(__name__)

# =========================
# Local MongoDB Connection
# =========================
client = MongoClient("mongodb://localhost:27017/")
db = client["water_quality_db"]
collection = db["sensor_data"]

# =========================
# Load ML Model
# =========================
model = joblib.load("model.pkl")

# =========================
# Home Route
# =========================
@app.route("/")
def home():
    return "Smart Water Quality Monitoring API is running."

# =========================
# Receive Sensor Data
# =========================
@app.route("/api/data", methods=["POST"])
def receive_data():
    data = request.json

    ph = data.get("ph")
    turbidity = data.get("turbidity")
    temperature = data.get("temperature")

    if ph is None or turbidity is None or temperature is None:
        return jsonify({"error": "Invalid data"}), 400

    # ML Prediction
    prediction = model.predict([[ph, turbidity, temperature]])[0]
    result = "Safe" if prediction == 1 else "Unsafe"

    # Store in MongoDB
    record = {
        "ph": ph,
        "turbidity": turbidity,
        "temperature": temperature,
        "prediction": result,
        "timestamp": datetime.now()
    }

    collection.insert_one(record)

    return jsonify({
        "message": "Data stored successfully",
        "prediction": result
    })

# =========================
# Fetch Latest Data
# =========================
@app.route("/api/latest", methods=["GET"])
def get_latest():
    doc = collection.find_one(
        {},
        sort=[("timestamp", -1)],
        projection={"_id": 0}
    )

    if not doc:
        return jsonify({"message": "No data available"})

    return jsonify(doc)

# =========================
# Run App (Same WiFi Access)
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
