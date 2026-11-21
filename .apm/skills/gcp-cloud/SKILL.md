---
name: gcp-cloud
description: "GCP cloud reference for infrastructure-engineer, devops-engineer, and sre-agent: gcloud CLI essentials, Terraform patterns for GCP, common services (GKE, Cloud SQL, Cloud Storage, Cloud Run, Cloud Load Balancing), IAM service account best practices, VPC design, Cloud Monitoring/Logging, project and label conventions."
---

# GCP Cloud Skill

Version: 1.0 (2026-11-21)

## gcloud CLI Essentials

```bash
# Authenticate
gcloud auth login
gcloud auth application-default login   # for SDKs and Terraform

# Set project
gcloud config set project my-project-id
gcloud config set compute/region us-central1

# Current config
gcloud config list

# Common flags
--project <project-id>
--region us-central1
--format json | yaml | table | value(field)
--quiet                                 # suppress interactive prompts
```

## IAM Service Account Best Practices

- **Use service accounts for all workload identities** — never use user credentials for automated processes.
- **Workload Identity** (GKE) and **Service Account impersonation** (Cloud Run) eliminate the need for service account key files entirely. Prefer these.
- If you must use a key file: store it in Secret Manager, never in git or environment variables.
- Apply **least-privilege**: grant only the specific IAM roles needed on specific resources, not project-wide.
- Use **custom roles** when built-in roles grant too many permissions.
- Audit service account key usage with Cloud Audit Logs.

```bash
# Create service account
gcloud iam service-accounts create my-sa \
  --display-name "My Service Account" \
  --project my-project

# Grant role on a specific resource
gcloud storage buckets add-iam-policy-binding gs://my-bucket \
  --member="serviceAccount:my-sa@my-project.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"

# Enable Workload Identity for GKE
gcloud iam service-accounts add-iam-policy-binding my-sa@my-project.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:my-project.svc.id.goog[namespace/kube-sa]"
```

## Project and Label Conventions

```
Project naming: <org>-<project>-<env>
Example: acme-btengine-prod

Labels (applied to all billable resources):
  project: bt-engine
  environment: production
  sprint: sprint-0004
  managed-by: terraform
  owner: team-name
```

Use separate GCP projects per environment (dev, staging, prod) — this is the strongest isolation boundary in GCP.

## VPC Design

```
VPC (custom mode — never auto mode in production):
  Subnet: us-central1  10.0.0.0/20   — GKE nodes
    Secondary ranges:
      pods:     10.1.0.0/16
      services: 10.2.0.0/20
  Subnet: us-east1     10.0.16.0/20  — multi-region failover

Firewall rules:
  Allow: internal VPC traffic (10.0.0.0/8)
  Allow: health checks from Google ranges (130.211.0.0/22, 35.191.0.0/16)
  Allow: IAP SSH (35.235.240.0/20) for bastion access
  Deny: all other ingress
```

- Enable **Private Google Access** on all subnets to reach Google APIs without external IPs.
- Use **Cloud NAT** for egress from private instances; no external IPs on compute nodes.
- Use **Private Service Connect** or **VPC Service Controls** for Cloud SQL, Cloud Storage access from VPC.

## Common Services

### GKE (Google Kubernetes Engine)
```bash
# Create Autopilot cluster (recommended — no node management)
gcloud container clusters create-auto my-cluster \
  --region us-central1 \
  --project my-project

# Create Standard cluster (more control)
gcloud container clusters create my-cluster \
  --region us-central1 \
  --num-nodes 3 \
  --machine-type n2-standard-4 \
  --enable-ip-alias \
  --enable-private-nodes \
  --master-ipv4-cidr 172.16.0.0/28 \
  --workload-pool=my-project.svc.id.goog

# Get credentials
gcloud container clusters get-credentials my-cluster --region us-central1
```

### Cloud SQL
- Always enable encryption at rest (default) and in transit (SSL/TLS required).
- Use **Cloud SQL Auth Proxy** for local dev and GKE; never expose Cloud SQL public IP.
- Enable **automated backups** and **point-in-time recovery**.
- Use a private IP (VPC peering) — no public IP in production.
- Grant Cloud SQL client role to the service account; use IAM database authentication where possible.

