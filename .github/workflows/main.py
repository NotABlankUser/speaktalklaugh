from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time

app = Flask(__name__)
CORS(app)

limiter = Limiter(app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

# In-memory "DB"
USERS = {}      # username -> {password, email, last_post_time}
MESSAGES = []   # list of {id, username, title, message, replyTo, timestamp}
MSG_ID = 0

@app.route('/register', methods=['POST'])
@limiter.limit("10 per hour")
def register():
    data = request.json or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '')
    email = (data.get('email') or '').strip()

    if not username or not password:
        return jsonify({'error':'username/password required'}),400
    if username in USERS:
        return jsonify({'error':'username exists'}),400
    USERS[username] = {'password': password, 'email': email, 'last_post_time':0}
    return jsonify({'success':True, 'username':username})

@app.route('/login', methods=['POST'])
@limiter.limit("30 per hour")
def login():
    data = request.json or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '')
    user = USERS.get(username)
    if not user or user['password'] != password:
        return jsonify({'error':'invalid credentials'}),400
    return jsonify({'username':username, 'email':user['email']})

@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify({'messages':MESSAGES})

@app.route('/messages', methods=['POST'])
def post_message():
    global MSG_ID
    data = request.json or {}
    username = (data.get('username') or '').strip()
    message = (data.get('message') or '')[:1000]
    title = (data.get('title') or 'No Subject')[:200]
    replyTo = data.get('replyTo')
    user = USERS.get(username)
    if not user:
        return jsonify({'error':'unknown user'}),400
    now = time.time()
    if now - user['last_post_time'] < 10:  # 10 sec cooldown
        return jsonify({'error':'please wait before posting again'}),429
    MSG_ID += 1
    MESSAGES.append({'id':MSG_ID,'username':username,'title':title,'message':message,'replyTo':replyTo,'timestamp':int(now)})
    user['last_post_time'] = now
    return jsonify({'success':True})

if __name__ == '__main__':
    # For Render, use gunicorn app:app
    app.run(host='0.0.0.0', port=10000)
