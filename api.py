from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import joblib
import os

app = Flask(__name__)

# =========================
# MongoDB Atlas connection
# =========================
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://Bharat5741:Puli@3125@water-quality-cluster.d5ddvpd.mongodb.net/water_quality?retryWrites=true&w=majority"
)

client = MongoClient(MONGO_URI)
db = client["water_quality"]
collection = db["sensor_data"]

# =========================
# Load ML model
# =========================
model = joblib.load("model.pkl")

# =========================
# Routes
# =========================
@app.route("/")
def home():
    return "Smart Water Quality Monitoring API is running"

@app.route("/api/data", methods=["POST"])
def receive_data():
    data = request.get_json()

    ph = data.get("ph")
    turbidity = data.get("turbidity")
    temperature = data.get("temperature")

    prediction = model.predict([[ph, turbidity, temperature]])[0]

    record = {
        "ph": ph,
        "turbidity": turbidity,
        "temperature": temperature,
        "prediction": "Safe" if prediction == 1 else "Unsafe",
        "timestamp": datetime.utcnow()
    }

    collection.insert_one(record)

    return jsonify({
        "message": "Data stored successfully",
        "prediction": record["prediction"]
    })

@app.route("/api/latest", methods=["GET"])
def latest_data():
    doc = collection.find_one({}, {"_id": 0}, sort=[("timestamp", -1)])
    return jsonify(doc if doc else {})

# =========================
# Run server
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
