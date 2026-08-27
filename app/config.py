from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./citizeneye.db"
    gemini_api_key: str = ""
    africastalking_username: str = ""
    africastalking_api_key: str = ""
    africastalking_sender_id: str = ""
    allowed_origins: str = "http://localhost:8081,http://localhost:19006"
    scrape_interval_minutes: int = 30
    sms_delivery_interval_minutes: int = 5

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
