#!/bin/bash

# Backup script for Talking BI data

set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="talking-bi-backup-${TIMESTAMP}.tar.gz"

echo "=========================================="
echo "Talking BI - Backup"
echo "=========================================="

# Create backup directory
mkdir -p $BACKUP_DIR

# Stop services
echo "Stopping services..."
docker-compose stop

# Create backup
echo "Creating backup..."
tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" \
    --exclude='*.log' \
    --exclude='__pycache__' \
    --exclude='node_modules' \
    backend/data/ \
    .env

# Restart services
echo "Restarting services..."
docker-compose start

echo "=========================================="
echo "Backup Complete!"
echo "=========================================="
echo "Backup file: ${BACKUP_DIR}/${BACKUP_FILE}"
echo ""
echo "To restore:"
echo "  tar -xzf ${BACKUP_DIR}/${BACKUP_FILE}"
echo "=========================================="
