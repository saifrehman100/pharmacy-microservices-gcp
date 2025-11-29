#!/bin/bash

# Local Development Setup Script
# This script sets up the local development environment

echo "======================================"
echo "Pharmacy Microservices - Local Setup"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Step 1:${NC} Checking prerequisites..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker is installed"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker Compose is installed"

echo ""
echo -e "${YELLOW}Step 2:${NC} Creating .env file..."

if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓${NC} Created .env file from .env.example"
else
    echo ".env file already exists, skipping..."
fi

echo ""
echo -e "${YELLOW}Step 3:${NC} Building Docker images..."
docker-compose build

echo ""
echo -e "${YELLOW}Step 4:${NC} Starting services..."
docker-compose up -d

echo ""
echo -e "${YELLOW}Step 5:${NC} Waiting for services to be healthy..."
sleep 10

# Check service health
services=("api-gateway" "product-service" "order-service" "inventory-service")
all_healthy=true

for service in "${services[@]}"; do
    status=$(docker inspect --format='{{.State.Health.Status}}' $service 2>/dev/null || echo "not found")
    if [ "$status" = "healthy" ] || docker ps | grep -q $service; then
        echo -e "${GREEN}✓${NC} $service is running"
    else
        echo -e "⚠ $service status: $status"
        all_healthy=false
    fi
done

echo ""
if [ "$all_healthy" = true ]; then
    echo -e "${GREEN}All services are running!${NC}"
else
    echo "Some services may still be starting. Check with: docker-compose ps"
fi

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Services are now running at:"
echo "  API Gateway:        http://localhost:8000"
echo "  API Documentation:  http://localhost:8000/docs"
echo "  Product Service:    http://localhost:8001"
echo "  Order Service:      http://localhost:8002"
echo "  Inventory Service:  http://localhost:8003"
echo ""
echo "Next steps:"
echo "  1. Run seed script: python scripts/seed_data.py"
echo "  2. Test the API:    bash scripts/test_api.sh"
echo "  3. View logs:       docker-compose logs -f"
echo "  4. Stop services:   docker-compose down"
echo ""
