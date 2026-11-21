---
name: cloud-security
description: "Cloud security reference for security-reviewer and infrastructure-engineer: IAM least-privilege, secrets management, network security, encryption at rest and in transit, audit logging, container image scanning, and a cloud-agnostic security checklist for AWS/Azure/GCP."
---

# Cloud Security Skill

Version: 1.0 (2026-11-21)

## IAM Least-Privilege

### Universal rules (all clouds)
- **No wildcard permissions**: never grant `Action: "*"` (AWS), `"*"` role (GCP), or Contributor at subscription scope (Azure) to a service identity.
- **One role per service**: each microservice gets its own identity with only the permissions it needs.
- **No long-lived credentials**: use platform-native identity mechanisms.
- **Separate human and machine identities**: service accounts/roles must not be shared with human users.
- **Principle of least privilege audit**: run a quarterly access review.

## Secrets Management

### No secrets should exist in:
- Source code (any file in git)
- Docker image layers
- Environment variables set in plain text in deployment configs
- CI/CD pipeline logs
- Application logs
- Error messages returned to clients

## Network Security

### Universal rules
- No direct internet access to databases: databases must be in private subnets with no public IP.
- No 0.0.0.0/0 ingress except on load balancers (ports 80/443 only).
- Separate network tiers: load balancer tier, application tier, data tier.
- TLS everywhere for service-to-service communication.

## Encryption

### At rest
- Databases: encryption at rest enabled (default on most managed services).
- Object storage: server-side encryption on all buckets (AES-256 minimum).
- Disks: root volumes encrypted.

### In transit
- TLS 1.2 minimum. TLS 1.0 and 1.1 must be disabled.
- HSTS header on all HTTPS responses.

## Audit Logging

Minimum requirements:
- Cloud management API calls logged.
- Authentication events logged.
- Logs retained for at least 90 days.
- Alert configured for critical security events (root/admin account usage).

## Container Image Security

- Non-root user in Dockerfile.
- No secrets in image layers.
- Base image pinned to specific version (not latest).
- No Critical CVEs in image.

## Cloud-Agnostic Security Checklist

### Identity and Access
- [ ] No wildcard permissions on service identities
- [ ] Platform-native identity used (no access keys for cloud services)
- [ ] MFA required for all human console access
- [ ] Root/Global Admin accounts protected with MFA

### Data Protection
- [ ] Encryption at rest enabled on all data stores
- [ ] Encryption in transit (TLS 1.2+) enforced
- [ ] No secrets in source code, images, or logs
- [ ] Secrets stored in managed secrets service

### Network
- [ ] No 0.0.0.0/0 ingress except load balancers on 443
- [ ] Databases in private subnets with no public IP
- [ ] WAF enabled on public-facing load balancers
- [ ] VPC/VNet flow logging enabled

### Operations
- [ ] Audit logging enabled in all regions
- [ ] Log retention at least 90 days
- [ ] Alerts for critical security events configured
- [ ] Container images scanned for CVEs before deployment
- [ ] Dependency CVE scanning in CI pipeline

## Change log
- 1.0 (2026-11-21): first release in agent-stack.
