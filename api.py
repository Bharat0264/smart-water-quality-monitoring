from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import joblib
import os

app = Flask(__name__)

# ----------------------------
# MongoDB Atlas Configuration
# ----------------------------
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://Bharat5741:Puli@3125@water-quality-cluster.d5ddvpd.mongodb.net/water_quality?retryWrites=true&w=majority"
)

client = MongoClient(MONGO_URI)
db = client["water_quality"]
collection = db["readings"]

# ----------------------------
# Load ML Model
# ----------------------------
model = joblib.load("model.pkl")

# ----------------------------
# Utility: Safe / Unsafe Logic
# ----------------------------
def rule_based_check(ph, turbidity, temperature):
    if ph < 6.5 or ph > 8.5:
        return "Unsafe"
    if turbidity > 5:
        return "Unsafe"
    if temperature < 10 or temperature > 35:
        return "Unsafe"
    return "Safe"

# ----------------------------
# Root Route
# ----------------------------
@app.route("/")
def home():
    return jsonify({
        "message": "Smart Water Quality Monitoring API is running"
    })

# ----------------------------
# POST Sensor Data
# ----------------------------
@app.route("/api/data", methods=["POST"])
def receive_data():
    try:
        data = request.json

        ph = float(data["ph"])
        turbidity = float(data["turbidity"])
        temperature = float(data["temperature"])

        # ML Prediction
        prediction = model.predict([[ph, turbidity, temperature]])[0]

        # Rule-based override (safety critical)
        final_status = rule_based_check(ph, turbidity, temperature)

        record = {
            "ph": ph,
            "turbidity": turbidity,
            "temperature": temperature,
            "ml_prediction": str(prediction),
            "final_status": final_status,
            "timestamp": datetime.utcnow()
        }

        collection.insert_one(record)

        return jsonify({
            "message": "Data stored successfully",
            "prediction": final_status
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------------
# GET Latest Reading
# ----------------------------
@app.route("/api/latest", methods=["GET"])
def get_latest():
    doc = collection.find_one({}, {"_id": 0}, sort=[("timestamp", -1)])

    if not doc:
        return jsonify({"message": "No data available"})

    return jsonify(doc)

# ----------------------------
# Run App (Render Compatible)
# ----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
