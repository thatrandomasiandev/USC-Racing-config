"""
Manage parameter defaults in JSON file
Similar to registered_users.json - stores default parameter values and metadata
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).parent.parent.parent
PARAMETER_DEFAULTS_FILE = BASE_DIR / "data" / "parameter_defaults.json"


def ensure_parameter_defaults_file():
    """Ensure the parameter defaults file exists"""
    PARAMETER_DEFAULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not PARAMETER_DEFAULTS_FILE.exists():
        with open(PARAMETER_DEFAULTS_FILE, 'w') as f:
            json.dump([], f)


def load_parameter_defaults() -> List[Dict[str, Any]]:
    """Load all parameter defaults from JSON file"""
    ensure_parameter_defaults_file()
    try:
        with open(PARAMETER_DEFAULTS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_parameter_defaults(defaults: List[Dict[str, Any]]):
    """Save parameter defaults to JSON file"""
    ensure_parameter_defaults_file()
    with open(PARAMETER_DEFAULTS_FILE, 'w') as f:
        json.dump(defaults, f, indent=2, default=str)


def get_parameter_default(parameter_name: str) -> Optional[Dict[str, Any]]:
    """Get default value for a specific parameter"""
    defaults = load_parameter_defaults()
    return next((d for d in defaults if d.get("parameter_name") == parameter_name), None)


def add_parameter_default(
    parameter_name: str,
    subteam: str,
    default_value: str,
    source: str = "manual",  # "manual", "ldx_import", "ld_import"
    source_file: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """Add or update a parameter default in JSON file"""
    defaults = load_parameter_defaults()
    
    # Check if already exists
    existing_index = None
    for i, d in enumerate(defaults):
        if d.get("parameter_name") == parameter_name:
            existing_index = i
            break
    
    default_data = {
        "parameter_name": parameter_name,
        "subteam": subteam,
        "default_value": default_value,
        "source": source,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    if source_file:
        default_data["source_file"] = source_file
    
    if metadata:
        default_data["metadata"] = metadata
    
    if existing_index is not None:
        # Update existing - preserve created_at
        existing = defaults[existing_index]
        default_data["created_at"] = existing.get("created_at", default_data["created_at"])
        defaults[existing_index] = default_data
    else:
        defaults.append(default_data)
    
    save_parameter_defaults(defaults)
    return True


def update_parameter_default(
    parameter_name: str,
    default_value: Optional[str] = None,
    subteam: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """Update an existing parameter default"""
    defaults = load_parameter_defaults()
    
    for default in defaults:
        if default.get("parameter_name") == parameter_name:
            if default_value is not None:
                default["default_value"] = default_value
            if subteam is not None:
                default["subteam"] = subteam
            if metadata is not None:
                default["metadata"] = metadata
            default["updated_at"] = datetime.now().isoformat()
            
            save_parameter_defaults(defaults)
            return True
    
    return False


def remove_parameter_default(parameter_name: str) -> bool:
    """Remove a parameter default"""
    defaults = load_parameter_defaults()
    original_count = len(defaults)
    defaults = [d for d in defaults if d.get("parameter_name") != parameter_name]
    
    if len(defaults) < original_count:
        save_parameter_defaults(defaults)
        return True
    
    return False


def get_all_parameter_defaults() -> List[Dict[str, Any]]:
    """Get all parameter defaults"""
    return load_parameter_defaults()


def get_defaults_by_subteam(subteam: str) -> List[Dict[str, Any]]:
    """Get all parameter defaults for a specific subteam"""
    defaults = load_parameter_defaults()
    return [d for d in defaults if d.get("subteam") == subteam]


def get_defaults_by_source(source: str) -> List[Dict[str, Any]]:
    """Get all parameter defaults from a specific source"""
    defaults = load_parameter_defaults()
    return [d for d in defaults if d.get("source") == source]

