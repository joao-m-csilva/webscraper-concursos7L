from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./concursos.db"
    base_portal_url: str = "https://www.setelagoas.mg.gov.br"
    request_timeout: float = 20.0
    user_agent: str = "Mozilla/5.0 (compatible; ConcursosScraper/1.0)"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
