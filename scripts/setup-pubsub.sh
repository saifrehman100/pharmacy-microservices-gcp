#!/bin/bash
# Setup Pub/Sub with Workload Identity for Pharmacy Microservices

set -e

PROJECT_ID="pharmacy-ms-458074"
CLUSTER_NAME="pharmacy-cluster"
CLUSTER_ZONE="us-central1-a"
NAMESPACE="pharmacy-system"
KSA_NAME="pubsub-service-account"
GSA_NAME="pharmacy-pubsub"
GSA_EMAIL="${GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "========================================="
echo "Setting up Pub/Sub for Pharmacy System"
echo "========================================="
echo ""

# 1. Create GCP IAM Service Account
echo "1. Creating GCP IAM service account..."
if gcloud iam service-accounts describe ${GSA_EMAIL} --project=${PROJECT_ID} &>/dev/null; then
    echo "   ✓ Service account already exists: ${GSA_EMAIL}"
else
    gcloud iam service-accounts create ${GSA_NAME} \
        --display-name="Pharmacy Pub/Sub Service Account" \
        --project=${PROJECT_ID}
    echo "   ✓ Created service account: ${GSA_EMAIL}"
fi

# 2. Grant Pub/Sub permissions
echo ""
echo "2. Granting Pub/Sub permissions..."
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${GSA_EMAIL}" \
    --role="roles/pubsub.publisher" \
    --condition=None

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${GSA_EMAIL}" \
    --role="roles/pubsub.subscriber" \
    --condition=None

echo "   ✓ Granted Pub/Sub publisher and subscriber roles"

# 3. Enable Workload Identity binding
echo ""
echo "3. Setting up Workload Identity binding..."
gcloud iam service-accounts add-iam-policy-binding ${GSA_EMAIL} \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:${PROJECT_ID}.svc.id.goog[${NAMESPACE}/${KSA_NAME}]" \
    --project=${PROJECT_ID}

echo "   ✓ Workload Identity binding created"

# 4. Create Pub/Sub topic
echo ""
echo "4. Creating Pub/Sub topic..."
if gcloud pubsub topics describe order-events --project=${PROJECT_ID} &>/dev/null; then
    echo "   ✓ Topic already exists: order-events"
else
    gcloud pubsub topics create order-events --project=${PROJECT_ID}
    echo "   ✓ Created topic: order-events"
fi

# 5. Create Pub/Sub subscription
echo ""
echo "5. Creating Pub/Sub subscription..."
if gcloud pubsub subscriptions describe inventory-order-subscription --project=${PROJECT_ID} &>/dev/null; then
    echo "   ✓ Subscription already exists: inventory-order-subscription"
else
    gcloud pubsub subscriptions create inventory-order-subscription \
        --topic=order-events \
        --ack-deadline=60 \
        --message-retention-duration=7d \
        --project=${PROJECT_ID}
    echo "   ✓ Created subscription: inventory-order-subscription"
fi

# 6. Apply updated configmap
echo ""
echo "6. Applying updated ConfigMap..."
kubectl apply -f ../k8s/base/configmap.yaml

echo ""
echo "========================================="
echo "✓ Pub/Sub setup completed successfully!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Commit and push the configmap changes"
echo "2. Restart the order-service and inventory-service pods:"
echo "   kubectl rollout restart deployment/order-service -n ${NAMESPACE}"
echo "   kubectl rollout restart deployment/inventory-service -n ${NAMESPACE}"
echo ""
echo "The services will now be able to publish and consume order events via Pub/Sub."
