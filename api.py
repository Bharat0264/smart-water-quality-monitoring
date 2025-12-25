from flask import Flask, request, jsonify
from pymongo import MongoClient
import joblib
import os
from datetime import datetime

app = Flask(__name__)

# ===============================
# MongoDB Atlas Connection
# ===============================
MONGO_URI = os.environ.get("MONGO_URI")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI environment variable not set")

client = MongoClient(MONGO_URI)
db = client["water_quality"]
collection = db["sensor_data"]

# ===============================
# Load ML Model
# ===============================
MODEL_PATH = "model.pkl"

if not os.path.exists(MODEL_PATH):
    raise RuntimeError("model.pkl not found")

model = joblib.load(MODEL_PATH)

# ===============================
# Health Check Route
# ===============================
@app.route("/", methods=["GET"])
def home():
    return "Smart Water Quality Monitoring API is running."

# ===============================
# Receive Sensor Data + Predict
# ===============================
@app.route("/api/data", methods=["POST"])
def receive_data():
    try:
        data = request.get_json()

        ph = float(data.get("ph"))
        turbidity = float(data.get("turbidity"))
        temperature = float(data.get("temperature"))

        # ML Prediction
        prediction = model.predict([[ph, turbidity, temperature]])[0]
        result = "Safe" if prediction == 1 else "Unsafe"

        record = {
            "ph": ph,
            "turbidity": turbidity,
            "temperature": temperature,
            "prediction": result,
            "timestamp": datetime.utcnow()
        }

        collection.insert_one(record)

        return jsonify({
            "message": "Data stored successfully",
            "prediction": result
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

# ===============================
# Fetch Latest Reading
# ===============================
@app.route("/api/latest", methods=["GET"])
def latest_data():
    doc = collection.find_one(sort=[("timestamp", -1)], {"_id": 0})
    if doc:
        return jsonify(doc)
    return jsonify({"message": "No data available"}), 404

# ===============================
# Run App (Render Compatible)
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
