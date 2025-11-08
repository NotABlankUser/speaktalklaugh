from flask import Flask, request, jsonify, render_template_string
from tinydb import TinyDB, Query
from datetime import datetime

app = Flask(__name__)
db = TinyDB('db.json')

users_table = db.table('users')
messages_table = db.table('messages')

# Initialize admin if not exists
if not users_table.contains(Query().username == 'admin'):
    users_table.insert({
        'username':'admin',
        'password':'Administrator555',  # plain text for simplicity; hash in real app
        'is_admin': True,
        'is_moderator': False,
        'joined': datetime.now().strftime('%Y-%m-%d'),
        'banned_until': None,
        'terminated': False,
        'online': False,
        'badges': ['Administrator']
    })

# ----------------- HTML -----------------
html = """<!DOCTYPE html>
<html>
<head>
    <title>Retro Forum 2008</title>
    <style>
        body { 
            font-family: Verdana, Arial, sans-serif; 
            font-size: 11px; 
            background: #E8F0F8 url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAFklEQVQIW2P8////fwYGBgZGRkYGAABGAQX9/q3ZAAAAAABJRU5ErkJggg==') repeat;
            margin: 0; 
            color: #333;
        }
        .wrapper { background: #fff; min-height: 100vh; }
        .header { 
            background: linear-gradient(to bottom, #6BA3D8 0%, #4A90E2 50%, #2E5C8A 100%);
            padding: 20px; 
            color: white; 
            text-align: center; 
            border-bottom: 3px solid #1A3A5A;
            box-shadow: 0 3px 8px rgba(0,0,0,0.3);
        }
        .header h1 { 
            margin: 0; 
            font-size: 28px; 
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            letter-spacing: 2px;
        }
        .header-subtitle {
            font-size: 10px;
            margin-top: 5px;
            opacity: 0.9;
        }
        .nav-bar {
            background: linear-gradient(to bottom, #5B9BD5, #4A7AB8);
            padding: 8px 20px;
            border-bottom: 2px solid #2E5C8A;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.3);
        }
        .nav-bar a {
            color: white;
            text-decoration: none;
            padding: 5px 12px;
            margin-right: 5px;
            font-weight: bold;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }
        .nav-bar a:hover {
            background: rgba(255,255,255,0.2);
            border-radius: 3px;
        }
        .container { 
            max-width: 900px; 
            margin: 20px auto; 
            padding: 0 10px;
        }
        .box { 
            background: #fff; 
            border: 1px solid #A9A9A9; 
            margin-bottom: 15px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.15);
            border-radius: 4px;
        }
        .box-header { 
            background: linear-gradient(to bottom, #F5F5F5 0%, #E8E8E8 50%, #D0D0D0 100%);
            padding: 8px 12px; 
            font-weight: bold; 
            border-bottom: 2px solid #999;
            color: #333;
            text-shadow: 1px 1px 0 rgba(255,255,255,0.8);
            border-radius: 4px 4px 0 0;
        }
        .box-body { 
            padding: 12px;
            background: #FEFEFE;
        }
        input, textarea { 
            width: 98%; 
            padding: 5px; 
            margin: 4px 0; 
            font-size: 11px;
            border: 1px solid #999;
            box-shadow: inset 1px 1px 2px rgba(0,0,0,0.1);
            font-family: Verdana, Arial, sans-serif;
        }
        input:focus, textarea:focus {
            border-color: #4A90E2;
            outline: none;
            box-shadow: inset 1px 1px 2px rgba(0,0,0,0.1), 0 0 3px rgba(74,144,226,0.5);
        }
        button { 
            padding: 5px 12px; 
            font-size: 11px; 
            background: linear-gradient(to bottom, #6BA3D8, #4A90E2);
            color: white; 
            border: 1px solid #2E5C8A;
            border-radius: 3px;
            cursor: pointer;
            font-weight: bold;
            text-shadow: 1px 1px 1px rgba(0,0,0,0.3);
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
            margin-right: 3px;
        }
        button:hover {
            background: linear-gradient(to bottom, #7BB3E8, #5AA0F2);
        }
        button:active {
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.3);
        }
        .message { 
            border-bottom: 1px solid #E0E0E0; 
            padding: 10px;
            background: #FAFAFA;
        }
        .message:hover {
            background: #F5F9FC;
        }
        .reply { 
            margin-left: 35px; 
            border-left: 4px solid #4A90E2; 
            padding: 8px 0 8px 12px; 
            background: #F8FCFF;
            margin-bottom: 8px;
        }
        .admin { 
            color: #C00; 
            font-weight: bold;
            text-shadow: 1px 1px 0 rgba(255,255,0,0.3);
        }
        .moderator { 
            color: #090; 
            font-weight: bold;
        }
        .badge { 
            font-size: 9px; 
            margin-left: 4px; 
            padding: 2px 5px; 
            background: linear-gradient(to bottom, #FFE66D, #FFD700);
            border: 1px solid #CCA000;
            border-radius: 3px;
            font-weight: bold;
            color: #664400;
            text-shadow: 0 1px 0 rgba(255,255,255,0.5);
            box-shadow: 0 1px 2px rgba(0,0,0,0.2);
        }
        .profile { 
            border: 2px solid #4A90E2; 
            background: linear-gradient(to bottom, #FFFFFF, #F0F8FF);
            padding: 10px; 
            position: absolute; 
            display: none;
            box-shadow: 3px 3px 10px rgba(0,0,0,0.4);
            border-radius: 5px;
            min-width: 200px;
            z-index: 1000;
        }
        .profile strong {
            font-size: 13px;
            color: #2E5C8A;
        }
        .username-link {
            cursor: pointer;
            text-decoration: underline;
            color: #0066CC;
            font-weight: bold;
        }
        .username-link:hover {
            color: #004499;
        }
        .message-title {
            font-size: 13px;
            font-weight: bold;
            color: #2E5C8A;
            margin-bottom: 5px;
        }
        .message-meta {
            font-size: 10px;
            color: #666;
            margin-top: 8px;
        }
        .footer {
            background: linear-gradient(to bottom, #4A90E2, #2E5C8A);
            color: white;
            text-align: center;
            padding: 15px;
            margin-top: 30px;
            border-top: 3px solid #1A3A5A;
            font-size: 10px;
        }
        textarea {
            resize: vertical;
            min-height: 80px;
        }
        .info-message {
            background: #FFF9E6;
            border: 1px solid #FFD700;
            padding: 8px;
            margin-bottom: 10px;
            border-radius: 3px;
            color: #664400;
        }
    </style>
</head>
<body>
<div class="wrapper">
    <div class="header">
        <h1>★ Admin's Forum 2008 ★</h1>
        <div class="header-subtitle">Welcome to the best forum on the internet!</div>
    </div>
    <div class="nav-bar">
        <a href="#">Home</a>
        <a href="#">Forums</a>
        <a href="#">Members</a>
        <a href="#">Search</a>
        <a href="#">Help</a>
    </div>
    <div class="container">
        <div id="authBox" class="box">
            <div class="box-header" id="authHeader">🔒 Member Login</div>
            <div class="box-body">
                <strong>Username:</strong><br>
                <input id="username" placeholder="Enter your username"><br>
                <strong>Password:</strong><br>
                <input type="password" id="password" placeholder="Enter your password"><br><br>
                <button onclick="login()">Login</button>
                <button onclick="showRegister()">Register New Account</button>
            </div>
        </div>

        <div id="forumBox" style="display:none;">
            <div class="box">
                <div class="box-header">📝 Post New Message</div>
                <div class="box-body">
                    <div id="replyInfo" class="info-message" style="display:none;">
                        <strong>Replying to:</strong> <span id="replyToTitle"></span> 
                        <button onclick="cancelReply()">Cancel Reply</button>
                    </div>
                    <strong>Subject:</strong><br>
                    <input id="title" placeholder="Enter message subject"><br>
                    <strong>Message:</strong><br>
                    <textarea id="msg" placeholder="Type your message here..."></textarea><br>
                    <button onclick="postMessage()">Post Message</button>
                    <button onclick="logout()" style="background: linear-gradient(to bottom, #D88, #C66); border-color: #A44;">Logout</button>
                </div>
            </div>
            <div id="messagesBox"></div>
        </div>
    </div>
    <div class="footer">
        Powered by RetroForum v2.1 © 2008 | All times are GMT | <a href="#" style="color: #fff;">Privacy Policy</a>
    </div>
</div>

<div id="profileBox" class="profile"></div>

<script>
let currentUser = null;
let isAdmin = false;
let replyTo = null;

window.onload = () => { 
    // Don't use localStorage in artifacts
    if(currentUser) { 
        document.getElementById('authBox').style.display='none'; 
        document.getElementById('forumBox').style.display='block'; 
        loadMessages(); 
    } 
}

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
        document.getElementById('authBox').style.display='none';
        document.getElementById('forumBox').style.display='block';
        loadMessages();
    } else alert(data.error);
}

async function registerUser(){
    const u = document.getElementById('username').value.trim();
    const p = document.getElementById('password').value;
    if(!u||!p) return alert("Username and password required!");
    const res = await fetch('/register',{
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({username:u,password:p})
    });
    const data = await res.json();
    if(data.success) { alert("Registration successful! Please login."); showLogin(); }
    else alert(data.error);
}

function showRegister(){
    document.getElementById('authHeader').innerText='📝 Register New Account';
    const btns = document.querySelectorAll('#authBox button');
    btns[0].innerText='Create Account'; btns[0].onclick=registerUser;
    btns[1].innerText='Back to Login'; btns[1].onclick=showLogin;
}
function showLogin(){
    document.getElementById('authHeader').innerText='🔒 Member Login';
    const btns = document.querySelectorAll('#authBox button');
    btns[0].innerText='Login'; btns[0].onclick=login;
    btns[1].innerText='Register New Account'; btns[1].onclick=showRegister;
}

async function postMessage(){
    const t=document.getElementById('title').value;
    const m=document.getElementById('msg').value;
    if(!m) return alert("Message cannot be empty!");
    await fetch('/messages',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({username:currentUser,title:t,message:m,replyTo:replyTo?replyTo.id:null})
    });
    document.getElementById('msg').value=''; 
    document.getElementById('title').value=''; 
    replyTo=null; 
    document.getElementById('replyInfo').style.display='none';
    loadMessages();
}

function cancelReply(){ 
    replyTo=null; 
    document.getElementById('replyInfo').style.display='none'; 
}

function logout(){ 
    currentUser=null; 
    isAdmin=false; 
    document.getElementById('authBox').style.display='block'; 
    document.getElementById('forumBox').style.display='none'; 
}

async function loadMessages(){
    const res=await fetch('/messages'); 
    const data=await res.json();
    const container=document.getElementById('messagesBox'); 
    container.innerHTML='';
    
    data.messages.filter(m=>!m.replyTo).forEach(m=>{
        let badgeHtml = '';
        if(m.badges) badgeHtml = m.badges.map(b=>`<span class="badge">${b}</span>`).join(' ');
        let role = m.is_admin?' <span class="admin">[ADMIN]</span>':(m.is_moderator?' <span class="moderator">[MOD]</span>':'');
        
        let html = `<div class="box message">
            <div class="message-title">${m.title || '(No Subject)'}</div>
            <div>Posted by <span class="username-link" onclick="showProfile('${m.username}', event)">${m.username}</span> (ID: ${m.user_id})${role} ${badgeHtml}</div>
            <div style="margin: 8px 0;">${m.message}</div>
            <div class="message-meta">
                <em>${m.timestamp}</em><br>`;
        
        if(isAdmin){
            html += `<button onclick="deleteMessage(${m.id})">Delete</button>
                     <button onclick="banUser('${m.username}')">Ban User</button>
                     <button onclick="terminateUser('${m.username}')">Terminate</button>
                     <button onclick="promoteUser('${m.username}')">Promote to Mod</button>`;
        }
        html += ` <button onclick='startReply(${m.id},"${(m.title||'').replace(/"/g,'&quot;')}")'>Reply</button>`;
        html += `</div></div>`;
        container.innerHTML+=html;

        data.messages.filter(r=>r.replyTo===m.id).forEach(r=>{
            let replyRole = r.is_admin?' <span class="admin">[ADMIN]</span>':(r.is_moderator?' <span class="moderator">[MOD]</span>':'');
            container.innerHTML += `<div class="reply">
                <strong>${r.username}</strong> (ID: ${r.user_id})${replyRole}
                <div style="margin: 5px 0;">${r.message}</div>
                <div class="message-meta"><em>${r.timestamp}</em></div>
            </div>`;
        });
    });
}

function startReply(id,title){ 
    replyTo={id:id,title:title}; 
    document.getElementById('replyInfo').style.display='block'; 
    document.getElementById('replyToTitle').innerText=title || '(No Subject)'; 
}

async function deleteMessage(id){ 
    if(confirm('Are you sure you want to delete this message?')) {
        await fetch(`/delete_message/${id}`,{method:'POST'}); 
        loadMessages(); 
    }
}
async function banUser(username){ 
    if(confirm('Ban user '+username+'?')) {
        await fetch(`/ban_user/${username}`,{method:'POST'}); 
        loadMessages(); 
    }
}
async function terminateUser(username){ 
    if(confirm('TERMINATE user '+username+'? This is permanent!')) {
        await fetch(`/terminate_user/${username}`,{method:'POST'}); 
        loadMessages(); 
    }
}
async function promoteUser(username){ 
    if(confirm('Promote '+username+' to moderator?')) {
        await fetch(`/promote_user/${username}`,{method:'POST'}); 
        loadMessages(); 
    }
}

async function showProfile(username,event){
    const res=await fetch(`/profile/${username}`); 
    const data=await res.json();
    const box=document.getElementById('profileBox'); 
    box.style.display='block'; 
    box.style.left=(event.pageX+10)+'px'; 
    box.style.top=(event.pageY+10)+'px';
    box.innerHTML = `<strong>${data.username}</strong>${data.is_admin?' <span class="admin">[ADMIN]</span>':''}${data.is_moderator?' <span class="moderator">[MOD]</span>':''}<br>
                     <strong>Member Since:</strong> ${data.joined}<br>
                     <strong>Status:</strong> <span style="color:${data.online?'green':'red'}">${data.online?'● Online':'○ Offline'}</span><br>
                     <strong>Badges:</strong> ${(data.badges||['None']).join(", ")}`;
    setTimeout(()=>{box.style.display='none';},5000);
}

// Close profile on click anywhere
document.addEventListener('click', function(e) {
    const profileBox = document.getElementById('profileBox');
    if(!e.target.classList.contains('username-link') && profileBox.style.display === 'block') {
        setTimeout(() => profileBox.style.display = 'none', 100);
    }
});
</script>
</body>
</html>
"""

