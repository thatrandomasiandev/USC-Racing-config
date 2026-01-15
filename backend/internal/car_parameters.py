"""
Car Parameters Management - Define and manage car parameters like tire pressure
Similar to registered_users.py pattern - stores parameter definitions
"""
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).parent.parent.parent
CAR_PARAMETERS_FILE = BASE_DIR / "data" / "car_parameters.json"


def generate_link_key(subteam: str, tab: str, variable_name: str) -> str:
    """
    Generate composite link key: subteam_tab_variablename
    Normalizes input by lowercasing, replacing spaces/special chars with underscores,
    and collapsing multiple underscores.
    
    Args:
        subteam: Subteam name (e.g., "Suspension")
        tab: Tab/category name (e.g., "Damper" or empty string)
        variable_name: Variable name (e.g., "FL HS Rebound")
    
    Returns:
        Normalized link key (e.g., "suspension_damper_fl_hs_rebound")
    """
    def normalize(text: str) -> str:
        """Normalize a string for use in link key"""
        if not text:
            return ""
        # Lowercase and replace spaces/special chars with underscores
        normalized = text.lower()
        normalized = re.sub(r'[^a-z0-9]', '_', normalized)
        # Collapse multiple underscores
        normalized = re.sub(r'_+', '_', normalized)
        # Strip leading/trailing underscores
        return normalized.strip('_')
    
    parts = []
    parts.append(normalize(subteam))
    
    # Only add tab if it's not empty
    if tab and tab.strip():
        parts.append(normalize(tab))
    
    parts.append(normalize(variable_name))
    
    # Join parts with underscores and clean up
    link_key = '_'.join(filter(None, parts))
    return link_key


def ensure_car_parameters_file():
    """Ensure the car parameters file exists with defaults"""
    CAR_PARAMETERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not CAR_PARAMETERS_FILE.exists():
        # Create default file with tire pressure parameters
        default_params = {
            "description": "Car parameters to track - definitions and default values",
            "version": "1.0",
            "parameters": [
                {
                    "parameter_name": "tire_pressure_fl",
                    "display_name": "Front Left Tire Pressure",
                    "subteam": "Mechanical",
                    "unit": "psi",
                    "default_value": "20.0",
                    "min_value": "10.0",
                    "max_value": "40.0",
                    "motec_channel": None,
                    "description": "Front left tire pressure in PSI"
                },
                {
                    "parameter_name": "tire_pressure_fr",
                    "display_name": "Front Right Tire Pressure",
                    "subteam": "Mechanical",
                    "unit": "psi",
                    "default_value": "20.0",
                    "min_value": "10.0",
                    "max_value": "40.0",
                    "motec_channel": None,
                    "description": "Front right tire pressure in PSI"
                },
                {
                    "parameter_name": "tire_pressure_rl",
                    "display_name": "Rear Left Tire Pressure",
                    "subteam": "Mechanical",
                    "unit": "psi",
                    "default_value": "20.0",
                    "min_value": "10.0",
                    "max_value": "40.0",
                    "motec_channel": None,
                    "description": "Rear left tire pressure in PSI"
                },
                {
                    "parameter_name": "tire_pressure_rr",
                    "display_name": "Rear Right Tire Pressure",
                    "subteam": "Mechanical",
                    "unit": "psi",
                    "default_value": "20.0",
                    "min_value": "10.0",
                    "max_value": "40.0",
                    "motec_channel": None,
                    "description": "Rear right tire pressure in PSI"
                }
            ]
        }
        with open(CAR_PARAMETERS_FILE, 'w') as f:
            json.dump(default_params, f, indent=2, default=str)


def load_car_parameters() -> Dict[str, Any]:
    """Load car parameters definitions from JSON file"""
    ensure_car_parameters_file()
    try:
        with open(CAR_PARAMETERS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"parameters": []}


