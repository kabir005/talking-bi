#!/bin/bash

# Restore script for Talking BI data

set -e

if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <backup-file>"
    echo "Example: ./restore.sh backups/talking-bi-backup-20260407_120000.tar.gz"
    exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "=========================================="
echo "Talking BI - Restore"
echo "=========================================="

# Stop services
echo "Stopping services..."
docker-compose down

# Restore backup
echo "Restoring from: $BACKUP_FILE"
tar -xzf "$BACKUP_FILE"

# Start services
echo "Starting services..."
docker-compose up -d

echo "=========================================="
echo "Restore Complete!"
echo "=========================================="
