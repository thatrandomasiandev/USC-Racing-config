"""
SQLite database setup and queries for parameter management system
Optimized for Raspberry Pi performance
"""
import aiosqlite
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
import os
from .config.settings import settings

# Database file path
# From backend/internal/database.py -> backend/internal -> backend -> project root
BASE_DIR = Path(__file__).parent.parent.parent
DB_PATH = BASE_DIR / "data" / "parameters.db"

# Ensure data directory exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


async def get_db():
    """Get database connection"""
    return await aiosqlite.connect(str(DB_PATH))


async def reset_database(keep_users: bool = True):
    """
    Reset database - clear all parameters, history, and queue
    Optionally keep users (default: True)
    
    Args:
        keep_users: If True, keep user accounts. If False, delete all users.
    
    Returns:
        Dict with counts of deleted records
    """
    db = await get_db()
    try:
        await db.execute("PRAGMA foreign_keys = ON")
        
        # Get counts before deletion
        cursor = await db.execute("SELECT COUNT(*) FROM parameters")
        param_count = (await cursor.fetchone())[0]
        
        cursor = await db.execute("SELECT COUNT(*) FROM parameter_history")
        history_count = (await cursor.fetchone())[0]
        
        cursor = await db.execute("SELECT COUNT(*) FROM parameter_queue")
        queue_count = (await cursor.fetchone())[0]
        
        # Delete all data
        await db.execute("DELETE FROM parameter_history")
        await db.execute("DELETE FROM parameter_queue")
        await db.execute("DELETE FROM parameters")
        
        if not keep_users:
            cursor = await db.execute("SELECT COUNT(*) FROM users")
            user_count = (await cursor.fetchone())[0]
            await db.execute("DELETE FROM users")
            # Recreate default admin if we deleted users
            import hashlib
            password_hash = hashlib.sha256("admin".encode()).hexdigest()
            await db.execute("""
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            """, ("admin", password_hash, "admin"))
        else:
            user_count = None
        
        await db.commit()
        
        return {
            "parameters_deleted": param_count,
            "history_deleted": history_count,
            "queue_deleted": queue_count,
            "users_deleted": user_count if not keep_users else "kept"
        }
    finally:
        await db.close()


