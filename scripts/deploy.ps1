param(
    [string]$ImageTag = "latest"
)

$ErrorActionPreference = "Stop"

if (-not $env:ACR_LOGIN_SERVER) {
    throw "Set ACR_LOGIN_SERVER, for example: `$env:ACR_LOGIN_SERVER = 'myregistry.azurecr.io'"
}

kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

$manifest = Get-Content k8s/deployment.yaml -Raw
$manifest = $manifest.Replace("ACR_LOGIN_SERVER/image-generator:latest", "$env:ACR_LOGIN_SERVER/image-generator:$ImageTag")
$manifest | kubectl apply -f -
kubectl -n image-generator rollout status deployment/image-generator
