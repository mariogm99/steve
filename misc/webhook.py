from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    event_type = data.get("event")  # Extract event type
    print(f"Received {event_type} event:", data)

    # Process the event (store in database, trigger actions, etc.)
    
    return jsonify({"status": "received"}), 200


if __name__ == "__main__":
    app.run(port=5000)
