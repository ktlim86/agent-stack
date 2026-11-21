---
name: docker
description: "Docker reference for devops-engineer: Dockerfile best practices (minimal base images, multi-stage builds, layer caching, non-root user), .dockerignore, docker-compose for local dev, image tagging conventions, health checks, secrets handling, and vulnerability scanning with docker scout or trivy."
---

# Docker Skill

Version: 1.0 (2026-11-21)

## Dockerfile Best Practices

### Minimal base images
```dockerfile
# Python — use slim or alpine variants
FROM python:3.13-slim AS base

# Node — use alpine for smallest footprint
FROM node:20-alpine AS base

# For distroless (even smaller, no shell — harder to debug)
FROM gcr.io/distroless/python3-debian12
```

**Never use** `latest` tag for base images — it changes without warning. Pin to a specific version (`python:3.13-slim`, not `python:latest`).

### Multi-stage builds (Python example)
```dockerfile
# Stage 1: build/install dependencies
FROM python:3.13-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: production image
FROM python:3.13-slim AS runner
WORKDIR /app

# Non-root user (security)
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --no-create-home appuser

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY --chown=appuser:appgroup . .

USER appuser
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Multi-stage builds (Node.js example)
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production  # install only prod deps
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
RUN addgroup --gid 1001 appgroup && adduser --uid 1001 --ingroup appgroup --disabled-password appuser
COPY --from=builder --chown=appuser:appgroup /app/dist ./dist
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
USER appuser
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

## Layer Caching Optimisation

**Order matters**: put layers that change least frequently first.

```dockerfile
# WRONG — requirements.txt reinstalled every time code changes
COPY . .
RUN pip install -r requirements.txt

# CORRECT — dependencies cached unless requirements.txt changes
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

## COPY vs ADD

- **Always use COPY** unless you specifically need ADD's features.
- ADD can extract tar archives and fetch URLs — this is rarely desirable in a Dockerfile and can introduce unexpected behaviour.
- Exception: `ADD https://...` for a single-file download from a trusted source (but prefer a `RUN curl` with checksum verification).

## Non-Root User

**Always run the application as a non-root user.** Root in a container can become root on the host if container escape occurs.

```dockerfile
# Create group and user with specific UID/GID (reproducible)
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --no-create-home --shell /bin/false appuser
USER appuser
```

## .dockerignore

```
.git
.gitignore
.env
.env.*
*.md
__pycache__
*.pyc
*.pyo
.pytest_cache
.venv
node_modules
dist
.DS_Store
*.log
```

Never let `.env` files, credentials, or test artifacts into the image.

## Health Checks

```dockerfile
# HTTP service
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Non-HTTP: check a process is running
HEALTHCHECK --interval=30s --timeout=3s \
  CMD pgrep -f "python main" || exit 1
```

The `--start-period` gives the container time to initialise before health checks begin (avoids false failures on slow startup).

## Secrets Handling

**Never put secrets in the image.** Layers are inspectable with `docker history` and `docker inspect`.

```dockerfile
# WRONG — secret visible in layer
ENV DB_PASSWORD=s3cr3t
RUN echo $DB_PASSWORD > /app/config

# CORRECT — pass secrets at runtime via environment
# (set DB_PASSWORD via orchestrator secrets mechanism, not in Dockerfile)

# CORRECT — BuildKit secrets for build-time secrets (e.g. private PyPI)
# syntax=docker/dockerfile:1
RUN --mount=type=secret,id=pip_token \
    pip install --extra-index-url https://$(cat /run/secrets/pip_token)@...
```

At runtime:
- Kubernetes: use `Secret` objects mounted as environment variables or files.
- ECS: use Secrets Manager references in task definition.
- Docker Compose: use `secrets:` block pointing to local files (not hardcoded values).

## docker-compose for Local Dev

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/mydb
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - .:/app                    # hot reload for dev (remove in prod)

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass     # dev only — never commit real creds
      POSTGRES_DB: mydb
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "user"]
      interval: 5s
      timeout: 3s
      retries: 5
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

```bash
docker compose up -d          # start detached
docker compose logs -f app    # follow app logs
docker compose down           # stop and remove containers
docker compose down -v        # also remove volumes (resets DB)
```

## Image Tagging Conventions

```bash
# Format: <registry>/<project>/<service>:<version>-<git-sha>
docker build \
  -t registry.example.com/bt-engine/api:1.0.0-$(git rev-parse --short HEAD) \
  -t registry.example.com/bt-engine/api:latest \
  .

# In CI/CD pipelines: use full git SHA for traceability
IMAGE_TAG=$(git rev-parse HEAD)
docker build -t registry.example.com/bt-engine/api:${IMAGE_TAG} .
```

**Never overwrite a previously pushed tag** (except `latest`). Immutable tags by SHA allow rollback to any version.

## Vulnerability Scanning

### Docker Scout
```bash
# Scan local image
docker scout cves my-image:latest

# Quick view
docker scout quickview my-image:latest

# Only show critical/high
docker scout cves --only-severity critical,high my-image:latest
```

### Trivy (alternative, CI-friendly)
```bash
# Install
brew install trivy  # macOS
# or: pip install trivy (via aqua)

# Scan image
trivy image my-image:latest

# Fail CI on critical vulnerabilities
trivy image --exit-code 1 --severity CRITICAL my-image:latest

# Output sarif for GitHub Security tab
trivy image --format sarif --output trivy-results.sarif my-image:latest
```

**Policy**: do not push images with Critical CVEs. For High CVEs, document the finding and apply a mitigation plan if no fix is yet available from the base image maintainer.

## Change log
- 1.0 (2026-11-21): first release in agent-stack.
