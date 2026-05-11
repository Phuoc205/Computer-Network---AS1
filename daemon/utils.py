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

import base64
import secrets
from urllib.parse import unquote, urlparse


SESSION_COOKIE_NAME = "ASYNAPROUS_SESSION"
DEFAULT_AUTH_CREDENTIALS = {"admin": "password"}
SESSIONS = {}


def get_auth_from_url(url):
    """Given a url with authentication components, extract username/password."""
    parsed = urlparse(url)

    try:
        auth = (unquote(parsed.username), unquote(parsed.password))
    except (AttributeError, TypeError):
        auth = ("", "")

    return auth


def parse_cookie_header(cookie_header):
    """Parse a Cookie header into a plain dictionary."""
    cookies = {}
    if not cookie_header:
        return cookies

    for item in cookie_header.split(";"):
        if "=" not in item:
            continue
        key, value = item.strip().split("=", 1)
        if key:
            cookies[key] = value
    return cookies


def parse_basic_authorization(value):
    """Return (username, password) from a Basic Authorization header."""
    if not value:
        return None, None

    scheme, _, token = value.partition(" ")
    if scheme.lower() != "basic" or not token:
        return None, None

    try:
        decoded = base64.b64decode(token).decode("utf-8")
    except Exception:
        return None, None

    username, sep, password = decoded.partition(":")
    if not sep:
        return None, None
    return username, password


def verify_basic_auth(headers, credentials=None):
    """Validate Basic Auth credentials and return the username on success."""
    credentials = credentials or DEFAULT_AUTH_CREDENTIALS
    username, password = parse_basic_authorization(headers.get("authorization", ""))
    if not username:
        return None
    expected_password = credentials.get(username)
    if expected_password is None:
        return None
    if not secrets.compare_digest(str(expected_password), str(password)):
        return None
    return username


def create_session(username):
    """Create an in-memory session token for an authenticated user."""
    token = secrets.token_urlsafe(24)
    SESSIONS[token] = username
    return token


def get_session_user(cookies):
    """Return the authenticated username from a session cookie if it exists."""
    token = cookies.get(SESSION_COOKIE_NAME)
    if not token:
        return None
    return SESSIONS.get(token)


def build_set_cookie(name, value, path="/", http_only=True, same_site="Lax"):
    """Build one Set-Cookie header value."""
    parts = ["{}={}".format(name, value), "Path={}".format(path)]
    if http_only:
        parts.append("HttpOnly")
    if same_site:
        parts.append("SameSite={}".format(same_site))
    return "; ".join(parts)


def build_basic_challenge(realm="AsynapRous"):
    """Build the WWW-Authenticate challenge for Basic Auth."""
    return 'Basic realm="{}"'.format(realm)
