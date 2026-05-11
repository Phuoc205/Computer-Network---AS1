#
# Copyright (C) 2026 pdnguyen of HCMC University of Technology VNU-HCM.
# All rights reserved.
# This file is part of the CO3093/CO3094 course.
#
# AsynapRous release
#
# The authors hereby grant to Licensee personal permission to use
# and modify the Licensed Source Code for the sole purpose of studying
# while attending the course
#

"""
daemon.proxy
~~~~~~~~~~~~~~~~~

This module implements a simple proxy server using Python's socket and threading libraries.
It routes incoming HTTP requests to backend services based on hostname mappings and returns
the corresponding responses to clients.

Requirement:
-----------------
- socket: provides socket networking interface.
- threading: enables concurrent client handling via threads.
- response: customized :class: `Response <Response>` utilities.
- httpadapter: :class: `HttpAdapter <HttpAdapter >` adapter for HTTP request processing.
- dictionary: :class: `CaseInsensitiveDict <CaseInsensitiveDict>` for managing headers and cookies.

"""
import socket
import threading
from .response import *
from .httpadapter import HttpAdapter
from .dictionary import CaseInsensitiveDict

#: A dictionary mapping hostnames to backend IP and port tuples.
#: Used to determine routing targets for incoming requests.
PROXY_PASS = {
    "192.168.56.103:8080": ('192.168.56.103', 9000),
    "app1.local": ('192.168.56.103', 9001),
    "app2.local": ('192.168.56.103', 9002),
}


#: State for round-robin policy: {hostname: index}
RR_STATE = {}
RR_LOCK = threading.Lock()

def forward_request(host, port, request):
    """
    Forwards an HTTP request to a backend server and retrieves the response.

    :params host (str): IP address of the backend server.
    :params port (int): port number of the backend server.
    :params request (str): incoming HTTP request.

    :rtype bytes: Raw HTTP response from the backend server. If the connection
                  fails, returns a 502 Bad Gateway response.
    """

    backend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        backend.connect((host, port))
        backend.sendall(request.encode())
        response = b""
        while True:
            chunk = backend.recv(4096)
            if not chunk:
                break
            response += chunk
        return response
    except socket.error as e:
      print("Socket error: {}".format(e))
      return (
            "HTTP/1.1 502 Bad Gateway\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 15\r\n"
            "Connection: close\r\n"
            "\r\n"
            "502 Bad Gateway"
        ).encode('utf-8')


def resolve_routing_policy(hostname, routes):
    """
    Handles an routing policy to return the matching proxy_pass.
    It determines the target backend to forward the request to.

    :params hostname (str): The Host header from the request.
    :params routes (dict): dictionary mapping hostnames and location.
    """

    if hostname not in routes:
        print("[Proxy] Unrecognized hostname: {}".format(hostname))
        return None, None

    proxy_map, policy = routes.get(hostname)
    print("[Proxy] Policy: {} for Host: {}".format(policy, hostname))

    proxy_host = ''
    proxy_port = '9000'

    if isinstance(proxy_map, list):
        if len(proxy_map) == 0:
            print("[Proxy] Empty resolved routing for hostname {}".format(hostname))
            return None, None
        elif len(proxy_map) == 1:
            proxy_host, proxy_port = proxy_map[0].split(":", 1)
        else:
            if policy == 'round-robin':
                with RR_LOCK:
                    index = RR_STATE.get(hostname, 0)
                    target = proxy_map[index % len(proxy_map)]
                    RR_STATE[hostname] = (index + 1) % len(proxy_map)
                print("[Proxy] Round-robin target: {}".format(target))
                proxy_host, proxy_port = target.split(":", 1)
            else:
                # Default to first if policy unknown
                proxy_host, proxy_port = proxy_map[0].split(":", 1)
    else:
        proxy_host, proxy_port = proxy_map.split(":", 1)

    return proxy_host, proxy_port

def handle_client(ip, port, conn, addr, routes):
    """
    Handles an individual client connection by parsing the request,
    determining the target backend, and forwarding the request.

    The handler extracts the Host header from the request to
    matches the hostname against known routes. In the matching
    condition,it forwards the request to the appropriate backend.

    The handler sends the backend response back to the client or
    returns 404 if the hostname is unreachable or is not recognized.

    :params ip (str): IP address of the proxy server.
    :params port (int): port number of the proxy server.
    :params conn (socket.socket): client connection socket.
    :params addr (tuple): client address (IP, port).
    :params routes (dict): dictionary mapping hostnames and location.
    """

    try:
        data = conn.recv(1024)
        if not data:
            conn.close()
            return
        request = data.decode('utf-8', errors='ignore')
    except Exception as e:
        print("[Proxy] Error receiving request: {}".format(e))
        conn.close()
        return

    # Extract hostname from Host header
    hostname = None
    for line in request.splitlines():
        if line.lower().startswith('host:'):
            hostname = line.split(':', 1)[1].strip()
            break

    if not hostname:
        print("[Proxy] Missing Host header from {}".format(addr))
        response = (
            "HTTP/1.1 400 Bad Request\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 15\r\n"
            "Connection: close\r\n"
            "\r\n"
            "400 Bad Request"
        ).encode('utf-8')
        conn.sendall(response)
        conn.close()
        return

    print("[Proxy] Connection from {} for Host: {}".format(addr, hostname))

    # Resolve the matching destination in routes
    resolved_host, resolved_port = resolve_routing_policy(hostname, routes)
    
    if resolved_host:
        try:
            resolved_port = int(resolved_port)
            print("[Proxy] Forwarding to {}:{}".format(resolved_host, resolved_port))
            response = forward_request(resolved_host, resolved_port, request)        
        except ValueError:
            print("[Proxy] Invalid port: {}".format(resolved_port))
            response = (
                "HTTP/1.1 500 Internal Server Error\r\n"
                "Content-Type: text/plain\r\n"
                "Content-Length: 21\r\n"
                "\r\n"
                "500 Internal Server Error"
            ).encode('utf-8')
    else:
        response = (
            "HTTP/1.1 404 Not Found\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 13\r\n"
            "Connection: close\r\n"
            "\r\n"
            "404 Not Found"
        ).encode('utf-8')
    
    try:
        conn.sendall(response)
    except Exception as e:
        print("[Proxy] Error sending response: {}".format(e))
    finally:
        conn.close()

def run_proxy(ip, port, routes):
    """
    Starts the proxy server and listens for incoming connections. 

    The process dinds the proxy server to the specified IP and port.
    In each incomping connection, it accepts the connections and
    spawns a new thread for each client using `handle_client`.
 

    :params ip (str): IP address to bind the proxy server.
    :params port (int): port number to listen on.
    :params routes (dict): dictionary mapping hostnames and location.

    """

    proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        proxy.bind((ip, port))
        proxy.listen(50)
        print("[Proxy] Listening on IP {} port {}".format(ip,port))
        while True:
            conn, addr = proxy.accept()
            print("[Proxy] Connection accepted from {}".format(addr))
            # Multi-thread handling for proxy connections
            proxy_thread = threading.Thread(
                target=handle_client,
                args=(ip, port, conn, addr, routes),
                daemon=True
            )
            proxy_thread.start()
    except socket.error as e:
      print("Socket error: {}".format(e))

def create_proxy(ip, port, routes):
    """
    Entry point for launching the proxy server.

    :params ip (str): IP address to bind the proxy server.
    :params port (int): port number to listen on.
    :params routes (dict): dictionary mapping hostnames and location.
    """

    run_proxy(ip, port, routes)
