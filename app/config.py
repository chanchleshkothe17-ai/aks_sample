from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Non-secret configuration only.

    Notice there is no password, connection string secret, or token field here.
    The database credential is never something this app holds — it's fetched
    fresh, per connection, via Azure AD Workload Identity. See app/db.py.
    """

    model_config = SettingsConfigDict(env_prefix="APP_")

    azure_mysql_server: str = "aks-sql.mysql.database.azure.com"
    azure_mysql_database: str = "imagegendb"
    # This must exactly match the username used in `CREATE AADUSER` inside MySQL
    # (see SETUP.md) — for a managed identity, use its display name.
    azure_mysql_aad_username: str = "image-generator-identity"


@lru_cache
def get_settings() -> Settings:
    return Settings()
