from flask import Flask, render_template_string, jsonify
import redis
from datetime import datetime

app = Flask(__name__)
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>RedisStorageBot Admin</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        .users-list {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        .user-card {
            border-bottom: 1px solid #eee;
            padding: 15px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .user-card:hover {
            background: #f5f5f5;
        }
        .user-id {
            font-weight: bold;
            color: #667eea;
        }
        .last-message {
            color: #666;
            font-size: 0.9rem;
            margin-top: 5px;
        }
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        .modal-content {
            background: white;
            border-radius: 15px;
            padding: 30px;
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }
        .close {
            float: right;
            cursor: pointer;
            font-size: 1.5rem;
            font-weight: bold;
        }
        .history-list {
            margin-top: 15px;
        }
        .history-item {
            background: #f5f5f5;
            padding: 10px;
            margin: 5px 0;
            border-radius: 8px;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 10px;
        }
        .refresh-btn {
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 RedisStorageBot Admin</h1>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="totalUsers">0</div>
                <div class="stat-label">Total Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="totalMessages">0</div>
                <div class="stat-label">Total Messages</div>
            </div>
        </div>
        <button class="refresh-btn" onclick="loadData()">🔄 Refresh</button>
        <div class="users-list" id="usersList">Loading...</div>
    </div>

    <div id="modal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal()">&times;</span>
            <h2 id="modalTitle">User Details</h2>
            <div id="modalBody"></div>
        </div>
    </div>

    <script>
        async function loadData() {
            const response = await fetch('/api/data');
            const data = await response.json();
            document.getElementById('totalUsers').textContent = data.total_users;
            document.getElementById('totalMessages').textContent = data.total_messages;
            const usersList = document.getElementById('usersList');
            if (data.users.length === 0) {
                usersList.innerHTML = '<div class="user-card">No users yet</div>';
                return;
            }
            usersList.innerHTML = data.users.map(user => `
                <div class="user-card" onclick="showUser(${user.user_id})">
                    <div class="user-id">User ID: ${user.user_id}</div>
                    <div class="last-message">Last: ${user.last_message || 'No messages'}</div>
                </div>
            `).join('');
        }
        async function showUser(userId) {
            const response = await fetch(`/api/user/${userId}`);
            const user = await response.json();
            document.getElementById('modalTitle').textContent = `User ${userId}`;
            document.getElementById('modalBody').innerHTML = `
                <p><strong>Last Message:</strong> ${user.last_message || 'None'}</p>
                <p><strong>Total Messages:</strong> ${user.total_messages}</p>
                <div class="history-list">
                    <strong>History:</strong>
                    ${user.history.map(msg => `<div class="history-item">${msg}</div>`).join('') || 'No history'}
                </div>
            `;
            document.getElementById('modal').style.display = 'flex';
        }
        function closeModal() {
            document.getElementById('modal').style.display = 'none';
        }
        loadData();
        setInterval(loadData, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/data')
def get_data():
    keys = redis_client.keys("user:*:last")
    users = []
    total_messages = 0
    for key in keys:
        user_id = key.split(":")[1]
        last_message = redis_client.get(key)
        history = redis_client.lrange(f"user:{user_id}:history", 0, -1)
        total_messages += len(history)
        users.append({'user_id': int(user_id), 'last_message': last_message})
    return jsonify({'total_users': len(users), 'total_messages': total_messages, 'users': users})

@app.route('/api/user/<int:user_id>')
def get_user(user_id):
    last_message = redis_client.get(f"user:{user_id}:last")
    history = redis_client.lrange(f"user:{user_id}:history", 0, -1)
    return jsonify({'user_id': user_id, 'last_message': last_message, 'history': history, 'total_messages': len(history)})

if __name__ == '__main__':
    print("🌐 Web Admin running at http://localhost:5002")
    app.run(host='0.0.0.0', port=5002, debug=True)
