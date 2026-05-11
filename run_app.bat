@echo off
title Hybrid Chat App Runner

echo Starting Hybrid Chat App Infrastructure...

:: 1. Start Tracker Server in a new window
echo [1/4] Starting Tracker on port 8000...
start "Tracker" cmd /k "python start_sampleapp.py --role tracker --server-port 8000"

:: Wait for tracker to initialize
timeout /t 2 /nobreak > nul

:: 2. Start Peer Alice
echo [2/4] Starting Peer Alice on port 9001...
start "Alice" cmd /k "python start_sampleapp.py --role peer --username alice --server-port 9001"

:: 3. Start Peer Bob
echo [3/4] Starting Peer Bob on port 9002...
start "Bob" cmd /k "python start_sampleapp.py --role peer --username bob --server-port 9002"

:: 4. Start Proxy Server
echo [4/4] Starting Proxy Server on port 8080...
start "Proxy" cmd /k "python start_proxy.py"

echo ------------------------------------------------
echo All systems started in separate windows!
echo - Tracker: http://127.0.0.1:8000
echo - Alice:   http://127.0.0.1:9001/chat.html (admin:password)
echo - Bob:     http://127.0.0.1:9002/chat.html (admin:password)
echo - Proxy:   http://127.0.0.1:8080
echo ------------------------------------------------
echo Close the individual windows to stop the servers.
pause
