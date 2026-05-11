# Project TODO List: Non-blocking HTTP Server and Hybrid Chat Application

Based on the assignment specification and current codebase analysis, here is the plan to complete the project.

## 1. Non-blocking Infrastructure (`daemon/backend.py`)
- [ ] **Multi-thread Mode**: Implement thread-per-connection handling in `run_backend`.
- [ ] **Callback Mode**: 
    - [ ] Correctly implement the `selectors` event loop in `run_backend`.
    - [ ] Ensure non-blocking socket operations (`setblocking(False)`).
- [ ] **Coroutine Mode**: 
    - [ ] Refine `async_server` and `handle_client_coroutine`.
    - [ ] Integrate `asyncio` properly with the `AsynapRous` framework.
- [ ] **Dynamic Mode Selection**: Allow switching between modes via configuration or command-line arguments.

## 2. HTTP Server Core (`daemon/httpadapter.py`, `daemon/request.py`, `daemon/response.py`)
- [ ] **Request Parsing**:
    - [ ] Implement robust header extraction (case-insensitive).
    - [ ] Implement body extraction based on `Content-Length`.
    - [ ] Implement cookie parsing from the `Cookie` header.
- [ ] **Response Construction**:
    - [ ] Implement a method to format headers into valid HTTP/1.1 response strings.
    - [ ] Implement dynamic status code and reason phrase mapping.
    - [ ] Support for more MIME types (JSON, CSS, JS, etc.).
- [ ] **Content Serving**:
    - [ ] Implement serving files from `www/` and `static/`.
    - [ ] Implement "App Hook" handling to route requests to `AsynapRous` handlers.
- [ ] **Async Support**: Ensure `HttpAdapter` can handle both sync and async route handlers.

## 3. Authentication & Security (`daemon/utils.py`, `daemon/httpadapter.py`)
- [ ] **HTTP Authentication**:
    - [ ] Implement `WWW-Authenticate` and `Authorization` header handling (Basic/Digest).
    - [ ] Create a mechanism to protect specific routes.
- [ ] **Cookie Management**:
    - [ ] Implement `Set-Cookie` in `Response`.
    - [ ] Implement session tracking using cookies.

## 4. Hybrid Chat Application (`apps/chat/` - New Module)
- [ ] **Client-Server Phase (Tracker)**:
    - [ ] Peer registration API (`/login`, `/submit-info`).
    - [ ] Tracker service to maintain active peer list.
    - [ ] Peer discovery API (`/get-list`).
- [ ] **Peer-to-Peer Phase**:
    - [ ] Peer-to-peer connection setup logic.
    - [ ] Message broadcasting to all connected peers.
    - [ ] Direct peer-to-peer communication.
- [ ] **Channel Management**:
    - [ ] Channel listing and switching.
    - [ ] Notification system for new messages.

## 5. Proxy Server (`daemon/proxy.py`)
- [ ] **Non-blocking Handling**: Implement multi-threading or async handling for proxy connections.
- [ ] **Routing Policies**:
    - [ ] Implement `round-robin` distribution for multiple backends.
    - [ ] Add support for custom headers (`proxy_set_header`).
- [ ] **Error Handling**: Properly handle 404/502/504 errors when backends are unreachable.

## 6. Testing & Validation
- [ ] Create test scripts to verify each non-blocking mode.
- [ ] Validate HTTP compliance using standard browsers and tools (e.g., `curl`).
- [ ] Test hybrid chat functionality with multiple concurrent peers.
- [ ] Verify proxy routing and load balancing.
