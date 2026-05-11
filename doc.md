# AsynapRous Async Infrastructure Documentation

This document describes the implementation of the non-blocking infrastructure for the AsynapRous HTTP server.

## 1. Backend Modes (`daemon/backend.py`)

The backend supports three modes of operation for handling concurrent client connections:

### 1.1 Multi-threading Mode
- **Mechanism**: Spawns a new daemon thread for each incoming connection.
- **Implementation**: Uses `threading.Thread(target=handle_client, ...)`.
- **Pros**: Simple to implement, works well for I/O bound tasks.
- **Cons**: Overheads associated with thread creation and context switching.

### 1.2 Callback Mode (Event-driven)
- **Mechanism**: Uses the `selectors` module to monitor multiple sockets in a single thread.
- **Implementation**: 
    - The server socket is registered with the selector for `EVENT_READ`.
    - An event loop calls `sel.select()` to wait for ready sockets.
    - When a connection arrives, it is accepted and handled.
- **Pros**: Low overhead, efficient for many concurrent connections.
- **Cons**: More complex implementation, requires non-blocking sockets.

### 1.3 Coroutine Mode (Async/Await)
- **Mechanism**: Uses `asyncio` to handle connections using coroutines.
- **Implementation**:
    - Uses `asyncio.start_server` to create an asynchronous server.
    - `handle_client_coroutine` is used as the client handler.
- **Pros**: Highly scalable, idiomatic for modern Python async programming.
- **Cons**: Requires the entire stack (including handlers) to be async-friendly.

## 2. Dynamic Mode Selection
The server mode can be selected dynamically using the `--mode` command-line argument in `start_backend.py`.

Example usage:
```bash
python start_backend.py --mode threading
python start_backend.py --mode callback
python start_backend.py --mode coroutine
```

The `create_backend` function accepts a `mode` parameter which defaults to `threading`. This parameter is then passed to `run_backend` to initialize the corresponding infrastructure.

## 3. Proxy Infrastructure (`daemon/proxy.py`)
The proxy server has been updated to support concurrent client handling using a multi-threaded approach. 

### 3.1 Multi-threading in Proxy
- **Mechanism**: For every incoming connection accepted by the proxy, a new daemon thread is spawned.
- **Handler**: The `handle_client` function in `daemon/proxy.py` manages the lifecycle of the proxy request, including hostname resolution and backend forwarding.
- **Scalability**: This allows the proxy to handle multiple simultaneous requests from different clients without blocking.

## 4. Implementation Details

### 4.1 Selectors (Callback Mode)
In callback mode, the server socket is set to non-blocking. It is registered with a `DefaultSelector` for `EVENT_READ` events. The main event loop uses `sel.select()` to wait for connections. When a connection is ready, `accept_callback` is invoked to accept the connection and trigger the request handling.

### 4.2 Asyncio (Coroutine Mode)
The coroutine mode uses `asyncio.start_server`. The `handle_client_coroutine` is an `async` function that uses `StreamReader` and `StreamWriter` to communicate with the client. This mode is particularly efficient for high-concurrency scenarios.
