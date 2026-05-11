# Project TODO List: Non-blocking HTTP Server and Hybrid Chat Application - COMPLETED

Based on the assignment specification and current codebase analysis, the project is now 100% complete.

## 1. Non-blocking Infrastructure (`daemon/backend.py`)
- [x] **Multi-thread Mode**: Implement thread-per-connection handling in `run_backend`.
- [x] **Callback Mode**: 
    - [x] Correctly implement the `selectors` event loop in `run_backend`.
    - [x] Ensure non-blocking socket operations (`setblocking(False)`).
- [x] **Coroutine Mode**: 
    - [x] Refine `async_server` and `handle_client_coroutine`.
    - [x] Integrate `asyncio` properly with the `AsynapRous` framework.
- [x] **Dynamic Mode Selection**: Allow switching between modes via configuration or command-line arguments.

## 2. HTTP Server Core (`daemon/httpadapter.py`, `daemon/request.py`, `daemon/response.py`)
- [x] **Request Parsing**:
    - [x] Implement robust header extraction (case-insensitive).
    - [x] Implement body extraction based on `Content-Length`.
    - [x] Implement cookie parsing from the `Cookie` header.
- [x] **Response Construction**:
    - [x] Implement a method to format headers into valid HTTP/1.1 response strings.
    - [x] Implement dynamic status code and reason phrase mapping.
    - [x] Support for more MIME types (JSON, CSS, JS, etc.).
- [x] **Content Serving**:
    - [x] Implement serving files from `www/` and `static/`.
    - [x] Implement "App Hook" handling to route requests to `AsynapRous` handlers.
- [x] **Async Support**: Ensure `HttpAdapter` can handle both sync and async route handlers.

## 3. Authentication & Security (`daemon/utils.py`, `daemon/httpadapter.py`)
- [x] **HTTP Authentication**:
    - [x] Implement `WWW-Authenticate` and `Authorization` header handling (Basic/Digest).
    - [x] Create a mechanism to protect specific routes.
- [x] **Cookie Management**:
    - [x] Implement `Set-Cookie` in `Response`.
    - [x] Implement session tracking using cookies.

## 4. Hybrid Chat Application (`apps/chat/` - New Module)
- [x] **Client-Server Phase (Tracker)**:
    - [x] Peer registration API (`/login`, `/submit-info`).
    - [x] Tracker service to maintain active peer list.
    - [x] Peer discovery API (`/get-list`).
- [x] **Peer-to-Peer Phase**:
    - [x] Peer-to-peer connection setup logic.
    - [x] Message broadcasting to all connected peers.
    - [x] Direct peer-to-peer communication.
- [x] **Channel Management**:
    - [x] Channel listing and switching.
    - [x] Notification system for new messages.

## 5. Proxy Server (`daemon/proxy.py`)
- [x] **Non-blocking Handling**: Implement multi-threading or async handling for proxy connections.
- [x] **Routing Policies**:
    - [x] Implement `round-robin` distribution for multiple backends.
    - [x] Add support for custom headers (`proxy_set_header`).
- [x] **Error Handling**: Properly handle 404/502/504 errors when backends are unreachable.

## 6. Testing & Validation
- [x] Create test scripts to verify each non-blocking mode.
- [x] Validate HTTP compliance using standard browsers and tools (e.g., `curl`).
- [x] Test hybrid chat functionality with multiple concurrent peers.
- [x] Verify proxy routing and load balancing.
