from flask import Flask, request, jsonify, render_template_string
from tinydb import TinyDB, Query
from datetime import datetime, timedelta
import hashlib

app = Flask(__name__)
db = TinyDB("db.json")
users_table = db.table("users")
messages_table = db.table("messages")

# --- Ensure admin account exists ---
admin_user = users_table.get(Query().username == "admin")
if not admin_user:
    users_table.insert({
        "user_id": 1,
        "username": "admin",
        "password": hashlib.sha256("Administrator555".encode()).hexdigest(),
        "is_admin": True,
        "is_moderator": False,
        "joined": datetime.now().strftime("%Y-%m-%d"),
        "banned_until": None,
        "terminated": False,
        "badges": ["Administrator"],
        "online": False
    })

# --- Helpers ---
def get_next_user_id():
    users = users_table.all()
    if not users: return 1
    return max(u["user_id"] for u in users) + 1

def get_next_message_id():
    msgs = messages_table.all()
    if not msgs: return 1
    return max(m["id"] for m in msgs) + 1

def get_user(username):
    return users_table.get(Query().username == username)

# --- Routes ---
@app.route("/")
def index():
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Retro Forum 2008</title>
    <style>
        body { font-family: Verdana,sans-serif; font-size:11px; background:#E8E8E8; margin:0; }
        .header { background:linear-gradient(to bottom,#4A90E2,#2E5C8A); padding:15px; color:white; text-align:center; border-bottom:3px solid #1A3A5A; }
        .container { max-width:900px; margin:20px auto; }
        .box { background:#fff; border:1px solid #ccc; margin-bottom:20px; }
        .box-header { background:linear-gradient(to bottom,#F0F0F0,#D8D8D8); padding:8px 12px; font-weight:bold; border-bottom:1px solid #999; }
        .box-body { padding:10px; }
        input, textarea { width:100%; padding:4px; margin:2px 0; font-size:11px; }
        button { padding:4px 8px; font-size:11px; background:#4A90E2; color:white; border:1px solid #2E5C8A; cursor:pointer; }
        .message { border-bottom:1px solid #E0E0E0; padding:8px; }
        .reply { margin-left:30px; border-left:3px solid #4A90E2; padding-left:8px; background:#FAFAFA; }
        .admin { color:red; font-weight:bold; }
        .moderator { color:green; font-weight:bold; }
        .badge { font-size:10px; margin-left:3px; padding:2px 4px; background:#EEE; border-radius:3px; }
        .profile { border:1px solid #999; background:#f0f0f0; padding:8px; position:absolute; display:none; }
    </style>
</head>
<body>
<div class="header">
    <h1>★ Admin's forum ★</h1>
</div>
<div class="container">
    <div id="authBox" class="box">
        <div class="box-header" id="authHeader">Login</div>
        <div class="box-body">
            Username:<br><input id="username"><br>
            Password:<br><input type="password" id="password"><br>
            <button onclick="login()">Login</button>
            <button onclick="showRegister()">Register</button>
        </div>
    </div>

    <div id="forumBox" style="display:none;">
        <div class="box">
            <div class="box-header">New Message</div>
            <div class="box-body">
                <div id="replyInfo" style="display:none;">Replying to: <span id="replyToTitle"></span> <button onclick="cancelReply()">Cancel</button></div>
                Subject:<br><input id="title"><br>
                Message:<br><textarea id="msg"></textarea><br>
                <button onclick="postMessage()">Post</button>
                <button onclick="logout()">Logout</button>
            </div>
        </div>
        <div id="messagesBox"></div>
    </div>
</div>

<div id="profileBox" class="profile"></div>

<script>
let currentUser = localStorage.getItem("username") || null;
let isAdmin = localStorage.getItem("is_admin") === "true";
let replyTo = null;

window.onload = () => { if(currentUser) { document.getElementById('authBox').style.display='none'; document.getElementById('forumBox').style.display='block'; loadMessages(); } }

async function login(){
    const u = document.getElementById('username').value.trim();
    const p = document.getElementById('password').value;
    const res = await fetch('/login', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({username:u,password:p})
    });
    const data = await res.json();
    if(data.success){
        currentUser = data.username;
        isAdmin = data.is_admin;
        localStorage.setItem("username",currentUser);
        localStorage.setItem("is_admin",isAdmin);
        document.getElementById('authBox').style.display='none';
        document.getElementById('forumBox').style.display='block';
        loadMessages();
    } else alert(data.error);
}

async function registerUser(){
    const u = document.getElementById('username').value.trim();
    const p = document.getElementById('password').value;
    if(!u||!p) return alert("Username/password required");
    const res = await fetch('/register',{
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({username:u,password:p})
    });
    const data = await res.json();
    if(data.success) { alert("Registered! Login now."); showLogin(); }
    else alert(data.error);
}

function showRegister(){
    document.getElementById('authHeader').innerText='Register';
    const btns = document.querySelectorAll('#authBox button');
    btns[0].innerText='Register'; btns[0].onclick=registerUser;
    btns[1].innerText='Back to Login'; btns[1].onclick=showLogin;
}
function showLogin(){
    document.getElementById('authHeader').innerText='Login';
    const btns = document.querySelectorAll('#authBox button');
    btns[0].innerText='Login'; btns[0].onclick=login;
    btns[1].innerText='Register'; btns[1].onclick=showRegister;
}

async function postMessage(){
    const t=document.getElementById('title').value;
    const m=document.getElementById('msg').value;
    if(!m) return alert("Message required");
    await fetch('/messages',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({username:currentUser,title:t,message:m,replyTo:replyTo?replyTo.id:null})
    });
    document.getElementById('msg').value=''; document.getElementById('title').value=''; replyTo=null; document.getElementById('replyInfo').style.display='none';
    loadMessages();
}

function cancelReply(){ replyTo=null; document.getElementById('replyInfo').style.display='none'; }
function logout(){ localStorage.removeItem("username"); localStorage.removeItem("is_admin"); currentUser=null; isAdmin=false; document.getElementById('authBox').style.display='block'; document.getElementById('forumBox').style.display='none'; }

async function loadMessages(){
    const res=await fetch('/messages'); const data=await res.json();
    const container=document.getElementById('messagesBox'); container.innerHTML='';
    data.messages.filter(m=>!m.replyTo).forEach(m=>{
        let badgeHtml = '';
        if(m.badges) badgeHtml = m.badges.map(b=>`<span class="badge">${b}</span>`).join(' ');
        let role = m.is_admin?' <span class="admin">[ADMIN]</span>':(m.is_moderator?' <span class="moderator">[MOD]</span>':'');
        let html = `<div class="box message">
            <strong>${m.title}</strong> by <span onclick="showProfile('${m.username}', event)" style="cursor:pointer;text-decoration:underline;">${m.username}</span> (ID: ${m.user_id})${role} ${badgeHtml}<br>
            ${m.message}<br>
            <small>${m.timestamp}</small><br>`;
        if(isAdmin){
            html += `<button onclick="deleteMessage(${m.id})">Delete</button>
                     <button onclick="banUser('${m.username}')">Ban User</button>
                     <button onclick="terminateUser('${m.username}')">Terminate</button>
                     <button onclick="promoteUser('${m.username}')">Promote to Mod</button>`;
        }
        html += ` <button onclick='startReply(${m.id},"${m.title.replace(/"/g,'&quot;')}")'>Reply</button>`;
        html += `</div>`;
        container.innerHTML+=html;

        data.messages.filter(r=>r.replyTo===m.id).forEach(r=>{
            let replyRole = r.is_admin?' <span class="admin">[ADMIN]</span>':(r.is_moderator?' <span class="moderator">[MOD]</span>':'');
            container.innerHTML += `<div class="box reply">${r.username} (ID: ${r.user_id})${replyRole}: ${r.message}<br><small>${r.timestamp}</small></div>`;
        });
    });
}

function startReply(id,title){ replyTo={id:id,title:title}; document.getElementById('replyInfo').style.display='block'; document.getElementById('replyToTitle').innerText=title; }

async function deleteMessage(id){ await fetch(`/delete_message/${id}`,{method:'POST'}); loadMessages(); }
async function banUser(username){ await fetch(`/ban_user/${username}`,{method:'POST'}); loadMessages(); }
async function terminateUser(username){ await fetch(`/terminate_user/${username}`,{method:'POST'}); loadMessages(); }
async function promoteUser(username){ await fetch(`/promote_user/${username}`,{method:'POST'}); loadMessages(); }

async function showProfile(username,event){
    const res=await fetch(`/profile/${username}`); const data=await res.json();
    const box=document.getElementById('profileBox'); box.style.display='block'; box.style.left=event.pageX+'px'; box.style.top=event.pageY+'px';
    box.innerHTML = `<strong>${data.username}</strong>${data.is_admin?' <span class="admin">[ADMIN]</span>':''}${data.is_moderator?' <span class="moderator">[MOD]</span>':''}<br>
                     Joined: ${data.joined}<br>
                     Status: ${data.online?'Online':'Offline'}<br>
                     Badges: ${(data.badges||[]).join(", ")}`;
    setTimeout(()=>{box.style.display='none';},5000);
}
</script>
</body>
</html>"""
    return render_template_string(html)

# --- API Routes ---
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    u = data.get("username","").strip()
    p = data.get("password","")
    if not u or not p: return jsonify(success=False,error="Username/password required")
    if get_user(u): return jsonify(success=False,error="Username exists")
    users_table.insert({
        "user_id": get_next_user_id(),
        "username": u,
        "password": hashlib.sha256(p.encode()).hexdigest(),
        "is_admin": False,
        "is_moderator": False,
        "joined": datetime.now().strftime("%Y-%m-%d"),
        "banned_until": None,
        "terminated": False,
        "badges": [],
        "online": False
    })
    return jsonify(success=True)

@app.route("/login", methods=["POST"])
def login_route():
    data = request.get_json()
    u = data.get("username","").strip()
    p = data.get("password","")
    user = get_user(u)
    if user:
        banned = user["banned_until"] and datetime.now() < datetime.fromisoformat(user["banned_until"])
        if not user["terminated"] and not banned and hashlib.sha256(p.encode()).hexdigest() == user["password"]:
            users_table.update({"online": True}, Query().username == u)
            return jsonify(success=True, username=u, is_admin=user["is_admin"])
    return jsonify(success=False, error="Invalid credentials / banned / terminated")

@app.route("/messages", methods=["GET","POST"])
def msgs():
    if request.method=="POST":
        data = request.get_json()
        user = get_user(data.get("username"))
        if not user: return jsonify(success=False,error="User not found")
        banned = user["banned_until"] and datetime.now() < datetime.fromisoformat(user["banned_until"])
        if user["terminated"] or banned:
            return jsonify(success=False,error="Cannot post")
        messages_table.insert({
            "id": get_next_message_id(),
            "user_id": user["user_id"],
            "username": user["username"],
            "title": data.get("title") or "No Subject",
            "message": data.get("message"),
            "reply_to": data.get("replyTo"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        return jsonify(success=True)

    messages = messages_table.all()
    result = []
    for m in messages:
        user = users_table.get(Query().user_id == m["user_id"])
        result.append({
            "id": m["id"],
            "user_id": m["user_id"],
            "username": m["username"],
            "title": m["title"],
            "message": m["message"],
            "replyTo": m.get("reply_to"),
            "timestamp": m["timestamp"],
            "badges": user["badges"] if user else [],
            "is_admin": user["is_admin"] if user else False,
            "is_moderator": user["is_moderator"] if user else False
        })
    return jsonify(messages=result)

@app.route("/delete_message/<int:id>", methods=["POST"])
def delete_message(id):
    messages_table.remove(Query().id == id)
    return jsonify(success=True)

@app.route("/ban_user/<username>", methods=["POST"])
def ban_user(username):
    user = get_user(username)
    if user:
        users_table.update({"banned_until": (datetime.now() + timedelta(days=7)).isoformat()}, Query().username == username)
    return jsonify(success=True)

@app.route("/terminate_user/<username>", methods=["POST"])
def terminate_user(username):
    user = get_user(username)
    if user:
        users_table.update({"terminated": True}, Query().username == username)
    return jsonify(success=True)

@app.route("/promote_user/<username>", methods=["POST"])
def promote_user(username):
    user = get_user(username)
    if user and not user["is_admin"]:
        users_table.update({"is_moderator": True}, Query().username == username)
    return jsonify(success=True)

@app.route("/profile/<username>")
def profile(username):
    user = get_user(username)
    if not user: return jsonify(success=False,error="User not found")
    return jsonify(
        username=user["username"],
        is_admin=user["is_admin"],
        is_moderator=user["is_moderator"],
        joined=user["joined"],
        online=user["online"],
        badges=user["badges"]
    )

if __name__=="__main__":
    app.run(debug=True)
