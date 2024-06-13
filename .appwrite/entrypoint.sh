#!/bin/sh

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI application
uvicorn src.main:app --host 0.0.0.0 --port 3000
