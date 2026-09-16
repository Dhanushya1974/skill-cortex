from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str = "development"
    DATABASE_URL: str
    CORS_ORIGINS: list[str] = []
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    RAZORPAY_KEY_ID: str
    RAZORPAY_KEY_SECRET: str
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "Skill Cortex <no-reply@skillcortex.com>"
    SMTP_USE_TLS: bool = True
    FRONTEND_URL: str = "http://localhost:5173"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.6-flash"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
