"""
Manage registered users in JSON file
This file tracks ALL users (active and deleted) for easy reference
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import aiosqlite

BASE_DIR = Path(__file__).parent.parent.parent
REGISTERED_USERS_FILE = BASE_DIR / "data" / "registered_users.json"
DB_PATH = BASE_DIR / "data" / "parameters.db"


def ensure_registered_users_file():
    """Ensure the registered users file exists"""
    REGISTERED_USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not REGISTERED_USERS_FILE.exists():
        with open(REGISTERED_USERS_FILE, 'w') as f:
            json.dump([], f)


def load_registered_users() -> List[Dict[str, Any]]:
    """Load all registered users from JSON file"""
    ensure_registered_users_file()
    try:
        with open(REGISTERED_USERS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_registered_users(users: List[Dict[str, Any]]):
    """Save registered users to JSON file"""
    ensure_registered_users_file()
    with open(REGISTERED_USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2, default=str)


async def sync_registered_users_from_db():
    """Sync registered users JSON from database (only active users)"""
    ensure_registered_users_file()
    
    # Get all users from database (these are active users)
    db = await aiosqlite.connect(str(DB_PATH))
    try:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT id, username, role, created_at FROM users ORDER BY username ASC")
        db_users = await cursor.fetchall()
        
        # Only keep active users (those in database)
        registered_users = []
        
        # Add all users from database (they are all active)
        for row in db_users:
            user_data = dict(row)
            username = user_data["username"]
            
            # Load existing to get password if it exists
            existing = load_registered_users()
            existing_user = next((u for u in existing if u.get("username") == username), None)
            
            user_entry = {
                "username": username,
                "role": user_data["role"],
                "created_at": user_data["created_at"],
                "status": "active"
            }
            
            # Preserve password if it exists
            if existing_user and "password" in existing_user:
                user_entry["password"] = existing_user["password"]
            
            # Add subteam if it exists
            if user_data.get("subteam"):
                user_entry["subteam"] = user_data["subteam"]
            
            registered_users.append(user_entry)
        
        save_registered_users(registered_users)
    finally:
        await db.close()


def add_registered_user(username: str, role: str, created_at: Optional[str] = None, password: Optional[str] = None, subteam: Optional[str] = None):
    """Add a user to the registered users JSON"""
    registered_users = load_registered_users()
    
    # Check if already exists
    if any(u.get("username") == username for u in registered_users):
        return False
    
    user_data = {
        "username": username,
        "role": role,
        "created_at": created_at or datetime.now().isoformat(),
        "status": "active"
    }
    
    # Store password in plaintext for visibility (if provided)
    if password:
        user_data["password"] = password
    
    # Store subteam if provided
    if subteam:
        user_data["subteam"] = subteam
    
    registered_users.append(user_data)
    save_registered_users(registered_users)
    return True


def update_user_password(username: str, password: str) -> bool:
    """Update a user's password in registered users JSON (plaintext for visibility)"""
    registered_users = load_registered_users()
    
    for user in registered_users:
        if user.get("username") == username:
            user["password"] = password
            save_registered_users(registered_users)
            return True
    
    return False


def remove_user_from_registered(username: str):
    """Remove a user from registered_users.json (they go to recently_deleted_users.json)"""
    registered_users = load_registered_users()
    
    # Remove user from registered users (only active users stay here)
    original_count = len(registered_users)
    registered_users = [u for u in registered_users if u.get("username") != username]
    
    if len(registered_users) < original_count:
        save_registered_users(registered_users)
        return True
    
    return False


def update_user_role(username: str, role: str) -> bool:
    """Update a user's role in registered users JSON
    
    This is called automatically when roles are changed in the admin console.
    Changes are reversible - you can change admin → user → admin and the JSON updates each time.
    """
    registered_users = load_registered_users()
    
    for user in registered_users:
        if user.get("username") == username:
            user["role"] = role
            save_registered_users(registered_users)
            return True
    
    return False


def get_all_registered_users() -> List[Dict[str, Any]]:
    """Get all registered users (active and deleted)"""
    return load_registered_users()

