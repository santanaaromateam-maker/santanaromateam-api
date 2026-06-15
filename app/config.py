from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    secret_key: str = "dev-secret-change-me"
    access_token_expire_minutes: int = 480

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "santana_aroma"

    admin_email: str = "admin@santanaaromateam.com"
    admin_password: str = "change-me"

    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""
    cloudinary_folder: str = "santana-aroma/services"

    admin_origin: str = "http://localhost:5173"
    web_origin: str = "http://localhost:5500,https://santanaaromateam.com"
    # Optional extra origins (comma-separated), e.g. alternate admin URLs on Render
    cors_origins: str = ""

    @staticmethod
    def _normalize_origin(value: str) -> str:
        return value.strip().strip('"').strip("'").rstrip("/")

    @property
    def cors_origin_list(self) -> list[str]:
        origins: set[str] = set()
        for raw in (self.admin_origin, self.web_origin, self.cors_origins):
            for origin in raw.split(","):
                origin = self._normalize_origin(origin)
                if origin:
                    origins.add(origin)
        return sorted(origins)

    @property
    def cloudinary_configured(self) -> bool:
        return bool(self.cloudinary_cloud_name and self.cloudinary_api_key and self.cloudinary_api_secret)


settings = Settings()
