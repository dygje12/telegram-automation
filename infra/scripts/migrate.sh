#!/bin/bash

# Database migration script for Telegram Automation

set -e

echo "Starting database migration..."

# Check if we're in the correct directory
if [ ! -f "backend/app/main.py" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Change to backend directory
cd backend

# Check if alembic is installed
if ! command -v alembic &> /dev/null; then
    echo "Error: Alembic is not installed. Please install it first:"
    echo "pip install alembic"
    exit 1
fi

# Initialize alembic if not already done
if [ ! -f "alembic.ini" ]; then
    echo "Initializing Alembic..."
    alembic init alembic
    
    # Update alembic.ini with correct database URL
    sed -i 's|sqlalchemy.url = driver://user:pass@localhost/dbname|sqlalchemy.url = sqlite:///./telegram_automation.db|g' alembic.ini
    
    echo "Alembic initialized successfully"
fi

# Check if there are any migration files
if [ ! "$(ls -A alembic/versions/ 2>/dev/null)" ]; then
    echo "Creating initial migration..."
    alembic revision --autogenerate -m "Initial migration"
fi

# Run migrations
echo "Running database migrations..."
alembic upgrade head

echo "Database migration completed successfully!"

# Return to project root
cd ..

echo "Migration script finished."

