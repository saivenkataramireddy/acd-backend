from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Accident & Emergency Alert API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    MYSQL_URL: str = "mysql+aiomysql://user:password@localhost:3306/acd_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

    # Allow extra environment variables automatically injected by Windows or other services
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
