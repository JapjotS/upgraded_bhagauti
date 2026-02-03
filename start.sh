#!/bin/bash

# Upgraded Bhagauti Startup Script
# This script starts all required services

set -e

echo "🚀 Starting Upgraded Bhagauti Trading System..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found! Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your API keys before continuing."
    exit 1
fi

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  Redis is not running. Starting Redis..."
    redis-server --daemonize yes
    sleep 2
fi

echo "✅ Redis is running"

# Start Celery worker in background
echo "🔧 Starting Celery worker..."
celery -A app.core.celery_app worker --loglevel=info &
CELERY_PID=$!

# Start Celery beat for periodic tasks in background
echo "⏰ Starting Celery beat..."
celery -A app.core.celery_app beat --loglevel=info &
BEAT_PID=$!

# Wait a bit for Celery to start
sleep 3

# Start Flask application
echo "🌐 Starting Flask application..."
python app.py

# Cleanup on exit
trap "kill $CELERY_PID $BEAT_PID 2>/dev/null" EXIT
