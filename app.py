from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

# Simple in-memory "database"
messages = []
users = []

# Serve HTML
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# API endpoints
@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify({"messages": messages})

@app.route('/messages', methods=['POST'])
def post_message():
    data = request.get_json()
    if not data.get('message') or not data.get('username'):
        return jsonify({"error": "Message and username required"}), 400
    messages.append({
        "id": data.get('id', int(time.time()*1000)),
        "username": data['username'],
        "title": data.get('title', 'No Subject'),
        "message": data['message'],
        "timestamp": data.get('timestamp', time.strftime("%Y-%m-%dT%H:%M:%S")),
        "replyTo": data.get('replyTo')
    })
    return jsonify({"success": True}), 200

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({"error": "All fields required"}), 400
    users.append({
        "username": data['username'],
        "password": data['password'],  # plain for now, sha256 optional
        "email": data['email'],
        "joinDate": data.get('joinDate', time.strftime("%Y-%m-%dT%H:%M:%S"))
    })
    return jsonify({"success": True, "username": data['username'], "email": data['email']}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = next((u for u in users if u['username']==data.get('username') and u['password']==data.get('password')), None)
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401
    return jsonify({"success": True, "username": user['username'], "email": user['email']}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
