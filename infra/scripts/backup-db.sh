#!/bin/bash

# Database backup script for Telegram Automation

set -e

# Configuration
BACKUP_DIR="backups"
DB_FILE="backend/telegram_automation.db"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/telegram_automation_backup_${TIMESTAMP}.db"

echo "Starting database backup..."

# Check if we're in the correct directory
if [ ! -f "backend/app/main.py" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if database file exists
if [ ! -f "$DB_FILE" ]; then
    echo "Warning: Database file not found at $DB_FILE"
    echo "This might be normal if the database hasn't been created yet."
    exit 0
fi

# Create backup
echo "Creating backup: $BACKUP_FILE"
cp "$DB_FILE" "$BACKUP_FILE"

# Verify backup
if [ -f "$BACKUP_FILE" ]; then
    ORIGINAL_SIZE=$(stat -f%z "$DB_FILE" 2>/dev/null || stat -c%s "$DB_FILE" 2>/dev/null)
    BACKUP_SIZE=$(stat -f%z "$BACKUP_FILE" 2>/dev/null || stat -c%s "$BACKUP_FILE" 2>/dev/null)
    
    if [ "$ORIGINAL_SIZE" -eq "$BACKUP_SIZE" ]; then
        echo "Backup created successfully: $BACKUP_FILE"
        echo "Backup size: $BACKUP_SIZE bytes"
    else
        echo "Error: Backup verification failed. Size mismatch."
        rm -f "$BACKUP_FILE"
        exit 1
    fi
else
    echo "Error: Failed to create backup file"
    exit 1
fi

# Clean up old backups (keep last 10)
echo "Cleaning up old backups..."
cd "$BACKUP_DIR"
ls -t telegram_automation_backup_*.db | tail -n +11 | xargs -r rm -f
REMAINING_BACKUPS=$(ls -1 telegram_automation_backup_*.db 2>/dev/null | wc -l)
echo "Remaining backups: $REMAINING_BACKUPS"

cd ..

echo "Database backup completed successfully!"

