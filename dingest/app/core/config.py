from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Dingest"
    debug: bool = False
    max_upload_size_mb: int = 20
    allowed_extensions: set[str] = {"pdf", "docx", "xlsx", "xls", "pptx", "csv"}
    upload_dir: str = "/tmp/dingest_uploads"

    class Config:
        env_file = ".env"


settings = Settings()
