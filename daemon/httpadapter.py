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
daemon.httpadapter
~~~~~~~~~~~~~~~~~

This module provides a http adapter object to manage and persist 
http settings (headers, bodies). The adapter supports both
raw URL paths and RESTful route definitions, and integrates with
Request and Response objects to handle client-server communication.
"""

from .request import Request
from .response import Response
from .utils import (
    SESSION_COOKIE_NAME,
    build_basic_challenge,
    build_set_cookie,
    create_session,
    get_session_user,
    verify_basic_auth,
)

import asyncio
import inspect
import json

class HttpAdapter:
    """
    A mutable :class:`HTTP adapter <HTTP adapter>` for managing client connections
    and routing requests.

    The `HttpAdapter` class encapsulates the logic for receiving HTTP requests,
    dispatching them to appropriate route handlers, and constructing responses.
    It supports RESTful routing via hooks and integrates with :class:`Request <Request>` 
    and :class:`Response <Response>` objects for full request lifecycle management.

    Attributes:
        ip (str): IP address of the client.
        port (int): Port number of the client.
        conn (socket): Active socket connection.
        connaddr (tuple): Address of the connected client.
        routes (dict): Mapping of route paths to handler functions.
        request (Request): Request object for parsing incoming data.
        response (Response): Response object for building and sending replies.
    """

    __attrs__ = [
        "ip",
        "port",
        "conn",
        "connaddr",
        "routes",
        "request",
        "response",
    ]

    def __init__(self, ip, port, conn, connaddr, routes):
        """
        Initialize a new HttpAdapter instance.

        :param ip (str): IP address of the client.
        :param port (int): Port number of the client.
        :param conn (socket): Active socket connection.
        :param connaddr (tuple): Address of the connected client.
        :param routes (dict): Mapping of route paths to handler functions.
        """

        #: IP address.
        self.ip = ip
        #: Port.
        self.port = port
        #: Connection
        self.conn = conn
        #: Conndection address
        self.connaddr = connaddr
        #: Routes
        self.routes = routes
        #: Request
        self.request = Request()
        #: Response
        self.response = Response()

    def handle_client(self, conn, addr, routes):
        """
        Handle an incoming client connection.

        This method reads the request from the socket, prepares the request object,
        invokes the appropriate route handler if available, builds the response,
        and sends it back to the client.

        :param conn (socket): The client socket connection.
        :param addr (tuple): The client's address.
        :param routes (dict): The route mapping for dispatching requests.
        """

        # Connection handler.
        self.conn = conn        
        # Connection address.
        self.connaddr = addr
        # Request handler
        req = self.request
        # Response handler
        resp = self.response

        # Handle the request
        msg = self._recv_http_request(conn).decode("utf-8", errors="replace")
        req.prepare(msg, routes)
        print("[HttpAdapter] Invoke handle_client connection {}".format(addr))

        response = self._dispatch_request(req, resp)

        #print("[HttpAdapter] Response content {}".format(response))
        conn.sendall(response)
        conn.close()

    def _recv_http_request(self, conn):
        """Read headers and the full body declared by Content-Length."""
        data = b""
        while b"\r\n\r\n" not in data:
            chunk = conn.recv(1024)
            if not chunk:
                return data
            data += chunk

        header_bytes, body = data.split(b"\r\n\r\n", 1)
        content_length = 0
        for line in header_bytes.decode("iso-8859-1").split("\r\n")[1:]:
            if line.lower().startswith("content-length:"):
                try:
                    content_length = int(line.split(":", 1)[1].strip())
                except ValueError:
                    content_length = 0
                break

        while len(body) < content_length:
            chunk = conn.recv(content_length - len(body))
            if not chunk:
                break
            body += chunk

        return header_bytes + b"\r\n\r\n" + body

    def _build_hook_response(self, result, status_code=200, reason="OK", headers=None):
        """Serialize route handler output into a minimal HTTP response."""
        headers = headers or {}
        content_type = "text/plain; charset=utf-8"

        if isinstance(result, bytes):
            body = result
            stripped = body.lstrip()
            if stripped.startswith((b"{", b"[")):
                content_type = "application/json; charset=utf-8"
            elif stripped.startswith(b"<"):
                content_type = "text/html; charset=utf-8"
        elif isinstance(result, (dict, list)):
            body = json.dumps(result).encode("utf-8")
            content_type = "application/json; charset=utf-8"
        elif isinstance(result, str):
            body = result.encode("utf-8")
            if result.lstrip().startswith("<"):
                content_type = "text/html; charset=utf-8"
        else:
            body = str(result).encode("utf-8")

        header = (
            "HTTP/1.1 {} {}\r\n"
            "Content-Type: {}\r\n"
            "Content-Length: {}\r\n"
        ).format(status_code, reason, content_type, len(body))
        for key, value in headers.items():
            if isinstance(value, list):
                for item in value:
                    header += "{}: {}\r\n".format(key, item)
            else:
                header += "{}: {}\r\n".format(key, value)
        header += "Connection: close\r\n\r\n"
        header = header.encode("utf-8")
        return header + body

    def _authorize_request(self, req):
        """Check session cookie or Basic Auth for protected routes."""
        if not getattr(req.hook, "_auth_required", False):
            return True, None, {}

        session_user = get_session_user(req.cookies or {})
        if session_user:
            req.auth_user = session_user
            return True, session_user, {}

        credentials = getattr(req.hook, "_auth_credentials", None)
        username = verify_basic_auth(req.headers or {}, credentials)
        if not username:
            return False, None, {
                "WWW-Authenticate": build_basic_challenge(
                    getattr(req.hook, "_auth_realm", "AsynapRous")
                )
            }

        req.auth_user = username
        token = create_session(username)
        return True, username, {
            "Set-Cookie": build_set_cookie(SESSION_COOKIE_NAME, token),
        }

    def _dispatch_request(self, req, resp):
        """Call a matched route hook or fall back to static-file response."""
        if not req.hook:
            return resp.build_response(req)

        authorized, _username, auth_headers = self._authorize_request(req)
        if not authorized:
            return self._build_hook_response(
                {"error": "Unauthorized"},
                status_code=401,
                reason="Unauthorized",
                headers=auth_headers,
            )

        result = req.hook(**self._hook_kwargs(req))
        if inspect.isawaitable(result):
            result = asyncio.run(result)
        return self._build_hook_response(result, headers=auth_headers)

    async def _dispatch_request_async(self, req, resp):
        """Async variant of route dispatch for stream-based connections."""
        if not req.hook:
            return resp.build_response(req)

        authorized, _username, auth_headers = self._authorize_request(req)
        if not authorized:
            return self._build_hook_response(
                {"error": "Unauthorized"},
                status_code=401,
                reason="Unauthorized",
                headers=auth_headers,
            )

        result = req.hook(**self._hook_kwargs(req))
        if inspect.isawaitable(result):
            result = await result
        return self._build_hook_response(result, headers=auth_headers)

    def _hook_kwargs(self, req):
        """Build route-handler kwargs without breaking older handlers."""
        kwargs = {"headers": req.headers, "body": req.body}
        try:
            signature = inspect.signature(req.hook)
        except (TypeError, ValueError):
            return kwargs

        if "query" in signature.parameters:
            kwargs["query"] = req.query
        if "auth_user" in signature.parameters:
            kwargs["auth_user"] = getattr(req, "auth_user", None)
        return kwargs

    async def handle_client_coroutine(self, reader, writer):
        """
        Handle an incoming client connection using stream reader writer asynchronously.

        This method reads the request from the socket, prepares the request object,
        invokes the appropriate route handler if available, builds the response,
        and sends it back to the client.

        :param conn (socket): The client socket connection.
        :param addr (tuple): The client's address.
        :param routes (dict): The route mapping for dispatching requests.
        """
        # Request handler
        req = self.request
        # Response handler
        resp = self.response

        addr = writer.get_extra_info("peername")
        print("[HttpAdapter] Invoke handle_client_coroutine connection {}".format(addr))

        msg = await self._read_http_stream(reader)
        req.prepare(msg.decode("utf-8", errors="replace"), self.routes)
        response = await self._dispatch_request_async(req, resp)

        # Send all the response asynchronously
        writer.write(response)
        await writer.drain()

    async def _read_http_stream(self, reader):
        """Read headers and the full body declared by Content-Length from streams."""
        data = await reader.readuntil(b"\r\n\r\n")
        header_bytes, body = data.split(b"\r\n\r\n", 1)
        content_length = 0
        for line in header_bytes.decode("iso-8859-1").split("\r\n")[1:]:
            if line.lower().startswith("content-length:"):
                try:
                    content_length = int(line.split(":", 1)[1].strip())
                except ValueError:
                    content_length = 0
                break

        if len(body) < content_length:
            body += await reader.readexactly(content_length - len(body))

        return header_bytes + b"\r\n\r\n" + body

    @property
    def extract_cookies(self, req, resp):
        """
        Build cookies from the :class:`Request <Request>` headers.

        :param req:(Request) The :class:`Request <Request>` object.
        :param resp: (Response) The res:class:`Response <Response>` object.
        :rtype: cookies - A dictionary of cookie key-value pairs.
        """
        cookies = {}
        for header in headers:
            if header.startswith("Cookie:"):
                cookie_str = header.split(":", 1)[1].strip()
                for pair in cookie_str.split(";"):
                    key, value = pair.strip().split("=")
                    cookies[key] = value
        return cookies

    def build_response(self, req, resp):
        """Builds a :class:`Response <Response>` object 

        :param req: The :class:`Request <Request>` used to generate the response.
        :param resp: The  response object.
        :rtype: Response
        """
        response = Response()

        # Set encoding.
        response.encoding = get_encoding_from_headers(response.headers)
        response.raw = resp
        response.reason = response.raw.reason

        if isinstance(req.url, bytes):
            response.url = req.url.decode("utf-8")
        else:
            response.url = req.url

        # Add new cookies from the server.
        response.cookies = extract_cookies(req)

        # Give the Response some context.
        response.request = req
        response.connection = self

        return response

    def build_json_response(self, req, resp):
        """Builds a :class:`Response <Response>` object from JSON data

        :param req: The :class:`Request <Request>` used to generate the response.
        :param resp: The  response object.
        :rtype: Response
        """
        response = Response(req)

        # Set encoding.
        response.raw = resp

        if isinstance(req.url, bytes):
            response.url = req.url.decode("utf-8")
        else:
            response.url = req.url

        # Give the Response some context.
        response.request = req
        response.connection = self

        return response


    # def get_connection(self, url, proxies=None):
        # """Returns a url connection for the given URL. 

        # :param url: The URL to connect to.
        # :param proxies: (optional) A Requests-style dictionary of proxies used on this request.
        # :rtype: int
        # """

        # proxy = select_proxy(url, proxies)

        # if proxy:
            # proxy = prepend_scheme_if_needed(proxy, "http")
            # proxy_url = parse_url(proxy)
            # if not proxy_url.host:
                # raise InvalidProxyURL(
                    # "Please check proxy URL. It is malformed "
                    # "and could be missing the host."
                # )
            # proxy_manager = self.proxy_manager_for(proxy)
            # conn = proxy_manager.connection_from_url(url)
        # else:
            # # Only scheme should be lower case
            # parsed = urlparse(url)
            # url = parsed.geturl()
            # conn = self.poolmanager.connection_from_url(url)

        # return conn


    def add_headers(self, request):
        """
        Add headers to the request.

        This method is intended to be overridden by subclasses to inject
        custom headers. It does nothing by default.

        
        :param request: :class:`Request <Request>` to add headers to.
        """
        pass

    def build_proxy_headers(self, proxy):
        """Returns a dictionary of the headers to add to any request sent
        through a proxy. 

        :class:`HttpAdapter <HttpAdapter>`.

        :param proxy: The url of the proxy being used for this request.
        :rtype: dict
        """
        headers = {}
        #
        # TODO: build your authentication here
        #       username, password =...
        # we provide dummy auth here
        #
        username, password = ("user1", "password")

        if username:
            headers["Proxy-Authorization"] = (username, password)

        return headers
