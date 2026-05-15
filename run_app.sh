#!/bin/bash

# Script to run the Hybrid Chat App on Unix/macOS

# Kill existing processes on these ports if any
lsof -ti:8000,9001,9002,8080 | xargs kill -9 2>/dev/null

# Set default mode or use provided argument
MODE=${1:-threading}

echo "Starting Hybrid Chat App Infrastructure in $MODE mode..."

# 1. Start Tracker Server
echo "[1/4] Starting Tracker on port 8000..."
python3 start_sampleapp.py --role tracker --server-port 8000 --mode $MODE > tracker.log 2>&1 &
TRACKER_PID=$!

sleep 2

# 2. Start Peer Alice
echo "[2/4] Starting Peer Alice on port 9001..."
python3 start_sampleapp.py --role peer --username alice --server-port 9001 --mode $MODE > alice.log 2>&1 &
ALICE_PID=$!

# 3. Start Bob
echo "[3/4] Starting Peer Bob on port 9002..."
python3 start_sampleapp.py --role peer --username bob --server-port 9002 --mode $MODE > bob.log 2>&1 &
BOB_PID=$!

# 4. Start Proxy Server
echo "[4/4] Starting Proxy Server on port 8080..."
python3 start_proxy.py > proxy.log 2>&1 &
PROXY_PID=$!

echo "------------------------------------------------"
echo "All systems started using $MODE mode!"
echo "- Tracker: http://127.0.0.1:8000"
echo "- Alice:   http://127.0.0.1:9001/chat.html (admin:password)"
echo "- Bob:     http://127.0.0.1:9002/chat.html (admin:password)"
echo "- Proxy:   http://127.0.0.1:8080"
echo "------------------------------------------------"
echo "Logs are being written to: tracker.log, alice.log, bob.log, proxy.log"
echo "Press Ctrl+C to stop all servers."

# Trap Ctrl+C and kill background processes
trap "echo 'Stopping servers...'; kill $TRACKER_PID $ALICE_PID $BOB_PID $PROXY_PID; exit" INT

# Wait for background processes
wait
