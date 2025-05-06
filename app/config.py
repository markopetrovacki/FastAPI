#from pydantic import BaseSettings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    database_url: str

    class Config:
        env_file = ".env"


settings = Settings()