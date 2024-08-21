


# Card Replacer

This project is a scalable microservice application for processing bank card replacement requests. It utilises Flask for the web interface, Celery for task queue management, and Kubernetes for orchestration and auto-scaling.

## Features

-   **Flask Web App**: A simple web interface to submit card replacement requests.
-   **Celery Workers**: Background task processing using Celery and Redis.
-   **Kubernetes Orchestration**: Deployment, scaling, and management of the application using Kubernetes.
-   **Horizontal Pod Autoscaler (HPA)**: Automatic scaling of Celery workers based on CPU utilisation.

## Prerequisites

-   Docker
- Python (if you want to run the test scripts)
## Setup
I wrote a shell script that will start up a minikube cluster, build the image and deploy the project to it (I think there might be a more sophisticated way to do this). Run this script to do that:
```
./update_flask_app.sh
```
Expose the flask service:
```
minikube service flask-app-service
```
> This exposes the service to localhost and assigns a random port.
## Test Celery Tasks
There are test scripts you can run to test the Celery tasks.

### Add
Add two numbers together:
```
python tests/test_add.py
```
### Request Card
Registers/ logs in a user then makes a card request
```
python tests/test_request_card.py
```
## Known Issues and Limitations
- There isn't a graceful way to give user feedback of task completion. Explored using callback URLs and websockets, but not satisfied with those solutions yet. So we instead poll the tasks endpoint which isn't exactly elegant.
- No Flask service loadbalancer and not using HTTPS.
- Don't currently have load test for *request_card*. A bit awkward to setup thanks to needing a unique user for each concurrent card request (a user can only make one card request at a time).
- Redis and Postgres databases aren't exactly scalable at this point. Could have the potential to cause a bottle neck.
- Concerns that HPA might not effectively scale celery worker pods as it scales based on cpu usage but the request card task is planned to be very I/O bound not so much by heavy computation. I don't know if this would scale (that is why I need to write some load tests)
- I feel like there must be a more sophisticated way to deploy project to the cluster other than using a shell script.