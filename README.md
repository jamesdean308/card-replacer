# Card Replacer
This project is a prototype of what I imagine a scalable microservice application for processing bank card replacement requests would look like. It utilises Flask for the web interface, Celery for task queue management, and Kubernetes for orchestration and auto-scaling.

## Features

-  **Flask Web App**: A simple web interface to submit card replacement requests.

-  **Celery Workers**: Background task processing using Celery and Redis.

-  **Kubernetes Orchestration**: Deployment, scaling, and management of the application using Kubernetes.

-  **Horizontal Pod Autoscaler (HPA)**: Automatic scaling of Celery workers based on CPU utilisation.

  

## Prerequisites
- Docker
- Python (for testing)
> Python virtual environment is recommended. Install requirements.txt dependancies. 
## Setup

This shell script will start up a minikube cluster, deploy the project to it, and expose the Flask service to localhost.
```
chmod +x start-cluster.sh
./start-cluster.sh
```

## Testing
All tests assume you have the cluster up and running using the previous step.

### End to End Tests

```
pytest tests/e2e
```
> The add task test is a sanity check I left in to ensure celery and redis are working without having to mess around with creating + logging in users (aka not reliant on the Postgres db working).

### Load Tests
Monitor the pods scaling up in a separate terminal:
```
kubectl get hpa --watch
```
Run script that will put load on the service:
```
python tests/load/test_multiple_request_cards.py
```

## Known Issues and Limitations
- There isn't a graceful way to give user feedback of task completion. Explored using callback URLs and websockets, but not satisfied with those solutions yet. So we instead poll the tasks endpoint which isn't the most elegant solution.
- No Flask service load balancer and not using HTTPS.
- Redis and Postgres databases aren't scalable at this point, which could potentially cause a bottleneck in a real system.
- No proper monitoring service. Relying on kubectl to debug right now, making it difficult to proactively identify performance issues or scaling needs.
- Load tests could be more elegant. Use Locust, gather metrics, and simulate real-world traffic patterns rather than relying on x simultaneous requests to trigger the HPA.
- The minikube cluster and its HPA resource values I have set are slightly arbitrary and based on what works well on my local machine (https://support.apple.com/en-gb/111902) for the purpose of demonstrating HPA scaling. Results may vary depending on the machine you run it on.
- The way I have secrets stored as environment variables in plain text isn’t best practice. I wanted to keep things simple so anyone can clone the repo and get it working.

## Areas for Future Improvement
- **Dynamic Rate Limiting**: Current rate limiting is set on a per-replica basis, which may hinder horizontal scaling. A more dynamic, distributed rate limiting approach could be implemented to better manage traffic as the system grows.
- **Capacity Allocation Adjustments**: Implement a system to dynamically adjust rate limits based on real-time usage metrics to prevent sudden spikes and improve overall system performance.
> Note: This article was published the week I completed this project, and I found its insights valuable for identifying areas for future improvement: [Enabling horizontal autoscaling with co-operative distributed rate limiting](https://monzo.com/blog/distributed-rate-limiting).