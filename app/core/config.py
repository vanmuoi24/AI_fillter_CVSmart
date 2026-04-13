class Settings:
    APP_NAME: str = "CV Screening API"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    ALLOWED_ORIGINS = ["*"]  # Khi deploy thì thay bằng domain frontend


settings = Settings()