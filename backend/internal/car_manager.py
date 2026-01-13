"""
Car Manager - Handles car identification and management
Extracts car identifiers from MoTeC files and manages car registry
"""
import re
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import aiosqlite
from .database import get_db
from .config.settings import settings


async def get_or_create_car(car_identifier: str, display_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get existing car or create new one
    
    Args:
        car_identifier: Unique identifier for the car (e.g., "Car1", "FSAE-2024-01")
        display_name: Optional display name (e.g., "Primary Race Car")
    
    Returns:
        Car dictionary with id, car_identifier, display_name, etc.
    """
    db = await get_db()
    try:
        db.row_factory = aiosqlite.Row
        
        # Check if car exists
        cursor = await db.execute(
            "SELECT * FROM cars WHERE car_identifier = ?",
            (car_identifier,)
        )
        row = await cursor.fetchone()
        
        if row:
            # Update last_seen_at
            now = datetime.now().isoformat()
            await db.execute(
                "UPDATE cars SET last_seen_at = ? WHERE car_identifier = ?",
                (now, car_identifier)
            )
            await db.commit()
            return dict(row)
        else:
            # Create new car
            now = datetime.now().isoformat()
            cursor = await db.execute(
                """
                INSERT INTO cars (car_identifier, display_name, created_at, last_seen_at)
                VALUES (?, ?, ?, ?)
                """,
                (car_identifier, display_name or car_identifier, now, now)
            )
            await db.commit()
            
            # Get the newly created car
            cursor = await db.execute(
                "SELECT * FROM cars WHERE car_identifier = ?",
                (car_identifier,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    finally:
        await db.close()


async def get_all_cars() -> List[Dict[str, Any]]:
    """Get all registered cars"""
    db = await get_db()
    try:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM cars ORDER BY last_seen_at DESC, car_identifier ASC"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


async def get_car_by_identifier(car_identifier: str) -> Optional[Dict[str, Any]]:
    """Get car by identifier"""
    db = await get_db()
    try:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM cars WHERE car_identifier = ?",
            (car_identifier,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await db.close()


def extract_car_identifier_from_motec_file(
    file_path: Path,
    parsed_data: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Extract car identifier from MoTeC file
    
    Tries multiple methods:
    1. Parse Details section for car-related fields
    2. Check filename patterns
    3. Look for car identifiers in metadata
    
    Args:
        file_path: Path to MoTeC file
        parsed_data: Optional pre-parsed file data
    
    Returns:
        Car identifier string or None if not found
    """
    # Method 1: Check Details section (LDX files)
    if parsed_data and parsed_data.get("file_type") == "ldx":
        details = parsed_data.get("details", {})
        
        # Common car identifier fields in MoTeC Details (from config)
        car_fields = settings.CAR_ID_DETAILS_FIELDS
        
        for field in car_fields:
            if field in details:
                value = details[field]
                if value and value.strip():
                    return value.strip()
        
        # Also check for variations
        for key, value in details.items():
            key_lower = key.lower()
            if any(term in key_lower for term in ["car", "vehicle", "chassis"]) and value:
                return str(value).strip()
    
    # Method 2: Check filename patterns
    filename = file_path.stem  # Without extension
    filename_lower = filename.lower()
    
    # Pattern: Car1_Session.ldx, Car-2_Session.ldx, etc. (from config)
    car_patterns = settings.CAR_ID_PATTERNS
    
    for pattern in car_patterns:
        match = re.search(pattern, filename_lower, re.IGNORECASE)
        if match:
            car_num = match.group(1) if match.lastindex else match.group(0)
            return f"Car{car_num}"
    
    # Pattern: FSAE-2024-01, USC-2024-Car1, etc.
    team_pattern = r'([A-Z]+)[_\s-]?(\d{4})[_\s-]?(car|vehicle|chassis)?[_\s-]?(\d+)?'
    match = re.search(team_pattern, filename, re.IGNORECASE)
    if match:
        team = match.group(1)
        year = match.group(2)
        car_num = match.group(4) or "01"
        return f"{team}-{year}-Car{car_num}"
    
    # Method 3: Check parsed metadata (LD files)
    if parsed_data and parsed_data.get("file_type") == "ld":
        # Check device name or other metadata
        device_name = parsed_data.get("device_name", "")
        if device_name:
            # Sometimes device name contains car info
            car_match = re.search(r'car[_\s-]?(\d+)', device_name.lower())
            if car_match:
                return f"Car{car_match.group(1)}"
    
    # Method 4: Check if filename contains any car-like identifier
    # Look for patterns like "C1", "C2", etc.
    simple_pattern = r'\b[Cc](\d+)\b'
    match = re.search(simple_pattern, filename)
    if match:
        return f"Car{match.group(1)}"
    
    return None


async def identify_car_from_file(
    file_path: Path,
    parsed_data: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Identify car from MoTeC file and register it if new
    
    Args:
        file_path: Path to MoTeC file
        parsed_data: Optional pre-parsed file data
    
    Returns:
        Car dictionary or None if car cannot be identified
    """
    car_identifier = extract_car_identifier_from_motec_file(file_path, parsed_data)
    
    if car_identifier:
        # Get or create car
        car = await get_or_create_car(car_identifier)
        return car
    
    return None
