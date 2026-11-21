---
name: aws-cloud
description: "AWS cloud reference for infrastructure-engineer, devops-engineer, and sre-agent: CLI essentials, CDK/CloudFormation patterns, common services (ECS/EKS, RDS, S3, Lambda, ALB), IAM least-privilege, VPC layout, CloudWatch monitoring, tagging strategy, and multi-region considerations."
---

# AWS Cloud Skill

Version: 1.0 (2026-11-21)

## AWS CLI Essentials

```bash
# Configure credentials
aws configure                          # interactive setup
aws configure --profile <name>        # named profile

# Verify identity
aws sts get-caller-identity

# Common flags
--region us-east-1
--output json | table | text
--profile <name>
--no-cli-pager                        # suppress pager for scripts
```

## IAM Least-Privilege Patterns

- **Never use `Action: "*"` or `Resource: "*"`** — always scope to the specific service, action, and resource ARN.
- Use IAM roles (not IAM users) for all compute workloads (EC2, ECS tasks, Lambda, EKS pods).
- Attach policies to roles, not users. Users get their access via groups.
- Use `aws:RequestedRegion` condition to restrict cross-region calls.
- Enable MFA for all human IAM users with console access.
- Rotate access keys every 90 days; prefer role-based access (no long-lived keys).

**Minimal ECS task role example:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::my-bucket/*"
    },
    {
      "Effect": "Allow",
      "Action": ["secretsmanager:GetSecretValue"],
      "Resource": "arn:aws:secretsmanager:us-east-1:123456789012:secret:my-secret-*"
    }
  ]
}
```

## VPC Layout Best Practices

```
VPC: 10.0.0.0/16
  Public subnets  (one per AZ): 10.0.0.0/24, 10.0.1.0/24, 10.0.2.0/24
    - Internet Gateway attached
    - NAT Gateway placed here
    - Only load balancers and bastion hosts
  Private subnets (one per AZ): 10.0.10.0/24, 10.0.11.0/24, 10.0.12.0/24
    - ECS tasks, EC2 instances, Lambda (VPC mode)
    - Outbound via NAT Gateway only
  Data subnets   (one per AZ): 10.0.20.0/24, 10.0.21.0/24, 10.0.22.0/24
    - RDS, ElastiCache — no internet access at all
```

**Security group rules:**
- ALB: inbound 443 from 0.0.0.0/0; outbound to app security group on app port
- App: inbound from ALB security group only; outbound to data security group and NAT
- Data: inbound from app security group only; no outbound internet

## Common Services

### ECS (Fargate)
```bash
# Create cluster
aws ecs create-cluster --cluster-name prod-cluster

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-def.json

# Deploy service
aws ecs create-service \
  --cluster prod-cluster \
  --service-name my-service \
  --task-definition my-task:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=DISABLED}"

# Update service (rolling deploy)
aws ecs update-service --cluster prod-cluster --service my-service --task-definition my-task:2 --force-new-deployment
```

### RDS
- Always deploy in Multi-AZ for production.
- Use RDS Proxy for Lambda/ECS to manage connection pooling.
- Enable encryption at rest (AWS-managed KMS key minimum; CMK for regulated data).
- Store connection string in Secrets Manager; rotate automatically using the RDS rotation Lambda.

### S3
```bash
# Create bucket with versioning and encryption
aws s3api create-bucket --bucket my-bucket --region us-east-1
aws s3api put-bucket-versioning --bucket my-bucket --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --bucket my-bucket \
  --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

# Block all public access
aws s3api put-public-access-block --bucket my-bucket \
  --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

### Lambda
- Set reserved concurrency to prevent runaway costs and protect downstream services.
- Always set a timeout (default 3s is often too low; max 15 minutes).
- Use Lambda Powertools for structured logging and tracing.
- Deploy in VPC only when the Lambda needs access to VPC resources — adds cold start latency.

### ALB
- Terminate TLS at the ALB; backend uses HTTP on private subnet.
- Use HTTPS listener with ACM certificate; redirect HTTP → HTTPS.
- Set idle timeout to match your application's request timeout.
- Enable access logs to S3 for audit.

## CloudFormation / CDK Patterns

### CDK (preferred)
```python
# Typical CDK stack structure
from aws_cdk import Stack, aws_ecs as ecs, aws_ec2 as ec2
from constructs import Construct

class AppStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        vpc = ec2.Vpc(self, "VPC", max_azs=3)
        cluster = ecs.Cluster(self, "Cluster", vpc=vpc)
        # ...
```

```bash
cdk diff        # show what will change
cdk deploy      # apply changes
cdk destroy     # tear down (careful in prod)
```

### CloudFormation
```bash
# Validate template
aws cloudformation validate-template --template-body file://template.yaml

# Deploy stack
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name my-stack \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides Env=prod

# Describe stack events (for troubleshooting failures)
aws cloudformation describe-stack-events --stack-name my-stack
```

## CloudWatch Monitoring

### Key metrics to alarm on
| Service | Metric | Recommended threshold |
|---------|--------|-----------------------|
| ECS | `CPUUtilization` | > 80% for 5 minutes |
| ECS | `MemoryUtilization` | > 85% for 5 minutes |
| ALB | `HTTPCode_ELB_5XX_Count` | > 10 per minute |
| ALB | `TargetResponseTime` | p99 > 2s |
| RDS | `CPUUtilization` | > 75% |
| RDS | `FreeStorageSpace` | < 20% of allocated |
| Lambda | `Errors` | > 1% error rate |

### Create alarm via CLI
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "HighCPU-ECS" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-east-1:123456789:alerts \
  --dimensions Name=ClusterName,Value=prod-cluster Name=ServiceName,Value=my-service
```

## Tagging Strategy

Every resource must carry these tags at minimum:

| Tag Key | Value example | Purpose |
|---------|--------------|---------|
| `project` | `bt-engine` | Cost allocation |
| `environment` | `production` | Distinguish envs |
| `sprint` | `SPRINT-0004` | Cost attribution to sprint |
| `managed-by` | `cdk` or `terraform` | Identify IaC-managed resources |
| `owner` | `team-name` | Escalation |

## Multi-Region Considerations

- Use Route 53 health checks + failover routing for cross-region disaster recovery.
- RDS Global Database for sub-second RPO; Aurora Global preferred over Multi-AZ cross-region.
- S3 Cross-Region Replication for static assets and backups.
- CloudFront reduces latency for global users and offloads ALB.
- Secrets Manager has a replication feature — replicate secrets to secondary regions before enabling failover.

## Secrets Management

```bash
# Store a secret
aws secretsmanager create-secret \
  --name /prod/db/password \
  --secret-string '{"username":"app","password":"s3cr3t"}'

# Retrieve in application code (Python)
import boto3, json
client = boto3.client("secretsmanager", region_name="us-east-1")
secret = json.loads(client.get_secret_value(SecretId="/prod/db/password")["SecretString"])
```

**Never**: store secrets in environment variables passed at deploy time in plain text, in CloudFormation parameters without `NoEcho`, or in task definition JSON committed to git.

## Change log
- 1.0 (2026-11-21): first release in agent-stack.