def save_car_parameters(data: Dict[str, Any]):
    """Save car parameters definitions to JSON file"""
    ensure_car_parameters_file()
    with open(CAR_PARAMETERS_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def get_all_car_parameter_definitions() -> List[Dict[str, Any]]:
    """Get all car parameter definitions"""
    data = load_car_parameters()
    return data.get("parameters", [])


def get_car_parameter_definition(parameter_name: str) -> Optional[Dict[str, Any]]:
    """Get definition for a specific car parameter by parameter_name"""
    params = get_all_car_parameter_definitions()
    return next((p for p in params if p.get("parameter_name") == parameter_name), None)


def get_car_parameter_definition_by_link_key(link_key: str) -> Optional[Dict[str, Any]]:
    """Get definition for a specific car parameter by link_key"""
    params = get_all_car_parameter_definitions()
    return next((p for p in params if p.get("link_key") == link_key), None)


def add_car_parameter_definition(
    parameter_name: str,
    display_name: str,
    subteam: str,
    unit: str,
    default_value: str,
    min_value: Optional[str] = None,
    max_value: Optional[str] = None,
    motec_channel: Optional[str] = None,
    description: Optional[str] = None,
    link_key: Optional[str] = None,
    tab: Optional[str] = None,
    inject_type: Optional[str] = None,
    variable_name: Optional[str] = None,
    param_type: Optional[str] = None
) -> bool:
    """
    Add or update a car parameter definition.
    
    Args:
        parameter_name: Snake case parameter name (for backward compatibility)
        display_name: Human-readable display name
        subteam: Subteam name
        unit: Unit of measurement
        default_value: Default value
        min_value: Minimum allowed value (optional)
        max_value: Maximum allowed value (optional)
        motec_channel: MoTeC channel name (optional)
        description: Description text (optional)
        link_key: Link key identifier (optional, will be generated if not provided and tab/variable_name are provided)
        tab: Tab/category name (optional)
        inject_type: Inject type - "Constant" or "Comment" (optional)
        variable_name: Variable name (optional, used for link key generation)
        param_type: Parameter type - "int", "float", "string", "dropdown" (optional)
    """
    data = load_car_parameters()
    params = data.get("parameters", [])
    
    # Generate link_key if not provided but we have the necessary fields
    if not link_key and subteam and variable_name:
        link_key = generate_link_key(subteam, tab or "", variable_name)
    
    # Check if already exists by parameter_name or link_key
    existing_index = None
    for i, p in enumerate(params):
        if p.get("parameter_name") == parameter_name:
            existing_index = i
            break
        # Also check by link_key if provided
        if link_key and p.get("link_key") == link_key:
            existing_index = i
            break
    
    param_def = {
        "parameter_name": parameter_name,
        "display_name": display_name,
        "subteam": subteam,
        "unit": unit,
        "default_value": default_value,
        "min_value": min_value or "",
        "max_value": max_value or "",
        "motec_channel": motec_channel,
        "description": description or ""
    }
    
    # Add new fields if provided
    if link_key:
        param_def["link_key"] = link_key
    if tab is not None:
        param_def["tab"] = tab or ""
    if inject_type:
        param_def["inject_type"] = inject_type
    if variable_name:
        param_def["variable_name"] = variable_name
    if param_type:
        param_def["type"] = param_type
    
    if existing_index is not None:
        # Update existing - merge new fields with existing ones
        existing_param = params[existing_index]
        existing_param.update(param_def)
        params[existing_index] = existing_param
    else:
        params.append(param_def)
    
    data["parameters"] = params
    save_car_parameters(data)
    return True


def remove_car_parameter_definition(parameter_name: str) -> bool:
    """Remove a car parameter definition"""
    data = load_car_parameters()
    params = data.get("parameters", [])
    original_count = len(params)
    params = [p for p in params if p.get("parameter_name") != parameter_name]
    
    if len(params) < original_count:
        data["parameters"] = params
        save_car_parameters(data)
        return True
    
    return False


async def initialize_car_parameters_in_db():
    """
    Initialize car parameters in the database with default values
    This creates parameters from the definitions file if they don't exist
    """
    from .database import get_parameter, update_parameter
    
    params = get_all_car_parameter_definitions()
    initialized = []
    
    for param_def in params:
        param_name = param_def["parameter_name"]
        existing = await get_parameter(param_name)
        
        if not existing:
            # Create parameter with default value
            await update_parameter(
                parameter_name=param_name,
                subteam=param_def["subteam"],
                new_value=param_def["default_value"],
                updated_by="system",
                comment=f"Initialized from car_parameters.json"
            )
            initialized.append(param_name)
    
    return initialized


def get_parameters_by_subteam(subteam: str) -> List[Dict[str, Any]]:
    """Get all car parameter definitions for a specific subteam"""
    params = get_all_car_parameter_definitions()
    return [p for p in params if p.get("subteam") == subteam]

