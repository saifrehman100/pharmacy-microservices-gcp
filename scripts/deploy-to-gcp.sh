#!/bin/bash

# Pharmacy Microservices - GCP Deployment Script
# This script deploys the entire application to Google Cloud Platform

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Pharmacy Microservices GCP Deployment${NC}"
echo -e "${BLUE}========================================${NC}"

# Configuration Variables
export PROJECT_ID="${PROJECT_ID:-pharmacy-microservices}"
export REGION="${REGION:-us-central1}"
export ZONE="${ZONE:-us-central1-a}"
export CLUSTER_NAME="${CLUSTER_NAME:-pharmacy-cluster}"
export REPO_NAME="${REPO_NAME:-pharmacy-services}"

echo -e "\n${GREEN}Configuration:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Zone: $ZONE"
echo "  Cluster Name: $CLUSTER_NAME"
echo "  Repository: $REPO_NAME"

# Step 1: Set active project
echo -e "\n${GREEN}Step 1: Setting active project...${NC}"
gcloud config set project $PROJECT_ID

# Step 2: Enable required APIs
echo -e "\n${GREEN}Step 2: Enabling required GCP APIs...${NC}"
gcloud services enable \
  container.googleapis.com \
  artifactregistry.googleapis.com \
  pubsub.googleapis.com \
  sqladmin.googleapis.com \
  compute.googleapis.com \
  cloudresourcemanager.googleapis.com

echo -e "${GREEN}✓ APIs enabled${NC}"

# Step 3: Create Artifact Registry repository
echo -e "\n${GREEN}Step 3: Creating Artifact Registry repository...${NC}"
gcloud artifacts repositories create $REPO_NAME \
  --repository-format=docker \
  --location=$REGION \
  --description="Docker repository for pharmacy microservices" \
  || echo "Repository already exists"

echo -e "${GREEN}✓ Artifact Registry ready${NC}"

# Step 4: Configure Docker authentication
echo -e "\n${GREEN}Step 4: Configuring Docker authentication...${NC}"
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Step 5: Build and push Docker images
echo -e "\n${GREEN}Step 5: Building and pushing Docker images...${NC}"

SERVICES=("api-gateway" "product-service" "order-service" "inventory-service")
IMAGE_BASE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}"

for SERVICE in "${SERVICES[@]}"; do
  echo -e "\n${BLUE}Building $SERVICE...${NC}"

  docker build -t ${IMAGE_BASE}/${SERVICE}:latest \
    -t ${IMAGE_BASE}/${SERVICE}:v1.0 \
    ./services/${SERVICE}

  echo -e "${BLUE}Pushing $SERVICE to Artifact Registry...${NC}"
  docker push ${IMAGE_BASE}/${SERVICE}:latest
  docker push ${IMAGE_BASE}/${SERVICE}:v1.0

  echo -e "${GREEN}✓ $SERVICE image pushed${NC}"
done

# Step 6: Create GKE cluster
echo -e "\n${GREEN}Step 6: Creating GKE cluster...${NC}"
gcloud container clusters create $CLUSTER_NAME \
  --zone=$ZONE \
  --num-nodes=3 \
  --machine-type=e2-medium \
  --enable-autoscaling \
  --min-nodes=3 \
  --max-nodes=10 \
  --enable-autorepair \
  --enable-autoupgrade \
  --disk-size=20 \
  --disk-type=pd-standard \
  || echo "Cluster may already exist"

echo -e "${GREEN}✓ GKE cluster created${NC}"

# Step 7: Get cluster credentials
echo -e "\n${GREEN}Step 7: Getting cluster credentials...${NC}"
gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE

# Step 8: Create Pub/Sub topics and subscriptions
echo -e "\n${GREEN}Step 8: Setting up Cloud Pub/Sub...${NC}"

# Create topic for order events
gcloud pubsub topics create order-events || echo "Topic already exists"

# Create subscription for inventory service
gcloud pubsub subscriptions create inventory-order-subscription \
  --topic=order-events \
  --ack-deadline=60 \
  || echo "Subscription already exists"

