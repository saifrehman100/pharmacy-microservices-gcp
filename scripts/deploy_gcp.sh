#!/bin/bash

# GCP Deployment Script
# This script automates the deployment to Google Cloud Platform

set -e

echo "======================================"
echo "Pharmacy Microservices - GCP Deploy"
echo "======================================"
echo ""

# Check if PROJECT_ID is set
if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID environment variable is not set"
    echo "Usage: PROJECT_ID=your-project-id bash scripts/deploy_gcp.sh"
    exit 1
fi

echo "Deploying to project: $PROJECT_ID"
echo ""

# Step 1: Enable required APIs
echo "Step 1: Enabling required GCP APIs..."
gcloud services enable container.googleapis.com --project=$PROJECT_ID
gcloud services enable pubsub.googleapis.com --project=$PROJECT_ID
gcloud services enable containerregistry.googleapis.com --project=$PROJECT_ID

# Step 2: Build and push Docker images
echo ""
echo "Step 2: Building and pushing Docker images..."

services=("api-gateway" "product-service" "order-service" "inventory-service")

for service in "${services[@]}"; do
    echo "Building $service..."
    docker build -t gcr.io/$PROJECT_ID/$service:latest ./services/$service
    docker push gcr.io/$PROJECT_ID/$service:latest
done

# Step 3: Create Pub/Sub resources
echo ""
echo "Step 3: Creating Pub/Sub resources..."

# Create topic
gcloud pubsub topics create order-events --project=$PROJECT_ID 2>/dev/null || echo "Topic already exists"

# Create subscription
gcloud pubsub subscriptions create inventory-order-subscription \
    --topic=order-events \
    --project=$PROJECT_ID 2>/dev/null || echo "Subscription already exists"

# Step 4: Create GKE cluster (if it doesn't exist)
echo ""
echo "Step 4: Checking for GKE cluster..."

if ! gcloud container clusters describe pharmacy-cluster --zone=us-central1-a --project=$PROJECT_ID &>/dev/null; then
    echo "Creating GKE cluster..."
    gcloud container clusters create pharmacy-cluster \
        --zone=us-central1-a \
        --num-nodes=3 \
        --machine-type=e2-medium \
        --enable-autoscaling \
        --min-nodes=3 \
        --max-nodes=10 \
        --project=$PROJECT_ID
else
    echo "GKE cluster already exists"
fi

# Step 5: Get cluster credentials
echo ""
echo "Step 5: Configuring kubectl..."
gcloud container clusters get-credentials pharmacy-cluster --zone=us-central1-a --project=$PROJECT_ID

# Step 6: Update manifests with project ID
echo ""
echo "Step 6: Updating Kubernetes manifests..."

# This is a simple replacement - in production, use a templating tool like Kustomize or Helm
find k8s/base -type f -name "*.yaml" -exec sed -i.bak "s/YOUR_PROJECT_ID/$PROJECT_ID/g" {} \;

# Step 7: Deploy to Kubernetes
echo ""
echo "Step 7: Deploying to Kubernetes..."

kubectl apply -f k8s/base/namespace.yaml
kubectl apply -f k8s/base/configmap.yaml
kubectl apply -f k8s/base/secrets.yaml
kubectl apply -f k8s/base/service-account.yaml
kubectl apply -f k8s/base/api-gateway-deployment.yaml
kubectl apply -f k8s/base/product-service-deployment.yaml
kubectl apply -f k8s/base/order-service-deployment.yaml
kubectl apply -f k8s/base/inventory-service-deployment.yaml
kubectl apply -f k8s/base/hpa.yaml

echo ""
echo "======================================"
echo "Deployment Complete!"
echo "======================================"
echo ""
echo "To check the status of your deployment:"
echo "  kubectl get pods -n pharmacy-system"
echo "  kubectl get services -n pharmacy-system"
echo ""
echo "To get the external IP of the API Gateway:"
echo "  kubectl get service api-gateway -n pharmacy-system"
echo ""
echo "To view logs:"
echo "  kubectl logs -n pharmacy-system -l app=api-gateway"
echo ""
