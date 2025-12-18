"""
Configuration settings for Parameter Management System
All settings can be overridden via environment variables
"""
import os
from pathlib import Path
from typing import List

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed, use environment variables only

class Settings:
    """Application settings loaded from environment variables"""
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    RELOAD: bool = os.getenv("RELOAD", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Data Directory
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", str(BASE_DIR.parent / "data")))
    
    # Frontend paths
    TEMPLATES_DIR: Path = BASE_DIR.parent / "frontend" / "templates"
    STATIC_DIR: Path = BASE_DIR.parent / "frontend" / "static"
    
    @classmethod
    def get_settings_dict(cls) -> dict:
        """Get all settings as a dictionary"""
        return {
            "host": cls.HOST,
            "port": cls.PORT,
            "reload": cls.RELOAD,
            "log_level": cls.LOG_LEVEL,
            "cors_origins": cls.CORS_ORIGINS,
            "data_dir": str(cls.DATA_DIR),
            "templates_dir": str(cls.TEMPLATES_DIR),
            "static_dir": str(cls.STATIC_DIR),
        }


# Create singleton instance
settings = Settings()
