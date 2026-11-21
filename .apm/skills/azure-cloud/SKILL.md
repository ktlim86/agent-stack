---
name: azure-cloud
description: "Azure cloud reference for infrastructure-engineer, devops-engineer, and sre-agent: Azure CLI essentials, Bicep/ARM patterns, common services (AKS, Azure SQL, Blob Storage, App Service, Application Gateway), Entra ID/Managed Identity, VNet layout, Azure Monitor alerts, resource group conventions, and tagging."
---

# Azure Cloud Skill

Version: 1.0 (2026-11-21)

## Azure CLI Essentials

```bash
# Login
az login
az login --service-principal -u <app-id> -p <password> --tenant <tenant-id>

# Set subscription
az account set --subscription <subscription-id>
az account show

# Common flags
--output json | table | tsv | yaml
--resource-group <rg>
--location eastus
```

## Entra ID / Managed Identity Patterns

- **Always use Managed Identity** for Azure workloads instead of service principal secrets.
  - System-assigned: tied to the resource lifecycle; simpler.
  - User-assigned: reusable across multiple resources; preferred for shared services.
- **Never store credentials** in application config or environment variables when Managed Identity is available.
- Use **Azure RBAC** (role-based access control) over classic access policies for all new resources (Key Vault, Storage, etc.).
- Apply principle of least privilege: assign only the specific built-in or custom role required.

```bash
# Assign Managed Identity to App Service
az webapp identity assign --name my-app --resource-group my-rg

# Grant MI access to Key Vault secrets
az keyvault set-policy --name my-kv \
  --object-id $(az webapp identity show --name my-app --resource-group my-rg --query principalId -o tsv) \
  --secret-permissions get list
```

## Resource Group Conventions

```
Naming: <project>-<environment>-<region>-rg
Example: btengine-prod-eastus-rg

Structure:
  btengine-prod-eastus-rg          ← all production resources
  btengine-staging-eastus-rg       ← staging resources
  btengine-shared-eastus-rg        ← shared: ACR, Key Vault, networking
```

All resources in a resource group share the same lifecycle — delete the RG to delete everything. Keep stateful (databases) and stateless (compute) resources in separate resource groups where practical.

## VNet Layout Best Practices

```
VNet: 10.0.0.0/16
  Subnet: public-subnet    10.0.0.0/24   — Application Gateway
  Subnet: app-subnet       10.0.10.0/24  — AKS nodes, App Service VNet integration
  Subnet: data-subnet      10.0.20.0/24  — Azure SQL, Redis — service endpoints
  Subnet: bastion-subnet   10.0.30.0/24  — Azure Bastion (RDP/SSH)
```

- Use **Network Security Groups (NSGs)** on every subnet.
- Use **Service Endpoints** or **Private Endpoints** to access PaaS services (SQL, Storage, Key Vault) over the Azure backbone — not public internet.
- Enable Azure DDoS Protection Standard for production VNets.

## Common Services

### AKS (Azure Kubernetes Service)
```bash
# Create cluster
az aks create \
  --resource-group my-rg \
  --name my-cluster \
  --node-count 3 \
  --enable-managed-identity \
  --enable-oidc-issuer \
  --enable-workload-identity \
  --network-plugin azure \
  --vnet-subnet-id /subscriptions/.../subnets/app-subnet

# Get credentials
az aks get-credentials --resource-group my-rg --name my-cluster

# Update cluster (rolling node upgrade)
az aks upgrade --resource-group my-rg --name my-cluster --kubernetes-version 1.29
```

### Azure SQL
- Always enable Transparent Data Encryption (TDE) — on by default for new databases.
- Use **Azure AD authentication** with Managed Identity; disable SQL authentication for service accounts.
- Configure firewall to allow only VNet subnets via service endpoints; deny public access.
- Enable Auditing and Threat Detection.
- Use Geo-redundant backups; set retention to ≥ 7 days.

