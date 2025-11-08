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
        'password':'Administrator555',
        'is_admin': True,
        'is_moderator': False,
        'joined': datetime.now().strftime('%Y-%m-%d'),
        'banned_until': None,
        'terminated': False,
        'online': False,
        'badges': ['Administrator']
    })

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
        <a href="/home">Home</a>
        <a href="/forums">Forums</a>
        <a href="/members">Members</a>
        <a href="/help">Help</a>
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
let currentUser = localStorage.getItem("username") || null;
let isAdmin = localStorage.getItem("is_admin") === "true";
let isModerator = localStorage.getItem("is_moderator") === "true";
let replyTo = null;

window.onload = () => { 
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
        isModerator = data.is_moderator;
        localStorage.setItem("username",currentUser);
        localStorage.setItem("is_admin",isAdmin);
        localStorage.setItem("is_moderator",isModerator);
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
    localStorage.removeItem("username"); 
    localStorage.removeItem("is_admin");
    localStorage.removeItem("is_moderator");
    currentUser=null; 
    isAdmin=false;
    isModerator=false;
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

@app.route("/")
def index():
    return render_template_string(html)

@app.route("/home")
def home():
    total_users = len(users_table)
    total_messages = len(messages_table)
    latest_user = users_table.all()[-1]['username'] if users_table.all() else 'None'
    
    home_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Home - Admin's Forum 2008</title>
        <style>
            body { font-family: Verdana, Arial, sans-serif; font-size: 11px; background: #E8F0F8; margin: 0; color: #333; }
            .wrapper { background: #fff; min-height: 100vh; }
            .header { background: linear-gradient(to bottom, #6BA3D8 0%, #4A90E2 50%, #2E5C8A 100%); padding: 20px; color: white; text-align: center; border-bottom: 3px solid #1A3A5A; box-shadow: 0 3px 8px rgba(0,0,0,0.3); }
            .header h1 { margin: 0; font-size: 28px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); letter-spacing: 2px; }
            .nav-bar { background: linear-gradient(to bottom, #5B9BD5, #4A7AB8); padding: 8px 20px; border-bottom: 2px solid #2E5C8A; }
            .nav-bar a { color: white; text-decoration: none; padding: 5px 12px; margin-right: 5px; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
            .nav-bar a:hover { background: rgba(255,255,255,0.2); border-radius: 3px; }
            .container { max-width: 900px; margin: 20px auto; padding: 0 10px; }
            .box { background: #fff; border: 1px solid #A9A9A9; margin-bottom: 15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.15); border-radius: 4px; }
            .box-header { background: linear-gradient(to bottom, #F5F5F5 0%, #E8E8E8 50%, #D0D0D0 100%); padding: 8px 12px; font-weight: bold; border-bottom: 2px solid #999; color: #333; text-shadow: 1px 1px 0 rgba(255,255,255,0.8); border-radius: 4px 4px 0 0; }
            .box-body { padding: 12px; background: #FEFEFE; }
            .stat-box { display: inline-block; width: 30%; margin: 5px; padding: 15px; background: linear-gradient(to bottom, #F0F8FF, #E0F0FF); border: 1px solid #4A90E2; border-radius: 5px; text-align: center; }
            .stat-number { font-size: 24px; font-weight: bold; color: #2E5C8A; }
            .stat-label { font-size: 10px; color: #666; margin-top: 5px; }
            .footer { background: linear-gradient(to bottom, #4A90E2, #2E5C8A); color: white; text-align: center; padding: 15px; margin-top: 30px; border-top: 3px solid #1A3A5A; font-size: 10px; }
            a { color: #0066CC; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
    <div class="wrapper">
        <div class="header">
            <h1>★ Admin's Forum 2008 ★</h1>
        </div>
        <div class="nav-bar">
            <a href="/home">Home</a>
            <a href="/forums">Forums</a>
            <a href="/members">Members</a>
            <a href="/search">Search</a>
            <a href="/help">Help</a>
            <a href="/">Back to Forum</a>
        </div>
        <div class="container">
            <div class="box">
                <div class="box-header">📊 Forum Statistics</div>
                <div class="box-body" style="text-align: center;">
                    <div class="stat-box">
                        <div class="stat-number">""" + str(total_users) + """</div>
                        <div class="stat-label">Total Members</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">""" + str(total_messages) + """</div>
                        <div class="stat-label">Total Posts</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">""" + latest_user + """</div>
                        <div class="stat-label">Newest Member</div>
                    </div>
                </div>
            </div>
            
            <div class="box">
                <div class="box-header">👋 Welcome to Admin's Forum!</div>
                <div class="box-body">
                    <p><strong>Welcome to the coolest forum on the internet!</strong></p>
                    <p>This is a retro-styled forum bringing back the golden age of 2008 internet culture. Join our community, make friends, and have fun discussions!</p>
                    <p><strong>Quick Links:</strong></p>
                    <ul>
                        <li><a href="/forums">Browse Forums</a> - Check out all discussion topics</li>
                        <li><a href="/members">View Members</a> - See who's part of our community</li>
                        <li><a href="/help">Forum Rules</a> - Read the rules before posting</li>
                        <li><a href="/">Main Forum</a> - Start posting!</li>
                    </ul>
                </div>
            </div>
            
            <div class="box">
                <div class="box-header">🎮 Features</div>
                <div class="box-body">
                    <ul>
                        <li>✨ Classic 2008 Web 2.0 design</li>
                        <li>💬 Real-time messaging and replies</li>
                        <li>👥 User profiles with badges</li>
                        <li>🛡️ Admin and moderator system</li>
                        <li>🔍 Search functionality (coming soon!)</li>
                    </ul>
                </div>
            </div>
        </div>
        <div class="footer">
            Powered by RetroForum v2.1 © 2008 | All times are GMT
        </div>
    </div>
    </body>
    </html>
    """
    return render_template_string(home_html)

@app.route("/forums")
def forums():
    forums_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Forums - Admin's Forum 2008</title>
        <style>
            body { font-family: Verdana, Arial, sans-serif; font-size: 11px; background: #E8F0F8; margin: 0; color: #333; }
            .wrapper { background: #fff; min-height: 100vh; }
            .header { background: linear-gradient(to bottom, #6BA3D8 0%, #4A90E2 50%, #2E5C8A 100%); padding: 20px; color: white; text-align: center; border-bottom: 3px solid #1A3A5A; box-shadow: 0 3px 8px rgba(0,0,0,0.3); }
            .header h1 { margin: 0; font-size: 28px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); letter-spacing: 2px; }
            .nav-bar { background: linear-gradient(to bottom, #5B9BD5, #4A7AB8); padding: 8px 20px; border-bottom: 2px solid #2E5C8A; }
            .nav-bar a { color: white; text-decoration: none; padding: 5px 12px; margin-right: 5px; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
            .nav-bar a:hover { background: rgba(255,255,255,0.2); border-radius: 3px; }
            .container { max-width: 900px; margin: 20px auto; padding: 0 10px; }
            .box { background: #fff; border: 1px solid #A9A9A9; margin-bottom: 15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.15); border-radius: 4px; }
            .box-header { background: linear-gradient(to bottom, #F5F5F5 0%, #E8E8E8 50%, #D0D0D0 100%); padding: 8px 12px; font-weight: bold; border-bottom: 2px solid #999; color: #333; text-shadow: 1px 1px 0 rgba(255,255,255,0.8); border-radius: 4px 4px 0 0; }
            .box-body { padding: 12px; background: #FEFEFE; }
            .forum-item { padding: 10px; border-bottom: 1px solid #E0E0E0; }
            .forum-item:hover { background: #F5F9FC; }
            .forum-icon { font-size: 24px; margin-right: 10px; vertical-align: middle; }
            .forum-title { font-weight: bold; color: #2E5C8A; font-size: 13px; }
            .forum-desc { font-size: 10px; color: #666; margin-top: 3px; }
            .footer { background: linear-gradient(to bottom, #4A90E2, #2E5C8A); color: white; text-align: center; padding: 15px; margin-top: 30px; border-top: 3px solid #1A3A5A; font-size: 10px; }
            a { color: #0066CC; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
    <div class="wrapper">
        <div class="header">
            <h1>★ Admin's Forum 2008 ★</h1>
        </div>
        <div class="nav-bar">
            <a href="/home">Home</a>
            <a href="/forums">Forums</a>
            <a href="/members">Members</a>
            <a href="/search">Search</a>
            <a href="/help">Help</a>
            <a href="/">Back to Forum</a>
        </div>
        <div class="container">
            <div class="box">
                <div class="box-header">📁 Forum Categories</div>
                <div class="box-body">
                    <div class="forum-item">
                        <span class="forum-icon">💬</span>
                        <a href="/" class="forum-title">General Discussion</a>
                        <div class="forum-desc">Talk about anything and everything here!</div>
                    </div>
                </div>
            </div>
        </div>
        <div class="footer">
            Powered by RetroForum v2.1 © 2008 | All times are GMT
        </div>
    </div>
    </body>
    </html>
    """
    return render_template_string(forums_html)

@app.route("/members")
def members():
    users = users_table.all()
    
    members_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Members - Admin's Forum 2008</title>
        <style>
            body { font-family: Verdana, Arial, sans-serif; font-size: 11px; background: #E8F0F8; margin: 0; color: #333; }
            .wrapper { background: #fff; min-height: 100vh; }
            .header { background: linear-gradient(to bottom, #6BA3D8 0%, #4A90E2 50%, #2E5C8A 100%); padding: 20px; color: white; text-align: center; border-bottom: 3px solid #1A3A5A; box-shadow: 0 3px 8px rgba(0,0,0,0.3); }
            .header h1 { margin: 0; font-size: 28px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); letter-spacing: 2px; }
            .nav-bar { background: linear-gradient(to bottom, #5B9BD5, #4A7AB8); padding: 8px 20px; border-bottom: 2px solid #2E5C8A; }
            .nav-bar a { color: white; text-decoration: none; padding: 5px 12px; margin-right: 5px; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
            .nav-bar a:hover { background: rgba(255,255,255,0.2); border-radius: 3px; }
            .container { max-width: 900px; margin: 20px auto; padding: 0 10px; }
            .box { background: #fff; border: 1px solid #A9A9A9; margin-bottom: 15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.15); border-radius: 4px; }
            .box-header { background: linear-gradient(to bottom, #F5F5F5 0%, #E8E8E8 50%, #D0D0D0 100%); padding: 8px 12px; font-weight: bold; border-bottom: 2px solid #999; color: #333; text-shadow: 1px 1px 0 rgba(255,255,255,0.8); border-radius: 4px 4px 0 0; }
            .box-body { padding: 12px; background: #FEFEFE; }
            .member-item { padding: 8px; border-bottom: 1px solid #E0E0E0; display: flex; align-items: center; }
            .member-item:hover { background: #F5F9FC; }
            .member-name { font-weight: bold; color: #2E5C8A; margin-right: 10px; }
            .admin { color: #C00; font-weight: bold; }
            .moderator { color: #090; font-weight: bold; }
            .badge { font-size: 9px; margin-left: 4px; padding: 2px 5px; background: linear-gradient(to bottom, #FFE66D, #FFD700); border: 1px solid #CCA000; border-radius: 3px; font-weight: bold; color: #664400; }
            .online-status { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 5px; }
            .online { background: #0F0; }
            .offline { background: #999; }
            .footer { background: linear-gradient(to bottom, #4A90E2, #2E5C8A); color: white; text-align: center; padding: 15px; margin-top: 30px; border-top: 3px solid #1A3A5A; font-size: 10px; }
        </style>
    </head>
    <body>
    <div class="wrapper">
        <div class="header">
            <h1>★ Admin's Forum 2008 ★</h1>
        </div>
        <div class="nav-bar">
            <a href="/home">Home</a>
            <a href="/forums">Forums</a>
            <a href="/members">Members</a>
            <a href="/search">Search</a>
            <a href="/help">Help</a>
            <a href="/">Back to Forum</a>
        </div>
        <div class="container">
            <div class="box">
                <div class="box-header">👥 Forum Members (""" + str(len(users)) + """ total)</div>
                <div class="box-body">
    """
    
    for user in users:
        status_class = "online" if user.get('online') else "offline"
        role = ""
        if user.get('is_admin'):
            role = ' <span class="admin">[ADMIN]</span>'
        elif user.get('is_moderator'):
            role = ' <span class="moderator">[MOD]</span>'
        
        badges_html = ""
        if user.get('badges'):
            badges_html = " ".join([f'<span class="badge">{b}</span>' for b in user['badges']])
        
        members_html += f"""
                    <div class="member-item">
                        <span class="online-status {status_class}"></span>
                        <span class="member-name">{user['username']}</span>{role} {badges_html}
                        <span style="margin-left: auto; font-size: 10px; color: #666;">Joined: {user['joined']}</span>
                    </div>
        """
    
    members_html += """
                </div>
            </div>
        </div>
        <div class="footer">
            Powered by RetroForum v2.1 © 2008 | All times are GMT
        </div>
    </div>
    </body>
    </html>
    """
    return render_template_string(members_html)

@app.route("/search")
def search():
    search_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Search - Admin's Forum 2008</title>
        <style>
            body { font-family: Verdana, Arial, sans-serif; font-size: 11px; background: #E8F0F8; margin: 0; color: #333; }
            .wrapper { background: #fff; min-height: 100vh; }
            .header { background: linear-gradient(to bottom, #6BA3D8 0%, #4A90E2 50%, #2E5C8A 100%); padding: 20px; color: white; text-align: center; border-bottom: 3px solid #1A3A5A; box-shadow: 0 3px 8px rgba(0,0,0,0.3); }
            .header h1 { margin: 0; font-size: 28px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); letter-spacing: 2px; }
            .nav-bar { background: linear-gradient(to bottom, #5B9BD5, #4A7AB8); padding: 8px 20px; border-bottom: 2px solid #2E5C8A; }
            .nav-bar a { color: white; text-decoration: none; padding: 5px 12px; margin-right: 5px; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
            .nav-bar a:hover { background: rgba(255,255,255,0.2); border-radius: 3px; }
            .container { max-width: 900px; margin: 20px auto; padding: 0 10px; }
            .box { background: #fff; border: 1px solid #A9A9A9; margin-bottom: 15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.15); border-radius: 4px; }
            .box-header { background: linear-gradient(to bottom, #F5F5F5 0%, #E8E8E8 50%, #D0D0D0 100%); padding: 8px 12px; font-weight: bold; border-bottom: 2px solid #999; color: #333; text-shadow: 1px 1px 0 rgba(255,255,255,0.8); border-radius: 4px 4px 0 0; }
            .box-body { padding: 12px; background: #FEFEFE; }
            input { width: 95%; padding: 8px; margin: 8px 0; font-size: 12px; border: 1px solid #999; box-shadow: inset 1px 1px 2px rgba(0,0,0,0.1); }
            button { padding: 6px 15px; font-size: 11px; background: linear-gradient(to bottom, #6BA3D8, #4A90E2); color: white; border: 1px solid #2E5C8A; border-radius: 3px; cursor: pointer; font-weight: bold; }
            .footer { background: linear-gradient(to bottom, #4A90E2, #2E5C8A); color: white; text-align: center; padding: 15px; margin-top: 30px; border-top: 3px solid #1A3A5A; font-size: 10px; }
            .coming-soon { text-align: center; padding: 30px; color: #999; font-size: 14px; }
        </style>
    </head>
    <body>
    <div class="wrapper">
        <div class="header">
            <h1>★ Admin's Forum 2008 ★</h1>
        </div>
        <div class="nav-bar">
            <a href="/home">Home</a>
            <a href="/forums">Forums</a>
            <a href="/members">Members</a>
            <a href="/search">Search</a>
            <a href="/help">Help</a>
            <a href="/">Back to Forum</a>
        </div>
        <div class="container">
            <div class="box">
                <div class="box-header">🔍 Search Forum</div>
                <div class="box-body">
                    <strong>Search for posts and members:</strong><br>
                    <input type="text" placeholder="Enter search keywords..." disabled>
                    <button disabled>Search</button>
                    <div class="coming-soon">
                        <p><strong>🚧 Coming Soon! 🚧</strong></p>
                        <p>Search functionality is currently under development.</p>
                        <p>In the meantime, browse the <a href="/">main forum</a> or check out our <a href="/members">members list</a>!</p>
                    </div>
                </div>
            </div>
        </div>
        <div class="footer">
            Powered by RetroForum v2.1 © 2008 | All times are GMT
        </div>
    </div>
    </body>
    </html>
    """
    return render_template_string(search_html)

@app.route("/help")
def help_page():
    help_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Help & Rules - Admin's Forum 2008</title>
        <style>
            body { font-family: Verdana, Arial, sans-serif; font-size: 11px; background: #E8F0F8; margin: 0; color: #333; }
            .wrapper { background: #fff; min-height: 100vh; }
            .header { background: linear-gradient(to bottom, #6BA3D8 0%, #4A90E2 50%, #2E5C8A 100%); padding: 20px; color: white; text-align: center; border-bottom: 3px solid #1A3A5A; box-shadow: 0 3px 8px rgba(0,0,0,0.3); }
            .header h1 { margin: 0; font-size: 28px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); letter-spacing: 2px; }
            .nav-bar { background: linear-gradient(to bottom, #5B9BD5, #4A7AB8); padding: 8px 20px; border-bottom: 2px solid #2E5C8A; }
            .nav-bar a { color: white; text-decoration: none; padding: 5px 12px; margin-right: 5px; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
            .nav-bar a:hover { background: rgba(255,255,255,0.2); border-radius: 3px; }
            .container { max-width: 900px; margin: 20px auto; padding: 0 10px; }
            .box { background: #fff; border: 1px solid #A9A9A9; margin-bottom: 15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.15); border-radius: 4px; }
            .box-header { background: linear-gradient(to bottom, #F5F5F5 0%, #E8E8E8 50%, #D0D0D0 100%); padding: 8px 12px; font-weight: bold; border-bottom: 2px solid #999; color: #333; text-shadow: 1px 1px 0 rgba(255,255,255,0.8); border-radius: 4px 4px 0 0; }
            .box-body { padding: 12px; background: #FEFEFE; line-height: 1.6; }
            .rule-item { padding: 10px; margin: 10px 0; background: #FFF9E6; border-left: 4px solid #FFD700; }
            .warning { color: #C00; font-weight: bold; }
            .footer { background: linear-gradient(to bottom, #4A90E2, #2E5C8A); color: white; text-align: center; padding: 15px; margin-top: 30px; border-top: 3px solid #1A3A5A; font-size: 10px; }
        </style>
    </head>
    <body>
    <div class="wrapper">
        <div class="header">
            <h1>★ Admin's Forum 2008 ★</h1>
        </div>
        <div class="nav-bar">
            <a href="/home">Home</a>
            <a href="/forums">Forums</a>
            <a href="/members">Members</a>
            <a href="/search">Search</a>
            <a href="/help">Help</a>
            <a href="/">Back to Forum</a>
        </div>
        <div class="container">
            <div class="box">
                <div class="box-header">📜 Forum Rules</div>
                <div class="box-body">
                    <p><strong>Please read and follow these rules to keep our community awesome!</strong></p>
                    
                    <div class="rule-item">
                        <strong>1. No Spam</strong><br>
                        Don't spam, don't hack other people's accounts.
                    </div>
                    
                    <div class="rule-item">
                        <strong>2. No Alting or Ban Evading</strong><br>
                        No alting/ban evading. If you are found to be or suspected to be a banned user, you will be terminated along with your main account.
                    </div>
                    
                    <div class="rule-item">
                        <strong>3. Be Cool & Respectful</strong><br>
                        Be cool, and respect other people.
                    </div>
                    
                    <p class="warning">⚠️ Breaking these rules may result in warnings, bans, or account termination.</p>
                    
                    <p><strong>The rules are very straightforward.</strong> Follow them and we'll all have a great time!</p>
                </div>
            </div>
            
            <div class="box">
                <div class="box-header">❓ FAQ</div>
                <div class="box-body">
                    <p><strong>Q: How do I register?</strong><br>
                    A: Click "Register New Account" on the main page and create your username and password.</p>
                    
                    <p><strong>Q: How do I post a message?</strong><br>
                    A: After logging in, use the "Post New Message" box to create a new thread or click "Reply" on existing messages.</p>
                    
                    <p><strong>Q: What are badges?</strong><br>
                    A: Badges are special awards given to members for contributions or achievements on the forum.</p>
                    
                    <p><strong>Q: How do I become a moderator?</strong><br>
                    A: Moderators are promoted by administrators based on their activity and helpfulness in the community.</p>
                    
                    <p><strong>Q: I forgot my password, what do I do?</strong><br>
                    A: Contact an administrator for assistance with account recovery.</p>
                </div>
            </div>
            
            <div class="box">
                <div class="box-header">📞 Contact</div>
                <div class="box-body">
                    <p>If you have any questions or concerns, please contact the forum administrators.</p>
                    <p><strong>Admin:</strong> admin</p>
                </div>
            </div>
        </div>
        <div class="footer">
            Powered by RetroForum v2.1 © 2008 | All times are GMT
        </div>
    </div>
    </body>
    </html>
    """
    return render_template_string(help_html)

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
