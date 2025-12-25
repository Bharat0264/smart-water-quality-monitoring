from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import joblib
import numpy as np

app = Flask(__name__)

# =========================
# MongoDB (LOCAL)
# =========================
client = MongoClient("mongodb://localhost:27017/")
db = client["water_quality_db"]
collection = db["readings"]

# =========================
# Load ML Model
# =========================
model = joblib.load("model.pkl")

# =========================
# HOME ROUTE
# =========================
@app.route("/")
def home():
    return "Smart Water Quality Monitoring API is running"

# =========================
# POST SENSOR DATA
# =========================
@app.route("/api/data", methods=["POST"])
def receive_data():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    ph = data.get("ph")
    turbidity = data.get("turbidity")
    temperature = data.get("temperature")

    if ph is None or turbidity is None or temperature is None:
        return jsonify({"error": "Missing parameters"}), 400

    # ML Prediction
    features = np.array([[ph, turbidity, temperature]])
    prediction = model.predict(features)[0]
    result = "Safe" if prediction == 1 else "Unsafe"

    record = {
        "ph": ph,
        "turbidity": turbidity,
        "temperature": temperature,
        "prediction": result,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    collection.insert_one(record)

    return jsonify({
        "message": "Data stored successfully",
        "prediction": result
    })

# =========================
# GET LATEST READING
# =========================
@app.route("/api/latest", methods=["GET"])
def get_latest():
    doc = collection.find_one(sort=[("_id", -1)], projection={"_id": 0})

    if not doc:
        return jsonify({"error": "No data found"}), 404

    return jsonify(doc)

# =========================
# GET HISTORY (FOR GRAPHS)
# =========================
@app.route("/api/history", methods=["GET"])
def get_history():
    docs = list(
        collection.find({}, {"_id": 0}).sort("_id", -1).limit(50)
    )
    return jsonify(docs[::-1])

# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
