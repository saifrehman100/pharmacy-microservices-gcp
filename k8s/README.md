# Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying the Pharmacy Microservices system on Google Kubernetes Engine (GKE).

## Prerequisites

1. Google Cloud SDK installed and configured
2. kubectl installed
3. GKE cluster created
4. Docker images built and pushed to GCR

## Quick Start

### 1. Set up GCP Project

```bash
# Set your project ID
export PROJECT_ID=your-gcp-project-id
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable container.googleapis.com
gcloud services enable pubsub.googleapis.com
gcloud services enable sqladmin.googleapis.com
```

### 2. Create GKE Cluster

```bash
gcloud container clusters create pharmacy-cluster \
  --zone=us-central1-a \
  --num-nodes=3 \
  --machine-type=e2-medium \
  --enable-autoscaling \
  --min-nodes=3 \
  --max-nodes=10 \
  --enable-autorepair \
  --enable-autoupgrade
```

### 3. Configure kubectl

```bash
gcloud container clusters get-credentials pharmacy-cluster --zone=us-central1-a
```

### 4. Set up Pub/Sub

```bash
# Create topic
gcloud pubsub topics create order-events

# Create subscription
gcloud pubsub subscriptions create inventory-order-subscription \
  --topic=order-events
```

### 5. Set up Workload Identity (for Pub/Sub access)

```bash
# Create GCP service account
gcloud iam service-accounts create pharmacy-pubsub \
  --display-name="Pharmacy Pub/Sub Service Account"

# Grant Pub/Sub permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:pharmacy-pubsub@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/pubsub.publisher"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:pharmacy-pubsub@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/pubsub.subscriber"

# Bind to Kubernetes service account
gcloud iam service-accounts add-iam-policy-binding \
  pharmacy-pubsub@$PROJECT_ID.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:$PROJECT_ID.svc.id.goog[pharmacy-system/pubsub-service-account]"
```

### 6. Build and Push Docker Images

```bash
# Build images
cd services/api-gateway
docker build -t gcr.io/$PROJECT_ID/api-gateway:latest .

cd ../product-service
docker build -t gcr.io/$PROJECT_ID/product-service:latest .

cd ../order-service
docker build -t gcr.io/$PROJECT_ID/order-service:latest .

cd ../inventory-service
docker build -t gcr.io/$PROJECT_ID/inventory-service:latest .

# Push images
docker push gcr.io/$PROJECT_ID/api-gateway:latest
docker push gcr.io/$PROJECT_ID/product-service:latest
docker push gcr.io/$PROJECT_ID/order-service:latest
docker push gcr.io/$PROJECT_ID/inventory-service:latest
```

### 7. Update Kubernetes Manifests

Update the following in the manifest files:
- Replace `YOUR_PROJECT_ID` with your actual GCP project ID
- Update database connection strings in `secrets.yaml`
- Update domain name in `ingress.yaml`

### 8. Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -f k8s/base/namespace.yaml
kubectl apply -f k8s/base/configmap.yaml
kubectl apply -f k8s/base/secrets.yaml
kubectl apply -f k8s/base/service-account.yaml
kubectl apply -f k8s/base/api-gateway-deployment.yaml
kubectl apply -f k8s/base/product-service-deployment.yaml
kubectl apply -f k8s/base/order-service-deployment.yaml
kubectl apply -f k8s/base/inventory-service-deployment.yaml
kubectl apply -f k8s/base/hpa.yaml
kubectl apply -f k8s/base/ingress.yaml
```

### 9. Verify Deployment

```bash
# Check pods
kubectl get pods -n pharmacy-system

# Check services
kubectl get services -n pharmacy-system

# Check ingress
kubectl get ingress -n pharmacy-system

# View logs
kubectl logs -n pharmacy-system -l app=api-gateway
```

## Using Cloud SQL (Recommended for Production)

Instead of running databases in pods, use Cloud SQL:

1. Create Cloud SQL instances:
```bash
gcloud sql instances create pharmacy-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1
```

2. Update database connection strings in secrets to use Cloud SQL proxy or private IP.

## Monitoring and Logging

View logs in Cloud Logging:
```bash
gcloud logging read "resource.type=k8s_container AND resource.labels.namespace_name=pharmacy-system" --limit 50
```

## Cleanup

```bash
# Delete all resources
kubectl delete namespace pharmacy-system

# Delete GKE cluster
gcloud container clusters delete pharmacy-cluster --zone=us-central1-a
```
