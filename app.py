from flask import Flask, request, jsonify, render_template_string
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import hashlib
from datetime import datetime, timedelta

app = Flask(__name__)
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)

# --- Users ---
users = {
    "admin": {
        "password": hashlib.sha256("Administrator555".encode()).hexdigest(),
        "is_admin": True,
        "is_moderator": False,
        "joined": datetime.now().strftime("%Y-%m-%d"),
        "banned_until": None,
        "terminated": False,
        "online": False,
        "badges": ["Administrator"]
    }
}

# --- Messages ---
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
            .moderator { color:green; font-weight:bold; }
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
            let currentUser = localStorage.getItem('currentUser') || null;
            let isAdmin = localStorage.getItem('isAdmin') === 'true';
            let replyTo = null;
            let usersData = {};  // cache for user info

            async function login() {
                const u = document.getElementById('username').value.trim();
                const p = document.getElementById('password').value;
                const res = await fetch('/login', {
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body:JSON.stringify({username:u,password:p})
                });
                const data = await res.json();

                if(data.success){
                    currentUser = data.username;
                    isAdmin = data.is_admin;
                    localStorage.setItem('currentUser', currentUser);
                    localStorage.setItem('isAdmin', isAdmin);
                    document.getElementById('authBox').style.display='none';
                    document.getElementById('forumBox').style.display='block';
                    loadMessages();
                } else {
                    // 2008-style ban or terminated screen
                    if(data.error.includes("banned") || data.error.includes("terminated")){
                        document.getElementById('authBox').innerHTML = `
                            <div style="max-width:600px; margin:50px auto; padding:30px; border:2px solid #900; background:#fee; text-align:center; font-family:Verdana, sans-serif;">
                                <h1 style="color:#900; font-size:24px;">${data.error}</h1>
                                <p style="font-size:12px; color:#600;">Please contact <strong>THE administrator</strong> if you think this is a mistake.</p>
                            </div>`;
                    } else {
                        alert(data.error);
                    }
                }
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
                    let userObj = usersData[m.username] || {};
                    let badgesHTML = (userObj.badges || []).map(b=>{
                        let color="#FFD700";
                        if(b==="Administrator") color="red";
                        else if(b==="Banned") color="darkred";
                        else if(b==="Tester") color="blue";
                        else if(b==="Terminated") color="black";
                        return `<span style="background:${color}; color:white; padding:1px 4px; margin-left:3px; font-size:10px; border-radius:3px;">${b}</span>`;
                    }).join("");
                    let roleTag = m.is_admin?' <span class="admin">[ADMIN]</span>':(m.is_moderator?' <span class="moderator">[MOD]</span>':'');
                    let html = `<div class="box message">
                        <strong>${m.title}</strong> by <span onclick="showProfile('${m.username}', event)" style="cursor:pointer; text-decoration:underline;">${m.username}</span>${roleTag} ${badgesHTML} (${m.timestamp})<br>${m.message}<br>`;
                    if(isAdmin){
                        if(!m.is_admin && !m.is_moderator) html += `<button onclick="promoteUser('${m.username}')">Promote to Moderator</button> `;
                        html += `<button onclick="deleteMessage(${m.id})">Delete</button> <button onclick="banUser('${m.username}',24)">Ban User</button> <button onclick="terminateUser('${m.username}')">Terminate</button>`;
                    } else if(usersData[currentUser]?.is_moderator){
                        html += `<button onclick="deleteMessage(${m.id})">Delete</button>`;
                    }
                    html += ` <button onclick='startReply(${m.id},"${m.title.replace(/"/g,'&quot;')}")'>Reply</button>`;
                    html += `</div>`;
                    container.innerHTML += html;

                    data.messages.filter(r=>r.replyTo===m.id).forEach(r=>{
                        let replyObj = usersData[r.username] || {};
                        let replyBadges = (replyObj.badges || []).map(b=>{
                            let color="#FFD700";
                            if(b==="Administrator") color="red";
                            else if(b==="Banned") color="darkred";
                            else if(b==="Tester") color="blue";
                            else if(b==="Terminated") color="black";
                            return `<span style="background:${color}; color:white; padding:1px 4px; margin-left:3px; font-size:10px; border-radius:3px;">${b}</span>`;
                        }).join("");
                        let roleTagR = r.is_admin?' <span class="admin">[ADMIN]</span>':(r.is_moderator?' <span class="moderator">[MOD]</span>':'');
                        container.innerHTML += `<div class="box reply">${r.username}${roleTagR} ${replyBadges}: ${r.message}</div>`;
                    });
                });
            }

            async function deleteMessage(id){
                await fetch(`/delete_message/${id}`,{
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body: JSON.stringify({username: currentUser})
                });
                loadMessages();
            }

            async function banUser(username, hours){
                const res = await fetch(`/ban_user/${username}`,{
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body: JSON.stringify({current_user: currentUser, duration_hours: hours})
                });
                const data = await res.json();
                if(!data.success) alert(data.error);
                loadMessages();
            }

            async function terminateUser(username){
                const res = await fetch(`/terminate_user/${username}`,{
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body: JSON.stringify({current_user: currentUser})
                });
                const data = await res.json();
                if(!data.success) alert(data.error);
                loadMessages();
            }

            function startReply(id,title){
                replyTo = {id:id,title:title};
                document.getElementById('replyInfo').style.display='block';
                document.getElementById('replyToTitle').innerText = title;
            }

            function logout(){
                currentUser=null;
                isAdmin=false;
                localStorage.removeItem('currentUser');
                localStorage.removeItem('isAdmin');
                document.getElementById('authBox').style.display='block';
                document.getElementById('forumBox').style.display='none';
            }

            async function showProfile(username, event){
                const res = await fetch(`/profile/${username}`);
                const data = await res.json();
                usersData[username] = data; // cache
                const box = document.getElementById('profileBox');
                box.style.display='block';
                box.style.left=event.pageX+'px';
                box.style.top=event.pageY+'px';
                box.innerHTML = `<strong>${data.username}</strong>${data.is_admin?' <span class="admin">[ADMIN]</span>':''}${data.is_moderator?' <span class="moderator">[MOD]</span>':''}<br>
                                 Joined: ${data.joined}<br>
                                 Status: ${data.online ? 'Online':'Offline'}<br>
                                 ${data.badges ? data.badges.join(', ') : ''}`;
                setTimeout(()=>{ box.style.display='none'; }, 5000);
            }

            async function promoteUser(username){
                const res = await fetch(`/promote_user/${username}`,{
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body: JSON.stringify({current_user: currentUser})
                });
                const data = await res.json();
                if(!data.success) alert(data.error);
                loadMessages();
            }

        </script>
    </body>
    </html>
    """
    return render_template_string(html)

# --- Backend APIs ---
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    u = data.get("username","").strip()
    p = data.get("password","")
    if not u or not p:
        return jsonify(success=False,error="Username and password required")
    if u in users:
        return jsonify(success=False,error="Username already exists")
    users[u] = {
        "password": hashlib.sha256(p.encode()).hexdigest(),
        "is_admin": False,
        "is_moderator": False,
        "joined": datetime.now().strftime("%Y-%m-%d"),
        "banned_until": None,
        "terminated": False,
        "online": False,
        "badges": []
    }
    return jsonify(success=True)

@app.route("/login", methods=["POST"])
def login_route():
    data = request.get_json()
    u = data.get("username","").strip()
    p = data.get("password","")
    user = users.get(u)
    
    if not user or user["terminated"]:
        return jsonify(success=False,error="Your account has been terminated.")
    
    if user.get("banned_until") and datetime.now() < user["banned_until"]:
        return jsonify(success=False,error=f"You have been banned. Activate your account on {user['banned_until'].strftime('%Y-%m-%d %H:%M')}.")

    if user and hashlib.sha256(p.encode()).hexdigest() == user["password"]:
        user["online"] = True
        return jsonify(success=True, username=u, is_admin=user["is_admin"], is_moderator=user.get("is_moderator", False))
    return jsonify(success=False, error="Invalid credentials")

@app.route("/messages", methods=["GET","POST"])
def msgs():
    if request.method=="POST":
        data = request.get_json()
        username = data.get("username")
        user = users.get(username, {})
        if user.get("banned_until") and datetime.now() < user["banned_until"]:
            return jsonify(success=False,error="You are banned")
        if user.get("terminated"):
            return jsonify(success=False,error="Account terminated")
        new_msg = {
            "id": len(messages)+1,
            "username": username,
            "title": data.get("title") or "No Subject",
            "message": data.get("message"),
            "replyTo": data.get("replyTo"),
            "is_admin": user.get("is_admin", False),
            "is_moderator": user.get("is_moderator", False),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        messages.append(new_msg)
        return jsonify(success=True)
    return jsonify(messages=messages)

@app.route("/delete_message/<int:id>", methods=["POST"])
def delete_message(id):
    data = request.get_json()
    username = data.get("username")
    user = users.get(username, {})
    if not user.get("is_admin") and not user.get("is_moderator"):
        return jsonify(success=False,error="Not authorized")
    messages[:] = [m for m in messages if m["id"] != id]
    return jsonify(success=True)

@app.route("/ban_user/<username>", methods=["POST"])
def ban_user(username):
    data = request.get_json()
    actor = data.get("current_user")
    duration_hours = data.get("duration_hours", 24)
    if not actor or not users.get(actor, {}).get("is_admin", False):
        return jsonify(success=False,error="Only admins can ban users")
    if username in users:
        users[username]["banned_until"] = datetime.now() + timedelta(hours=duration_hours)
        users[username].setdefault("badges", [])
        if "Banned" not in users[username]["badges"]:
            users[username]["badges"].append("Banned")
    return jsonify(success=True)

@app.route("/terminate_user/<username>", methods=["POST"])
def terminate_user(username):
    data = request.get_json()
    actor = data.get("current_user")
    if not actor or not users.get(actor, {}).get("is_admin", False):
        return jsonify(success=False,error="Only admins can terminate users")
    if username in users:
        users[username]["terminated"] = True
        users[username]["badges"] = ["Terminated"]
    return jsonify(success=True)

@app.route("/promote_user/<username>", methods=["POST"])
def promote_user_backend(username):
    data = request.get_json()
    actor = data.get("current_user")
    if not actor or not users.get(actor, {}).get("is_admin", False):
        return jsonify(success=False,error="Only admins can promote users")
    if username in users and not users[username].get("is_admin", False):
        users[username]["is_moderator"] = True
        if "Administrator" not in users[username]["badges"]:
            users[username]["badges"].append("Tester")  # can use Tester badge or add custom
    return jsonify(success=True)

@app.route("/profile/<username>")
def profile(username):
    user = users.get(username)
    if not user:
        return jsonify(success=False,error="User not found")
    return jsonify(username=username, is_admin=user["is_admin"], is_moderator=user.get("is_moderator", False), joined=user["joined"], online=user["online"], badges=user.get("badges", []))

if __name__=="__main__":
    app.run(debug=True)
