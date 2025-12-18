"""
Car Parameters Management - Define and manage car parameters like tire pressure
Similar to registered_users.py pattern - stores parameter definitions
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).parent.parent.parent
CAR_PARAMETERS_FILE = BASE_DIR / "data" / "car_parameters.json"


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
    """Get definition for a specific car parameter"""
    params = get_all_car_parameter_definitions()
    return next((p for p in params if p.get("parameter_name") == parameter_name), None)


def add_car_parameter_definition(
    parameter_name: str,
    display_name: str,
    subteam: str,
    unit: str,
    default_value: str,
    min_value: Optional[str] = None,
    max_value: Optional[str] = None,
    motec_channel: Optional[str] = None,
    description: Optional[str] = None
) -> bool:
    """Add or update a car parameter definition"""
    data = load_car_parameters()
    params = data.get("parameters", [])
    
    # Check if already exists
    existing_index = None
    for i, p in enumerate(params):
        if p.get("parameter_name") == parameter_name:
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
    
    if existing_index is not None:
        params[existing_index] = param_def
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