echo -e "${GREEN}✓ Pub/Sub configured${NC}"

# Step 9: Create Kubernetes namespace
echo -e "\n${GREEN}Step 9: Creating Kubernetes namespace...${NC}"
kubectl apply -f k8s/base/namespace.yaml

# Step 10: Create Kubernetes secrets
echo -e "\n${GREEN}Step 10: Creating Kubernetes secrets...${NC}"

# Generate random passwords for databases
DB_PASSWORD=$(openssl rand -base64 16)
JWT_SECRET=$(openssl rand -base64 32)

kubectl create secret generic app-secrets \
  --namespace=pharmacy \
  --from-literal=jwt-secret-key=$JWT_SECRET \
  --from-literal=db-password=$DB_PASSWORD \
  --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}✓ Secrets created${NC}"

# Step 11: Update ConfigMap with correct values
echo -e "\n${GREEN}Step 11: Creating ConfigMap...${NC}"
kubectl apply -f k8s/base/configmap.yaml

# Step 12: Create Service Account
echo -e "\n${GREEN}Step 12: Creating Service Account for Pub/Sub access...${NC}"

# Create GCP service account
gcloud iam service-accounts create pharmacy-pubsub-sa \
  --display-name="Pharmacy Pub/Sub Service Account" \
  || echo "Service account already exists"

# Grant Pub/Sub permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:pharmacy-pubsub-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/pubsub.publisher"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:pharmacy-pubsub-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/pubsub.subscriber"

# Bind to Kubernetes service account
kubectl apply -f k8s/base/service-account.yaml

gcloud iam service-accounts add-iam-policy-binding \
  pharmacy-pubsub-sa@${PROJECT_ID}.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:${PROJECT_ID}.svc.id.goog[pharmacy/pharmacy-service-account]"

echo -e "${GREEN}✓ Service Account configured${NC}"

# Step 13: Deploy databases (using PostgreSQL on persistent volumes)
echo -e "\n${GREEN}Step 13: Deploying databases...${NC}"

# Apply database deployments (if you have them in k8s/base/)
# kubectl apply -f k8s/base/database-deployments.yaml

# Step 14: Deploy microservices
echo -e "\n${GREEN}Step 14: Deploying microservices...${NC}"

kubectl apply -f k8s/base/product-service-deployment.yaml
kubectl apply -f k8s/base/order-service-deployment.yaml
kubectl apply -f k8s/base/inventory-service-deployment.yaml
kubectl apply -f k8s/base/api-gateway-deployment.yaml

echo -e "${GREEN}✓ Services deployed${NC}"

# Step 15: Apply HPA (Horizontal Pod Autoscaler)
echo -e "\n${GREEN}Step 15: Configuring autoscaling...${NC}"
kubectl apply -f k8s/base/hpa.yaml

# Step 16: Create Ingress
echo -e "\n${GREEN}Step 16: Creating Ingress...${NC}"
kubectl apply -f k8s/base/ingress.yaml

# Step 17: Wait for services to be ready
echo -e "\n${GREEN}Step 17: Waiting for services to be ready...${NC}"
kubectl wait --namespace=pharmacy \
  --for=condition=ready pod \
  --selector=app=api-gateway \
  --timeout=300s

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete! 🎉${NC}"
echo -e "${GREEN}========================================${NC}"

# Get service information
echo -e "\n${BLUE}Service Information:${NC}"
kubectl get services -n pharmacy
kubectl get pods -n pharmacy
kubectl get ingress -n pharmacy

echo -e "\n${BLUE}To get the external IP:${NC}"
echo "kubectl get ingress -n pharmacy"

echo -e "\n${BLUE}To view logs:${NC}"
echo "kubectl logs -n pharmacy -l app=api-gateway --tail=50"

echo -e "\n${BLUE}To access the API:${NC}"
echo "Wait for the Ingress to get an external IP, then access:"
echo "http://<EXTERNAL-IP>/docs"

echo -e "\n${GREEN}Deployment script completed!${NC}"
