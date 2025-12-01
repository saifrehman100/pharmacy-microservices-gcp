# Pharmacy Order Management System - Microservices Architecture

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green?logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)
![Kubernetes](https://img.shields.io/badge/Kubernetes-GKE-blue?logo=kubernetes)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![CI/CD](https://img.shields.io/badge/CI/CD-GitHub_Actions-green?logo=githubactions)
![License](https://img.shields.io/badge/License-MIT-yellow)

A production-ready, cloud-native microservices application for pharmacy order management, built with FastAPI and deployed on Google Cloud Platform (GKE).

**[Live Demo](http://35.223.190.243/docs)** • **[Architecture](#system-architecture)** • **[Quick Start](#quick-start---local-development)** • **[GCP Deployment](#deployment-to-gcp)**

## 🎯 Key Highlights

✅ **Microservices Architecture** - 4 independent, scalable services
✅ **Event-Driven** - Real-time inventory updates via Cloud Pub/Sub
✅ **Auto-Scaling** - Horizontal pod autoscaling (2-10 replicas)
✅ **Zero-Downtime Deployments** - Rolling updates with health checks
✅ **Complete CI/CD** - Automated deployment pipeline with GitHub Actions
✅ **Production-Ready** - Monitoring, logging, and security best practices

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         API Gateway (8000)                       │
│                    JWT Auth, Rate Limiting, Routing              │
└────────────┬────────────────┬─────────────────┬─────────────────┘
             │                │                 │
    ┌────────▼────────┐  ┌────▼─────────┐  ┌───▼────────────┐
    │  Product Service│  │Order Service │  │Inventory Service│
    │     (8001)      │  │    (8002)    │  │     (8003)     │
    │   PostgreSQL    │  │  PostgreSQL  │  │   PostgreSQL   │
    └─────────────────┘  └──────┬───────┘  └────────▲────────┘
                                │                    │
                         ┌──────▼────────────────────┘
                         │    GCP Pub/Sub           │
                         │   (order-events)          │
                         └───────────────────────────┘
```

## Features

### API Gateway Service
- JWT-based authentication and authorization
- Request routing to microservices
- Rate limiting (configurable)
- Request/response logging
- Health check endpoints

### Product Service
- CRUD operations for pharmacy products
- Pagination support
- Search by name and manufacturer
- Category filtering
- SKU-based product identification

### Order Service
- Order creation and management
- Order status tracking
- User order history
- Pub/Sub event publishing for order events
- Automatic total calculation

### Inventory Service
- Real-time inventory tracking
- Automatic inventory updates via Pub/Sub
- Low stock alerts
- Manual inventory adjustments
- Reorder level management

## Technology Stack

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL (one per service)
- **Message Broker**: Google Cloud Pub/Sub
- **Container Orchestration**: Kubernetes (GKE)
- **Cloud Platform**: Google Cloud Platform
- **ORM**: SQLAlchemy
- **API Documentation**: OpenAPI (Swagger)
- **Authentication**: JWT

## Project Structure

```
pharmacy-microservices-gcp/
├── services/
│   ├── api-gateway/          # API Gateway service
│   │   ├── app/
│   │   │   ├── main.py       # Application entry point
│   │   │   ├── auth.py       # JWT authentication
│   │   │   ├── routes.py     # API routes
│   │   │   ├── proxy.py      # Request forwarding
│   │   │   ├── middleware.py # Logging, rate limiting
│   │   │   ├── models.py     # Database models
│   │   │   └── schemas.py    # Pydantic schemas
│   │   ├── tests/            # Unit tests
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── product-service/      # Product management
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── routes.py
│   │   │   ├── models.py
│   │   │   └── schemas.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── order-service/        # Order processing
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── routes.py
│   │   │   ├── pubsub.py     # Pub/Sub publisher
│   │   │   ├── models.py
│   │   │   └── schemas.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── inventory-service/    # Inventory management
│       ├── app/
│       │   ├── main.py
│       │   ├── routes.py
│       │   ├── pubsub_subscriber.py  # Pub/Sub subscriber
│       │   ├── inventory_service.py   # Business logic
│       │   ├── models.py
│       │   └── schemas.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── k8s/                      # Kubernetes manifests
│   ├── base/
│   │   ├── namespace.yaml
│   │   ├── configmap.yaml
│   │   ├── secrets.yaml
│   │   ├── *-deployment.yaml
│   │   ├── hpa.yaml          # Horizontal Pod Autoscaler
│   │   └── ingress.yaml
│   └── README.md
│
├── scripts/
│   ├── seed_data.py          # Seed sample data
│   ├── setup_local.sh        # Local development setup
│   ├── test_api.sh           # API testing script
│   └── deploy_gcp.sh         # GCP deployment automation
│
├── docker-compose.yml        # Local development environment
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## Quick Start - Local Development

### Prerequisites
- Docker and Docker Compose installed
- Python 3.11+ (for running seed scripts)
- 8GB RAM minimum

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/saifrehman100/pharmacy-microservices-gcp
cd pharmacy-microservices-gcp

# Run setup script
bash scripts/setup_local.sh
```

This will:
- Create `.env` file from template
- Build all Docker images
- Start all services and databases

### 2. Seed Sample Data

```bash
# Install requests library
pip install requests

# Run seed script
python scripts/seed_data.py
```

This creates:
- An admin user (username: `admin`, password: `admin123456`)
- 10 sample pharmacy products
- Inventory records for all products

### 3. Test the API

```bash
# Run automated tests
bash scripts/test_api.sh

# Or explore the interactive API documentation
open http://localhost:8000/docs
```

### 4. Access Services

- **API Gateway**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Product Service**: http://localhost:8001/docs
- **Order Service**: http://localhost:8002/docs
- **Inventory Service**: http://localhost:8003/docs

## API Usage Examples

### 1. Register and Login

```bash
# Register a new user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "password123",
    "full_name": "Test User"
  }'

# Login to get JWT token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### 2. Browse Products

```bash
# Get all products (paginated)
curl -X GET "http://localhost:8000/products?page=1&page_size=10" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Search products
curl -X GET "http://localhost:8000/products/search?name=aspirin" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get specific product
curl -X GET "http://localhost:8000/products/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Create an Order

```bash
curl -X POST http://localhost:8000/orders \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "products": [
      {
        "product_id": 1,
        "quantity": 2,
        "price": 9.99
      },
      {
        "product_id": 3,
        "quantity": 1,
        "price": 24.99
      }
    ],
    "shipping_address": "123 Main St, City, State 12345",
    "notes": "Please deliver before 5 PM"
  }'
