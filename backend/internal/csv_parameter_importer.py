"""
CSV Parameter Importer - Import car parameter definitions from CSV
Parses CSV with columns: Subteam, Tab, Variable Name, Type, Inject, Unit
"""
import csv
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from io import StringIO

from .car_parameters import (
    generate_link_key, 
    add_car_parameter_definition,
    get_car_parameter_definition_by_link_key
)


def normalize_type(type_str: str) -> str:
    """
    Normalize type string to standard format.
    
    Args:
        type_str: Type string from CSV (e.g., "Int", "Float", "Foat?", "String", "drop down")
    
    Returns:
        Normalized type: "int", "float", "string", or "dropdown"
    """
    if not type_str:
        return "string"
    
    type_lower = type_str.lower().strip()
    
    # Handle integer types
    if type_lower in ["int", "integer"]:
        return "int"
    
    # Handle float types (including typos like "Foat?")
    if type_lower in ["float", "foat", "foat?"]:
        return "float"
    
    # Handle string types
    if type_lower in ["string", "str"]:
        return "string"
    
    # Handle dropdown
    if "drop" in type_lower and "down" in type_lower:
        return "dropdown"
    
    # Default to string if unrecognized
    return "string"


def extract_min_max_from_unit(unit_str: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract min/max values from unit/description string.
    
    Looks for patterns like:
    - "expected value of -5 to 5"
    - "-15 to 15"
    - "-5 to 5 maybe"
    
    Args:
        unit_str: Unit/description string from CSV
    
    Returns:
        Tuple of (min_value, max_value) or (None, None) if not found
    """
    if not unit_str:
        return None, None
    
    # Look for range pattern: "-X to Y" or "X to Y"
    range_match = re.search(r'(-?\d+(?:\.\d+)?)\s+to\s+(-?\d+(?:\.\d+)?)', unit_str, re.IGNORECASE)
    if range_match:
        min_val = range_match.group(1)
        max_val = range_match.group(2)
        return min_val, max_val
    
    return None, None


def normalize_parameter_name(variable_name: str, tab: str = "") -> str:
    """
    Generate snake_case parameter_name for backward compatibility.
    
    Args:
        variable_name: Variable name from CSV
        tab: Tab name (optional, may be included as prefix)
    
    Returns:
        Snake case parameter name
    """
    # Clean variable name
    param_name_base = variable_name.lower().replace(' ', '_').replace('/', '_')
    param_name_base = re.sub(r'[^a-z0-9_]', '_', param_name_base)
    param_name_base = re.sub(r'_+', '_', param_name_base).strip('_')
    
    # Add tab prefix if provided
    if tab and tab.strip():
        tab_prefix = tab.lower().replace(' ', '_')
        tab_prefix = re.sub(r'[^a-z0-9_]', '_', tab_prefix)
        tab_prefix = re.sub(r'_+', '_', tab_prefix).strip('_')
        param_name = f"{tab_prefix}_{param_name_base}"
    else:
        param_name = param_name_base
    
    return param_name


def parse_csv_row(row: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """
    Parse a single CSV row into a parameter definition dictionary.
    
    Args:
        row: Dictionary with CSV column names as keys
    
    Returns:
        Parameter definition dictionary or None if row is invalid
    """
    # Extract columns (case-insensitive matching)
    subteam = row.get("Subteam", "").strip()
    tab = row.get("Tab", "").strip()
    variable_name = row.get("Variable Name", "").strip()
    type_str = row.get("Type", "").strip()
    inject = row.get("Inject", "").strip()
    unit = row.get("Unit", "").strip()
    
    # Skip empty rows or rows without required fields
    if not subteam or not variable_name:
        return None
    
    # Normalize values
    param_type = normalize_type(type_str)
    inject_type = inject if inject in ["Constant", "Comment"] or inject.startswith("Comment") else None
    
    # Generate link key
    link_key = generate_link_key(subteam, tab, variable_name)
    
    # Generate parameter_name for backward compatibility
    parameter_name = normalize_parameter_name(variable_name, tab)
    
    # Extract min/max from unit column
    min_value, max_value = extract_min_max_from_unit(unit)
    
    # Clean up unit string (remove range info)
    clean_unit = unit
    if "expected value of" in clean_unit.lower():
        clean_unit = re.sub(r'expected value of\s+-?\d+(?:\.\d+)?\s+to\s+-?\d+(?:\.\d+)?', '', clean_unit, flags=re.IGNORECASE)
        clean_unit = re.sub(r'-?\d+(?:\.\d+)?\s+to\s+-?\d+(?:\.\d+)?', '', clean_unit)
        clean_unit = clean_unit.strip()
    
    # Remove common words that aren't units
    unit_words_to_remove = ["maybe", "constant", "description"]
    for word in unit_words_to_remove:
        clean_unit = re.sub(rf'\b{word}\b', '', clean_unit, flags=re.IGNORECASE)
    
    clean_unit = re.sub(r'\s+', ' ', clean_unit).strip()
    
    # Create display name (clean variable name)
    display_name = variable_name.replace('?', '').strip()
    
    # Determine default value based on type
    if param_type == "int":
        default_value = "0"
    elif param_type == "float":
        default_value = "0.0"
    else:
        default_value = ""
    
    # Build parameter definition
    param_def = {
        "subteam": subteam,
        "tab": tab,
        "variable_name": variable_name,
        "parameter_name": parameter_name,
        "display_name": display_name,
        "type": param_type,
        "inject_type": inject_type or "Constant",
        "unit": clean_unit,
        "default_value": default_value,
        "min_value": min_value or "",
        "max_value": max_value or "",
        "link_key": link_key
    }
    
    # Add description if unit column has extra info
    description_parts = []
    if unit and "FOR TEMPTAB" in unit:
        description_parts.append("FOR TEMPTAB DO NOT LOAD PREVIOUS VALUES")
    if unit and "DEFAULT LINK KEY" in unit:
        description_parts.append("DEFAULT LINK KEY TO PREV RUN")
    if unit and "need to be able" in unit.lower():
        description_parts.append(unit)
    
    if description_parts:
        param_def["description"] = " ".join(description_parts)
    
    return param_def


def import_csv_file(csv_file_path: Path, overwrite_existing: bool = False) -> Dict[str, Any]:
    """
    Import parameter definitions from CSV file.
    
    Args:
        csv_file_path: Path to CSV file
        overwrite_existing: Whether to overwrite existing definitions with same link_key
    
    Returns:
        Dictionary with import results:
        - created: Number of new definitions created
        - updated: Number of existing definitions updated
        - skipped: Number of rows skipped (duplicates or invalid)
        - errors: List of error messages
        - total_rows: Total rows processed
    """
    results = {
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "errors": [],
        "total_rows": 0
    }
    
    if not csv_file_path.exists():
        results["errors"].append(f"CSV file not found: {csv_file_path}")
        return results
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            # Read CSV content
            content = f.read()
            
            # Try to detect delimiter
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(content).delimiter
            
            # Reset file pointer
            f.seek(0)
            
            # Parse CSV
            reader = csv.DictReader(f, delimiter=delimiter)
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 because row 1 is header
                results["total_rows"] += 1
                
                try:
                    # Skip empty rows
                    if not any(row.values()):
                        continue
                    
                    # Parse row
                    param_def = parse_csv_row(row)
                    
                    if not param_def:
                        results["skipped"] += 1
                        continue
                    
                    # Check if already exists
                    existing = get_car_parameter_definition_by_link_key(param_def["link_key"])
                    
                    if existing and not overwrite_existing:
                        results["skipped"] += 1
                        continue
                    
                    # Add or update definition
                    success = add_car_parameter_definition(
                        parameter_name=param_def["parameter_name"],
                        display_name=param_def["display_name"],
                        subteam=param_def["subteam"],
                        unit=param_def["unit"],
                        default_value=param_def["default_value"],
                        min_value=param_def["min_value"] or None,
                        max_value=param_def["max_value"] or None,
                        description=param_def.get("description"),
                        link_key=param_def["link_key"],
                        tab=param_def["tab"],
                        inject_type=param_def["inject_type"],
                        variable_name=param_def["variable_name"],
                        param_type=param_def["type"]
                    )
                    
                    if success:
                        if existing:
                            results["updated"] += 1
                        else:
                            results["created"] += 1
                    else:
                        results["errors"].append(f"Row {row_num}: Failed to save parameter {param_def['link_key']}")
                
                except Exception as e:
                    results["errors"].append(f"Row {row_num}: Error processing row - {str(e)}")
                    results["skipped"] += 1
    
    except Exception as e:
        results["errors"].append(f"Error reading CSV file: {str(e)}")
    
    return results


def import_csv_content(csv_content: str, overwrite_existing: bool = False) -> Dict[str, Any]:
    """
    Import parameter definitions from CSV content string.
    
    Args:
        csv_content: CSV file content as string
        overwrite_existing: Whether to overwrite existing definitions with same link_key
    
    Returns:
        Dictionary with import results (same format as import_csv_file)
    """
    # Write content to temporary file-like object
    from io import StringIO
    
    results = {
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "errors": [],
        "total_rows": 0
    }
    
    try:
        # Try to detect delimiter
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(csv_content).delimiter
        
        # Parse CSV from string
        reader = csv.DictReader(StringIO(csv_content), delimiter=delimiter)
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 because row 1 is header
            results["total_rows"] += 1
            
            try:
                # Skip empty rows
                if not any(row.values()):
                    continue
                
                # Parse row
                param_def = parse_csv_row(row)
                
                if not param_def:
                    results["skipped"] += 1
                    continue
                
                # Check if already exists
                existing = get_car_parameter_definition_by_link_key(param_def["link_key"])
                
                if existing and not overwrite_existing:
                    results["skipped"] += 1
                    continue
                
                # Add or update definition
                success = add_car_parameter_definition(
                    parameter_name=param_def["parameter_name"],
                    display_name=param_def["display_name"],
                    subteam=param_def["subteam"],
                    unit=param_def["unit"],
                    default_value=param_def["default_value"],
                    min_value=param_def["min_value"] or None,
                    max_value=param_def["max_value"] or None,
                    description=param_def.get("description"),
                    link_key=param_def["link_key"],
                    tab=param_def["tab"],
                    inject_type=param_def["inject_type"],
                    variable_name=param_def["variable_name"],
                    param_type=param_def["type"]
                )
                
                if success:
                    if existing:
                        results["updated"] += 1
                    else:
                        results["created"] += 1
                else:
                    results["errors"].append(f"Row {row_num}: Failed to save parameter {param_def['link_key']}")
            
            except Exception as e:
                results["errors"].append(f"Row {row_num}: Error processing row - {str(e)}")
                results["skipped"] += 1
    
    except Exception as e:
        results["errors"].append(f"Error parsing CSV content: {str(e)}")
    
    return results
