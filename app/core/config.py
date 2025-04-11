from pydantic_settings import BaseSettings

class Settings(BaseSettings):  
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str

    # JWT
    JWT_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Database
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str
    SQLALCHEMY_DATABASE_URI: str = ""

    def __init__(self, **values):
        super().__init__(**values)
        self.SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@"
            f"{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    class Config:
        env_file = ".env"

settings = Settings()