# ----------------- Routes -----------------
@app.route("/")
def index():
    return render_template_string(html)

@app.route("/home")
def home():
    return render_template_string("<h2>Welcome to Admin's Forum Home!</h2><p>Enjoy your stay.</p><a href='/'>Back</a>")

@app.route("/forums")
def forums():
    return render_template_string("<h2>Forums</h2><p>All discussion boards go here.</p><a href='/'>Back</a>")

@app.route("/members")
def members():
    users = users_table.all()
    user_list = "<ul>" + "".join([f"<li>{u['username']}</li>" for u in users]) + "</ul>"
    return render_template_string(f"<h2>Members</h2>{user_list}<a href='/'>Back</a>")

@app.route("/help")
def help_page():
    return render_template_string("<h2>Help</h2><p>Forum rules and FAQ go here.</p><a href='/'>Back</a>")

# ----------------- Auth -----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = users_table.get(Query().username == data.get('username'))
    if user and user['password'] == data.get('password') and not user.get('terminated'):
        users_table.update({'online': True}, Query().username == data.get('username'))
        return jsonify(success=True, username=user['username'], is_admin=user['is_admin'], is_moderator=user['is_moderator'])
    return jsonify(success=False, error="Invalid credentials or terminated/banned account")

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if users_table.contains(Query().username == data.get('username')):
        return jsonify(success=False, error="Username already exists")
    users_table.insert({
        'username': data.get('username'),
        'password': data.get('password'),
        'is_admin': False,
        'is_moderator': False,
        'joined': datetime.now().strftime('%Y-%m-%d'),
        'banned_until': None,
        'terminated': False,
        'online': False,
        'badges': []
    })
    return jsonify(success=True)

