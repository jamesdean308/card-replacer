#!/bin/bash
set -e

cleanup() {
    minikube delete
}
minikube delete

# Delete cluster when script finishes 
trap cleanup EXIT

minikube start --cpus=2 --memory=4000

kubectl config use-context minikube

minikube addons enable metrics-server

IMAGE_NAME="card-replacer-web"
TAG="latest"
FULL_IMAGE_NAME="$IMAGE_NAME:$TAG"

echo "Building Docker image..."
docker build -t $FULL_IMAGE_NAME .

minikube image load $FULL_IMAGE_NAME

echo "Reapplying deployments..."

kubectl apply -f deployments/postgres-deployment.yaml
kubectl apply -f deployments/redis-deployment.yaml

echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres --timeout=120s

echo "Waiting for Redis to be ready..."
kubectl wait --for=condition=ready pod -l app=redis --timeout=120s

kubectl apply -f deployments/flask-app-deployment.yaml

echo "Waiting for Flask app to be ready..."
kubectl wait --for=condition=ready pod -l app=flask-app --timeout=120s

kubectl apply -f deployments/celery-worker-deployment.yaml

echo "Waiting for Celery worker to be ready..."
kubectl wait --for=condition=ready pod -l app=celery-worker --timeout=120s

# Create the Horizontal Pod Autoscaler for the Celery workers
kubectl create -f deployments/celery-worker-hpa.yaml

echo "Verifying the update..."

kubectl get pods

kubectl get hpa celery-worker-hpa

echo "Update complete."

# Port forward the Flask app service to localhost
# it will run in the background while we run the e2e tests to make sure everything is working
kubectl port-forward service/flask-app-service 5000:80 &
PORT_FORWARD_PID=$!

# Not the most elegant solution, but we need to give the cluster some time to finish the port 
# forwarding because e2e tests are dependant on being able to access the cluster
sleep 5

# Run end to end tests to ensure things are working
pytest tests/e2e

# CLI will hang until you Ctrl + C
wait $PORT_FORWARD_PID