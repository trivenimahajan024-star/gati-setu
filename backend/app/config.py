import os

def load_env_file():
    possible_paths = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env")),
        os.path.abspath(".env")
    ]
    for env_path in possible_paths:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, val = line.split("=", 1)
                            key = key.strip()
                            val = val.strip().strip('"').strip("'")
                            if key and key not in os.environ:
                                os.environ[key] = val
            except Exception:
                pass

load_env_file()

class Settings:
    PROJECT_NAME: str = "GatiSetu"
    VERSION: str = "2.0.0"
    DESCRIPTION: str = "GatiSetu - Dynamic ETA & Railway Operations Platform"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    MOCK_MODE: bool = False
    MAPTILER_API_KEY: str = os.getenv("MAPTILER_API_KEY", "")
    RAILRADAR_API_KEY: str = os.getenv("RAILRADAR_API_KEY", "")
    GPS_FEED_URL: str = os.getenv("GPS_FEED_URL", "")
    GPS_API_KEY: str = os.getenv("GPS_API_KEY", "")
    
settings = Settings()
