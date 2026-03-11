# Deploying AlphaForge on Microsoft Azure

Two options — pick based on your skill level:

| Option | Difficulty | Cost | Best For |
|--------|-----------|------|----------|
| **A. Azure App Service** (direct Python) | Easy | ~₹1,500/month (B1) | Quick deployment |
| **B. Azure Container Apps** (Docker) | Medium | ~₹500–₹2,000/month | Production, scalable |

---

## Prerequisites (install these first)

```bash
# 1. Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# 2. Docker (only needed for Option B)
sudo apt-get install docker.io

# 3. Login to Azure
az login
# A browser window opens — sign in with your Microsoft account
```

---

## Option A: Azure App Service (Easiest)

### Step 1 — Create a Resource Group

A resource group is just a folder that holds all your Azure resources.

```bash
az group create \
  --name alphaforge-rg \
  --location eastasia
```

> **Why eastasia?** Closest Azure region to India with low latency. You can also use `centralindia` or `southindia` if available in your subscription.

### Step 2 — Create an App Service Plan

This is the server (virtual machine) that will run your app.

```bash
az appservice plan create \
  --name alphaforge-plan \
  --resource-group alphaforge-rg \
  --sku B1 \
  --is-linux
```

> **B1 plan:** 1 CPU core, 1.75 GB RAM — sufficient for AlphaForge. ~$13/month (~₹1,100).
> For more traffic, upgrade to B2 or P1V2.

### Step 3 — Create the Web App

```bash
az webapp create \
  --name alphaforge-app \
  --resource-group alphaforge-rg \
  --plan alphaforge-plan \
  --runtime "PYTHON:3.11"
```

> The app name must be globally unique. If `alphaforge-app` is taken, try `alphaforge-yourname-app`.

### Step 4 — Set Your API Key as an Environment Variable

**Never put secrets in your code.** Azure stores them securely as App Settings.

```bash
az webapp config appsettings set \
  --name alphaforge-app \
  --resource-group alphaforge-rg \
  --settings \
    GEMINI_API_KEY="your_actual_gemini_key_here" \
    SQLITE_DB_PATH="/home/data/db/alphaforge.db" \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

### Step 5 — Set the Startup Command

```bash
az webapp config set \
  --name alphaforge-app \
  --resource-group alphaforge-rg \
  --startup-file "startup.sh"
```

### Step 6 — Deploy the Code

```bash
cd /home/dharunthegreat/AlphaForge

# Create a zip of the project (excluding cache and secrets)
zip -r alphaforge.zip . \
  --exclude "*.pyc" \
  --exclude ".env" \
  --exclude "data/cache/*" \
  --exclude "data/db/*" \
  --exclude ".git/*" \
  --exclude "__pycache__/*"

# Deploy the zip
az webapp deploy \
  --name alphaforge-app \
  --resource-group alphaforge-rg \
  --src-path alphaforge.zip \
  --type zip
```

### Step 7 — Open Your App

```bash
az webapp browse --name alphaforge-app --resource-group alphaforge-rg
```

Your app will be live at:
```
https://alphaforge-app.azurewebsites.net
```

---

## Option B: Azure Container Apps (Recommended for Production)

This uses Docker — the app runs in an isolated container. More reliable, easier to update.

### Step 1 — Create Resource Group

```bash
az group create --name alphaforge-rg --location eastasia
```

### Step 2 — Create Azure Container Registry (ACR)

ACR is Azure's private Docker image storage.

```bash
az acr create \
  --name alphaforgeregistry \
  --resource-group alphaforge-rg \
  --sku Basic \
  --admin-enabled true
```

Get the registry credentials:
```bash
az acr credential show --name alphaforgeregistry
# Note down: username and password
```

### Step 3 — Build and Push the Docker Image

```bash
cd /home/dharunthegreat/AlphaForge

# Log into the registry
az acr login --name alphaforgeregistry

# Build the Docker image
docker build -t alphaforgeregistry.azurecr.io/alphaforge:latest .

# Push to Azure Container Registry
docker push alphaforgeregistry.azurecr.io/alphaforge:latest
```

> This will take 5-10 minutes the first time (downloading Python, installing packages).

### Step 4 — Create Container Apps Environment

```bash
az containerapp env create \
  --name alphaforge-env \
  --resource-group alphaforge-rg \
  --location eastasia
```

### Step 5 — Deploy the Container App

```bash
az containerapp create \
  --name alphaforge \
  --resource-group alphaforge-rg \
  --environment alphaforge-env \
  --image alphaforgeregistry.azurecr.io/alphaforge:latest \
  --registry-server alphaforgeregistry.azurecr.io \
  --registry-username alphaforgeregistry \
  --registry-password "$(az acr credential show --name alphaforgeregistry --query passwords[0].value -o tsv)" \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 1.0 \
  --memory 2.0Gi \
  --env-vars \
    GEMINI_API_KEY="your_actual_gemini_key_here" \
    SQLITE_DB_PATH="data/db/alphaforge.db"
