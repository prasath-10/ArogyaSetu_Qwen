from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    qwen_api_key: str = ""
    qwen_base_url: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    qwen_model: str = "qwen-max"

    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_verify_token: str = "arogya_verify"

    database_url: str = "postgresql://user:password@localhost:5432/arogya"
    redis_url: str = "redis://localhost:6379/0"

    emergency_webhook_url: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
