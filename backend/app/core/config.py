from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TrustLayer API Gateway"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True

    database_url: str = (
        "postgresql+psycopg://trustmesh:"
        "trustmesh_dev_password@localhost:5432/trustmesh"
    )

    siwe_chain_id: int = 80002
    siwe_domain: str = "localhost"

    polygon_amoy_rpc_url: str = "https://polygon-amoy-bor-rpc.publicnode.com"
    polygon_chain_id: int = 80002

    deployer_private_key: str | None = None
    did_registry_address: str | None = None
    policy_engine_address: str | None = None
    asset_nft_address: str | None = None
    audit_logger_address: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