async def init_db():
    """Initialize database tables"""
    db = await get_db()
    try:
        # Enable foreign keys
        await db.execute("PRAGMA foreign_keys = ON")
        
        # Create parameters table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS parameters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parameter_name TEXT NOT NULL UNIQUE,
                subteam TEXT NOT NULL,
                current_value TEXT NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                updated_by TEXT NOT NULL
            )
        """)
        
        # Create parameter_history table (audit trail)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS parameter_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parameter_id INTEGER NOT NULL,
                parameter_name TEXT NOT NULL,
                subteam TEXT NOT NULL,
                prior_value TEXT,
                new_value TEXT NOT NULL,
                updated_by TEXT NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                FOREIGN KEY (parameter_id) REFERENCES parameters(id)
            )
        """)
        
        # Add comment and form_id columns if they don't exist (migration)
        try:
            await db.execute("ALTER TABLE parameter_history ADD COLUMN comment TEXT")
        except aiosqlite.OperationalError:
            pass  # Column already exists
        
        try:
            await db.execute("ALTER TABLE parameter_history ADD COLUMN form_id TEXT")
        except aiosqlite.OperationalError:
            pass  # Column already exists
        
        # Create users table with roles
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT ?,
                subteam TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add subteam column to existing users table if it doesn't exist
        try:
            await db.execute("ALTER TABLE users ADD COLUMN subteam TEXT")
        except aiosqlite.OperationalError:
            pass  # Column already exists
        
        # Create queue table for pending changes
        await db.execute("""
            CREATE TABLE IF NOT EXISTS parameter_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parameter_name TEXT NOT NULL,
                subteam TEXT NOT NULL,
                new_value TEXT NOT NULL,
                current_value TEXT,
                submitted_by TEXT NOT NULL,
                submitted_at TIMESTAMP NOT NULL,
                comment TEXT,
                status TEXT NOT NULL DEFAULT '{settings.QUEUE_STATUS_PENDING}',
                form_id TEXT NOT NULL UNIQUE,
                car_id TEXT
            )
        """)
        
        # Create cars table for car identification
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                car_identifier TEXT NOT NULL UNIQUE,
                display_name TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_seen_at TIMESTAMP
            )
        """)
        
        # Add car_id column to parameter_queue if it doesn't exist (migration)
        try:
            await db.execute("ALTER TABLE parameter_queue ADD COLUMN car_id TEXT")
        except aiosqlite.OperationalError:
            pass  # Column already exists
        
        # Create indexes for performance
        await db.execute("CREATE INDEX IF NOT EXISTS idx_parameter_name ON parameters(parameter_name)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_subteam ON parameters(subteam)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_history_parameter ON parameter_history(parameter_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_history_name ON parameter_history(parameter_name)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_history_form ON parameter_history(form_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_queue_status ON parameter_queue(status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_queue_form ON parameter_queue(form_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_queue_car ON parameter_queue(car_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_queue_status_car ON parameter_queue(status, car_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_queue_submitted_at ON parameter_queue(submitted_at)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_cars_identifier ON cars(car_identifier)")
        
        # Initialize default admin user if users table is empty
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        count = (await cursor.fetchone())[0]
        if count == 0:
            # Default admin user
            import hashlib
            password_hash = hashlib.sha256(settings.DEFAULT_ADMIN_PASSWORD.encode()).hexdigest()
            await db.execute("""
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            """, (settings.DEFAULT_ADMIN_USERNAME, password_hash, settings.ROLE_ADMIN))
            await db.commit()
        
        await db.commit()
    finally:
        await db.close()


async def get_all_parameters(subteam: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all parameters, sorted alphabetically by name"""
    db = await get_db()
    try:
        db.row_factory = aiosqlite.Row
        
        if subteam:
            cursor = await db.execute(
                "SELECT * FROM parameters WHERE subteam = ? ORDER BY parameter_name ASC",
                (subteam,)
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM parameters ORDER BY parameter_name ASC"
            )
        
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


