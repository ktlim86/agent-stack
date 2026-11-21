---
name: kubernetes
description: "Kubernetes reference for devops-engineer: Deployment and Service manifest patterns, resource requests/limits, liveness/readiness probes, ConfigMap and Secret usage, HPA, Namespace conventions, Helm chart structure, rolling update strategy, PodDisruptionBudget, and common pitfalls."
---

# Kubernetes Skill

Version: 1.0 (2026-11-21)

## Deployment Manifest Pattern

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: production
  labels:
    app: my-app
    version: "1.0.0"
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1     # at most 1 pod unavailable during update
      maxSurge: 1           # at most 1 extra pod during update
  template:
    metadata:
      labels:
        app: my-app
        version: "1.0.0"
    spec:
      serviceAccountName: my-app-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        fsGroup: 1001
      containers:
        - name: my-app
          image: registry.example.com/my-app:sha256-abc123
          imagePullPolicy: IfNotPresent   # see pitfalls below
          ports:
            - containerPort: 8000
              protocol: TCP
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
          env:
            - name: DB_HOST
              valueFrom:
                configMapKeyRef:
                  name: my-app-config
                  key: db_host
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: my-app-secrets
                  key: db_password
```

## Service Manifest

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app
  namespace: production
spec:
  selector:
    app: my-app
  ports:
    - name: http
      port: 80
      targetPort: 8000
  type: ClusterIP  # internal only; use LoadBalancer or Ingress for external
```

## Resource Requests and Limits

- **Always set both `requests` and `limits`** — pods without requests cannot be scheduled predictably; pods without limits can starve neighbours.
- `requests`: what the scheduler uses to place the pod. Set to typical usage.
- `limits`: hard cap. CPU limit causes throttling; memory limit causes OOM kill.
- Set memory `limits` ≈ 2x `requests` as a starting point; tune based on actual metrics.
- CPU `limits` are optional in some policies — CPU throttling is safer than OOM, but limits can cause latency spikes. Monitor and adjust.

```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"   # 100 millicores = 0.1 CPU
  limits:
    memory: "256Mi"
    cpu: "500m"
```

## Liveness vs Readiness Probes

| Probe | Failure action | Use for |
|-------|---------------|---------|
| `livenessProbe` | Restart the container | Detecting deadlocks / hung processes |
| `readinessProbe` | Remove from Service endpoints | Detecting startup completion, temporary unavailability |
| `startupProbe` | Give slow-starting containers time | Containers with long init (e.g. DB migrations) |

**Rule**: liveness probe must only fail for truly unrecoverable states. A slow DB query should not kill the pod — that's what readiness is for.

## ConfigMap and Secret Usage

```yaml
# ConfigMap (non-sensitive config)
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-app-config
  namespace: production
data:
  db_host: "db.internal.svc.cluster.local"
  log_level: "INFO"
  allowed_origins: "https://app.example.com"
---
# Secret (base64 encoded, but NOT encrypted at rest by default)
# Use Sealed Secrets, External Secrets Operator, or cloud provider CSI driver
apiVersion: v1
kind: Secret
metadata:
  name: my-app-secrets
  namespace: production
type: Opaque
data:
  db_password: czNjcjN0  # base64("s3cr3t") — never commit real values
```

**Prefer External Secrets Operator** in production — it pulls secrets from AWS Secrets Manager, Azure Key Vault, or GCP Secret Manager at pod creation, avoiding base64 secrets in git.

## Horizontal Pod Autoscaler (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70   # scale up when avg CPU > 70%
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

## Namespace Conventions

```
production     — production workloads
staging        — staging workloads
monitoring     — Prometheus, Grafana, alerting
ingress        — ingress controllers
cert-manager   — TLS certificate management
```

Use Namespace-scoped RBAC: service accounts should only have permissions within their own namespace.

## PodDisruptionBudget

Ensures a minimum number of pods remain available during voluntary disruptions (node drain, rolling upgrade):

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: my-app-pdb
  namespace: production
spec:
  minAvailable: 2        # or use maxUnavailable: 1
  selector:
    matchLabels:
      app: my-app
```

Always set a PDB for production deployments with ≥ 2 replicas.

## Helm Chart Structure

```
my-chart/
  Chart.yaml             ← metadata (name, version, appVersion)
  values.yaml            ← default values
  values-prod.yaml       ← production overrides (committed)
  values-staging.yaml    ← staging overrides (committed)
  templates/
    deployment.yaml
    service.yaml
    configmap.yaml
    hpa.yaml
    pdb.yaml
    _helpers.tpl         ← named templates / partials
```

```bash
# Deploy
helm upgrade --install my-app ./my-chart \
  --namespace production \
  --values values.yaml \
  --values values-prod.yaml \
  --set image.tag=sha256-abc123

# Diff before deploy (requires helm-diff plugin)
helm diff upgrade my-app ./my-chart --values values.yaml --values values-prod.yaml

# Rollback
helm rollback my-app 1   # 1 = previous revision
```

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| `imagePullPolicy: Always` in production | Use `IfNotPresent` with immutable SHA tags; `Always` adds latency and hits registry rate limits |
| No resource requests | Set requests; unset requests cause unpredictable scheduling |
| `latest` image tag | Use immutable SHA or semver tag; `latest` breaks rollback |
| Single replica in production | ≥ 2 replicas + PDB; single replicas cause downtime during node drain |
| Secrets in ConfigMap | Secrets only in Secret objects (or External Secrets Operator) |
| Missing readiness probe | Without readiness probe, pods receive traffic before they are ready |
| Liveness probe too aggressive | If liveness probe fires during high load, it restarts healthy pods — set generous thresholds |
| Wide RBAC permissions | Scope to specific resources and verbs; never `verbs: ["*"]` in production |

## Change log
- 1.0 (2026-11-21): first release in agent-stack.
