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
start_sampleapp
~~~~~~~~~~~~~~~~~

This module provides a sample RESTful web application using the AsynapRous framework.

It defines basic route handlers and launches a TCP-based backend server to serve
HTTP requests. The application includes a login endpoint and a greeting endpoint,
and can be configured via command-line arguments.
"""

import json
import socket
import argparse
import os

from apps import create_sampleapp

PORT = 2026  # Default port

if __name__ == "__main__":
    # Parse command-line arguments to configure server IP and port
    parser = argparse.ArgumentParser(prog='Backend', description='', epilog='Beckend daemon')
    parser.add_argument('--server-ip', default='127.0.0.1')
    parser.add_argument('--server-port', type=int, default=PORT)
    parser.add_argument(
        '--role',
        choices=['sample', 'tracker', 'peer'],
        default='sample',
        help='Run the original sample app, tracker, or peer in the original source entrypoint.',
    )
    parser.add_argument('--username', help='Peer username when --role peer is used.')
    parser.add_argument('--tracker-ip', default='127.0.0.1')
    parser.add_argument('--tracker-port', type=int, default=8000)
    parser.add_argument(
        '--auth-user',
        default=os.environ.get('CHAT_AUTH_USER', 'admin'),
        help='Basic Auth username for protected peer APIs.',
    )
    parser.add_argument(
        '--auth-password',
        default=os.environ.get('CHAT_AUTH_PASSWORD', 'password'),
        help='Basic Auth password for protected peer APIs.',
    )
    parser.add_argument(
        '--mode',
        type=str,
        default='threading',
        choices=['threading', 'callback', 'coroutine'],
        help='Concurrency mode for the backend (threading, callback, coroutine). Default is threading.'
    )
 
    args = parser.parse_args()
    ip = args.server_ip
    port = args.server_port

    # Prepare and launch the RESTful application
    create_sampleapp(
        ip,
        port,
        role=args.role,
        username=args.username,
        tracker_ip=args.tracker_ip,
        tracker_port=args.tracker_port,
        auth_user=args.auth_user,
        auth_password=args.auth_password,
        mode=args.mode,
    )
