"""
Manage recently deleted users in JSON file
Users in this file are denied login access
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).parent.parent.parent
DELETED_USERS_FILE = BASE_DIR / "data" / "recently_deleted_users.json"


def ensure_deleted_users_file():
    """Ensure the deleted users file exists"""
    DELETED_USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DELETED_USERS_FILE.exists():
        with open(DELETED_USERS_FILE, 'w') as f:
            json.dump([], f)


def load_deleted_users() -> List[Dict[str, Any]]:
    """Load recently deleted users from JSON file"""
    ensure_deleted_users_file()
    try:
        with open(DELETED_USERS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_deleted_users(users: List[Dict[str, Any]]):
    """Save recently deleted users to JSON file"""
    ensure_deleted_users_file()
    with open(DELETED_USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2, default=str)


def add_deleted_user(username: str, role: str, deleted_by: str, subteam: Optional[str] = None) -> bool:
    """Add a user to the recently deleted users list"""
    deleted_users = load_deleted_users()
    
    # Check if already in list
    if any(u.get("username") == username for u in deleted_users):
        return False
    
    deleted_user = {
        "username": username,
        "role": role,
        "deleted_at": datetime.now().isoformat(),
        "deleted_by": deleted_by
    }
    
    # Add subteam if provided
    if subteam:
        deleted_user["subteam"] = subteam
    
    deleted_users.append(deleted_user)
    save_deleted_users(deleted_users)
    return True


def remove_deleted_user(username: str) -> bool:
    """Permanently remove a user from recently deleted users list"""
    deleted_users = load_deleted_users()
    original_count = len(deleted_users)
    
    deleted_users = [u for u in deleted_users if u.get("username") != username]
    
    if len(deleted_users) < original_count:
        save_deleted_users(deleted_users)
        return True
    return False


def is_user_deleted(username: str) -> bool:
    """Check if a user is in the recently deleted users list"""
    deleted_users = load_deleted_users()
    return any(u.get("username") == username for u in deleted_users)


def get_all_deleted_users() -> List[Dict[str, Any]]:
    """Get all recently deleted users"""
    return load_deleted_users()

