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

import base64
import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone

from   daemon import AsynapRous

app = AsynapRous()
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{1,32}$")
CHANNEL_RE = re.compile(r"^[A-Za-z0-9_.-]{1,32}$")
MAX_MESSAGE_LENGTH = 1000

@app.route('/login', methods=['POST'])
def login(headers="guest", body="anonymous"):
    """
    Handle user login via POST request.

    This route simulates a login process and prints the provided headers and body
    to the console.

    :param headers (str): The request headers or user identifier.
    :param body (str): The request body or login payload.
    """
    print("[SampleApp] Logging in {} to {}".format(headers, body))
    data = {"message": "Welcome to the RESTful TCP WebApp"}

    # Convert to JSON string
    json_str = json.dumps(data)
    return (json_str.encode("utf-8"))

@app.route("/echo", methods=["POST"])
def echo(headers="guest", body="anonymous"):
    print("[SampleApp] received body {}".format(body))

    try:
        message = json.loads(body)
        data = {"received": message }
        # Convert to JSON string
        json_str = json.dumps(data)
        return (json_str.encode("utf-8"))
    except json.JSONDecodeError:
        data = {"error": "Invalid JSON"}
        # Convert to JSON string
        json_str = json.dumps(data)
        return (json_str.encode("utf-8"))


@app.route('/hello', methods=['PUT'])
async def hello(headers, body):
    """
    Handle greeting via PUT request.

    This route prints a greeting message to the console using the provided headers
    and body.

    :param headers (str): The request headers or user identifier.
    :param body (str): The request body or message payload.
    """
    print("[SampleApp] ['PUT'] **ASYNC** Hello in {} to {}".format(headers, body))
    data =  {"id": 1, "name": "Alice", "email": "alice@example.com"}

    # Convert to JSON string
    json_str = json.dumps(data)
    return (json_str.encode("utf-8"))

def _json_body(body):
    try:
        return json.loads(body or "{}")
    except json.JSONDecodeError:
        return None


def _error(message):
    return {"ok": False, "error": message}


def _valid_username(username):
    return isinstance(username, str) and USERNAME_RE.match(username) is not None


def _valid_channel(channel):
    return isinstance(channel, str) and CHANNEL_RE.match(channel) is not None


def _valid_message(message):
    return isinstance(message, str) and 0 < len(message) <= MAX_MESSAGE_LENGTH


def _now():
    return datetime.now(timezone.utc).isoformat()


