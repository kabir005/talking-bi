#!/bin/bash

# Deployment script for Talking BI
# Run this on your EC2 instance after setup

set -e

echo "=========================================="
echo "Talking BI - Deployment"
echo "=========================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please create .env file from .env.example"
    exit 1
fi

# Pull latest changes
echo "Pulling latest changes..."
git pull origin main

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down

# Remove old images
echo "Removing old images..."
docker-compose rm -f

# Build new images
echo "Building new images..."
docker-compose build --no-cache

# Start services
echo "Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "Waiting for services to start..."
sleep 10

# Check service health
echo "Checking service health..."
docker-compose ps

# Show logs
echo "Recent logs:"
docker-compose logs --tail=50

echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Services:"
echo "- Frontend: http://$(curl -s ifconfig.me)"
echo "- Backend API: http://$(curl -s ifconfig.me):8000"
echo "- API Docs: http://$(curl -s ifconfig.me):8000/docs"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo "=========================================="
