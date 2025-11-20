#!/bin/sh
echo "Installing email-validator..."
pip install email-validator
echo "Starting uvicorn..."
uvicorn app.main:app --host 0.0.0.0 --port 8000