```

### Step 6 — Get Your App URL

```bash
az containerapp show \
  --name alphaforge \
  --resource-group alphaforge-rg \
  --query properties.configuration.ingress.fqdn \
  --output tsv
```

Output will look like:
```
alphaforge.nicepebble-abc123.eastasia.azurecontainerapps.io
```

Open that URL in your browser — AlphaForge is live.

---

## Updating the App After Code Changes

### App Service update:
```bash
cd /home/dharunthegreat/AlphaForge
zip -r alphaforge.zip . --exclude "*.pyc" --exclude ".env" --exclude "data/*" --exclude ".git/*"
az webapp deploy --name alphaforge-app --resource-group alphaforge-rg --src-path alphaforge.zip --type zip
```

### Container Apps update:
```bash
cd /home/dharunthegreat/AlphaForge
docker build -t alphaforgeregistry.azurecr.io/alphaforge:latest .
docker push alphaforgeregistry.azurecr.io/alphaforge:latest

az containerapp update \
  --name alphaforge \
  --resource-group alphaforge-rg \
  --image alphaforgeregistry.azurecr.io/alphaforge:latest
```

---

## Automatic Deployment (GitHub Actions)

Every time you push code to GitHub, this automatically rebuilds and deploys.

### Setup:
1. Push your code to a GitHub repository (make sure `.env` is in `.gitignore`)
2. Go to your GitHub repo → Settings → Secrets and variables → Actions
3. Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `ACR_LOGIN_SERVER` | `alphaforgeregistry.azurecr.io` |
| `ACR_NAME` | `alphaforgeregistry` |
| `ACR_USERNAME` | From `az acr credential show` |
| `ACR_PASSWORD` | From `az acr credential show` |
| `AZURE_RESOURCE_GROUP` | `alphaforge-rg` |

Now every `git push` to `main` triggers automatic deployment.

---

## Important: Database Persistence

SQLite stores data in a file. On Azure, some compute options reset the filesystem on restart.

**App Service:** The `/home` directory IS persistent across restarts.
- The `startup.sh` already sets `SQLITE_DB_PATH=/home/data/db/alphaforge.db` ✅

**Container Apps:** The container filesystem resets on restart.
- For production, upgrade to **Azure Database for PostgreSQL** (or SQLite with Azure File Share mounted as a volume)
- For a demo/portfolio project, SQLite in the container is fine — you just lose saved data on restart

To mount persistent storage in Container Apps:
```bash
# Create a storage account
az storage account create \
  --name alphaforgestorage \
  --resource-group alphaforge-rg \
  --sku Standard_LRS

# Get the storage key
STORAGE_KEY=$(az storage account keys list \
  --account-name alphaforgestorage \
  --resource-group alphaforge-rg \
  --query "[0].value" -o tsv)

# Mount it to your container app
az containerapp storage mount create \
  --name alphaforgestorage \
  --app alphaforge \
  --resource-group alphaforge-rg \
  --storage-account-name alphaforgestorage \
  --storage-account-key "$STORAGE_KEY" \
  --mount-path /app/data \
  --share-name alphaforgedata
```

---

## Cost Estimate (India region)

| Service | Plan | Monthly Cost (approx) |
|---------|------|----------------------|
| App Service B1 | 1 core, 1.75GB | ~₹1,100 |
| App Service B2 | 2 core, 3.5GB | ~₹2,200 |
| Container Apps (1 core, 2GB, always on) | ~₹1,500 | |
| Container Registry Basic | | ~₹400 |
| Storage Account (10GB) | | ~₹20 |

**Cheapest option:** App Service B1 — ~₹1,100/month total.
**Free option:** Azure gives $200 free credits to new accounts — enough for 2-3 months.

---

## Troubleshooting

**App won't start / 500 error:**
```bash
# View live logs
az webapp log tail --name alphaforge-app --resource-group alphaforge-rg

# For Container Apps:
az containerapp logs show --name alphaforge --resource-group alphaforge-rg --follow
```

**Packages not installing:**
Make sure `requirements.txt` is in the root of the zip and `SCM_DO_BUILD_DURING_DEPLOYMENT=true` is set.

**Port error:**
Azure App Service always routes to port 8000 for Python apps. The `.streamlit/config.toml` already sets this. Do not change it.

**Memory issues:**
ML features (Random Forest, Monte Carlo with 5000 simulations) use a lot of RAM. Upgrade to B2 (3.5GB) if you see out-of-memory errors.

**yfinance rate limiting:**
Azure's outbound IP may get rate-limited by Yahoo Finance after many requests. Cache all data before deploying (run the app locally first to populate the cache, then include the `data/cache/` folder in your zip).

