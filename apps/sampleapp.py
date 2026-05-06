#
# Copyright (C) 2026 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.
#
# AsynapRous release
#
# The authors hereby grant to Licensee personal permission to use
# and modify the Licensed Source Code for the sole purpose of studying
# while attending the course
#


"""
app.sampleapp
~~~~~~~~~~~~~~~~~

"""

import sys
import os
import importlib.util
import json
import base64
import asyncio

from daemon import AsynapRous
from daemon.utils import get_local_ip

app = AsynapRous()

# In-memory storage for tracker
active_peers = {}
# In-memory storage for messages
inbox_messages = []

@app.route('/slow-api', methods=['GET'])
async def slow_api(req, resp):
    print("Đã nhận request /slow-api, đợi 5s ....")
    await asyncio.sleep(5)
    print("[!] Đã xử lý xong /slow-api!")
    return b'{"message": "Slow task complete!"}'

@app.route('/get-my-info', methods=['GET'])
def get_my_info(req, resp):
    """
    Returns server metadata to the client, including its detected local IP.
    """
    data = {
        "ip": get_local_ip(),
        "port": app.port,
        "name": "AsynapRous Node"
    }
    return json.dumps(data).encode("utf-8")

@app.route('/login', methods=['POST', 'PUT'])
def login(req, resp):
    print(f"[SampleApp] /login called with headers: {req.headers}")
    
    # 1. Authentication Check
    auth_header = req.headers.get("authorization")
    if not auth_header:
        resp.status_code = 401
        resp.headers["WWW-Authenticate"] = 'Basic realm="Restricted Area"'
        return b'{"error": "Unauthorized"}'
    
    try:
        auth_type, credentials = auth_header.split(" ")
        decoded = base64.b64decode(credentials).decode("utf-8")
        username, password = decoded.split(":")
    except Exception as e:
        resp.status_code = 401
        return b'{"error": "Invalid Authorization header"}'

    # Simple auth check
    if password == "1234":
        resp.status_code = 200
        # Set session cookie
        session_id = f"sess_{username}_123"
        resp.cookies["session_id"] = session_id
        data = {"message": "Logged in", "username": username, "token": session_id}
        return json.dumps(data).encode("utf-8")
    else:
        resp.status_code = 401
        return b'{"error": "Wrong credentials (password must be 1234)"}'

@app.route('/submit-info', methods=['POST'])
def submit_info(req, resp):
    # Require Authentication (check cookie or auth header)
    session_id = req.cookies.get("session_id")
    auth_header = req.headers.get("authorization")
    if not session_id and not auth_header:
        resp.status_code = 401
        return b'{"error": "Unauthorized. Please login first."}'

    try:
        body_data = json.loads(req.body)
        peer_ip = body_data.get("ip")
        peer_port = body_data.get("port")
        peer_name = body_data.get("name")
        active_peers[peer_name] = {"ip": peer_ip, "port": peer_port}
        data = {"message": "Peer info submitted successfully"}
        return json.dumps(data).encode("utf-8")
    except Exception as e:
        resp.status_code = 400
        return b'{"error": "Invalid payload"}'

@app.route('/get-list', methods=['GET'])
def get_list(req, resp):
    session_id = req.cookies.get("session_id")
    auth_header = req.headers.get("authorization")
    if not session_id and not auth_header:
        resp.status_code = 401
        return b'{"error": "Unauthorized"}'
    
    data = {"peers": active_peers}
    return json.dumps(data).encode("utf-8")

@app.route('/connect-peer', methods=['POST'])
def connect_peer(req, resp):
    # Dummy logic to handle P2P connection init
    return json.dumps({"message": "Connected to peer"}).encode("utf-8")

@app.route('/broadcast-peer', methods=['POST'])
def broadcast_peer(req, resp):
    return json.dumps({"message": "Broadcast sent"}).encode("utf-8")

@app.route('/send-peer', methods=['POST'])
def send_peer(req, resp):
    try:
        body_data = json.loads(req.body)
        sender = body_data.get('sender', 'Unknown')
        msg = body_data.get('message')
        group = body_data.get('group', None)
        group_members = body_data.get('groupMembers', None)
        print(f"[Peer] Message received: {msg} from {sender} (Group: {group})")
        inbox_messages.append({"sender": sender, "message": msg, "group": group, "groupMembers": group_members})
        return json.dumps({"message": "Message received"}).encode("utf-8")
    except Exception as e:
        resp.status_code = 400
        return b'{"error": "Bad request"}'

@app.route('/get-messages', methods=['GET'])
def get_messages(req, resp):
    global inbox_messages
    data = {"messages": inbox_messages}
    inbox_messages = [] # Clear after reading
    return json.dumps(data).encode("utf-8")

def create_sampleapp(ip, port):
    # Prepare and launch the RESTful application
    app.prepare_address(ip, port)
    app.run()
