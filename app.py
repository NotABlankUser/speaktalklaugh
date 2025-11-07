from flask import Flask, request, jsonify, render_template_string
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import hashlib
import datetime

app = Flask(__name__)
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)

# --- Users ---
users = {
    "admin": {"password": hashlib.sha256("admin123123".encode()).hexdigest(), "is_admin": True}
}

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
        </style>
    </head>
    <body>
        <div class="header">
            <h1>★ AWESOME FORUM 2008 ★</h1>
        </div>
        <div class="container">
            <div id="loginBox" class="box">
                <div class="box-header">Login</div>
                <div class="box-body">
                    Username:<br><input id="username"><br>
                    Password:<br><input type="password" id="password"><br>
                    <button onclick="login()">Login</button>
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
        <script>
            let currentUser = null;
            let replyTo = null;

            async function login() {
                const u = document.getElementById('username').value;
                const p = document.getElementById('password').value;
                const res = await fetch('/login', {
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body:JSON.stringify({username:u,password:p})
                });
                const data = await res.json();
                if(data.success) {
                    currentUser = data.username;
                    document.getElementById('loginBox').style.display='none';
                    document.getElementById('forumBox').style.display='block';
                    loadMessages();
                } else alert(data.error);
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
                    let html = `<div class="box message">
                        <strong>${m.title}</strong> by ${m.username}${m.is_admin?' <span class="admin">[ADMIN]</span>':''}<br>${m.message}<br>
                        <button onclick='startReply(${m.id},"${m.title.replace(/"/g,'&quot;')}")'>Reply</button>
                    </div>`;
                    container.innerHTML += html;
                    data.messages.filter(r=>r.replyTo===m.id).forEach(r=>{
                        container.innerHTML += `<div class="box reply">${r.username}${r.is_admin?' <span class="admin">[ADMIN]</span>':''}: ${r.message}</div>`;
                    });
                });
            }

            function startReply(id,title){
                replyTo = {id:id,title:title};
                document.getElementById('replyInfo').style.display='block';
                document.getElementById('replyToTitle').innerText = title;
            }

            function logout(){
                currentUser=null;
                document.getElementById('loginBox').style.display='block';
                document.getElementById('forumBox').style.display='none';
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    u = data.get("username","").strip()
    p = data.get("password","")
    if u in users and hashlib.sha256(p.encode()).hexdigest() == users[u]["password"]:
        return jsonify(success=True, username=u, is_admin=users[u]["is_admin"])
    return jsonify(success=False, error="Invalid credentials")

@app.route("/messages", methods=["GET","POST"])
def msgs():
    if request.method=="POST":
        data = request.get_json()
        new_msg = {
            "id": len(messages)+1,
            "username": data.get("username"),
            "title": data.get("title") or "No Subject",
            "message": data.get("message"),
            "replyTo": data.get("replyTo"),
            "is_admin": users.get(data.get("username"),{}).get("is_admin",False)
        }
        messages.append(new_msg)
        return jsonify(success=True)
    return jsonify(messages=messages)

if __name__=="__main__":
    app.run(debug=True)

