from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
import certifi
import os
import requests

START_VID = PING_MP4 = [
    "https://telegra.ph/file/5ce0259747cdd75db040f.mp4",
    "https://telegra.ph/file/925d833773c3f75500255.mp4",
    "https://telegra.ph/file/3c1ca2ea64323e00426c2.mp4",
    "https://telegra.ph/file/436f9cacca9b37538dda3.mp4"

]


ALIVE_ANIMATION =  ["https://telegra.ph/file/5ce0259747cdd75db040f.mp4",
                    "https://telegra.ph/file/925d833773c3f75500255.mp4",
                    "https://telegra.ph/file/3c1ca2ea64323e00426c2.mp4",
                    "https://telegra.ph/file/436f9cacca9b37538dda3.mp4",]



app = Flask(__name__)
CORS(app)

# MongoDB connection
MONGO_URI = "mongodb+srv://Portfolio_Raxx:Portfolio_Raxx@cluster0.yp55tz8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())

# Database and Collections
db = client["PortfolioDB"]
contacts_collection = db["Contacts"]
visitor_collection = db["VisitorCounter"]

# Telegram bot setup
TELEGRAM_BOT_TOKEN = "6575470408:AAHvCcuNoWC0aWfy50bJxJjlwDlCJ2ZjfA0"
TELEGRAM_CHAT_ID = -1001997761568
TELEGRAM_VIDEO_URL = "https://telegra.ph/file/66f724ba5e211016e7024.mp4"






def send_telegram_video(caption):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "video": TELEGRAM_VIDEO_URL,
            "caption": caption
        }
        requests.post(url, data=payload)
    except Exception as e:
        print("Error sending Telegram video:", e)


@app.route('/')
def index():
    try:
        # Increment visitor count
        visitor_collection.update_one({}, {"$inc": {"count": 1}})

        # Get updated count
        visitor_data = visitor_collection.find_one()
        visitor_count = visitor_data.get("count", 0)

        # Send video with visitor count caption
        caption = f"👀 New Visitor!\nTotal Visitors: {visitor_count}"
        send_telegram_video(caption)

        return render_template('index.html', visitor_count=visitor_count)
    except Exception as e:
        print("Error updating visitor count:", e)
        return render_template('index.html', visitor_count="Error")


@app.route('/api/visitor-count', methods=['GET'])
def api_visitor_count():
    try:
        updated = visitor_collection.find_one_and_update(
            {},
            {"$inc": {"count": 0}},
            return_document=True
        )
        return jsonify({"count": updated.get("count", 0)})
    except Exception as e:
        print("Error in visitor count API:", e)
        return jsonify({"count": "Error"}), 500


@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json()

    if not data:
        return jsonify({"message": "No data received"}), 400

    contact_data = {
        "firstName": data.get("firstName"),
        "lastName": data.get("lastName"),
        "mobileNumber": data.get("mobileNumber"),
        "email": data.get("email"),
        "message": data.get("message")
    }

    try:
        result = contacts_collection.insert_one(contact_data)
        print("Inserted ID:", result.inserted_id)

        # Prepare video caption with contact info
        caption = (
            "📬 New Contact Form Submission:\n"
            f"👤 Name: {contact_data['firstName']} {contact_data['lastName']}\n"
            f"📞 Mobile: {contact_data['mobileNumber']}\n"
            f"📧 Email: {contact_data['email']}\n"
            f"📝 Message: {contact_data['message']}"
        )
        send_telegram_video(caption)

        return jsonify({"message": "Success"}), 200
    except Exception as e:
        print("MongoDB Insertion Error:", e)
        return jsonify({"message": "Failed to save data"}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
