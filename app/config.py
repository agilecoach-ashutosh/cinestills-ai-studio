from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    invoke_base_url: str = "http://127.0.0.1:9090"
    app_name: str = "CineStills AI Studio"
    version: str = "0.3.1"


CONFIG = AppConfig()
