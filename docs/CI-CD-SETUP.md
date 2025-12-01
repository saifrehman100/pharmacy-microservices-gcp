# CI/CD Setup Guide - GitHub Actions to GKE

This guide explains how to set up automatic deployment from GitHub to Google Kubernetes Engine (GKE).

## How It Works

```
Developer pushes code to GitHub
         ↓
GitHub Actions triggers automatically
         ↓
Detects which services changed
         ↓
Builds only changed Docker images
         ↓
Pushes images to Artifact Registry
         ↓
Deploys to GKE cluster
         ↓
Waits for deployment to complete
         ↓
Shows service status
```

## Setup Instructions

### Step 1: Create GCP Service Account for GitHub Actions

Run these commands in Cloud Shell:

```bash
# Set project ID
export PROJECT_ID=pharmacy-ms-458074

# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions CI/CD" \
  --project=$PROJECT_ID

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/container.developer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Create and download service account key
gcloud iam service-accounts keys create ~/github-actions-key.json \
  --iam-account=github-actions@${PROJECT_ID}.iam.gserviceaccount.com

# Display the key (copy this entire output)
cat ~/github-actions-key.json
```

### Step 2: Add Secret to GitHub Repository

1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/pharmacy-microservices-gcp`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `GCP_SA_KEY`
5. Value: Paste the entire JSON content from the previous step
6. Click **Add secret**

### Step 3: Push Your Code

```bash
# Commit the GitHub Actions workflow
git add .github/workflows/deploy-to-gke.yml
git commit -m "Add CI/CD pipeline with GitHub Actions"
git push origin main
```

### Step 4: Watch the Deployment

1. Go to GitHub repository
2. Click **Actions** tab
3. You'll see the workflow running
4. Click on it to see real-time logs
5. Wait for green checkmark ✅

## What Gets Deployed Automatically

The workflow triggers on:
- Push to `main` branch
- Changes in `services/` directory
- Changes in `k8s/` directory
- Changes in workflow files

### Smart Detection

The workflow only rebuilds **changed services**:

```
Change services/api-gateway/    → Only rebuild API Gateway
Change services/product-service/ → Only rebuild Product Service
Change all services/            → Rebuild all services
Change k8s/ only               → Just redeploy (no rebuild)
```

## How to Use

### Scenario 1: Fix a Bug in Product Service

```bash
# Make changes
vim services/product-service/app/routes/__init__.py

# Commit and push
git add services/product-service/
git commit -m "Fix product search bug"
git push origin main

# GitHub Actions will:
# 1. Build only product-service image
# 2. Push to Artifact Registry
# 3. Restart product-service pods in GKE
# 4. Wait for new pods to be ready
```

### Scenario 2: Add New Endpoint to API Gateway

```bash
# Make changes
vim services/api-gateway/app/routes.py

# Commit and push
git add services/api-gateway/
git commit -m "Add new inventory endpoints"
git push origin main

# GitHub Actions will:
# 1. Build only api-gateway image
# 2. Push to Artifact Registry
# 3. Restart api-gateway pods in GKE
```

### Scenario 3: Update Kubernetes Config

```bash
# Change replicas or resources
vim k8s/base/product-service-deployment.yaml

# Commit and push
git add k8s/
git commit -m "Scale product service to 3 replicas"
git push origin main

# GitHub Actions will:
# 1. Skip image building (no code changes)
# 2. Apply new K8s manifests
# 3. Rolling update to new config
```

## Viewing Deployment Status

### In GitHub

- Go to **Actions** tab
- Click on the running workflow
- See real-time build and deploy logs

### In GCP Console

1. Go to: https://console.cloud.google.com/kubernetes
2. Select your cluster: `pharmacy-cluster`
3. Click **Workloads** to see deployments
4. Click **Services & Ingress** to see load balancers

### Using kubectl (Cloud Shell)

```bash
# Watch deployments
kubectl get deployments -n pharmacy-system -w

# Watch pods
kubectl get pods -n pharmacy-system -w

# Check rollout status
kubectl rollout status deployment/api-gateway -n pharmacy-system
```

## Rollback (If Something Goes Wrong)

### Option 1: Revert Git Commit

```bash
# Revert the last commit
git revert HEAD
git push origin main

# GitHub Actions will deploy the previous version
```

### Option 2: Manual Rollback in GKE

```bash
# Rollback to previous version
kubectl rollout undo deployment/api-gateway -n pharmacy-system

# Check rollback status
kubectl rollout status deployment/api-gateway -n pharmacy-system
```

### Option 3: Deploy Specific Version

```bash
# Set image to specific SHA
kubectl set image deployment/api-gateway \
  api-gateway=us-central1-docker.pkg.dev/pharmacy-ms-458074/pharmacy-services/api-gateway:COMMIT_SHA \
  -n pharmacy-system
```

## Cost Optimization

GitHub Actions gives you:
- **2,000 free minutes/month** for private repos
- **Unlimited for public repos**

Each deployment takes ~3-5 minutes, so you can do:
- ~400-600 deployments/month for free

## Monitoring Deployments

### Email Notifications

GitHub automatically sends emails on:
- ❌ Failed deployments
- ✅ Successful deployments (if you enable it)

### Slack Integration (Optional)

Add to workflow to send Slack notifications:

```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## Best Practices

### 1. Use Feature Branches

```bash
# Create feature branch
git checkout -b feature/add-payment-service

# Make changes and commit
git add .
git commit -m "Add payment service"

# Push feature branch (won't trigger deployment)
git push origin feature/add-payment-service

# Create Pull Request on GitHub
# Review code
# Merge to main → Triggers automatic deployment
```

### 2. Test Locally First

```bash
# Test locally with docker-compose
docker-compose up

# Test all endpoints
# Only push when everything works
```

### 3. Use Staging Environment (Advanced)

Create a separate cluster for staging:

```yaml
on:
  push:
    branches:
      - develop  # Deploy to staging
      - main     # Deploy to production
```

## Troubleshooting

### Workflow Fails at Authentication

**Error:** "Unable to authenticate"

**Fix:**
1. Check `GCP_SA_KEY` secret is set correctly
2. Verify service account has correct permissions

### Workflow Fails at Build

**Error:** "Docker build failed"

**Fix:**
1. Test build locally: `docker build ./services/api-gateway`
2. Check Dockerfile syntax
3. Ensure all dependencies are in requirements.txt

### Workflow Fails at Deploy

**Error:** "Deployment not found"

**Fix:**
1. Ensure deployments exist: `kubectl get deployments -n pharmacy-system`
2. Check namespace is correct
3. Verify cluster credentials

### Workflow Succeeds but Pods Crash

**Check pod logs:**
```bash
kubectl logs -n pharmacy-system -l app=api-gateway --tail=50
```

Common issues:
- Database connection errors → Check secrets
- Import errors → Missing dependencies in requirements.txt
- Configuration errors → Check ConfigMap

## Advanced: Multi-Environment Setup

Create separate workflows for staging and production:

**.github/workflows/deploy-staging.yml** (triggers on develop branch)
**.github/workflows/deploy-production.yml** (triggers on main branch)

## Security Notes

✅ **DO:**
- Store service account key in GitHub Secrets
- Use least-privilege IAM roles
- Rotate service account keys regularly
- Use separate service accounts for staging/production

❌ **DON'T:**
- Commit service account keys to git
- Use overly permissive roles (like Owner)
- Share service account keys

## Next Steps

Now that CI/CD is set up:

1. ✅ Make a code change
2. ✅ Commit and push
3. ✅ Watch GitHub Actions deploy automatically
4. ✅ Test the changes in production

Welcome to modern DevOps! 🚀
