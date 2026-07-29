# AKS Image Generator sample

A small, modular FastAPI service that returns a PNG generated from a text prompt. It is deliberately self-contained: it does not need a model API key, database, or persistent volume.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs`, or generate an image:

```powershell
curl.exe -X POST "http://localhost:8000/v1/images" -H "Content-Type: application/json" -d "{\"prompt\":\"purple mountain sunrise\"}" --output image.png
```

Run checks with `pytest`, `bandit -r app`, and `ruff check .`.

## Container

```powershell
docker build -t image-generator:local .
docker run --rm -p 8000:8000 image-generator:local
```

## Deploy to AKS

1. Install the NGINX Ingress Controller once per cluster. The included values file makes its service public:

   ```powershell
   helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
   helm repo update
   helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx --namespace ingress-nginx --create-namespace --values k8s/ingress-nginx-values.yaml
   ```

2. Substitute the ACR login server and (optionally) hostname, then apply the app resources:

   ```powershell
   $env:ACR_LOGIN_SERVER = "myregistry.azurecr.io"
   $env:INGRESS_HOST = "images.example.com" # omit to use the load-balancer IP
   .\scripts\deploy.ps1
   ```

   For a private ACR, attach it to AKS first: `az aks update --resource-group <rg> --name <aks-name> --attach-acr <acr-name>`.

3. Verify:

   ```powershell
   kubectl -n image-generator rollout status deployment/image-generator
   kubectl -n image-generator get pods,svc,ingress
   curl.exe -X POST "http://<INGRESS-IP>/v1/images" -H "Content-Type: application/json" -d "{\"prompt\":\"AKS test\"}" --output aks-image.png
   ```

Set `INGRESS_HOST` and update DNS before using the hostname. The ingress defaults to no host, which accepts traffic sent to the controller's external IP.

## GitHub Actions

The workflow runs unit tests, Ruff and Bandit source scans, Trivy filesystem/image scans, then builds and pushes to ACR on pushes to `main` (or manually). Configure these repository secrets:

- `AZURE_CREDENTIALS`: Azure service-principal JSON accepted by `azure/login`.
- `ACR_NAME`: registry resource name, e.g. `myregistry`.
- `ACR_LOGIN_SERVER`: e.g. `myregistry.azurecr.io`.

The Azure identity needs the **AcrPush** role on the registry. The published image is tagged with both the commit SHA and `latest`.
