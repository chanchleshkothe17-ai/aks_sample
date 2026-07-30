# Wiring up Azure Database for MySQL + Workload Identity (the "IRSA-equivalent" setup)

Corrected for the database you actually have — `aks-sql`, an **Azure Database for
MySQL Flexible Server** (not Azure SQL/SQL Server, which is a different product
with different Entra ID plumbing).

## 1 — turn on Entra ID authentication on the MySQL server
Open `aks-sql` → **Settings → Authentication** (not a top-level "Microsoft Entra ID"
item — that naming is specific to Azure SQL Database).
1. Choose **MySQL authentication and Microsoft Entra authentication** (keeps your
   existing `akssql` login working too, safest while testing).
2. **Set admin** → select your own Entra ID user or a group → **Save**.

## 2 — create the managed identity for the app
Search bar → **"Managed Identities"** → **+ Create** → name `image-generator-identity`,
same resource group as `aks-sql` → **Create**. Open it and copy both the **Client ID**
and the **Object (principal) ID** from the Overview page — you'll need both, for
different steps below.

## 3 — turn on Workload Identity on AKS (skip if already on)
Your AKS cluster → **Settings → Cluster configuration** → check **Workload Identity**
and **OIDC issuer** → **Save**.

## 4 — federate the identity to the exact namespace + service account
Open `image-generator-identity` → **Settings → Federated credentials** →
**+ Add credential** → scenario **Kubernetes accessing Azure resources** → your
cluster, namespace `image-generator`, service account `image-generator-sa` → **Add**.

## 5 — put the real client ID into the manifest
Edit `k8s/serviceaccount.yaml`, replace `<AZURE_MANAGED_IDENTITY_CLIENT_ID>` with
the Client ID from step 2.

## 6 — create the matching MySQL user (this is the step people forget)
Entra ID authentication alone only proves *who* is connecting — MySQL still needs
a user mapped to that identity, with real grants. Connect to `aks-sql` with your
own Entra admin account (via **MySQL Workbench**, `mysql` CLI, or Cloud Shell using
`mysql --host=aks-sql.mysql.database.azure.com --user=<your-aad-email> --enable-cleartext-plugin --password=<token from az account get-access-token --resource-type oss-rdbms>`),
then run:

```sql
SET aad_auth_validate_oids_in_tenant = OFF;
CREATE AADUSER 'image-generator-identity' IDENTIFIED BY '<Object ID from step 2>';
GRANT ALL PRIVILEGES ON imagegendb.* TO 'image-generator-identity'@'%';
FLUSH PRIVILEGES;
```

The username here (`image-generator-identity`) must exactly match
`azure_mysql_aad_username` in `app/config.py` — that's what the app authenticates as.
The value after `IDENTIFIED BY` is the identity's **Object ID**, not a real password —
MySQL uses it internally to map the login to the Entra identity.

## 7 — create the database if it doesn't exist yet
Still in the same session:
```sql
CREATE DATABASE IF NOT EXISTS imagegendb;
```

## 8 — deploy
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/serviceaccount.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

## 9 — prove it's actually passwordless
```bash
kubectl logs -n image-generator deploy/image-generator
```
On startup you should see the table get created with no connection error. Then:
```
POST /v1/images        {"prompt": "purple mountain sunrise"}
POST /v1/images        {"prompt": "purple mountain sunrise"}   # same prompt again
GET  /v1/images/history
```
The history endpoint should show `request_count: 2` for that prompt — proof the
fetch-and-update against MySQL is working, and nowhere in this flow did a password
touch your code, your image, or your cluster.

## If you hit "Client does not support authentication protocol"
This means the connection tried standard MySQL auth instead of the AAD cleartext
token path — almost always means SSL wasn't actually negotiated. Double-check the
server's **Settings → Networking** has **Enforce SSL connection** on (matches
what we set when this server was created), and that nothing in your network path
(NSG, firewall) is silently downgrading the connection.
