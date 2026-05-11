"""
Manual Hybrid Chat App flow test.

Assumes these servers are already running:
- tracker: 127.0.0.1:8000
- alice:   127.0.0.1:9001
- bob:     127.0.0.1:9002
"""

import json
import sys
import time
import urllib.error
import urllib.request


TRACKER = ("127.0.0.1", 8000)
ALICE = ("127.0.0.1", 9001)
BOB = ("127.0.0.1", 9002)
AUTH_HEADER_VALUE = "Basic YWRtaW46cGFzc3dvcmQ="


def request_json(method, target, path, payload=None, timeout=5, auth=False):
    host, port = target
    url = "http://{}:{}{}".format(host, port, path)
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if auth:
        headers["Authorization"] = AUTH_HEADER_VALUE

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
        return response.status, json.loads(raw) if raw else {}


def pass_step(name, detail=""):
    print("PASS - {}{}".format(name, ": " + detail if detail else ""))


def fail_step(name, detail):
    print("FAIL - {}: {}".format(name, detail))


def run_step(name, fn):
    try:
        detail = fn()
        pass_step(name, detail)
        return True
    except Exception as exc:
        fail_step(name, str(exc))
        return False


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def get_messages(peer):
    status, data = request_json("GET", peer, "/messages", auth=True)
    require(status == 200, "expected HTTP 200")
    return data.get("messages", [])


def main():
    direct_text = "manual direct {}".format(int(time.time()))
    broadcast_text = "manual broadcast {}".format(int(time.time()))
    results = []

    def tracker_list():
        status, data = request_json("GET", TRACKER, "/get-list")
        require(status == 200, "expected HTTP 200")
        peers = data.get("peers", [])
        usernames = {peer.get("username") for peer in peers}
        require("alice" in usernames, "alice is not registered")
        require("bob" in usernames, "bob is not registered")
        return "registered peers={}".format(sorted(usernames))

    results.append(run_step("tracker /get-list", tracker_list))

    def alice_direct_message():
        status, data = request_json(
            "POST",
            ALICE,
            "/direct-message",
            {"to": "bob", "channel": "general", "message": direct_text},
            auth=True,
        )
        require(status == 200, "expected HTTP 200")
        require(data.get("ok") is True, data)
        require(data.get("sent_to") == "bob", data)
        return json.dumps(data)

    results.append(run_step("alice direct-message to bob", alice_direct_message))

    def bob_has_direct_message():
        messages = get_messages(BOB)
        matched = [
            message for message in messages
            if message.get("message") == direct_text
            and message.get("from") == "alice"
            and message.get("direction") == "incoming"
        ]
        require(matched, "direct message not found in bob messages")
        return "bob message count={}".format(len(messages))

    results.append(run_step("bob /messages after direct", bob_has_direct_message))

    def alice_broadcast_message():
        status, data = request_json(
            "POST",
            ALICE,
            "/broadcast-peer",
            {"channel": "general", "message": broadcast_text},
            auth=True,
        )
        require(status == 200, "expected HTTP 200")
        require(data.get("ok") is True, data)
        require("bob" in data.get("sent", []), data)
        return json.dumps(data)

    results.append(run_step("alice broadcast message", alice_broadcast_message))

    def bob_has_broadcast_message():
        messages = get_messages(BOB)
        matched = [
            message for message in messages
            if message.get("message") == broadcast_text
            and message.get("from") == "alice"
            and message.get("direction") == "incoming"
            and message.get("type") == "broadcast"
        ]
        require(matched, "broadcast message not found in bob messages")
        return "bob message count={}".format(len(messages))

    results.append(run_step("bob /messages after broadcast", bob_has_broadcast_message))

    def bob_notifications():
        status, data = request_json("GET", BOB, "/notifications", auth=True)
        require(status == 200, "expected HTTP 200")
        notifications = data.get("notifications", [])
        direct_found = any(item.get("message") == direct_text for item in notifications)
        broadcast_found = any(item.get("message") == broadcast_text for item in notifications)
        require(direct_found, "direct notification not found")
        require(broadcast_found, "broadcast notification not found")
        return "notification count={}".format(len(notifications))

    results.append(run_step("bob /notifications", bob_notifications))

    passed = all(results)
    print("")
    print("SUMMARY: {}".format("PASS" if passed else "FAIL"))
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.URLError as exc:
        print("FAIL - connection error: {}".format(exc))
        print("Make sure tracker, alice, and bob are running.")
        raise SystemExit(1)
    except KeyboardInterrupt:
        raise SystemExit(130)
