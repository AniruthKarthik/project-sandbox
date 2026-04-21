from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")
    app_name: str = "Dingest"
    debug: bool = False
    max_upload_size_mb: int = 20
    allowed_extensions: set[str] = {"pdf", "docx", "xlsx", "xls", "pptx", "csv"}
    upload_dir: str = "/tmp/dingest_uploads"


settings = Settings()