# ----------------- Messages -----------------
@app.route("/messages", methods=["GET","POST"])
def messages():
    if request.method=="POST":
        data = request.get_json()
        user = users_table.get(Query().username == data['username'])
        msg_id = len(messages_table) + 1
        messages_table.insert({
            'id': msg_id,
            'username': data['username'],
            'user_id': user.doc_id,
            'title': data.get('title', '(No Subject)'),
            'message': data['message'],
            'replyTo': data.get('replyTo'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'is_admin': user['is_admin'],
            'is_moderator': user['is_moderator'],
            'badges': user.get('badges', [])
        })
        return jsonify(success=True)
    return jsonify(messages=messages_table.all())

# ----------------- Admin Actions -----------------
@app.route("/delete_message/<int:id>", methods=["POST"])
def delete_message(id):
    messages_table.remove(Query().id == id)
    return jsonify(success=True)

@app.route("/ban_user/<username>", methods=["POST"])
def ban_user(username):
    users_table.update({'banned_until': datetime.now().strftime('%Y-%m-%d')}, Query().username == username)
    return jsonify(success=True)

@app.route("/terminate_user/<username>", methods=["POST"])
def terminate_user(username):
    users_table.update({'terminated': True}, Query().username == username)
    return jsonify(success=True)

@app.route("/promote_user/<username>", methods=["POST"])
def promote_user(username):
    users_table.update({'is_moderator': True}, Query().username == username)
    return jsonify(success=True)

@app.route("/profile/<username>")
def profile(username):
    user = users_table.get(Query().username == username)
    if not user:
        return jsonify(success=False)
    return jsonify(username=user['username'],
                   is_admin=user['is_admin'],
                   is_moderator=user['is_moderator'],
                   joined=user['joined'],
                   online=user['online'],
                   badges=user.get('badges', []))

if __name__=="__main__":
    app.run(debug=True)
