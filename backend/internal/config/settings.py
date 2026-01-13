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
    
    # User Roles
    ROLE_ADMIN: str = os.getenv("ROLE_ADMIN", "admin")
    ROLE_USER: str = os.getenv("ROLE_USER", "user")
    
    # Default Admin Credentials
    DEFAULT_ADMIN_USERNAME: str = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_PASSWORD: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin")
    
    # Queue Status Values
    QUEUE_STATUS_PENDING: str = os.getenv("QUEUE_STATUS_PENDING", "pending")
    QUEUE_STATUS_AUTO_APPLIED: str = os.getenv("QUEUE_STATUS_AUTO_APPLIED", "auto-applied")
    QUEUE_STATUS_PROCESSED: str = os.getenv("QUEUE_STATUS_PROCESSED", "processed")
    QUEUE_STATUS_REJECTED: str = os.getenv("QUEUE_STATUS_REJECTED", "rejected")
    
    # Default Subteams
    DEFAULT_SUBTEAMS: List[str] = os.getenv(
        "DEFAULT_SUBTEAMS",
        "Aero,Engine,Suspension,Electronics,Chassis,Powertrain,Data Acquisition"
    ).split(",") if os.getenv("DEFAULT_SUBTEAMS") else [
        "Aero", "Engine", "Suspension", "Electronics", "Chassis", "Powertrain", "Data Acquisition"
    ]
    
    # MoTeC Configuration
    MOTEC_DEFAULT_SUBTEAM: str = os.getenv("MOTEC_DEFAULT_SUBTEAM", "MoTeC")
    MOTEC_LDX_EXTENSION: str = os.getenv("MOTEC_LDX_EXTENSION", ".ldx")
    MOTEC_LD_EXTENSION: str = os.getenv("MOTEC_LD_EXTENSION", ".ld")
    MOTEC_LD_HEADER_SIZE: int = int(os.getenv("MOTEC_LD_HEADER_SIZE", "2048"))
    
    # Car Identification Patterns (comma-separated regex patterns)
    CAR_ID_PATTERNS: List[str] = os.getenv(
        "CAR_ID_PATTERNS",
        "car[_\s-]?(\\d+),vehicle[_\s-]?(\\d+),chassis[_\s-]?(\\d+),(\\d+)[_\s-]?car"
    ).split(",") if os.getenv("CAR_ID_PATTERNS") else [
        r'car[_\s-]?(\d+)',
        r'vehicle[_\s-]?(\d+)',
        r'chassis[_\s-]?(\d+)',
        r'(\d+)[_\s-]?car'
    ]
    
    # Car identifier fields in MoTeC Details section (comma-separated)
    CAR_ID_DETAILS_FIELDS: List[str] = os.getenv(
        "CAR_ID_DETAILS_FIELDS",
        "Car,Car ID,Car Identifier,Vehicle,Vehicle ID,Chassis,Chassis Number,Car Number,Car Name"
    ).split(",") if os.getenv("CAR_ID_DETAILS_FIELDS") else [
        "Car", "Car ID", "Car Identifier", "Vehicle", "Vehicle ID",
        "Chassis", "Chassis Number", "Car Number", "Car Name"
    ]
    
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
            "role_admin": cls.ROLE_ADMIN,
            "role_user": cls.ROLE_USER,
            "default_subteams": cls.DEFAULT_SUBTEAMS,
            "motec_default_subteam": cls.MOTEC_DEFAULT_SUBTEAM,
        }


# Create singleton instance
settings = Settings()
