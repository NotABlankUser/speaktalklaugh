from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import hashlib
import datetime

app = Flask(__name__)
CORS(app)
limiter = Limiter(key_func=get_remote_address)  # don't pass app here
limiter.init_app(app)  # <-- attach limiter to the app


# In-memory DB
users = {}
messages = []

# Admin
admin_username = "admin"
admin_password = "admin123123"
users[admin_username] = {
    "username": admin_username,
    "password": hashlib.sha256(admin_password.encode()).hexdigest(),
    "email": "admin@forum.com",
    "is_admin": True,
    "joinDate": str(datetime.datetime.utcnow())
}

# --- API ---
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "")
    email = data.get("email", "").strip()
    if not username or not password or not email:
        return jsonify({"error": "All fields required"}), 400
    if username in users:
        return jsonify({"error": "Username exists"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password too short"}), 400
    users[username] = {
        "username": username,
        "password": hashlib.sha256(password.encode()).hexdigest(),
        "email": email,
        "is_admin": False,
        "joinDate": str(datetime.datetime.utcnow())
    }
    return jsonify({"message": "User created"}), 200

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "")
    user = users.get(username)
    if not user or user["password"] != hashlib.sha256(password.encode()).hexdigest():
        return jsonify({"error": "Invalid username or password"}), 401
    return jsonify({"username": user["username"], "email": user["email"], "is_admin": user["is_admin"]})

@app.route("/messages", methods=["GET"])
def get_messages():
    return jsonify({"messages": messages})

@app.route("/messages", methods=["POST"])
def post_message():
    data = request.json
    username = data.get("username")
    message_text = data.get("message", "").strip()
    title = data.get("title", "No Subject")
    reply_to = data.get("replyTo", None)
    if not username or not message_text:
        return jsonify({"error": "Username and message required"}), 400
    message = {
        "id": len(messages) + 1,
        "username": username,
        "title": title,
        "message": message_text,
        "timestamp": str(datetime.datetime.utcnow()),
        "replyTo": reply_to
    }
    messages.append(message)
    return jsonify({"message": "Message posted"}), 200

@app.route("/messages/<int:msg_id>", methods=["DELETE"])
def delete_message(msg_id):
    username = request.args.get("username")
    user = users.get(username)
    if not user or not user.get("is_admin"):
        return jsonify({"error": "Unauthorized"}), 403
    global messages
    messages = [m for m in messages if m["id"] != msg_id]
    return jsonify({"message": "Message deleted"}), 200

# --- Serve retro HTML ---
@app.route("/")
def index():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>★ AWESOME FORUM 2008 ★</title>
<style>
body { font-family: Verdana, sans-serif; font-size: 12px; background:#E8E8E8; }
.header { background: #4A90E2; color:white; padding: 10px; text-align:center; }
.box { background:white; padding:10px; border:1px solid #999; margin:10px auto; width:90%; }
input, textarea { width:100%; padding:5px; font-size:12px; }
button { padding:5px 10px; background:#4A90E2; color:white; border:none; cursor:pointer; }
.thread { border-bottom:1px solid #ccc; padding:5px; }
.reply { margin-left:20px; border-left:2px solid #4A90E2; padding-left:5px; }
</style>
</head>
<body>
<div class="header">
  <h1>★ AWESOME FORUM 2008 ★</h1>
  <div id="login-section">Please login or register</div>
</div>

<div class="box" id="auth-box">
  <input type="text" id="username" placeholder="Username">
  <input type="email" id="email" placeholder="Email (register only)">
  <input type="password" id="password" placeholder="Password">
  <button onclick="handleLogin()">Login / Register</button>
  <div id="auth-error" style="color:red;"></div>
</div>

<div class="box" id="forum-box" style="display:none;">
  <h3>Post a message</h3>
  <input type="text" id="title" placeholder="Title">
  <textarea id="message" placeholder="Message"></textarea>
  <button onclick="postMessage()">Post</button>
  <div id="forum-error" style="color:red;"></div>
  <h3>Messages</h3>
  <div id="threads"></div>
</div>

<script>
let currentUser = null;

async function handleLogin(){
  const username = document.getElementById('username').value;
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  let res;
  if(email){
    res = await fetch('/register', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username,password,email})});
  } else {
    res = await fetch('/login', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username,password})});
  }
  const data = await res.json();
  if(res.ok){
    currentUser = {username:data.username};
    document.getElementById('auth-box').style.display='none';
    document.getElementById('forum-box').style.display='block';
    loadMessages();
  } else {
    document.getElementById('auth-error').innerText = data.error;
  }
}

async function loadMessages(){
  const res = await fetch('/messages');
  const data = await res.json();
  const container = document.getElementById('threads');
  container.innerHTML = '';
  data.messages.forEach(msg=>{
    const div = document.createElement('div');
    div.className='thread';
    div.innerHTML = '<b>'+msg.title+'</b> by '+msg.username+'<br>'+msg.message;
    container.appendChild(div);
  });
}

async function postMessage(){
  const title = document.getElementById('title').value;
  const message = document.getElementById('message').value;
  const res = await fetch('/messages', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username:currentUser.username,title,message})});
  const data = await res.json();
  if(res.ok){
    document.getElementById('title').value='';
    document.getElementById('message').value='';
    loadMessages();
  } else {
    document.getElementById('forum-error').innerText=data.error;
  }
}
</script>
</body>
</html>
""")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