```

### 4. Check Inventory

```bash
# Get inventory for a product
curl -X GET "http://localhost:8000/inventory/1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get low stock items
curl -X GET "http://localhost:8000/inventory/low-stock" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Adjust inventory
curl -X PUT "http://localhost:8000/inventory/1/adjust" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "adjustment": 50,
    "reason": "Restocking"
  }'
```

## Deployment to GCP

### Prerequisites
- GCP account with billing enabled
- `gcloud` CLI installed and configured
- `kubectl` installed

### Option 1: Automated Deployment

```bash
# Set your GCP project ID
export PROJECT_ID=your-gcp-project-id

# Run deployment script
bash scripts/deploy_gcp.sh
```

### Option 2: Manual Deployment

See detailed instructions in [k8s/README.md](k8s/README.md)

## Event-Driven Architecture

The system uses Google Cloud Pub/Sub for asynchronous communication:

**Order Created Flow:**
1. User creates an order via API Gateway
2. Order Service saves order to database
3. Order Service publishes `order.created` event to Pub/Sub
4. Inventory Service subscribes to events
5. Inventory Service automatically decreases stock levels
6. Low stock alerts are generated if needed

**Benefits:**
- Loose coupling between services
- Resilience (messages are persisted)
- Scalability (parallel processing)
- Event sourcing capability

## Database Schema

### API Gateway - Users Table
```sql
users (
  id SERIAL PRIMARY KEY,
  email VARCHAR UNIQUE,
  username VARCHAR UNIQUE,
  hashed_password VARCHAR,
  full_name VARCHAR,
  is_active BOOLEAN,
  is_admin BOOLEAN,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

### Product Service - Products Table
```sql
products (
  id SERIAL PRIMARY KEY,
  name VARCHAR,
  description TEXT,
  price FLOAT,
  category VARCHAR,
  requires_prescription BOOLEAN,
  manufacturer VARCHAR,
  stock_keeping_unit VARCHAR UNIQUE,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

### Order Service - Orders Table
```sql
orders (
  id SERIAL PRIMARY KEY,
  user_id INTEGER,
  products JSON,
  total_amount FLOAT,
  status VARCHAR,
  shipping_address VARCHAR,
  notes VARCHAR,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

### Inventory Service - Inventory Table
```sql
inventory (
  product_id INTEGER PRIMARY KEY,
  quantity INTEGER,
  reorder_level INTEGER,
  last_updated TIMESTAMP
)
```

## Monitoring and Observability

### Health Checks
All services expose `/health` endpoints for monitoring:
```bash
curl http://localhost:8000/health
```

### Logs
```bash
# Docker Compose
docker-compose logs -f [service-name]

# Kubernetes
kubectl logs -n pharmacy-system -l app=api-gateway -f
```

### Metrics
- Kubernetes automatically provides CPU and memory metrics
- HPA (Horizontal Pod Autoscaler) configured for auto-scaling
- Liveness and readiness probes ensure service availability

## Security Best Practices

1. **JWT Authentication**: All endpoints (except registration/login) require valid JWT tokens
2. **Environment Variables**: Sensitive data stored in environment variables
3. **Database Isolation**: Each service has its own database (database-per-service pattern)
4. **Rate Limiting**: API Gateway implements rate limiting to prevent abuse
5. **HTTPS**: Use HTTPS in production (configured in Ingress)
6. **Secret Management**: Use Google Secret Manager in production

## Scaling Considerations

- **Horizontal Scaling**: Use HPA to scale pods based on CPU/memory
- **Database Scaling**: Consider Cloud SQL with read replicas for production
- **Pub/Sub**: Automatically scales with load
- **Caching**: Redis integration ready for caching frequently accessed data

## Development

### Running Tests

```bash
# API Gateway tests
cd services/api-gateway
pip install -r requirements.txt
pip install pytest
pytest tests/
```

### Adding New Endpoints

1. Add route in `routes.py`
2. Define Pydantic schema in `schemas.py`
3. Update database model in `models.py` if needed
4. Add tests in `tests/`
5. Update API documentation

## Troubleshooting

### Services not starting
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart

# Rebuild if needed
docker-compose up --build
```

### Database connection errors
```bash
# Check database status
docker-compose ps

# Restart databases
docker-compose restart gateway-db product-db order-db inventory-db
```

### Port conflicts
```bash
# Stop services and remove
docker-compose down

# Check ports
lsof -i :8000
lsof -i :8001
```

## Contributing

This is a portfolio project, but suggestions are welcome!

## License

MIT License - feel free to use this project for learning and portfolio purposes.

## Contact

For questions or feedback, please open an issue in the repository.

---

**Built with:** FastAPI, PostgreSQL, Google Cloud Platform, Kubernetes, Docker
