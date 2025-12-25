from flask import Flask, request, jsonify
from pymongo import MongoClient
import joblib
import os
from datetime import datetime
import numpy as np

app = Flask(__name__)

# ------------------ CONFIG ------------------

MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://Bharat5741:Puli@3125@water-quality-cluster.d5ddvpd.mongodb.net/?retryWrites=true&w=majority"
)

DB_NAME = "water_quality_db"
COLLECTION_NAME = "sensor_data"

# Load ML model
model = joblib.load("model.pkl")

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# ------------------ ROUTES ------------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Smart Water Quality Monitoring API is running"
    })

@app.route("/api/data", methods=["POST"])
def receive_data():
    try:
        data = request.json

        ph = float(data["ph"])
        turbidity = float(data["turbidity"])
        temperature = float(data["temperature"])

        # ML Prediction
        features = np.array([[ph, turbidity, temperature]])
        prediction = model.predict(features)[0]
        status = "Safe" if prediction == 1 else "Unsafe"

        record = {
            "ph": ph,
            "turbidity": turbidity,
            "temperature": temperature,
            "prediction": status,
            "timestamp": datetime.utcnow()
        }

        collection.insert_one(record)

        return jsonify({
            "message": "Data stored successfully",
            "prediction": status
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route("/api/latest", methods=["GET"])
def latest_data():
    try:
        doc = collection.find_one(
            {},
            {"_id": 0},
            sort=[("timestamp", -1)]
        )

        if doc:
            return jsonify(doc)
        else:
            return jsonify({"message": "No data available"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------ RUN ------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
