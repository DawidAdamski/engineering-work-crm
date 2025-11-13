# Kubernetes Deployment Fix

## Issue

The health probes are failing because they're configured incorrectly:

```
Liveness probe failed: Get "http://10.244.2.14:8000/health": dial tcp 10.244.2.14:8000: connect: connection refused
Readiness probe failed: Get "http://10.244.2.14:8000/health": dial tcp 10.244.2.14:8000: connect: connection refused
```

## Problem

1. **Port Mismatch**: Probes are checking port **8000**, but the container runs on port **8080**
2. **Missing Endpoint**: The `/health` endpoint has been added to the application

## Solution

Update your Kubernetes deployment manifest to fix the health probes:

### Fix the Port

Health probes check the **pod directly** (not through the service), so they must use the **container port (8080)**, not the service port (8000).

### Example Fix

In your Kubernetes deployment YAML, update the liveness and readiness probes:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crm-api
spec:
  template:
    spec:
      containers:
      - name: crm-api
        ports:
        - containerPort: 8080  # Container port
        livenessProbe:
          httpGet:
            path: /health
            port: 8080  # ← Change from 8000 to 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080  # ← Change from 8000 to 8080
          initialDelaySeconds: 10
          periodSeconds: 5
```

### Service Configuration

The Service should still map port 8000 to 8080:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: crm-api
spec:
  ports:
  - port: 8000        # External port
    targetPort: 8080  # Container port
  selector:
    app: crm-api
```

## Summary

- **Container Port**: 8080 (where the app runs)
- **Service Port**: 8000 (external access)
- **Health Probe Port**: 8080 (probes check pod directly)
- **Health Endpoint**: `/health` (now available)

After updating the deployment, the health probes should work correctly.

