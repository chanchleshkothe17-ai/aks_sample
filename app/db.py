"""Database connectivity — no password, connection string secret, or Key Vault
lookup anywhere in this file. Passwordless Azure AD Workload Identity auth
against Azure Database for MySQL Flexible Server.

  1. AKS's Workload Identity webhook sees this pod's ServiceAccount is annotated
     with an Azure managed identity's client ID (set up in Kubernetes, not here).
  2. It automatically injects a short-lived, auto-rotated federated token file
     into the pod plus a few env vars (AZURE_CLIENT_ID, AZURE_TENANT_ID,
     AZURE_FEDERATED_TOKEN_FILE) — no code change needed for that part.
  3. DefaultAzureCredential (below) finds those env vars on its own and
     exchanges the token for a real Azure AD access token, scoped to
     "https://ossrdbms-aad.database.windows.net/.default" (MySQL's AAD scope —
     different from Azure SQL's "https://database.windows.net/.default").
  4. That token is sent as the MySQL password, over a TLS connection, on every
     new physical connection — never written to disk, never reused past its
     ~60-90 minute lifetime.

If this same code runs on your laptop instead of in the cluster, DefaultAzureCredential
just falls back to your local `az login` session instead — nothing here is AKS-specific.
"""

from azure.identity import DefaultAzureCredential
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.config import get_settings

TOKEN_SCOPE = "https://ossrdbms-aad.database.windows.net/.default"

settings = get_settings()
credential = DefaultAzureCredential()

engine = create_engine(
    f"mysql+pymysql://{settings.azure_mysql_aad_username}@"
    f"{settings.azure_mysql_server}:3306/{settings.azure_mysql_database}",
    connect_args={"ssl": {"ssl": True}},
    pool_pre_ping=True,
    # Recycle connections well before a token would expire so a long-lived pod
    # never tries to reuse a stale one.
    pool_recycle=1500,
)


@event.listens_for(engine, "do_connect")
def _attach_fresh_access_token(dialect, conn_rec, cargs, cparams):
    """Runs on every new physical connection — fetches a brand-new AAD token each time
    and hands it to pymysql as the password."""
    cparams["password"] = credential.get_token(TOKEN_SCOPE).token
    cparams["ssl"] = {"ssl": True}


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """FastAPI dependency — yields a session, always closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
