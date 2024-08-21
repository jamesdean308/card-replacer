#!/bin/bash

minikube delete

minikube start

kubectl config use-context minikube

minikube addons enable metrics-server



# Variables
IMAGE_NAME="card-replacer-web"
TAG="latest"
FULL_IMAGE_NAME="$IMAGE_NAME:$TAG"

# Step 1: Build the Docker image using Minikube's Docker daemon
echo "Building Docker image..."
docker build -t $FULL_IMAGE_NAME .

minikube image load $FULL_IMAGE_NAME


# Step 4: Reapply the deployments
echo "Reapplying deployments..."

kubectl apply -f deployments/postgres-deployment.yaml
kubectl apply -f deployments/redis-deployment.yaml
kubectl apply -f deployments/flask-app-deployment.yaml
kubectl apply -f deployments/celery-worker-deployment.yaml

kubectl create -f deployments/celery-worker-hpa.yaml

# Step 5: Wait for the pods to be created and started
echo "Waiting for pods to start..."
sleep 30

# Step 5: Verify the update
echo "Verifying the update..."

# Check the status of the pods
kubectl get pods

# Check the status of the HPA
kubectl get hpa celery-worker-hpa



echo "Update complete."
