
import json
import time
import urllib.request

TRACKER = ("127.0.0.1", 8000)
ALICE = ("127.0.0.1", 9001)
BOB = ("127.0.0.1", 9002)
AUTH_HEADER_VALUE = "Basic YWRtaW46cGFzc3dvcmQ="

def request_json(method, target, path, payload=None, auth=True):
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
    with urllib.request.urlopen(request, timeout=5) as response:
        raw = response.read().decode("utf-8")
        return response.status, json.loads(raw) if raw else {}

def test_broadcast_is_private():
    print("Testing if broadcast is received as private...")
    text = "private broadcast {}".format(int(time.time()))
    status, data = request_json("POST", ALICE, "/broadcast-peer", {"message": text})
    assert status == 200
    assert data["ok"] is True
    
    time.sleep(1)
    
    status, data = request_json("GET", BOB, "/messages", auth=True)
    messages = data.get("messages", [])
    matched = [m for m in messages if m.get("message") == text]
    assert len(matched) > 0, "Bob did not receive broadcast"
    assert matched[0].get("is_private") is True, "Broadcast should be private for receiver"
    print("PASS: Broadcast is private for receiver")

def test_channel_messaging_no_recipient():
    print("Testing channel messaging without recipient...")
    # First, make sure Bob is in the channel
    request_json("POST", BOB, "/join-channel", {"channel": "test-channel"})
    
    text = "channel message {}".format(int(time.time()))
    # Alice sends to channel without 'to'
    status, data = request_json("POST", ALICE, "/direct-message", {"channel": "test-channel", "message": text})
    assert status == 200
    assert data["ok"] is True
    
    time.sleep(1)
    
    status, data = request_json("GET", BOB, "/messages", auth=True)
    messages = data.get("messages", [])
    matched = [m for m in messages if m.get("message") == text]
    assert len(matched) > 0, "Bob did not receive channel message"
    assert matched[0].get("channel") == "test-channel"
    assert matched[0].get("is_private") is False
    print("PASS: Channel messaging without recipient works")

if __name__ == "__main__":
    try:
        test_broadcast_is_private()
        test_channel_messaging_no_recipient()
        print("\nALL NEW FEATURES VERIFIED")
    except Exception as e:
        print("\nFAILURE: {}".format(e))
        import traceback
        traceback.print_exc()
        exit(1)
