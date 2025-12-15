"""
Configuration settings for trackside telemetry system
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
    
    # Paths - handle both local and Vercel deployment (define early for use in other settings)
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    
    # Server Configuration
    HOST: str = os.getenv("TEL_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("TEL_PORT", "8000"))
    RELOAD: bool = os.getenv("TEL_RELOAD", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("TEL_LOG_LEVEL", "info")
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = os.getenv("TEL_CORS_ORIGINS", "*").split(",")
    
    # WebSocket Configuration
    WS_UPDATE_RATE_HZ: float = float(os.getenv("TEL_WS_UPDATE_RATE", "10.0"))
    WS_UPDATE_INTERVAL: float = 1.0 / WS_UPDATE_RATE_HZ
    
    # Data Logging Configuration
    # Use /tmp on Vercel (writable), otherwise use project data dir
    DATA_DIR: Path = Path(os.getenv("TEL_DATA_DIR", str(BASE_DIR.parent / "data")))
    LOG_ENABLED: bool = os.getenv("TEL_LOG_ENABLED", "true").lower() == "true"
    LOG_FILE_PREFIX: str = os.getenv("TEL_LOG_PREFIX", "telemetry")
    
    # Telemetry Device Configuration
    DEVICE_PORT: str = os.getenv("TEL_DEVICE_PORT", "")
    DEVICE_BAUD: int = int(os.getenv("TEL_DEVICE_BAUD", "115200"))
    DEVICE_UPDATE_RATE_HZ: float = float(os.getenv("TEL_DEVICE_UPDATE_RATE", "10.0"))
    API_URL: str = os.getenv("TEL_API_URL", f"http://localhost:{PORT}")
    
    # Telemetry Data Schema (can be extended via config file)
    TELEMETRY_SCHEMA: dict = {}
    
    # Aero Configuration
    AERO_REF_DYNAMIC_PORT: int = int(os.getenv("AERO_REF_DYNAMIC_PORT", "7"))
    AERO_REF_STATIC_PORT: int = int(os.getenv("AERO_REF_STATIC_PORT", "8"))
    AERO_NUM_PORTS: int = int(os.getenv("AERO_NUM_PORTS", "8"))
    AERO_STRAIGHT_THRESHOLD: float = float(os.getenv("AERO_STRAIGHT_THRESHOLD", "0.1"))
    AERO_TURN_THRESHOLD: float = float(os.getenv("AERO_TURN_THRESHOLD", "0.3"))
    AERO_LATERAL_G_THRESHOLD: float = float(os.getenv("AERO_LATERAL_G_THRESHOLD", "0.2"))
    AERO_AVG_WINDOW_SIZE: int = int(os.getenv("AERO_AVG_WINDOW_SIZE", "100"))
    AERO_HISTOGRAM_BINS: int = int(os.getenv("AERO_HISTOGRAM_BINS", "20"))
    
    # Histogram range (parsed from comma-separated string)
    _histogram_range_str = os.getenv("AERO_HISTOGRAM_RANGE", "-3.0,3.0")
    AERO_HISTOGRAM_RANGE: List[float] = [float(x.strip()) for x in _histogram_range_str.split(",")]
    
    # Frontend histogram update rate
    AERO_HISTOGRAM_UPDATE_INTERVAL_MS: int = int(os.getenv("AERO_HISTOGRAM_UPDATE_INTERVAL_MS", "2000"))
    
    # MoTeC Configuration
    MOTEC_ENABLED: bool = os.getenv("MOTEC_ENABLED", "true").lower() == "true"
    MOTEC_NAS_BASE_PATH: str = os.getenv("MOTEC_NAS_BASE_PATH", "")
    MOTEC_LD_GLOB_PATTERN: str = os.getenv("MOTEC_LD_GLOB_PATTERN", "*.ld")
    MOTEC_LDX_TEMPLATE_DIR: Path = Path(os.getenv("MOTEC_LDX_TEMPLATE_DIR", "config/motec/templates"))
    MOTEC_LDX_OUTPUT_DIR: Path = Path(os.getenv("MOTEC_LDX_OUTPUT_DIR", "data/motec/ldx"))
    MOTEC_LD_SCAN_DIR: Path = Path(os.getenv("MOTEC_LD_SCAN_DIR", "data/motec/ld"))
    MOTEC_AUTO_GENERATE_LDX: bool = os.getenv("MOTEC_AUTO_GENERATE_LDX", "false").lower() == "true"
    MOTEC_OVERWRITE_POLICY: str = os.getenv("MOTEC_OVERWRITE_POLICY", "ifSafe")  # never, ifSafe, always
    MOTEC_CHANNEL_MAPPINGS_FILE: Path = Path(os.getenv("MOTEC_CHANNEL_MAPPINGS_FILE", "config/motec/channel_mappings.json"))
    MOTEC_CAR_PROFILES_FILE: Path = Path(os.getenv("MOTEC_CAR_PROFILES_FILE", "config/motec/car_profiles.json"))
    
    # NAS Discovery & Auto-Population
    MOTEC_NAS_DISCOVERY_ENABLED: bool = os.getenv("MOTEC_NAS_DISCOVERY_ENABLED", "true").lower() == "true"
    MOTEC_NAS_DISCOVERY_SCAN_ON_STARTUP: bool = os.getenv("MOTEC_NAS_DISCOVERY_SCAN_ON_STARTUP", "true").lower() == "true"
    MOTEC_NAS_DISCOVERY_SCAN_INTERVAL_MS: int = int(os.getenv("MOTEC_NAS_DISCOVERY_SCAN_INTERVAL_MS", "30000"))  # 30 seconds default
    MOTEC_AUTO_POPULATE_ENABLED: bool = os.getenv("MOTEC_AUTO_POPULATE_ENABLED", "true").lower() == "true"
    MOTEC_AUTO_POPULATE_MAX_FILES_PER_SCAN: int = int(os.getenv("MOTEC_AUTO_POPULATE_MAX_FILES_PER_SCAN", "1000"))
    MOTEC_AUTO_POPULATE_INFERENCE_MODE: str = os.getenv("MOTEC_AUTO_POPULATE_INFERENCE_MODE", "conservative")  # conservative or aggressive
    
    # Frontend paths - Check if we're in Vercel (project root is one level up from backend)
    if (BASE_DIR.parent / "api").exists():
        # Vercel structure: project_root/api/index.py, project_root/backend/
        TEMPLATES_DIR: Path = BASE_DIR.parent / "frontend" / "templates"
        STATIC_DIR: Path = BASE_DIR.parent / "frontend" / "static"
    else:
        # Local structure: backend/internal/config/
        TEMPLATES_DIR: Path = BASE_DIR.parent / "frontend" / "templates"
        STATIC_DIR: Path = BASE_DIR.parent / "frontend" / "static"
    
    @classmethod
    def get_aero_config(cls) -> dict:
        """Get aero configuration as a dictionary"""
        return {
            "reference_dynamic_port": cls.AERO_REF_DYNAMIC_PORT,
            "reference_static_port": cls.AERO_REF_STATIC_PORT,
            "num_ports": cls.AERO_NUM_PORTS,
            "straight_threshold": cls.AERO_STRAIGHT_THRESHOLD,
            "turn_threshold": cls.AERO_TURN_THRESHOLD,
            "lateral_g_threshold": cls.AERO_LATERAL_G_THRESHOLD,
            "averaging_window_size": cls.AERO_AVG_WINDOW_SIZE,
            "histogram_bins": cls.AERO_HISTOGRAM_BINS,
            "histogram_range": cls.AERO_HISTOGRAM_RANGE
        }
    
    @classmethod
    def get_motec_config(cls) -> dict:
        """Get MoTeC configuration as a dictionary"""
        return {
            "enabled": cls.MOTEC_ENABLED,
            "nas_base_path": cls.MOTEC_NAS_BASE_PATH,
            "ld_glob_pattern": cls.MOTEC_LD_GLOB_PATTERN,
            "ldx_template_dir": str(cls.MOTEC_LDX_TEMPLATE_DIR),
            "ldx_output_dir": str(cls.MOTEC_LDX_OUTPUT_DIR),
            "ld_scan_dir": str(cls.MOTEC_LD_SCAN_DIR),
            "auto_generate_ldx": cls.MOTEC_AUTO_GENERATE_LDX,
            "overwrite_policy": cls.MOTEC_OVERWRITE_POLICY,
            "channel_mappings_file": str(cls.MOTEC_CHANNEL_MAPPINGS_FILE),
            "car_profiles_file": str(cls.MOTEC_CAR_PROFILES_FILE),
            "nas_discovery": {
                "enabled": cls.MOTEC_NAS_DISCOVERY_ENABLED,
                "scan_on_startup": cls.MOTEC_NAS_DISCOVERY_SCAN_ON_STARTUP,
                "scan_interval_ms": cls.MOTEC_NAS_DISCOVERY_SCAN_INTERVAL_MS
            },
            "auto_populate": {
                "enabled": cls.MOTEC_AUTO_POPULATE_ENABLED,
                "max_files_per_scan": cls.MOTEC_AUTO_POPULATE_MAX_FILES_PER_SCAN,
                "inference_mode": cls.MOTEC_AUTO_POPULATE_INFERENCE_MODE
            }
        }
    
    @classmethod
    def load_schema_from_file(cls, schema_file: str = None):
        """Load telemetry schema from JSON file if provided"""
        if schema_file is None:
            schema_file = os.getenv("TEL_SCHEMA_FILE", "")
        
        if schema_file and Path(schema_file).exists():
            import json
            with open(schema_file, "r") as f:
                cls.TELEMETRY_SCHEMA = json.load(f)
    
    @classmethod
    def get_initial_telemetry_data(cls) -> dict:
        """Get initial telemetry data structure based on schema"""
        if cls.TELEMETRY_SCHEMA:
            # Use schema-defined defaults
            data = {}
            for field, config in cls.TELEMETRY_SCHEMA.items():
                data[field] = config.get("default", 0)
            return data
        
        # Default schema if none provided
        # Includes 8 pressure ports for aero team
        data = {
            "speed": 0.0,
            "rpm": 0,
            "throttle": 0.0,
            "brake": 0.0,
            "steering": 0.0,
            "oil_temp": 0.0,
            "water_temp": 0.0,
            "oil_pressure": 0.0,
            "fuel_level": 0.0,
            "lap_time": "0:00.000",
            "lap_number": 0,
            "sector_time": "0:00.000",
            "position": 0,
            "g_force_lat": 0.0,
            "g_force_long": 0.0,
        }
        
        # Add 8 pressure ports (ports 7 and 8 are reference)
        for i in range(1, 9):
            data[f"pressure_port_{i}"] = 0.0
        
        return data

# Load schema if configured
Settings.load_schema_from_file()

settings = Settings()

