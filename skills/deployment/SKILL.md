# Deployment Skill — ACUA

Guidance for containerizing and deploying Azure Cost & Usage Analyzer to Azure Container Apps using Docker and GitHub Actions.

## When to Use This Skill

Reference this skill when:
- Writing a `Dockerfile` for the Streamlit application
- Creating or updating GitHub Actions CI/CD workflows
- Configuring Azure Container Registry (ACR) for image storage
- Deploying or redeploying the app to Azure Container Apps
- Troubleshooting container image builds or deployment failures
- Setting up managed identity for the container app
- Configuring environment-specific settings (staging, production)

## Tech Context

- **Base image**: `python:3.11-slim` (minimal Python runtime)
- **Application framework**: Streamlit
- **App port**: `8501` (Streamlit default, cannot be easily changed)
- **Container registry**: Azure Container Registry (ACR)
- **Deployment target**: Azure Container Apps (serverless containers)
- **Authentication in container**: Managed Identity (no API keys, secrets, or connection strings in image)
- **CI/CD pipeline**: GitHub Actions
- **Build trigger**: Merge to main branch; manual trigger via workflow dispatch
- **Registry**: ACUA images tagged by Git branch/commit SHA or semantic version

## Rules

1. **Dockerfile must NOT include any Azure credentials, secrets, API keys, or connection strings** — all authentication is handled via managed identity at runtime in Container Apps; never bake secrets into the container image.

2. **Use managed identity for Azure authentication in Container Apps** — configure the Container App with a managed identity and assign appropriate RBAC roles; never use environment variables or secrets for Azure SDK authentication.

3. **Copy `requirements.txt` and install dependencies before copying app code** — this ensures Docker layer caching works correctly; dependencies don't need to rebuild if only app code changes.

4. **Start Streamlit with explicit server configuration: `streamlit run app/main.py --server.port=8501 --server.address=0.0.0.0`** — bind to `0.0.0.0` so the container is accessible from outside; Streamlit in container requires explicit settings.

5. **GitHub Actions workflow must run `pytest` tests before building and pushing the Docker image** — fail fast on test failures and never push a broken image to ACR.

6. **Configure Container Apps with `--min-replicas 0` for demo/dev environments to minimize costs** — apps scale to zero when not in use; use `--min-replicas 1` only for production.

7. **Never push to Azure Container Registry from a local machine or during manual workflows** — always use GitHub Actions running with service principal or managed identity; ensures consistent, auditable deployments.

8. **Use semantic versioning for image tags in production and Git commit SHA for development builds** — this enables rollback and clear versioning; commit SHA for dev builds enables quick iteration and traceability.

## Dockerfile Pattern

```dockerfile
# Use python:3.11-slim as base image for minimal footprint
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables for Streamlit (non-interactive mode)
ENV STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    PYTHONUNBUFFERED=1

# Install system dependencies if needed (keep minimal)
# RUN apt-get update && apt-get install -y --no-install-recommends <packages> && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install Python dependencies
# This layer is cached and only rebuilt if requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY context/ ./context/

# Create non-root user for security (optional but recommended)
RUN useradd -m -u 1000 streamlituser && chown -R streamlituser:streamlituser /app
USER streamlituser

# Expose Streamlit port (documentation only; Container Apps manages ingress)
EXPOSE 8501

# Health check endpoint (Streamlit doesn't have built-in health check)
# Container Apps will use HTTP probe on port 8501 by default
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8501')" || exit 1

# Start Streamlit app
CMD ["streamlit", "run", "app/main.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--logger.level=info"]
```

## GitHub Actions Pattern

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy to Azure Container Apps

on:
  push:
    branches:
      - main
  workflow_dispatch:  # Allow manual trigger

env:
  REGISTRY: ${{ secrets.ACR_LOGIN_SERVER }}  # Example: myacr.azurecr.io
  IMAGE_NAME: acua
  DOCKERFILE_PATH: ./Dockerfile

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run pytest
        run: |
          pytest tests/ -v --cov=app --cov-report=xml

      - name: Upload coverage to Codecov (optional)
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          fail_ci_if_error: false

  build-and-deploy:
    name: Build and Deploy
    runs-on: ubuntu-latest
    needs: test
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Azure Login (OIDC)
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Build and push Docker image to ACR
        run: |
          az acr build \
            --registry ${{ secrets.ACR_NAME }} \
            --image ${{ env.IMAGE_NAME }}:${{ github.sha }} \
            --image ${{ env.IMAGE_NAME }}:latest \
            --file ${{ env.DOCKERFILE_PATH }} \
            .

      - name: Deploy to Azure Container Apps
        run: |
          az containerapp update \
            --name acua-app \
            --resource-group ${{ secrets.RESOURCE_GROUP }} \
            --image ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}

      - name: Verify deployment
        run: |
          echo "Deployment complete. App URL: https://acua-app.${{ secrets.CONTAINER_APPS_ENVIRONMENT }}.azurecontainerapps.io"

  notify:
    name: Notify Deployment Status
    runs-on: ubuntu-latest
    needs: build-and-deploy
    if: always()
    steps:
      - name: Deployment Status
        run: |
          if [ "${{ job.status }}" = "success" ]; then
            echo "✅ Deployment succeeded"
          else
            echo "❌ Deployment failed"
            exit 1
          fi
```

**Required GitHub Secrets:**
- `AZURE_CLIENT_ID`: Entra app/client ID used by GitHub OIDC
- `AZURE_TENANT_ID`: Azure tenant ID
- `AZURE_SUBSCRIPTION_ID`: Azure subscription ID
- `ACR_NAME`: Azure Container Registry name (e.g., `myacr`)
- `ACR_LOGIN_SERVER`: ACR login server URL (e.g., `myacr.azurecr.io`)
- `RESOURCE_GROUP`: Azure resource group name
- `CONTAINER_APPS_ENVIRONMENT`: Container Apps environment name

## Common Mistakes

| Mistake | Fix |
|---|---|
| Hardcoding Azure credentials or connection strings in `Dockerfile` or `.env` files | Never. Use managed identity in Container Apps; let the runtime provide credentials via Azure SDK. |
| Starting Streamlit without `--server.address=0.0.0.0` in the container | Streamlit binds to `localhost` by default, making it unreachable from outside the container. Always use `0.0.0.0`. |
| Installing dependencies AFTER copying app code in `Dockerfile` | This defeats Docker layer caching. Always copy `requirements.txt` and install first; reinstalling only happens if dependencies change. |
| Pushing images to ACR directly from local machine via Docker CLI | Use GitHub Actions and `az acr build` or `az acr login` for consistency. Local pushes are error-prone and not auditable. |
| Forgetting to set `--min-replicas 0` for demo/dev containers | Keeps container running 24/7, wasting money. Use minimum replicas 0 for dev/demo and only 1+ for production. |
| Not running tests in the CI/CD pipeline before building the image | Broken code gets deployed. Always run `pytest` and fail fast before the Docker build step. |
