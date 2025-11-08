from flask import Flask, request, jsonify, render_template_string
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import hashlib
from datetime import datetime

app = Flask(__name__)
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)

# --- Users ---
users = {
    "admin": {
        "userid": 1,
        "password": hashlib.sha256("admin123123".encode()).hexdigest(),
        "is_admin": True,
        "joined": datetime.now().strftime("%Y-%m-%d"),
        "banned": False,
        "online": False
    }
}
next_userid = 2

# --- Messages storage ---
messages = []

# --- Routes ---
@app.route("/")
def index():
    html = """
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
            .profile { border:1px solid #999; background:#f0f0f0; padding:8px; position:absolute; display:none; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>★ AWESOME FORUM 2008 ★</h1>
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
            let currentUser = null;
            let currentUserId = null;
            let isAdmin = false;
            let replyTo = null;

            // --- Check localStorage on load ---
            window.onload = () => {
                const savedUser = localStorage.getItem('currentUser');
                const savedId = localStorage.getItem('currentUserId');
                const savedAdmin = localStorage.getItem('isAdmin');
                if(savedUser && savedId){
                    currentUser = savedUser;
                    currentUserId = savedId;
                    isAdmin = savedAdmin === 'true';
                    document.getElementById('authBox').style.display='none';
                    document.getElementById('forumBox').style.display='block';
                    loadMessages();
                }
            };

            async function login() {
                const u = document.getElementById('username').value.trim();
                const p = document.getElementById('password').value;
                const res = await fetch('/login', {
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body:JSON.stringify({username:u,password:p})
                });
                const data = await res.json();
                if(data.success) {
                    currentUser = data.username;
                    currentUserId = data.userid;
                    isAdmin = data.is_admin;
                    localStorage.setItem('currentUser', currentUser);
                    localStorage.setItem('currentUserId', currentUserId);
                    localStorage.setItem('isAdmin', isAdmin);
                    document.getElementById('authBox').style.display='none';
                    document.getElementById('forumBox').style.display='block';
                    loadMessages();
                } else alert(data.error);
            }

            async function registerUser() {
                const u = document.getElementById('username').value.trim();
                const p = document.getElementById('password').value;
                if(!u || !p) return alert("Username and password required");
                const res = await fetch('/register',{
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body:JSON.stringify({username:u,password:p})
                });
                const data = await res.json();
                if(data.success){
                    alert("Registration successful! You can login now.");
                    showLogin();
                } else alert(data.error);
            }

            function showRegister(){
                document.getElementById('authHeader').innerText='Register';
                const btns = document.querySelectorAll('#authBox button');
                btns[0].innerText='Register';
                btns[0].onclick=registerUser;
                btns[1].innerText='Back to Login';
                btns[1].onclick=showLogin;
            }

            function showLogin(){
                document.getElementById('authHeader').innerText='Login';
                const btns = document.querySelectorAll('#authBox button');
                btns[0].innerText='Login';
                btns[0].onclick=login;
                btns[1].innerText='Register';
                btns[1].onclick=showRegister;
            }

            async function postMessage() {
                const m = document.getElementById('msg').value;
                const t = document.getElementById('title').value;
                if(!m) return alert("Message required");
                await fetch('/messages',{
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body:JSON.stringify({
                        username:currentUser,
                        userid: currentUserId,
                        title:t,
                        message:m,
                        replyTo: replyTo ? replyTo.id : null
                    })
                });
                document.getElementById('msg').value='';
                document.getElementById('title').value='';
                replyTo = null;
                document.getElementById('replyInfo').style.display='none';
                loadMessages();
            }

            function cancelReply() {
                replyTo = null;
                document.getElementById('replyInfo').style.display='none';
            }

            async function loadMessages() {
                const res = await fetch('/messages');
                const data = await res.json();
                const container = document.getElementById('messagesBox');
                container.innerHTML='';
                data.messages.filter(m=>!m.replyTo).forEach(m=>{
                    let html = `<div class="box message">
                        <strong>${m.title}</strong> by <span onclick="showProfile('${m.username}', event)" style="cursor:pointer; text-decoration:underline;">${m.username}</span> (ID: ${m.userid})${m.is_admin?' <span class="admin">[ADMIN]</span>':''}<br>${m.message}<br>`;
                    if(isAdmin) html += `<button onclick="deleteMessage(${m.id})">Delete</button> <button onclick="banUser('${m.username}')">Ban User</button>`;
                    html += ` <button onclick='startReply(${m.id},"${m.title.replace(/"/g,'&quot;')}")'>Reply</button>`;
                    html += `</div>`;
                    container.innerHTML += html;

                    data.messages.filter(r=>r.replyTo===m.id).forEach(r=>{
                        container.innerHTML += `<div class="box reply">${r.username} (ID: ${r.userid})${r.is_admin?' <span class="admin">[ADMIN]</span>':''}: ${r.message}</div>`;
                    });
                });
            }

            async function deleteMessage(id){
                await fetch(`/delete_message/${id}`,{method:'POST'});
                loadMessages();
            }

            async function banUser(username){
                await fetch(`/ban_user/${username}`,{method:'POST'});
                loadMessages();
            }

            function startReply(id,title){
                replyTo = {id:id,title:title};
                document.getElementById('replyInfo').style.display='block';
                document.getElementById('replyToTitle').innerText = title;
            }

            function logout(){
                currentUser=null;
                currentUserId=null;
                isAdmin=false;
                localStorage.removeItem('currentUser');
                localStorage.removeItem('currentUserId');
                localStorage.removeItem('isAdmin');
                document.getElementById('authBox').style.display='block';
                document.getElementById('forumBox').style.display='none';
            }

            async function showProfile(username, event){
                const res = await fetch(`/profile/${username}`);
                const data = await res.json();
                const box = document.getElementById('profileBox');
                box.style.display='block';
                box.style.left=event.pageX+'px';
                box.style.top=event.pageY+'px';
                box.innerHTML = `<strong>${data.username}</strong>${data.is_admin?' <span class="admin">[ADMIN]</span>':''}<br>
                                 Joined: ${data.joined}<br>
                                 Status: ${data.online ? 'Online':'Offline'}<br>
                                 UserID: ${data.userid}`;
                setTimeout(()=>{ box.style.display='none'; }, 5000);
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route("/register", methods=["POST"])
def register():
    global next_userid
    data = request.get_json()
    u = data.get("username","").strip()
    p = data.get("password","")
    if not u or not p:
        return jsonify(success=False,error="Username and password required")
    if u in users:
        return jsonify(success=False,error="Username already exists")
    users[u] = {
        "userid": next_userid,
        "password": hashlib.sha256(p.encode()).hexdigest(),
        "is_admin": False,
        "joined": datetime.now().strftime("%Y-%m-%d"),
        "banned": False,
        "online": False
    }
    next_userid += 1
    return jsonify(success=True)

@app.route("/login", methods=["POST"])
def login_route():
    data = request.get_json()
    u = data.get("username","").strip()
    p = data.get("password","")
    user = users.get(u)
    if user and not user["banned"] and hashlib.sha256(p.encode()).hexdigest() == user["password"]:
        user["online"] = True
        return jsonify(success=True, username=u, is_admin=user["is_admin"], userid=user["userid"])
    return jsonify(success=False, error="Invalid credentials or banned user")

@app.route("/messages", methods=["GET","POST"])
def msgs():
    if request.method=="POST":
        data = request.get_json()
        if users.get(data.get("username"),{}).get("banned"): 
            return jsonify(success=False,error="You are banned")
        new_msg = {
            "id": len(messages)+1,
            "username": data.get("username"),
            "userid": data.get("userid"),
            "title": data.get("title") or "No Subject",
            "message": data.get("message"),
            "replyTo": data.get("replyTo"),
            "is_admin": users.get(data.get("username"),{}).get("is_admin",False)
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        messages.append(new_msg)
        return jsonify(success=True)
    return jsonify(messages=messages)

@app.route("/delete_message/<int:id>", methods=["POST"])
def delete_message(id):
    messages[:] = [m for m in messages if m["id"] != id]
    return jsonify(success=True)

@app.route("/ban_user/<username>", methods=["POST"])
def ban_user(username):
    if username in users:
        users[username]["banned"] = True
    return jsonify(success=True)

@app.route("/profile/<username>")
def profile(username):
    user = users.get(username)
    if not user:
        return jsonify(success=False,error="User not found")
    return jsonify(username=username, is_admin=user["is_admin"], joined=user["joined"], online=user["online"], userid=user["userid"])

if __name__=="__main__":
    app.run(debug=True)
