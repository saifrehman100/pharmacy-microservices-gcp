#!/bin/bash

# API Testing Script for Pharmacy Microservices
# This script tests all major endpoints to verify the system is working

API_GATEWAY="http://localhost:8000"

echo "======================================"
echo "Pharmacy Microservices - API Test"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test health endpoints
echo "1. Testing Health Endpoints..."
echo "------------------------------"

services=("api-gateway:8000" "product-service:8001" "order-service:8002" "inventory-service:8003")

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/health)
    if [ "$response" -eq 200 ]; then
        echo -e "${GREEN}✓${NC} $name is healthy"
    else
        echo -e "${RED}✗${NC} $name is not responding (HTTP $response)"
    fi
done

echo ""
echo "2. Testing Authentication..."
echo "------------------------------"

# Register a test user
echo "Registering user..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_GATEWAY/auth/register" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User"
    }')

echo "Register response: $REGISTER_RESPONSE"

# Login
echo "Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_GATEWAY/auth/login" \
    -H "Content-Type: application/json" \
    -d '{
        "username": "testuser",
        "password": "testpass123"
    }')

# Extract token
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}✗${NC} Failed to get authentication token"
    echo "Response: $LOGIN_RESPONSE"
else
    echo -e "${GREEN}✓${NC} Successfully authenticated"
fi

echo ""
echo "3. Testing Product Service..."
echo "------------------------------"

# List products
echo "Fetching products..."
PRODUCTS_RESPONSE=$(curl -s -X GET "$API_GATEWAY/products?page=1&page_size=5" \
    -H "Authorization: Bearer $TOKEN")

echo "Products: $PRODUCTS_RESPONSE" | head -c 200
echo "..."

echo ""
echo "4. Testing Order Service..."
echo "------------------------------"

# Create an order
echo "Creating a test order..."
ORDER_RESPONSE=$(curl -s -X POST "$API_GATEWAY/orders" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "user_id": 1,
        "products": [
            {
                "product_id": 1,
                "quantity": 2,
                "price": 9.99
            }
        ],
        "shipping_address": "123 Main St, City, State 12345"
    }')

ORDER_ID=$(echo $ORDER_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -z "$ORDER_ID" ]; then
    echo -e "${RED}✗${NC} Failed to create order"
    echo "Response: $ORDER_RESPONSE"
else
    echo -e "${GREEN}✓${NC} Order created with ID: $ORDER_ID"
fi

echo ""
echo "5. Testing Inventory Service..."
echo "------------------------------"

# Check inventory for product 1
echo "Checking inventory for product 1..."
INVENTORY_RESPONSE=$(curl -s -X GET "$API_GATEWAY/inventory/1" \
    -H "Authorization: Bearer $TOKEN")

echo "Inventory: $INVENTORY_RESPONSE"

# Check low stock
echo ""
echo "Checking low stock items..."
LOW_STOCK_RESPONSE=$(curl -s -X GET "$API_GATEWAY/inventory/low-stock" \
    -H "Authorization: Bearer $TOKEN")

echo "Low stock items: $LOW_STOCK_RESPONSE"

echo ""
echo "======================================"
echo "API Testing Complete!"
echo "======================================"
echo ""
echo "To explore the API interactively, visit:"
echo "  $API_GATEWAY/docs"
