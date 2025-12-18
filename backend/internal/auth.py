"""
Session-based authentication with database user management
Lightweight for Raspberry Pi
"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware.sessions import SessionMiddleware
import secrets
import hashlib
from typing import Optional
import aiosqlite
from pathlib import Path

# Database path
BASE_DIR = Path(__file__).parent.parent.parent
DB_PATH = BASE_DIR / "data" / "parameters.db"

security = HTTPBasic()


async def get_db():
    """Get database connection"""
    return await aiosqlite.connect(str(DB_PATH))


def get_current_user(request: Request) -> Optional[str]:
    """Get current user from session"""
    return request.session.get("username")


async def get_current_user_role(request: Request) -> Optional[str]:
    """Get current user role from database"""
    username = get_current_user(request)
    if not username:
        return None
    
    db = await get_db()
    try:
        cursor = await db.execute("SELECT role FROM users WHERE username = ?", (username,))
        row = await cursor.fetchone()
        return row[0] if row else None
    finally:
        await db.close()


async def get_current_user_subteam(request: Request) -> Optional[str]:
    """Get current user subteam from database"""
    username = get_current_user(request)
    if not username:
        return None
    
    db = await get_db()
    try:
        cursor = await db.execute("SELECT subteam FROM users WHERE username = ?", (username,))
        row = await cursor.fetchone()
        return row[0] if row else None
    finally:
        await db.close()


def require_auth(request: Request) -> str:
    """Require authentication, raise 401 if not authenticated"""
    username = get_current_user(request)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return username


async def require_role(request: Request, required_role: str) -> str:
    """Require authentication and specific role"""
    username = require_auth(request)
    role = await get_current_user_role(request)
    
    if role != required_role and role != "admin":  # Admin can do everything
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Requires {required_role} role"
        )
    return username


async def verify_login(username: str, password: str) -> bool:
    """Verify login credentials against database
    
    Rules:
    - User must exist in database (no fallback users)
    - User must NOT be in recently_deleted_users.json
    - Password must match
    """
    from internal.deleted_users import is_user_deleted
    from internal.database import verify_user_password
    
    # Check if user is in recently deleted list
    if is_user_deleted(username):
        return False
    
    # Verify password against database
    return await verify_user_password(username, password)


def init_auth_middleware(app):
    """Initialize session middleware"""
    app.add_middleware(
        SessionMiddleware,
        secret_key=secrets.token_urlsafe(32),
        max_age=86400  # 24 hours
    )