async def get_parameter(parameter_name: str) -> Optional[Dict[str, Any]]:
    """Get a single parameter by name"""
    db = await get_db()
    try:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM parameters WHERE parameter_name = ?",
            (parameter_name,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await db.close()


async def search_parameters(query: str) -> List[Dict[str, Any]]:
    """Search parameters by name (case-insensitive)"""
    db = await get_db()
    try:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM parameters WHERE parameter_name LIKE ? ORDER BY parameter_name ASC",
            (f"%{query}%",)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()




async def get_parameter_history(parameter_name: str) -> List[Dict[str, Any]]:
    """Get history for a specific parameter"""
    db = await get_db()
    try:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT * FROM parameter_history 
            WHERE parameter_name = ? 
            ORDER BY updated_at DESC
            """,
            (parameter_name,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


async def get_all_subteams() -> List[str]:
    """Get list of all unique subteams"""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT DISTINCT subteam FROM parameters ORDER BY subteam ASC")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
    finally:
        await db.close()


# User roles functions
async def get_user_role(username: str) -> Optional[str]:
    """Get user role"""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT role FROM users WHERE username = ?", (username,))
        row = await cursor.fetchone()
        return row[0] if row else None
    finally:
        await db.close()


async def get_all_users() -> List[Dict[str, Any]]:
    """Get all users with their roles"""
    db = await get_db()
    try:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT id, username, role, created_at FROM users ORDER BY username ASC")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


async def create_user(username: str, password: str, role: Optional[str] = None, subteam: Optional[str] = None) -> bool:
    """Create a new user"""
    import hashlib
    from datetime import datetime
    from internal.registered_users import add_registered_user
    
    db = await get_db()
    try:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        created_at = datetime.now().isoformat()
        await db.execute("""
            INSERT INTO users (username, password_hash, role, subteam)
            VALUES (?, ?, ?, ?)
        """, (username, password_hash, role, subteam))
        await db.commit()
        
        # Add to registered users JSON with plaintext password for visibility
        add_registered_user(username, user_role, created_at, password, subteam)
        
        return True
    except aiosqlite.IntegrityError:
        return False  # Username already exists
    finally:
        await db.close()


async def update_user_role(username: str, role: str) -> bool:
    """Update user role in database and registered_users.json"""
    from internal.registered_users import update_user_role as update_json_role
    
    db = await get_db()
    try:
        cursor = await db.execute("UPDATE users SET role = ? WHERE username = ?", (role, username))
        await db.commit()
        
        if cursor.rowcount > 0:
            # Also update in registered users JSON
            update_json_role(username, role)
            return True
        return False
    finally:
        await db.close()


async def update_user_password(username: str, password: str) -> bool:
    """Update user password in database (hashed)"""
    import hashlib
    db = await get_db()
    try:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor = await db.execute("UPDATE users SET password_hash = ? WHERE username = ?", (password_hash, username))
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await db.close()


async def update_user_subteam(username: str, subteam: Optional[str]) -> bool:
    """Update user subteam in database and registered_users.json"""
    from internal.registered_users import update_user_subteam as update_json_subteam
    
    db = await get_db()
    try:
        cursor = await db.execute("UPDATE users SET subteam = ? WHERE username = ?", (subteam, username))
        await db.commit()
        
        if cursor.rowcount > 0:
            # Also update in registered users JSON
            update_json_subteam(username, subteam)
            return True
        return False
    finally:
        await db.close()


async def delete_user(username: str) -> Optional[Dict[str, Any]]:
    """Delete a user and return user info before deletion"""
    db = await get_db()
    try:
        # Get user info before deletion (including subteam)
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT username, role, subteam FROM users WHERE username = ?", (username,))
        row = await cursor.fetchone()
        
        if not row:
            return None
        
        user_info = dict(row)
        
        # Delete from database
        await db.execute("DELETE FROM users WHERE username = ?", (username,))
        await db.commit()
        
        return user_info
    finally:
        await db.close()


async def verify_user_password(username: str, password: str) -> bool:
    """Verify user password against database"""
    import hashlib
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,)
        )
        row = await cursor.fetchone()
        return row[0] == password_hash if row else False
    finally:
        await db.close()


# Queue functions
async def add_to_queue(
    parameter_name: str,
    subteam: str,
    new_value: str,
    current_value: Optional[str],
    submitted_by: str,
    comment: Optional[str] = None,
    car_id: Optional[str] = None
) -> str:
    """Add parameter change to queue. Returns form_id."""
    import uuid
    form_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    db = await get_db()
    try:
        await db.execute("""
            INSERT INTO parameter_queue 
            (parameter_name, subteam, new_value, current_value, submitted_by, submitted_at, comment, form_id, car_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (parameter_name, subteam, new_value, current_value, submitted_by, now, comment, form_id, car_id))
        await db.commit()
        return form_id
    finally:
        await db.close()


async def get_queue(status: Optional[str] = None, car_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get queue items, optionally filtered by status and/or car_id"""
    db = await get_db()
    try:
        db.row_factory = aiosqlite.Row
        
        conditions = []
        params = []
        
        if status:
            conditions.append("status = ?")
            params.append(status)
        
        if car_id:
            conditions.append("car_id = ?")
            params.append(car_id)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        cursor = await db.execute(
            f"SELECT * FROM parameter_queue WHERE {where_clause} ORDER BY submitted_at DESC",
            tuple(params)
        )
        
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


async def process_queue_item(form_id: str, processed_by: str) -> bool:
    """Process a queue item and apply the change"""
    db = await get_db()
    try:
        # Use transaction for safety
        await db.execute("BEGIN IMMEDIATE")
        
        # Get queue item (with lock)
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            f"SELECT * FROM parameter_queue WHERE form_id = ? AND status IN ('{settings.QUEUE_STATUS_PENDING}', '{settings.QUEUE_STATUS_AUTO_APPLIED}')",
            (form_id,)
        )
        item = await cursor.fetchone()
        
        if not item:
            await db.rollback()
            return False
        
        item_dict = dict(item)
        
        # If already auto-applied, just mark as processed
        if item_dict["status"] == settings.QUEUE_STATUS_AUTO_APPLIED:
            await db.execute(f"UPDATE parameter_queue SET status = '{settings.QUEUE_STATUS_PROCESSED}' WHERE form_id = ?", (form_id,))
            await db.commit()
            return True
        
        # Apply the change
        await update_parameter(
            parameter_name=item_dict["parameter_name"],
            subteam=item_dict["subteam"],
            new_value=item_dict["new_value"],
            updated_by=processed_by,
            comment=item_dict.get("comment"),
            form_id=form_id
        )
        
        # Update all LDX files with this parameter change
        from .motec_ldx_updater import update_parameter_in_ldx_files
        await update_parameter_in_ldx_files(
            parameter_name=item_dict["parameter_name"],
            new_value=item_dict["new_value"],
            comment=item_dict.get("comment")
        )
        
        # Update queue status
        await db.execute(f"UPDATE parameter_queue SET status = '{settings.QUEUE_STATUS_PROCESSED}' WHERE form_id = ?", (form_id,))
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise
    finally:
        await db.close()


async def reject_queue_item(form_id: str) -> bool:
    """Reject a queue item. Uses transaction for safety."""
    db = await get_db()
    try:
        # Use transaction for safety
        await db.execute("BEGIN IMMEDIATE")
        cursor = await db.execute(f"UPDATE parameter_queue SET status = '{settings.QUEUE_STATUS_REJECTED}' WHERE form_id = ?", (form_id,))
        await db.commit()
        return cursor.rowcount > 0
    except Exception as e:
        await db.rollback()
        raise
    finally:
        await db.close()


# Enhanced update function with comment and form_id
async def update_parameter(
    parameter_name: str,
    subteam: str,
    new_value: str,
    updated_by: str,
    comment: Optional[str] = None,
    form_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update a parameter and create history entry.
    Returns the updated parameter.
    Uses transaction for safety.
    """
    now = datetime.now().isoformat()
    
    db = await get_db()
    try:
        # Use transaction for safety
        await db.execute("BEGIN IMMEDIATE")
        
        db.row_factory = aiosqlite.Row
        
        # Get current parameter to capture prior value (with lock)
        cursor = await db.execute(
            "SELECT * FROM parameters WHERE parameter_name = ?",
            (parameter_name,)
        )
        existing_row = await cursor.fetchone()
        existing = dict(existing_row) if existing_row else None
        prior_value = existing["current_value"] if existing else None
        parameter_id = existing["id"] if existing else None
        
        if existing:
            # Update existing parameter
            await db.execute("""
                UPDATE parameters 
                SET subteam = ?, current_value = ?, updated_at = ?, updated_by = ?
                WHERE parameter_name = ?
            """, (subteam, new_value, now, updated_by, parameter_name))
            
            # Get the parameter_id if we don't have it
            if not parameter_id:
                cursor = await db.execute(
                    "SELECT id FROM parameters WHERE parameter_name = ?",
                    (parameter_name,)
                )
                row = await cursor.fetchone()
                parameter_id = row[0] if row else None
        else:
            # Insert new parameter
            cursor = await db.execute("""
                INSERT INTO parameters (parameter_name, subteam, current_value, updated_at, updated_by)
                VALUES (?, ?, ?, ?, ?)
            """, (parameter_name, subteam, new_value, now, updated_by))
            
            parameter_id = cursor.lastrowid
        
        # Create history entry with comment and form_id
        await db.execute("""
            INSERT INTO parameter_history 
            (parameter_id, parameter_name, subteam, prior_value, new_value, updated_by, updated_at, comment, form_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (parameter_id, parameter_name, subteam, prior_value, new_value, updated_by, now, comment, form_id))
        
        await db.commit()
        
        # Return updated parameter (need to fetch it)
        cursor = await db.execute(
            "SELECT * FROM parameters WHERE parameter_name = ?",
            (parameter_name,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else {}
    except Exception as e:
        await db.rollback()
        raise
    finally:
        await db.close()
