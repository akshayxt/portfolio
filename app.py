from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
import certifi

import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Backend is live!"



# MongoDB connection
MONGO_URI = "mongodb+srv://Portfolio_Raxx:Portfolio_Raxx@cluster0.yp55tz8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())

try:
    mongo_uri = os.environ.get("MONGO_URI")
    client = MongoClient(mongo_uri)
    db = client["portfolio_db"]
    print("MongoDB connected successfully!")
except Exception as e:
    print("MongoDB connection error:", e)

# Select the database and collection
db = client["PortfolioDB"]  # You can name this anything
collection = db["Contacts"]

@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "No data received"}), 400

    # Extract fields
    contact_data = {
        "firstName": data.get("firstName"),
        "lastName": data.get("lastName"),
        "mobileNumber": data.get("mobileNumber"),
        "email": data.get("email"),
        "message": data.get("message")
    }

    try:
        # Insert into MongoDB
        result = collection.insert_one(contact_data)
        print("Inserted ID:", result.inserted_id)
        return jsonify({"message": "Success"}), 200
    except Exception as e:
        print("MongoDB Insertion Error:", e)
        return jsonify({"message": "Failed to save data"}), 500

# Serve the HTML page
@app.route('/')
def index():
    return render_template('index.html')  # templates/index.html must exist


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
