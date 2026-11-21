---
name: github-actions
description: "GitHub Actions reference for devops-engineer: workflow YAML structure, reusable workflows, matrix builds, caching, secrets handling, docker build and push pattern, deploy-to-staging and deploy-to-production job patterns with environment protection rules, status checks, and branch protection."
---

# GitHub Actions Skill

Version: 1.0 (2026-11-21)

## Workflow YAML Structure

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:          # allow manual trigger

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true   # cancel in-progress run on new push to same branch

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements*.txt') }}
          restore-keys: ${{ runner.os }}-pip-

      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-dev.txt

      - name: Run tests
        run: pytest --tb=short -q
```

## Secrets Handling

```yaml
# Reference secrets via ${{ secrets.SECRET_NAME }}
- name: Login to container registry
  uses: docker/login-action@v3
  with:
    registry: ${{ secrets.REGISTRY_URL }}
    username: ${{ secrets.REGISTRY_USER }}
    password: ${{ secrets.REGISTRY_PASSWORD }}
```

**Never:**
- Echo a secret: `run: echo ${{ secrets.TOKEN }}` — GitHub masks secrets in logs, but this is bad practice and can leak via string interpolation.
- Pass secrets as build args: `docker build --build-arg SECRET=${{ secrets.TOKEN }}` — secrets end up in image layer history.
- Store secrets in repository files — use GitHub Secrets or environment secrets.

**Do:**
- Use environment protection secrets for production credentials (only available when deploying to the `production` environment).
- Rotate secrets after any accidental exposure.

## Docker Build and Push Pattern

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image_tag: ${{ steps.meta.outputs.tags }}
      image_sha: ${{ steps.build.outputs.digest }}
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=sha,prefix=sha-
            type=semver,pattern={{version}}
            type=raw,value=latest,enable=${{ github.ref == 'refs/heads/main' }}

      - name: Build and push
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Scan image for vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/${{ github.repository }}:sha-${{ github.sha }}
          exit-code: '1'
          severity: 'CRITICAL'
```

## Deploy to Staging Job

```yaml
  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment: staging          # uses staging environment secrets
    steps:
      - name: Deploy to staging
        env:
          IMAGE_TAG: ${{ needs.build.outputs.image_sha }}
          KUBECONFIG_DATA: ${{ secrets.STAGING_KUBECONFIG }}
        run: |
          echo "$KUBECONFIG_DATA" | base64 -d > /tmp/kubeconfig
          KUBECONFIG=/tmp/kubeconfig kubectl set image deployment/my-app \
            my-app=ghcr.io/${{ github.repository }}@${IMAGE_TAG} \
            -n staging
          KUBECONFIG=/tmp/kubeconfig kubectl rollout status deployment/my-app -n staging

      - name: Run smoke tests
        run: |
          curl -f https://staging.example.com/health || exit 1
```

## Deploy to Production Job

```yaml
  deploy-production:
    needs: [build, deploy-staging]
    runs-on: ubuntu-latest
    environment: production        # uses production environment secrets
                                   # AND requires manual approval in GitHub UI
    steps:
      - name: Deploy to production
        env:
          IMAGE_TAG: ${{ needs.build.outputs.image_sha }}
          KUBECONFIG_DATA: ${{ secrets.PROD_KUBECONFIG }}
        run: |
          echo "$KUBECONFIG_DATA" | base64 -d > /tmp/kubeconfig
          KUBECONFIG=/tmp/kubeconfig kubectl set image deployment/my-app \
            my-app=ghcr.io/${{ github.repository }}@${IMAGE_TAG} \
            -n production
          KUBECONFIG=/tmp/kubeconfig kubectl rollout status deployment/my-app -n production

      - name: Production smoke test
        run: |
          curl -f https://app.example.com/health || exit 1
```

## Environment Protection Rules

Configure in GitHub → Repository Settings → Environments:

**production environment:**
- Required reviewers: 1+ (manual approval gate before workflow proceeds)
- Deployment branches: `main` only
- Secrets: `PROD_KUBECONFIG`, `PROD_DB_URL`, etc.

**staging environment:**
- No required reviewers (automated)
- Deployment branches: `main` only
- Secrets: `STAGING_KUBECONFIG`, etc.

## Reusable Workflows

```yaml
# .github/workflows/reusable-test.yml
on:
  workflow_call:
    inputs:
      python-version:
        type: string
        default: '3.13'
    secrets:
      PYPI_TOKEN:
        required: false

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}
      - run: pytest
```

```yaml
# Calling the reusable workflow
jobs:
  test:
    uses: ./.github/workflows/reusable-test.yml
    with:
      python-version: '3.13'
    secrets:
      PYPI_TOKEN: ${{ secrets.PYPI_TOKEN }}
```

## Matrix Builds

```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version: ['3.11', '3.12', '3.13']
        os: [ubuntu-latest, windows-latest]
      fail-fast: false  # continue other matrix jobs if one fails
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
```

## Caching

```yaml
# Python pip cache
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements*.txt') }}
    restore-keys: ${{ runner.os }}-pip-

# Node npm cache
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'               # built-in caching in setup-node

# Docker layer cache (via docker/build-push-action)
cache-from: type=gha
cache-to: type=gha,mode=max
```

## Branch Protection

Recommended settings for `main`:
- Require pull request reviews (1+ approver)
- Require status checks to pass: `test`, `build` jobs
- Require branches to be up to date before merging
- Do not allow force pushes
- Do not allow deletions

## Change log
- 1.0 (2026-11-21): first release in agent-stack.