### Cloud Storage
```bash
# Create bucket with uniform bucket-level access (disables ACLs)
gcloud storage buckets create gs://my-bucket \
  --location=US-CENTRAL1 \
  --uniform-bucket-level-access \
  --project=my-project

# Enable versioning
gcloud storage buckets update gs://my-bucket --versioning

# Block public access
gcloud storage buckets update gs://my-bucket --no-public-access-prevention=off
# (ensure public access prevention is enforced at org policy level)
```

### Cloud Run
```bash
# Deploy container
gcloud run deploy my-service \
  --image us-central1-docker.pkg.dev/my-project/my-repo/my-image:sha256-xxx \
  --region us-central1 \
  --platform managed \
  --no-allow-unauthenticated \
  --service-account my-sa@my-project.iam.gserviceaccount.com \
  --set-secrets=DB_PASSWORD=my-secret:latest \
  --vpc-connector my-connector \
  --vpc-egress private-ranges-only
```

### Cloud Load Balancing
- Use **Global HTTP(S) Load Balancer** for multi-region; **Regional** for single region.
- Terminate TLS at the load balancer; use Google-managed SSL certificates (automatic renewal).
- Configure **Cloud Armor** WAF policies for OWASP rule sets on external load balancers.

## Terraform Patterns for GCP

```hcl
# Provider setup
provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset(["run.googleapis.com", "sqladmin.googleapis.com", "secretmanager.googleapis.com"])
  service  = each.value
  disable_on_destroy = false
}

# Cloud Storage bucket
resource "google_storage_bucket" "data" {
  name          = "${var.project_id}-data"
  location      = "US-CENTRAL1"
  force_destroy = false

  uniform_bucket_level_access = true
  versioning { enabled = true }

  labels = local.common_labels
}
```

```bash
# GCS backend for Terraform state
terraform {
  backend "gcs" {
    bucket = "my-project-tfstate"
    prefix = "terraform/state"
  }
}
```

```bash
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

## Cloud Monitoring and Logging

### Key metrics to alert on
| Service | Metric | Recommended threshold |
|---------|--------|-----------------------|
| Cloud Run | `request_latencies` p99 | > 2s |
| Cloud Run | `request_count` (5xx) | > 1% error rate |
| GKE | Node CPU | > 80% |
| Cloud SQL | `database/cpu/utilization` | > 75% |
| Cloud Storage | `storage/total_bytes` | budget alert |

```bash
# Create alerting policy (use Cloud Monitoring UI or Terraform for complex policies)
gcloud alpha monitoring policies create --policy-from-file=alert-policy.json
```

### Cloud Logging — useful queries
```
# All errors in Cloud Run
resource.type="cloud_run_revision"
severity>=ERROR

# Audit logs for IAM changes
protoPayload.serviceName="iam.googleapis.com"
protoPayload.methodName=~"SetIamPolicy|CreateServiceAccount"
```

Enable **Cloud Audit Logs** (Admin Activity always on; Data Access must be enabled explicitly) for all services handling sensitive data.

## Secrets Management (Secret Manager)

```bash
# Create secret
echo -n "s3cr3t" | gcloud secrets create db-password --data-file=-

# Add version
echo -n "new-s3cr3t" | gcloud secrets versions add db-password --data-file=-

# Grant access to service account
gcloud secrets add-iam-policy-binding db-password \
  --role roles/secretmanager.secretAccessor \
  --member serviceAccount:my-sa@my-project.iam.gserviceaccount.com
```

```python
# Access in Python
from google.cloud import secretmanager
client = secretmanager.SecretManagerServiceClient()
response = client.access_secret_version(name="projects/my-project/secrets/db-password/versions/latest")
password = response.payload.data.decode("utf-8")
```

**Never** put secrets in Terraform `.tfvars` files committed to git. Reference Secret Manager in Terraform using the `google_secret_manager_secret_version` data source.

## Change log
- 1.0 (2026-11-21): first release in agent-stack.