def _post_json(ip, port, path, payload, timeout=5, auth_header=None):
    url = "http://{}:{}{}".format(ip, port, path)
    headers = {"Content-Type": "application/json"}
    if auth_header:
        headers["Authorization"] = auth_header
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def _get_json(ip, port, path, timeout=5, auth_header=None):
    headers = {}
    if auth_header:
        headers["Authorization"] = auth_header
    request = urllib.request.Request(
        "http://{}:{}{}".format(ip, port, path),
        headers=headers,
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def _create_tracker_app():
    tracker_app = AsynapRous()
    peers = {}

    def peer_response(peer):
        return {
            "username": peer["username"],
            "ip": peer["ip"],
            "port": peer["port"],
            "status": peer["status"],
            "channels": peer["channels"],
        }

    @tracker_app.route("/login", methods=["POST"])
    def tracker_login(headers=None, body=None):
        data = _json_body(body)
        if data is None:
            return _error("Invalid JSON")

        username = data.get("username")
        port = data.get("port")
        if not _valid_username(username):
            return _error("Missing or invalid username")
        if port is None:
            return _error("Missing port")

        current = peers.get(username, {})
        peers[username] = {
            "username": username,
            "ip": data.get("ip", current.get("ip", "")),
            "port": port,
            "status": "online",
            "channels": current.get("channels", []),
        }
        return {"peer": peer_response(peers[username])}

    @tracker_app.route("/submit-info", methods=["POST"])
    def submit_info(headers=None, body=None):
        data = _json_body(body)
        if data is None:
            return _error("Invalid JSON")

        username = data.get("username")
        port = data.get("port")
        channels = data.get("channels", [])
        if not _valid_username(username):
            return _error("Missing or invalid username")
        if port is None:
            return _error("Missing port")
        if not isinstance(channels, list):
            return _error("channels must be a list")

        peers[username] = {
            "username": username,
            "ip": data.get("ip", ""),
            "port": port,
            "status": "online",
            "channels": channels,
        }
        return {"peer": peer_response(peers[username])}

    @tracker_app.route("/get-list", methods=["GET"])
    def get_list(headers=None, body=None):
        return {"peers": [peer_response(peer) for peer in peers.values()]}

    @tracker_app.route("/logout", methods=["POST"])
    def logout(headers=None, body=None):
        data = _json_body(body)
        if data is None:
            return _error("Invalid JSON")

        username = data.get("username")
        if not _valid_username(username):
            return _error("Missing or invalid username")
        if username in peers:
            peers[username]["status"] = "offline"
        return {"message": "logged out", "username": username}

    return tracker_app


def _create_peer_app(username, peer_ip, peer_port, tracker_ip, tracker_port, auth_user, auth_password):
    peer_app = AsynapRous()
    credentials = {auth_user: auth_password}
    peer_app.prepare_auth(credentials, realm="Hybrid Chat Peer")
    auth_token = "{}:{}".format(auth_user, auth_password).encode("utf-8")
    auth_header = "Basic {}".format(base64.b64encode(auth_token).decode("ascii"))
    state = {
        "username": username,
        "ip": peer_ip,
        "port": peer_port,
        "tracker_ip": tracker_ip,
        "tracker_port": tracker_port,
        "channels": ["general"],
        "messages": [],
        "notifications": [],
        "known_peers": {},
    }

    def peer_info():
        return {
            "username": state["username"],
            "ip": state["ip"],
            "port": state["port"],
            "channels": state["channels"],
        }

    def register_with_tracker():
        try:
            return _post_json(
                state["tracker_ip"],
                state["tracker_port"],
                "/submit-info",
                peer_info(),
            )
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            print("[SampleApp Peer] tracker registration failed: {}".format(exc))
            return _error(str(exc))

    def ensure_channel(channel):
        if not _valid_channel(channel):
            raise ValueError("Invalid channel")
        if channel not in state["channels"]:
            state["channels"].append(channel)
            register_with_tracker()

    def get_tracker_peers():
        tracker_data = _get_json(state["tracker_ip"], state["tracker_port"], "/get-list")
        return tracker_data.get("peers", [])

    def find_peer(target_username):
        for peer in get_tracker_peers():
            if peer.get("username") == target_username:
                return peer
        return None

    @peer_app.route("/send-peer", methods=["POST"], auth=True)
    def send_peer(headers=None, body=None):
        data = _json_body(body)
        if data is None:
            return _error("Invalid JSON")

        sender = data.get("from")
        message = data.get("message")
        if not _valid_username(sender):
            return _error("Missing or invalid from")
        if not _valid_message(message):
            return _error("Missing or invalid message")

        item = {
            "from": sender,
            "to": data.get("to", state["username"]),
            "channel": data.get("channel", "general"),
            "message": message,
            "timestamp": data.get("timestamp", _now()),
            "direction": "incoming",
        }
        if data.get("type"):
            item["type"] = data.get("type")

        try:
            ensure_channel(item["channel"])
        except ValueError as exc:
            return _error(str(exc))

        state["messages"].append(item)
        state["notifications"].append({
            "type": "new_message",
            "from": item["from"],
            "channel": item["channel"],
            "message": item["message"],
            "timestamp": item["timestamp"],
        })
        return {"ok": True}

    @peer_app.route("/direct-message", methods=["POST"], auth=True)
    def direct_message(headers=None, body=None):
        data = _json_body(body)
        if data is None:
            return _error("Invalid JSON")

        receiver = data.get("to")
        message = data.get("message")
        if not _valid_username(receiver):
            return _error("Missing or invalid to")
        if receiver == state["username"]:
            return _error("Cannot send direct message to self")
        if not _valid_message(message):
            return _error("Missing or invalid message")

        try:
            peer = find_peer(receiver)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            return _error("Cannot get peer list: {}".format(exc))

        if peer is None:
            return _error("Peer '{}' not found".format(receiver))
        if peer.get("status") != "online":
            return _error("Peer '{}' is offline".format(receiver))

        channel = data.get("channel", "general")
        try:
            ensure_channel(channel)
        except ValueError as exc:
            return _error(str(exc))

        item = {
            "from": state["username"],
            "to": receiver,
            "channel": channel,
            "message": message,
            "timestamp": data.get("timestamp", _now()),
        }
        try:
            _post_json(peer.get("ip"), peer.get("port"), "/send-peer", item, auth_header=auth_header)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            return _error("Cannot send message to '{}': {}".format(receiver, exc))

        sent_item = dict(item)
        sent_item["direction"] = "outgoing"
        state["messages"].append(sent_item)
        return {"ok": True, "sent_to": receiver}

    @peer_app.route("/broadcast-peer", methods=["POST"], auth=True)
    def broadcast_peer(headers=None, body=None):
        data = _json_body(body)
        if data is None:
            return _error("Invalid JSON")

        message = data.get("message")
        if not _valid_message(message):
            return _error("Missing or invalid message")

        channel = data.get("channel", "general")
        try:
            ensure_channel(channel)
            peers = get_tracker_peers()
        except (ValueError, urllib.error.URLError, TimeoutError, OSError) as exc:
            return _error(str(exc))

        timestamp = data.get("timestamp", _now())
        state["messages"].append({
            "from": state["username"],
            "to": "*",
            "channel": channel,
            "message": message,
            "timestamp": timestamp,
            "direction": "outgoing",
            "type": "broadcast",
        })

        sent = []
        failed = []
        for peer in peers:
            target_username = peer.get("username")
            if target_username == state["username"]:
                continue
            payload = {
                "from": state["username"],
                "to": target_username,
                "channel": channel,
                "message": message,
                "timestamp": timestamp,
                "type": "broadcast",
            }
            try:
                _post_json(peer.get("ip"), peer.get("port"), "/send-peer", payload, timeout=3, auth_header=auth_header)
                sent.append(target_username)
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                failed.append({"username": target_username, "error": str(exc)})
        return {"ok": True, "sent": sent, "failed": failed}

    @peer_app.route("/connect-peer", methods=["POST"], auth=True)
    def connect_peer(headers=None, body=None):
        data = _json_body(body)
        if data is None:
            return _error("Invalid JSON")
        target_username = data.get("username")
        if not _valid_username(target_username):
            return _error("Missing or invalid username")
        state["known_peers"][target_username] = {
            "username": target_username,
            "ip": data.get("ip", ""),
            "port": data.get("port"),
        }
        return {"ok": True, "known_peers": list(state["known_peers"].values())}

    @peer_app.route("/messages", methods=["GET"], auth=True)
    def messages(headers=None, body=None, query=None):
        channel = (query or {}).get("channel")
        if channel:
            return {"messages": [m for m in state["messages"] if m.get("channel") == channel]}
        return {"messages": state["messages"]}

    @peer_app.route("/channels", methods=["GET"], auth=True)
    def channels(headers=None, body=None):
        return {"channels": state["channels"]}

    @peer_app.route("/notifications", methods=["GET"], auth=True)
    def notifications(headers=None, body=None):
        return {"notifications": state["notifications"]}

    @peer_app.route("/notifications/clear", methods=["POST"], auth=True)
    def clear_notifications(headers=None, body=None):
        state["notifications"].clear()
        return {"ok": True, "notifications": []}

    @peer_app.route("/join-channel", methods=["POST"], auth=True)
    def join_channel(headers=None, body=None):
        data = _json_body(body)
        if data is None:
            return _error("Invalid JSON")
        channel = data.get("channel")
        if not _valid_channel(channel):
            return _error("Missing or invalid channel")
        ensure_channel(channel)
        return {"ok": True, "channels": state["channels"]}

    @peer_app.route("/peer-info", methods=["GET"], auth=True)
    def get_peer_info(headers=None, body=None):
        return {
            "username": state["username"],
            "ip": state["ip"],
            "port": state["port"],
            "tracker": {"ip": state["tracker_ip"], "port": state["tracker_port"]},
        }

    @peer_app.route("/peers", methods=["GET"], auth=True)
    def peers(headers=None, body=None):
        try:
            return {"peers": get_tracker_peers()}
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            return _error("Cannot get peer list: {}".format(exc))

    register_with_tracker()
    return peer_app


def create_sampleapp(
    ip,
    port,
    role="sample",
    username=None,
    tracker_ip="127.0.0.1",
    tracker_port=8000,
    auth_user="admin",
    auth_password="password",
):
    # Prepare and launch the RESTful application
    if role == "sample":
        selected_app = app
    elif role == "tracker":
        selected_app = _create_tracker_app()
    elif role == "peer":
        if not _valid_username(username):
            raise ValueError("A valid --username is required for peer role")
        selected_app = _create_peer_app(
            username,
            ip,
            port,
            tracker_ip,
            tracker_port,
            auth_user,
            auth_password,
        )
    else:
        raise ValueError("Unsupported sample app role: {}".format(role))

    selected_app.prepare_address(ip, port)
    selected_app.run()
