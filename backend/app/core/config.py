import secrets
from typing import List, Optional, Union, Dict, Any
from pydantic import AnyHttpUrl, PostgresDsn, validator, SecretStr, EmailStr, constr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Nonprofit Donation Platform"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "your-super-secret-key-please-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "nonprofit_platform"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @property
    def get_database_url(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    # XRPL Settings
    XRPL_NETWORK: str = "testnet"
    @validator("XRPL_NETWORK")
    def validate_xrpl_network(cls, v: str) -> str:
        if v not in ["testnet", "devnet", "mainnet"]:
            raise ValueError("XRPL_NETWORK must be one of: testnet, devnet, mainnet")
        return v

    XRPL_SEED: Optional[SecretStr] = None
    XRPL_ACCOUNT: Optional[str] = None
    
    # XUMM Wallet Integration
    XUMM_API_KEY: Optional[SecretStr] = None
    XUMM_API_SECRET: Optional[SecretStr] = None

    # AWS Settings
    AWS_ACCESS_KEY_ID: Optional[SecretStr] = None
    AWS_SECRET_ACCESS_KEY: Optional[SecretStr] = None
    AWS_REGION: Optional[str] = None
    S3_BUCKET: Optional[str] = None

    # Email Settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[SecretStr] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # Admin user
    FIRST_ADMIN_EMAIL: EmailStr
    FIRST_ADMIN_PASSWORD: SecretStr

    @validator("FIRST_ADMIN_PASSWORD")
    def validate_admin_password(cls, v: SecretStr) -> SecretStr:
        if len(v.get_secret_value()) < 8:
            raise ValueError("Admin password must be at least 8 characters long")
        return v

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings() 