### Blob Storage
```bash
# Create storage account with encryption and HTTPS only
az storage account create \
  --name mystorageacct \
  --resource-group my-rg \
  --sku Standard_GRS \
  --kind StorageV2 \
  --https-only true \
  --min-tls-version TLS1_2

# Assign Blob Data Contributor role to Managed Identity
az role assignment create \
  --assignee <principal-id> \
  --role "Storage Blob Data Contributor" \
  --scope /subscriptions/.../storageAccounts/mystorageacct
```

- Disable public anonymous access on all containers.
- Enable soft delete and versioning for production blobs.

### App Service
- Use **Deployment Slots** (staging + production) for zero-downtime swaps.
- Enable **Managed Identity** and pull secrets from Key Vault using Key Vault references.
- Always use custom domains with App Service Managed Certificates (free TLS).
- Set HTTPS-only and minimum TLS 1.2 in App Service settings.

### Application Gateway
- Use WAF_v2 tier in production for built-in OWASP rule sets.
- Terminate TLS at the Application Gateway; use HTTP to backend in the VNet.
- Configure health probes on `/health` or equivalent endpoint.

## Bicep Patterns (preferred over ARM JSON)

```bicep
// main.bicep — minimal App Service + SQL example
param location string = resourceGroup().location
param appName string
param sqlAdminLogin string

resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: '${appName}-plan'
  location: location
  sku: { name: 'P1v3', tier: 'PremiumV3' }
}

resource webApp 'Microsoft.Web/sites@2022-03-01' = {
  name: appName
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
  }
}
```

```bash
# Preview changes
az deployment group what-if \
  --resource-group my-rg \
  --template-file main.bicep \
  --parameters appName=btengine sqlAdminLogin=appadmin

# Deploy
az deployment group create \
  --resource-group my-rg \
  --template-file main.bicep \
  --parameters appName=btengine sqlAdminLogin=appadmin
```

## Azure Monitor Alerts

### Key metrics to alarm on
| Service | Metric | Recommended threshold |
|---------|--------|-----------------------|
| App Service | `CpuPercentage` | > 80% for 5 min |
| App Service | `Http5xx` | > 10 per minute |
| AKS | Node CPU | > 80% |
| Azure SQL | `dtu_consumption_percent` | > 85% |
| Storage | `Availability` | < 99.9% |

```bash
# Create metric alert
az monitor metrics alert create \
  --name "High-CPU-App" \
  --resource-group my-rg \
  --scopes /subscriptions/.../sites/my-app \
  --condition "avg Percentage CPU > 80" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action /subscriptions/.../actionGroups/pagerduty-ag
```

## Tagging Strategy

| Tag Key | Value example | Purpose |
|---------|--------------|---------|
| `project` | `bt-engine` | Cost allocation |
| `environment` | `production` | Distinguish envs |
| `sprint` | `SPRINT-0004` | Cost attribution |
| `managed-by` | `bicep` | IaC-managed |
| `owner` | `team-name` | Escalation |

Apply tags at the resource group level; inherit to resources where possible using Azure Policy.

## Secrets Management (Key Vault)

```bash
# Create Key Vault
az keyvault create \
  --name my-kv-prod \
  --resource-group my-rg \
  --sku standard \
  --enable-rbac-authorization true  # use RBAC, not access policies

# Store secret
az keyvault secret set --vault-name my-kv-prod --name DBPassword --value "s3cr3t"

# Reference in App Service (Key Vault reference)
az webapp config appsettings set \
  --name my-app \
  --resource-group my-rg \
  --settings "DB_PASSWORD=@Microsoft.KeyVault(VaultName=my-kv-prod;SecretName=DBPassword)"
```

**Never** store secrets in Bicep parameter files committed to git. Use `secureString` parameter type or reference Key Vault in the parameter file:
```json
{
  "sqlPassword": {
    "reference": {
      "keyVault": { "id": "/subscriptions/.../vaults/my-kv-prod" },
      "secretName": "SqlPassword"
    }
  }
}
```

## Change log
- 1.0 (2026-11-21): first release in agent-stack.
