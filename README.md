# AsynapRous: Non-blocking HTTP Server Framework & Hybrid Chat App

AsynapRous is an HTTP Server project built from scratch in Python, focusing on non-blocking concurrency and its application in a Hybrid Chat system (combining Client-Server and Peer-to-Peer architectures).

This project was developed as an assignment for the Computer Network course (CO3093/CO3094) at Ho Chi Minh City University of Technology (HCMUT).

## 🚀 Key Features

### 1. HTTP Server Framework (`AsynapRous`)
- **Multiple Concurrency Modes:**
  - **Threading:** One thread per connection.
  - **Callback (Event-driven):** Uses the `selectors` module to manage multiple sockets in a single thread (Non-blocking I/O).
  - **Coroutine (Async/Await):** Leverages `asyncio` for high-performance asynchronous execution.
- **Routing:** Decorator-based routing system similar to Flask (`@app.route`).
- **Middleware/Security:** Supports Basic Authentication and Cookie-based Session management.
- **Static Files:** Serves static assets (HTML, CSS, JS, Images) from `www/` and `static/` directories.

### 2. Hybrid Chat Application
- **Tracker Server:** Acts as a centralized server for Peer registration and Service Discovery.
- **Peer Server:** Each user runs their own server. Peers exchange messages directly (P2P) without going through the Tracker.
- **Chat Features:** Group channels, Direct Messaging (Private), and a Notification system.

### 3. Reverse Proxy
- Supports Hostname-based routing.
- Load Balancing using the Round-robin algorithm.
- Custom Header injection (`proxy_set_header`).

## 🛠 Project Structure

```text
.
├── apps/                # Sample applications (Chat, Tracker, Peer)
├── config/              # Proxy and system configurations
├── daemon/              # Core framework (AsynapRous)
│   ├── asynaprous.py    # Main Router and logic
│   ├── backend.py       # Concurrency handling (Threading, Callback, Coroutine)
│   ├── httpadapter.py   # HTTP Request/Response processing
│   └── ...
├── scripts/             # Automated test scripts
├── static/              # Static assets (CSS, Images)
├── www/                 # Web UI (HTML)
├── run_app.bat          # Windows automation script
├── run_app.sh           # Unix/macOS automation script
├── start_backend.py     # Entry point for a basic backend server
├── start_proxy.py       # Entry point for the Reverse Proxy
└── start_sampleapp.py   # Main entry point for the Chat App (Tracker/Peer)
```

## 💻 Getting Started

### 1. Quick Start (Recommended)

The easiest way to start the entire infrastructure (Tracker, 2 Peers, and Proxy) is to use the provided automation scripts.

**On Windows:**
```powershell
# Default mode (threading)
.\run_app.bat

# Or specify a mode: threading, callback, or coroutine
.\run_app.bat coroutine
```

**On Unix/macOS:**
```bash
chmod +x run_app.sh
# Default mode (threading)
./run_app.sh

# Or specify a mode
./run_app.sh callback
```

The scripts will automatically:
1. Clean up existing processes on ports 8000, 9001, 9002, and 8080.
2. Launch the **Tracker** (Port 8000).
3. Launch **Peer Alice** (Port 9001).
4. Launch **Peer Bob** (Port 9002).
5. Launch the **Reverse Proxy** (Port 8080).

### 2. Manual Execution

If you prefer to run components manually:

**Terminal 1: Start the Tracker Server**
```bash
python start_sampleapp.py --role tracker --server-port 8000
```

**Terminal 2: Start Alice's Peer**
```bash
python start_sampleapp.py --role peer --username alice --server-port 9001 --tracker-port 8000
```

**Terminal 3: Start Bob's Peer**
```bash
python start_sampleapp.py --role peer --username bob --server-port 9002 --tracker-port 8000
```

### 3. Accessing the UI

Once the servers are running, access the Chat UI at:
- Alice: `http://127.0.0.1:9001/chat.html`
- Bob: `http://127.0.0.1:9002/chat.html`
*(Default login: `admin` / `password`)*

## ⚙️ Configuration

### Concurrency Modes
You can toggle the concurrency backend using the `--mode` argument in any `start_*.py` script or as the first argument to the `run_app` scripts.
- `threading`: Multi-threaded (classic).
- `callback`: Event-driven with `selectors` (non-blocking).
- `coroutine`: `asyncio`-based (modern).

### Reverse Proxy
Configure your virtual hosts in `config/proxy.conf`. The proxy supports round-robin load balancing and custom header forwarding.

## 🧪 Testing

The project includes automated scripts to verify stability and features:

```bash
# Test basic chat flow
python scripts/test_chat_flow.py

# Test new infrastructure features
python scripts/test_new_features.py
```

## 📝 License & Credits
Copyright (C) 2026 **pdnguyen** - HCMC University of Technology (VNU-HCM).
This project is released for educational purposes as part of the CO3093/CO3094 course.
