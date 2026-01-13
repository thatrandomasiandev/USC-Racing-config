"""
USC Racing Parameter Management System
Lightweight parameter management for subteams
Optimized for Raspberry Pi
"""
from fastapi import FastAPI, Request, Query, HTTPException, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import aiosqlite
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from internal.database import (
    init_db,
    get_all_parameters,
    get_parameter,
    search_parameters,
    update_parameter,
    get_parameter_history,
    get_all_subteams,
    get_user_role,
    get_all_users,
    create_user,
    update_user_role,
    update_user_subteam,
    delete_user,
    add_to_queue,
    get_queue,
    process_queue_item,
    reject_queue_item,
    reset_database
)
from internal.deleted_users import (
    add_deleted_user,
    remove_deleted_user,
    get_all_deleted_users,
    is_user_deleted
)
from internal.registered_users import (
    sync_registered_users_from_db,
    get_all_registered_users,
    remove_user_from_registered
)
from internal.models import ParameterUpdate, UserCreate
from internal.motec_file_manager import (
    save_uploaded_file,
    get_all_files,
    get_file_by_id,
    delete_file as delete_motec_file,
    get_file_path
)
from internal.motec_parser import MotecParser
from internal.motec_translator import MotecTranslator
from internal.motec_ldx_updater import MotecLdxUpdater
from internal.car_parameters import (
    get_all_car_parameter_definitions,
    get_car_parameter_definition,
    add_car_parameter_definition,
    remove_car_parameter_definition,
    initialize_car_parameters_in_db
)
from internal.session_tracker import (
    create_session_from_file,
    get_all_sessions,
    get_session_by_file_id,
    get_sessions_by_parameter,
    compare_sessions
)
from internal.car_manager import (
    get_or_create_car,
    get_all_cars,
    get_car_by_identifier,
    identify_car_from_file
)
from internal.queue_auto_applier import auto_apply_queued_changes_to_file
from internal.auth import (
    get_current_user,
    require_auth,
    verify_login,
    init_auth_middleware,
    get_current_user_role,
    get_current_user_subteam,
    require_role
)

app = FastAPI(title="USC Racing Parameter Management", version="2.0.0")

# CORS middleware (add first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize auth middleware (session middleware - add after CORS)
init_auth_middleware(app)

# Setup paths
# From backend/main.py -> backend -> project root
BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"
STATIC_DIR = BASE_DIR / "frontend" / "static"

# Ensure directories exist
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Mount static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Import settings for configurable values
from internal.config.settings import settings


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        await init_db()
        print("[OK] Database initialized successfully")
    except Exception as e:
        print(f"[ERROR] Database initialization error: {e}")
        import traceback
        traceback.print_exc()


# Authentication routes
@app.get("/test")
async def test():
    """Test endpoint"""
    return {"status": "ok", "message": "Server is running"}


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    try:
        return templates.TemplateResponse("login.html", {"request": request})
    except Exception as e:
        import traceback
        error_msg = f"Error rendering login page: {e}\n{traceback.format_exc()}"
        print(error_msg)
        # Return error page instead of raising
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(error_msg, status_code=500)


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle login"""
    # #region agent log
    import json
    from pathlib import Path
    log_path = Path(__file__).parent.parent / ".cursor" / "debug.log"
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"main.py:150","message":"Login attempt","data":{"username":username},"timestamp":int(__import__("time").time()*1000)}) + "\n")
    except: pass
    # #endregion
    if await verify_login(username, password):
        request.session["username"] = username
        # Store user role in session
        role = await get_current_user_role(request)
        request.session["role"] = role or "user"
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"main.py:158","message":"Login success","data":{"username":username,"role":role},"timestamp":int(__import__("time").time()*1000)}) + "\n")
        except: pass
        # #endregion
        return RedirectResponse(url="/", status_code=303)
    else:
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"main.py:160","message":"Login failed","data":{"username":username},"timestamp":int(__import__("time").time()*1000)}) + "\n")
        except: pass
        # #endregion
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid username or password"}
        )


@app.post("/logout")
async def logout(request: Request):
    """Handle logout"""
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


# Main application routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main parameter management page"""
    # #region agent log
    import json
    from pathlib import Path
    log_path = Path(__file__).parent.parent / ".cursor" / "debug.log"
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"main.py:174","message":"Index route entry","data":{"has_session":bool(request.session.get("username"))},"timestamp":int(__import__("time").time()*1000)}) + "\n")
    except: pass
    # #endregion
    username = get_current_user(request)
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    
    # Get user role and subteam
    role = await get_current_user_role(request) or settings.ROLE_USER
    user_subteam = await get_current_user_subteam(request)
    
    # Get parameters (filtered by subteam for non-admins)
    if role == settings.ROLE_ADMIN:
        parameters = await get_all_parameters()
    else:
        if user_subteam:
            parameters = await get_all_parameters(subteam=user_subteam)
        else:
            parameters = []
    
    subteams = await get_all_subteams()
    
    # Add default subteams if none exist
    if not subteams:
        subteams = settings.DEFAULT_SUBTEAMS
    
    # Get queue items if admin
    queue_items = []
    if role == settings.ROLE_ADMIN:
        queue_items = await get_queue(status=settings.QUEUE_STATUS_PENDING)
    
    # #region agent log
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"main.py:217","message":"Index route exit","data":{"username":username,"role":role,"user_subteam":user_subteam,"param_count":len(parameters),"queue_count":len(queue_items)},"timestamp":int(__import__("time").time()*1000)}) + "\n")
    except: pass
    # #endregion
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "username": username,
            "role": role,
            "user_subteam": user_subteam,  # Pass user subteam to template
            "parameters": parameters,
            "subteams": subteams,
            "default_subteams": settings.DEFAULT_SUBTEAMS,
            "queue_items": queue_items
        }
    )


# API routes
@app.get("/api/parameters")
async def api_get_parameters(
    request: Request,
    subteam: Optional[str] = Query(None, description="Filter by subteam")
):
    """Get all parameters, optionally filtered by subteam
    
    Non-admin users are automatically filtered to their subteam only.
    Admins can see all parameters or filter by specific subteam.
    """
    require_auth(request)
    
    # Get user role and subteam
    role = await get_current_user_role(request) or settings.ROLE_USER
    user_subteam = await get_current_user_subteam(request)
    
    # If not admin, filter to user's subteam only
    if role != settings.ROLE_ADMIN:
        if user_subteam:
            # Non-admin users can only see their own subteam
            parameters = await get_all_parameters(subteam=user_subteam)
        else:
            # User has no subteam assigned, return empty list
            parameters = []
    else:
        # Admin can see all or filter by specific subteam
        parameters = await get_all_parameters(subteam=subteam)
    
    return {"parameters": parameters}


@app.get("/api/parameters/{parameter_name}")
async def api_get_parameter(request: Request, parameter_name: str):
    """Get a specific parameter"""
    require_auth(request)
    parameter = await get_parameter(parameter_name)
    if not parameter:
        raise HTTPException(status_code=404, detail="Parameter not found")
    return parameter


@app.post("/api/parameters")
async def api_update_parameter(request: Request, update: ParameterUpdate):
    """Update a parameter or add to queue. Also updates associated LDX files."""
    # #region agent log
    import json
    from pathlib import Path
    log_path = Path(__file__).parent.parent / ".cursor" / "debug.log"
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"main.py:262","message":"Parameter update entry","data":{"param_name":update.parameter_name,"new_value":update.new_value,"queue":update.queue},"timestamp":int(__import__("time").time()*1000)}) + "\n")
    except: pass
    # #endregion
    username = require_auth(request)
    
    # Get user role and subteam
    role = await get_current_user_role(request) or settings.ROLE_USER
    user_subteam = await get_current_user_subteam(request)
    
    # Get current parameter value (if exists)
    existing = await get_parameter(update.parameter_name)
    
    # For non-admin users, validate that they can only update their subteam's parameters
    if role != settings.ROLE_ADMIN:
        if not user_subteam:
            raise HTTPException(
                status_code=403,
                detail="Your account is not assigned to a subteam. Please contact an admin."
            )
        
        # Check if the parameter belongs to user's subteam
        if update.subteam != user_subteam:
            raise HTTPException(
                status_code=403,
                detail=f"You can only update parameters for your subteam ({user_subteam})"
            )
        
        # Also verify the parameter name belongs to their subteam (if it exists)
        if existing and existing.get("subteam") != user_subteam:
            raise HTTPException(
                status_code=403,
                detail=f"Parameter '{update.parameter_name}' does not belong to your subteam ({user_subteam})"
            )
    
    try:
        current_value = existing["current_value"] if existing else None
        
        if update.queue:
            # Add to queue instead of applying immediately
            import uuid
            # Get car_id from request if provided (will be added to frontend)
            car_id = update.car_id if hasattr(update, 'car_id') and update.car_id else None
            form_id = await add_to_queue(
                parameter_name=update.parameter_name,
                subteam=update.subteam,
                new_value=update.new_value,
                current_value=current_value,
                submitted_by=username,
                comment=update.comment,
                car_id=car_id
            )
            return {
                "status": "queued",
                "message": "Parameter change added to queue",
                "form_id": form_id
            }
        else:
            # Apply immediately - update database and LDX files
            import uuid
            form_id = str(uuid.uuid4())
            
            # Update parameter in database
            updated = await update_parameter(
                parameter_name=update.parameter_name,
                subteam=update.subteam,
                new_value=update.new_value,
                updated_by=username,
                comment=update.comment,
                form_id=form_id
            )
            
            # ALWAYS update associated LDX files when parameter is updated from frontend
            # This ensures every frontend update is synchronized to the LDX files
            print(f"[API] Updating parameter '{update.parameter_name}' - will sync to LDX files")
            ldx_files_updated = await update_parameter_in_ldx_files(
                parameter_name=update.parameter_name,
                new_value=update.new_value,
                comment=update.comment
            )
            
            print(f"[API] Parameter update complete: {update.parameter_name} = {update.new_value}")
            print(f"[API] LDX files updated: {ldx_files_updated}")
            
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"main.py:342","message":"Parameter update success","data":{"param_name":update.parameter_name,"ldx_updated":ldx_files_updated},"timestamp":int(__import__("time").time()*1000)}) + "\n")
            except: pass
            # #endregion
            return {
                "status": "success",
                "parameter": updated,
                "form_id": form_id,
                "ldx_files_updated": ldx_files_updated
            }
    except Exception as e:
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"main.py:349","message":"Parameter update error","data":{"error":str(e)},"timestamp":int(__import__("time").time()*1000)}) + "\n")
        except: pass
        # #endregion
        raise HTTPException(status_code=500, detail=str(e))


async def update_parameter_in_ldx_files(
    parameter_name: str,
    new_value: str,
    comment: Optional[str] = None
) -> int:
    """
    Update parameter value in all associated LDX files
    
    Args:
        parameter_name: Name of the parameter to update
        new_value: New value to set
        comment: Optional comment to include in LDX documentation
    
    Returns:
        Number of LDX files updated
    """
    updated_count = 0
    
    try:
        file_ids_to_update = set()
        
        # Method 1: Find files from sessions that contain this parameter
        from internal.session_tracker import get_all_sessions
        sessions = get_all_sessions()
        
        for session in sessions:
            if session.get("file_type") != "ldx":
                continue
            
            # Check if this session's snapshot contains the parameter
            params_snapshot = session.get("parameters_snapshot", [])
            for param in params_snapshot:
                if param.get("parameter_name") == parameter_name:
                    file_ids_to_update.add(session.get("file_id"))
                    break
        
        # Method 2: Check all uploaded LDX files for:
        #   - ldx_ parameters (existing LDX data)
        #   - car parameters (should be auto-documented in Details)
        if parameter_name.startswith("ldx_"):
            # For ldx_ parameters, check if file contains this specific parameter
            from internal.motec_file_manager import get_all_files
            all_files = get_all_files()
            
            # Parse each LDX file to see if it contains this parameter
            print(f"[DEBUG] Checking {len(all_files)} uploaded files for parameter '{parameter_name}'")
            for file_meta in all_files:
                if file_meta.get("file_type") != "ldx":
                    continue
                
                file_id = file_meta.get("id")
                if not file_id or file_id in file_ids_to_update:
                    continue
                
                # Check if file contains this parameter by parsing it
                file_path = get_file_path(file_id)
                if file_path and file_path.exists():
                    contains_param = MotecLdxUpdater.ldx_file_contains_parameter(file_path, parameter_name)
                    if contains_param:
                        print(f"[DEBUG] Found parameter in file: {file_path.name} (ID: {file_id})")
                        file_ids_to_update.add(file_id)
                else:
                    if file_path:
                        print(f"[DEBUG] File path doesn't exist: {file_path}")
                    else:
                        print(f"[DEBUG] Could not resolve path for file ID: {file_id}")
            
            print(f"[DEBUG] Total files to update: {len(file_ids_to_update)}")
        
        elif not parameter_name.startswith("ld_"):
            # For car parameters (not ldx_ or ld_), auto-document in ALL LDX files
            from internal.motec_file_manager import get_all_files
            from internal.car_parameters import get_car_parameter_definition
            
            # Check if this is a car parameter that should be documented
            car_def = get_car_parameter_definition(parameter_name)
            if car_def:
                print(f"[DEBUG] Car parameter '{parameter_name}' will be auto-documented in all LDX files")
                all_files = get_all_files()
                
                # Add ALL LDX files for car parameter documentation
                for file_meta in all_files:
                    if file_meta.get("file_type") != "ldx":
                        continue
                    
                    file_id = file_meta.get("id")
                    if file_id and file_id not in file_ids_to_update:
                        file_ids_to_update.add(file_id)
                        print(f"[DEBUG] Will document '{parameter_name}' in file: {file_meta.get('filename')}")
                
                print(f"[DEBUG] Total files to update for car parameter: {len(file_ids_to_update)}")
        
        # Update each LDX file
        print(f"[PARAM_UPDATE] Processing {len(file_ids_to_update)} file(s) for parameter '{parameter_name}'")
        for file_id in file_ids_to_update:
            file_path = get_file_path(file_id)
            if file_path:
                file_path = file_path.resolve()  # Get absolute path
                print(f"[PARAM_UPDATE] Resolved path for ID '{file_id}': {file_path}")
            
            if file_path and file_path.exists() and file_path.suffix.lower() == settings.MOTEC_LDX_EXTENSION.lower():
                print(f"[PARAM_UPDATE] ✓ File exists and is LDX: {file_path.name}")
                print(f"[PARAM_UPDATE] Starting update for file ID: {file_id}")
                success = MotecLdxUpdater.update_parameter_in_ldx(
                    file_path=file_path,
                    parameter_name=parameter_name,
                    new_value=new_value,
                    comment=comment
                )
                if success:
                    updated_count += 1
                    print(f"[PARAM_UPDATE] ✓ Successfully updated file: {file_path.name} (total updated: {updated_count})")
                else:
                    print(f"[PARAM_UPDATE] ✗ Failed to update file: {file_path.name}")
            else:
                if file_path:
                    if not file_path.exists():
                        print(f"[PARAM_UPDATE] ✗ File does not exist: {file_path}")
                    elif file_path.suffix.lower() != settings.MOTEC_LDX_EXTENSION.lower():
                        print(f"[PARAM_UPDATE] ✗ File is not .ldx: {file_path} (extension: {file_path.suffix})")
                else:
                    print(f"[PARAM_UPDATE] ✗ Could not resolve file path for ID: {file_id}")
        
        print(f"[PARAM_UPDATE] === UPDATE SUMMARY ===")
        print(f"[PARAM_UPDATE] Parameter: {parameter_name}")
        print(f"[PARAM_UPDATE] New value: {new_value}")
        print(f"[PARAM_UPDATE] Files processed: {len(file_ids_to_update)}")
        print(f"[PARAM_UPDATE] Files successfully updated: {updated_count}")
        print(f"[PARAM_UPDATE] =========================")
        
        return updated_count
    
    except Exception as e:
        import traceback
        print(f"Error updating LDX files for parameter {parameter_name}: {e}")
        traceback.print_exc()
        return updated_count


@app.get("/api/history")
async def api_get_history(
    request: Request,
    parameter: Optional[str] = Query(None, description="Parameter name"),
    form_id: Optional[str] = Query(None, description="Form ID")
):
    """Get parameter history with form links"""
    require_auth(request)
    
    if form_id:
        # Get history by form_id
        from internal.database import get_db
        db = await get_db()
        try:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM parameter_history WHERE form_id = ? ORDER BY updated_at DESC",
                (form_id,)
            )
            rows = await cursor.fetchall()
            history = [dict(row) for row in rows]
            return {"history": history}
        finally:
            await db.close()
    elif parameter:
        history = await get_parameter_history(parameter)
        return {"history": history}
    else:
        # Get all history
        from internal.database import get_db
        import aiosqlite
        db = await get_db()
        try:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM parameter_history ORDER BY updated_at DESC LIMIT 100"
            )
            rows = await cursor.fetchall()
            history = [dict(row) for row in rows]
            return {"history": history}
        finally:
            await db.close()


@app.get("/api/search")
async def api_search_parameters(
    request: Request,
    q: str = Query(..., description="Search query")
):
    """Search parameters by name"""
    require_auth(request)
    parameters = await search_parameters(q)
    return {"parameters": parameters}


@app.get("/api/subteams")
async def api_get_subteams(request: Request):
    """Get all subteams"""
    require_auth(request)
    subteams = await get_all_subteams()
    if not subteams:
        subteams = settings.DEFAULT_SUBTEAMS
    return {"subteams": subteams}


# Queue management endpoints
@app.get("/api/queue")
async def api_get_queue(
    request: Request, 
    status: Optional[str] = Query(None),
    car_id: Optional[str] = Query(None)
):
    """Get queue items, optionally filtered by status and/or car_id"""
    require_auth(request)
    queue_items = await get_queue(status=status, car_id=car_id)
    return {"queue": queue_items}


@app.post("/api/queue/{form_id}/process")
async def api_process_queue(request: Request, form_id: str):
    """Process a queue item (admin only)"""
    username = await require_role(request, settings.ROLE_ADMIN)
    success = await process_queue_item(form_id, username)
    if success:
        return {"status": "success", "message": "Queue item processed"}
    else:
        raise HTTPException(status_code=404, detail="Queue item not found or already processed")


@app.post("/api/queue/{form_id}/reject")
async def api_reject_queue(request: Request, form_id: str):
    """Reject a queue item (admin only)"""
    await require_role(request, settings.ROLE_ADMIN)
    success = await reject_queue_item(form_id)
    if success:
        return {"status": "success", "message": "Queue item rejected"}
    else:
        raise HTTPException(status_code=404, detail="Queue item not found")


# User management endpoints (admin only)
@app.get("/api/users")
async def api_get_users(request: Request):
    """Get all users with passwords from registered_users.json"""
    await require_role(request, settings.ROLE_ADMIN)
    users = await get_all_users()
    
    # Get passwords from registered_users.json
    from internal.registered_users import get_all_registered_users
    registered_users = get_all_registered_users()
    registered_map = {u.get("username"): u for u in registered_users}
    
    # Add passwords and subteams to user data
    for user in users:
        if user["username"] in registered_map:
            user["password"] = registered_map[user["username"]].get("password", "N/A")
            user["subteam"] = registered_map[user["username"]].get("subteam") or user.get("subteam")
        else:
            user["password"] = "N/A"
    
    # Get subteams for dropdown
    subteams = await get_all_subteams()
    if not subteams:
        subteams = settings.DEFAULT_SUBTEAMS
    
    return {"users": users, "subteams": subteams}


@app.post("/api/users")
async def api_create_user(request: Request, user: UserCreate):
    """Create a new user (password stored in plaintext in registered_users.json)"""
    await require_role(request, settings.ROLE_ADMIN)
    success = await create_user(user.username, user.password, user.role, user.subteam)
    if success:
        return {"status": "success", "message": "User created"}
    else:
        raise HTTPException(status_code=400, detail="Username already exists")


@app.patch("/api/users/{username}/password")
async def api_update_user_password(request: Request, username: str, password: str = Query(...)):
    """Update user password (stores in plaintext in registered_users.json)"""
    await require_role(request, settings.ROLE_ADMIN)
    from internal.database import update_user_password as db_update_password
    from internal.registered_users import update_user_password as json_update_password
    
    # Update in database (hashed)
    success = await db_update_password(username, password)
    if success:
        # Also update in JSON (plaintext for visibility)
        json_update_password(username, password)
        return {"status": "success", "message": f"Password updated for {username}"}
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.patch("/api/users/{username}/role")
async def api_update_user_role(request: Request, username: str, role: str = Query(...)):
    """Update user role"""
    await require_role(request, settings.ROLE_ADMIN)
    success = await update_user_role(username, role)
    if success:
        return {"status": "success", "message": f"User {username} role updated to {role}"}
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.patch("/api/users/{username}/subteam")
async def api_update_user_subteam(request: Request, username: str, subteam: Optional[str] = Query(None)):
    """Update user subteam"""
    await require_role(request, settings.ROLE_ADMIN)
    success = await update_user_subteam(username, subteam)
    if success:
        subteam_text = subteam or "None"
        return {"status": "success", "message": f"User {username} subteam updated to {subteam_text}"}
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.delete("/api/users/{username}")
async def api_delete_user(request: Request, username: str):
    """Delete a user (moves to recently_deleted_users.json and updates registered_users.json)
    
    Admins can delete any user, including other admins.
    Prevents self-deletion to avoid locking yourself out.
    """
    admin_username = await require_role(request, "admin")
    
    # Prevent self-deletion
    if username == admin_username:
        raise HTTPException(
            status_code=400, 
            detail="You cannot delete your own account. Ask another admin to delete it."
        )
    
    # Get user info before deletion
    user_info = await delete_user(username)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Add to recently deleted users (including subteam)
    add_deleted_user(
        username=user_info["username"],
        role=user_info["role"],
        deleted_by=admin_username,
        subteam=user_info.get("subteam")
    )
    
    # Remove from registered users JSON (only active users stay there)
    remove_user_from_registered(user_info["username"])
    
    return {
        "status": "success",
        "message": f"User {username} deleted and moved to recently deleted users"
    }


@app.get("/api/users/deleted")
async def api_get_deleted_users(request: Request):
    """Get all recently deleted users"""
    await require_role(request, settings.ROLE_ADMIN)
    deleted_users = get_all_deleted_users()
    return {"deleted_users": deleted_users}


@app.get("/api/users/registered")
async def api_get_registered_users(request: Request):
    """Get all registered users (active and deleted) from JSON"""
    await require_role(request, settings.ROLE_ADMIN)
    # Sync from database first to ensure JSON is up to date
    await sync_registered_users_from_db()
    registered_users = get_all_registered_users()
    return {"registered_users": registered_users}


@app.post("/api/users/registered/sync")
async def api_sync_registered_users(request: Request):
    """Sync registered_users.json with database (bidirectional sync)"""
    await require_role(request, settings.ROLE_ADMIN)
    # Sync from database to JSON
    await sync_registered_users_from_db()
    return {"status": "success", "message": "Registered users JSON synced with database"}


@app.post("/api/users/deleted/{username}/remove")
async def api_remove_deleted_user(request: Request, username: str):
    """Permanently remove a user from recently_deleted_users.json (allows re-creation)"""
    await require_role(request, settings.ROLE_ADMIN)
    success = remove_deleted_user(username)
    if success:
        return {"status": "success", "message": f"User {username} removed from deleted users list"}
    else:
        raise HTTPException(status_code=404, detail="User not found in deleted users list")


# MoTeC File Management endpoints
@app.post("/api/motec/upload")
async def api_upload_motec_file(
    request: Request,
    file: UploadFile = File(...),
    file_type: str = Form("auto"),  # "ldx", "ld", or "auto"
    auto_populate: bool = Form(True),  # Auto-parse and create parameters
    subteam: str = Form(None),  # Subteam for auto-created parameters (defaults to MOTEC_DEFAULT_SUBTEAM)
    overwrite_existing: bool = Form(False)  # Overwrite existing parameters
):
    """Upload a MoTeC file (.ldx or .ld) and optionally auto-populate parameters"""
    # #region agent log
    import json
    from pathlib import Path
    log_path = Path(__file__).parent.parent / ".cursor" / "debug.log"
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"main.py:743","message":"MoTeC upload entry","data":{"filename":file.filename,"file_type":file_type,"auto_populate":auto_populate},"timestamp":int(__import__("time").time()*1000)}) + "\n")
    except: pass
    # #endregion
    require_auth(request)
    
    # Validate file type
    filename = file.filename
    if not filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    if not (filename.lower().endswith('.ldx') or filename.lower().endswith('.ld')):
        raise HTTPException(status_code=400, detail="File must be .ldx or .ld format")
    
    # Read file content
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
    
    # Determine file type if auto
    if file_type == "auto":
        if filename.lower().endswith(settings.MOTEC_LDX_EXTENSION.lower()):
            file_type = "ldx"
        elif filename.lower().endswith(settings.MOTEC_LD_EXTENSION.lower()):
            file_type = "ld"
        else:
            raise HTTPException(status_code=400, detail=f"Could not determine file type. Must be {settings.MOTEC_LDX_EXTENSION} or {settings.MOTEC_LD_EXTENSION}")
    
    # Save file and get metadata
    try:
        metadata = save_uploaded_file(content, filename, file_type)
        file_id = metadata.get("id", "")
        file_path = get_file_path(file_id)
        
        # Identify car from file
        car = None
        parsed = None
        if file_path and file_path.exists():
            try:
                parsed = MotecParser.parse_file(file_path)
                car = await identify_car_from_file(file_path, parsed)
                if car:
                    # Store car_id in file metadata
                    metadata["car_id"] = car.get("car_identifier")
                    metadata["car"] = {
                        "id": car.get("id"),
                        "car_identifier": car.get("car_identifier"),
                        "display_name": car.get("display_name")
                    }
            except Exception as e:
                print(f"Warning: Could not identify car from file: {str(e)}")
        
        # Initialize car parameters in database if they don't exist
        # This ensures all defined car parameters (like tire pressure) are available
        initialized_params = await initialize_car_parameters_in_db()
        
        # Capture snapshot of current parameters when file is uploaded
        # This links the session data to what parameters were active
        current_parameters = await get_all_parameters()
        parameters_snapshot = [
            {
                "parameter_name": p["parameter_name"],
                "current_value": p["current_value"],
                "subteam": p["subteam"]
            }
            for p in current_parameters
        ]
        
        # Extract performance data from the uploaded file (for analysis)
        session_data = {}
        if file_path and file_path.exists() and parsed:
            try:
                if file_type == "ldx" and "details" in parsed:
                    # Extract performance metrics from LDX Details
                    session_data = {
                        "total_laps": parsed["details"].get("Total Laps", ""),
                        "fastest_time": parsed["details"].get("Fastest Time", ""),
                        "fastest_lap": parsed["details"].get("Fastest Lap", "")
                    }
                    # Also store all details for reference
                    session_data["all_details"] = parsed["details"]
                elif file_type == "ld":
                    # Extract metadata from LD file
                    session_data = {
                        "session_date": parsed.get("date", ""),
                        "session_time": parsed.get("time", ""),
                        "device": parsed.get("device_name", ""),
                        "track": parsed.get("track_name", ""),
                        "driver": parsed.get("driver_name", "")
                    }
            except Exception as e:
                # Don't fail upload if extraction fails
                print(f"Warning: Could not extract session data: {str(e)}")
        
        # AUTOMATIC QUEUE INJECTION: Apply all pending queue items to the uploaded file
        # This happens when the car returns and data is pulled
        queue_application_result = None
        if file_type == "ldx" and file_path and file_path.exists():
            try:
                car_identifier = car.get("car_identifier") if car else None
                queue_application_result = await auto_apply_queued_changes_to_file(
                    file_path=file_path,
                    car_id=car_identifier
                )
                print(f"[AUTO-INJECT] Applied {queue_application_result['applied_count']} queued changes to {filename}")
                if queue_application_result['failed_count'] > 0:
                    print(f"[AUTO-INJECT] Warning: {queue_application_result['failed_count']} changes failed")
            except Exception as e:
                print(f"[AUTO-INJECT] Error applying queued changes: {str(e)}")
                import traceback
                traceback.print_exc()
                # Don't fail the upload if auto-injection fails
        
        # Reload parameters after queue application (in case new ones were created)
        if queue_application_result and queue_application_result.get("applied_count", 0) > 0:
            current_parameters = await get_all_parameters()
            parameters_snapshot = [
                {
                    "parameter_name": p["parameter_name"],
                    "current_value": p["current_value"],
                    "subteam": p["subteam"]
                }
                for p in current_parameters
            ]
        
        # Create session record linking file to parameter snapshot
        session_record = create_session_from_file(
            file_id=file_id,
            filename=filename,
            file_type=file_type,
            parameters_snapshot=parameters_snapshot,
            session_data=session_data
        )
        
        # Add car information to session record
        if car:
            session_record["car_id"] = car.get("car_identifier")
            session_record["car"] = {
                "id": car.get("id"),
                "car_identifier": car.get("car_identifier"),
                "display_name": car.get("display_name")
            }
        
        # Auto-populate parameters if requested
        parameters_created = 0
        parameters_updated = 0
        parameters_skipped = 0
        
        if auto_populate and file_path and file_path.exists():
            try:
                username = get_current_user(request) or "system"
                    
                if file_type == "ldx":
                    # Parse LDX and create parameters
                    parameters = MotecTranslator.ldx_to_parameters(
                        file_path=file_path,
                        subteam=subteam,
                        default_updated_by=username,
                        include_details=True,
                        include_math_items=True
                    )
                    
                    # Create/update parameters in database and defaults
                    for param in parameters:
                        param_name = param["parameter_name"]
                        param_value = param["current_value"]
                        param_subteam = param["subteam"]
                        
                        # Check if parameter already exists
                        existing = await get_parameter(param_name)
                        
                        if existing and not overwrite_existing:
                            parameters_skipped += 1
                            continue
                        
                        # Create/update in database
                        await update_parameter(
                            parameter_name=param_name,
                            subteam=param_subteam,
                            new_value=param_value,
                            updated_by=username,
                            comment=f"Auto-imported from {file_type.upper()} file: {filename}"
                        )
                        
                        if existing:
                            parameters_updated += 1
                        else:
                            parameters_created += 1
                
                elif file_type == "ld":
                    # Parse LD file metadata (limited parameter extraction)
                    parsed = MotecParser.parse_file(file_path)
                    
                    # Extract basic metadata as parameters
                    ld_params = []
                    if parsed.get("date"):
                        ld_params.append({
                            "parameter_name": f"ld_session_date",
                            "current_value": parsed["date"],
                            "subteam": subteam
                        })
                    if parsed.get("time"):
                        ld_params.append({
                            "parameter_name": f"ld_session_time",
                            "current_value": parsed["time"],
                            "subteam": subteam
                        })
                    if parsed.get("device_name"):
                        ld_params.append({
                            "parameter_name": f"ld_device_name",
                            "current_value": parsed["device_name"],
                            "subteam": subteam
                        })
                    if parsed.get("track_name"):
                        ld_params.append({
                            "parameter_name": f"ld_track_name",
                            "current_value": parsed["track_name"],
                            "subteam": subteam
                        })
                    if parsed.get("driver_name"):
                        ld_params.append({
                            "parameter_name": f"ld_driver_name",
                            "current_value": parsed["driver_name"],
                            "subteam": subteam
                        })
                    
                    # Create parameters from LD metadata
                    for param in ld_params:
                        param_name = param["parameter_name"]
                        param_value = param["current_value"]
                        param_subteam = param["subteam"]
                        
                        existing = await get_parameter(param_name)
                        
                        if existing and not overwrite_existing:
                            parameters_skipped += 1
                            continue
                        
                        # Create in database
                        await update_parameter(
                            parameter_name=param_name,
                            subteam=param_subteam,
                            new_value=param_value,
                            updated_by=username,
                            comment=f"Auto-imported from LD file: {filename}"
                        )
                        
                        if existing:
                            parameters_updated += 1
                        else:
                            parameters_created += 1
                
            except Exception as e:
                # Don't fail upload if auto-populate fails, just log it
                import traceback
                print(f"Warning: Auto-populate failed: {str(e)}")
                print(traceback.format_exc())
                # Continue with successful upload response
        
        response = {
            "status": "success",
            "message": f"File {filename} uploaded successfully",
            "file": metadata,
            "session": {
                "session_id": session_record.get("session_id"),
                "parameters_captured": len(parameters_snapshot),
                "performance_data": session_data
            }
        }
        
        # Add queue application results if auto-injection occurred
        if queue_application_result:
            response["queue_application"] = {
                "applied_count": queue_application_result.get("applied_count", 0),
                "failed_count": queue_application_result.get("failed_count", 0),
                "message": queue_application_result.get("message", ""),
                "applied_items": queue_application_result.get("applied_items", []),
                "failed_items": queue_application_result.get("failed_items", [])
            }
        
        if initialized_params:
            response["initialized_parameters"] = initialized_params
        
        if auto_populate:
            response["auto_populate"] = {
                "enabled": True,
                "created": parameters_created,
                "updated": parameters_updated,
                "skipped": parameters_skipped,
                "total": parameters_created + parameters_updated + parameters_skipped
            }
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"main.py:973","message":"MoTeC upload success","data":{"filename":filename,"params_created":parameters_created,"params_updated":parameters_updated},"timestamp":int(__import__("time").time()*1000)}) + "\n")
        except: pass
        # #endregion
        
        return response
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")


@app.get("/api/motec/files")
async def api_get_motec_files(request: Request):
    """Get all uploaded MoTeC files"""
    require_auth(request)
    try:
        files = get_all_files()
        # Sort by uploaded_at, newest first
        # Handle cases where uploaded_at might be missing or invalid
        files.sort(key=lambda x: x.get("uploaded_at", "") or "", reverse=True)
        return {"files": files}
    except Exception as e:
        import traceback
        error_msg = f"Error loading MoTeC files: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/api/motec/files/{file_id}")
async def api_get_motec_file(request: Request, file_id: str):
    """Get file metadata by ID"""
    require_auth(request)
    file_meta = get_file_by_id(file_id)
    if not file_meta:
        raise HTTPException(status_code=404, detail="File not found")
    return {"file": file_meta}


@app.get("/api/motec/files/{file_id}/download")
async def api_download_motec_file(request: Request, file_id: str):
    """Download a MoTeC file"""
    require_auth(request)
    file_path = get_file_path(file_id)
    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="application/octet-stream"
    )


@app.delete("/api/motec/files/{file_id}")
async def api_delete_motec_file(request: Request, file_id: str):
    """Delete a MoTeC file"""
    require_auth(request)
    success = delete_motec_file(file_id)
    if success:
        return {"status": "success", "message": "File deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="File not found")


@app.get("/api/motec/files/{file_id}/parse")
async def api_parse_motec_file(request: Request, file_id: str):
    """Parse a MoTeC file and return full parse results"""
    require_auth(request)
    file_path = get_file_path(file_id)
    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        parsed = MotecParser.parse_file(file_path)
        return {"status": "success", "parsed_data": parsed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing file: {str(e)}")


# MoTeC Translation endpoints (LDX <-> Admin Console)
@app.post("/api/motec/files/{file_id}/import-to-parameters")
async def api_import_ldx_to_parameters(
    request: Request,
    file_id: str,
    subteam: str = Query(None, description="Subteam name for imported parameters (defaults to MOTEC_DEFAULT_SUBTEAM)"),
    include_details: bool = Query(True, description="Import Details String elements"),
    include_math_items: bool = Query(True, description="Import MathItems")
):
    """
    Import LDX file and convert to parameters in admin console
    Returns list of parameters that would be created (dry run)
    Use POST with body to actually create them
    """
    require_auth(request)
    file_path = get_file_path(file_id)
    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    if file_path.suffix.lower() != settings.MOTEC_LDX_EXTENSION.lower():
        raise HTTPException(status_code=400, detail=f"File must be {settings.MOTEC_LDX_EXTENSION} format")
    
    try:
        username = request.session.get("username", "system")
        parameters = MotecTranslator.ldx_to_parameters(
            file_path=file_path,
            subteam=subteam or settings.MOTEC_DEFAULT_SUBTEAM,
            default_updated_by=username,
            include_details=include_details,
            include_math_items=include_math_items
        )
        
        return {
            "status": "success",
            "parameters": parameters,
            "count": len(parameters),
            "message": f"Found {len(parameters)} parameters to import"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing LDX: {str(e)}")


@app.post("/api/motec/files/{file_id}/import-to-parameters/apply")
async def api_apply_ldx_import(
    request: Request,
    file_id: str,
    subteam: str = Query(None, description="Subteam name for imported parameters (defaults to MOTEC_DEFAULT_SUBTEAM)"),
    include_details: bool = Query(True, description="Import Details String elements"),
    include_math_items: bool = Query(True, description="Import MathItems"),
    overwrite_existing: bool = Query(False, description="Overwrite existing parameters with same name")
):
    """Import LDX file and actually create/update parameters in admin console"""
    require_auth(request)
    file_path = get_file_path(file_id)
    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    if file_path.suffix.lower() != settings.MOTEC_LDX_EXTENSION.lower():
        raise HTTPException(status_code=400, detail=f"File must be {settings.MOTEC_LDX_EXTENSION} format")
    
    try:
        username = request.session.get("username", "system")
        parameters = MotecTranslator.ldx_to_parameters(
            file_path=file_path,
            subteam=subteam or settings.MOTEC_DEFAULT_SUBTEAM,
            default_updated_by=username,
            include_details=include_details,
            include_math_items=include_math_items
        )
        
        # Apply parameters to database
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for param in parameters:
            param_name = param["parameter_name"]
            existing = await get_parameter(param_name)
            
            if existing and not overwrite_existing:
                skipped_count += 1
                continue
            
            # Update or create parameter
            await update_parameter(
                parameter_name=param_name,
                subteam=param["subteam"],
                new_value=param["current_value"],
                updated_by=username,
                comment=f"Imported from LDX file: {file_path.name}"
            )
            
            if existing:
                updated_count += 1
            else:
                created_count += 1
        
        return {
            "status": "success",
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "total": len(parameters),
            "message": f"Imported {created_count} new, updated {updated_count}, skipped {skipped_count} parameters"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing LDX: {str(e)}")


# Car Management endpoints
@app.get("/api/cars")
async def api_get_cars(request: Request):
    """Get all registered cars"""
    require_auth(request)
    cars = await get_all_cars()
    return {"cars": cars}


@app.post("/api/cars")
async def api_create_car(request: Request, car_data: dict):
    """Create or update a car"""
    require_auth(request)
    car_identifier = car_data.get("car_identifier")
    display_name = car_data.get("display_name")
    
    if not car_identifier:
        raise HTTPException(status_code=400, detail="car_identifier is required")
    
    car = await get_or_create_car(car_identifier, display_name)
    return {"car": car}


@app.get("/api/cars/{car_identifier}")
async def api_get_car(request: Request, car_identifier: str):
    """Get car by identifier"""
    require_auth(request)
    car = await get_car_by_identifier(car_identifier)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return {"car": car}


@app.get("/api/cars/{car_identifier}/queue")
async def api_get_car_queue(request: Request, car_identifier: str, status: Optional[str] = Query(None)):
    """Get queue items for a specific car"""
    require_auth(request)
    queue_items = await get_queue(status=status, car_id=car_identifier)
    return {"queue": queue_items, "car_identifier": car_identifier}


@app.post("/api/motec/export-parameters-to-ldx")
async def api_export_parameters_to_ldx(
    request: Request,
    subteam: Optional[str] = Query(None, description="Filter parameters by subteam"),
    output_filename: str = Query("export.ldx", description="Output filename"),
    locale: str = Query("English_United States.1252", description="LDX locale"),
    version: str = Query("1.6", description="LDX version")
):
    """Export parameters from admin console to LDX file"""
    require_auth(request)
    
    try:
        # Get parameters from database
        parameters_data = await get_all_parameters(subteam=subteam)
        
        if not parameters_data:
            raise HTTPException(status_code=404, detail="No parameters found to export")
        
        # Convert to parameter format for translator
        parameters = []
        for param in parameters_data:
            parameters.append({
                "parameter_name": param["parameter_name"],
                "subteam": param["subteam"],
                "current_value": param["current_value"],
                "updated_at": param["updated_at"],
                "updated_by": param["updated_by"]
            })
        
        # Generate LDX file
        from internal.config.settings import settings
        
        output_dir = settings.DATA_DIR / "motec_files" / "ldx"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / output_filename
        
        MotecTranslator.parameters_to_ldx(
            parameters=parameters,
            output_path=output_path,
            locale=locale,
            version=version
        )
        
        # Return file info for download
        file_id = f"{datetime.now().timestamp()}_{output_filename}"
        
        return {
            "status": "success",
            "file_id": file_id,
            "filename": output_filename,
            "path": str(output_path.relative_to(settings.BASE_DIR)),
            "download_url": f"/api/motec/download-ldx/{file_id}",
            "message": f"Exported {len(parameters)} parameters to {output_filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting parameters: {str(e)}")


@app.post("/api/motec/files/{file_id}/merge-with-parameters")
async def api_merge_ldx_with_parameters(
    request: Request,
    file_id: str,
    subteam: Optional[str] = Query(None, description="Filter parameters by subteam"),
    output_filename: str = Query(None, description="Output filename (default: merged_{original_name})"),
    merge_strategy: str = Query("parameters_override", description="Merge strategy: parameters_override, ldx_override, merge")
):
    """Merge existing LDX file with parameters from admin console"""
    require_auth(request)
    
    file_path = get_file_path(file_id)
    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    if file_path.suffix.lower() != settings.MOTEC_LDX_EXTENSION.lower():
        raise HTTPException(status_code=400, detail=f"File must be {settings.MOTEC_LDX_EXTENSION} format")
    
    try:
        # Get parameters from database
        parameters_data = await get_all_parameters(subteam=subteam)
        
        # Convert to parameter format
        parameters = []
        for param in parameters_data:
            parameters.append({
                "parameter_name": param["parameter_name"],
                "subteam": param["subteam"],
                "current_value": param["current_value"]
            })
        
        # Determine output filename
        if not output_filename:
            output_filename = f"merged_{file_path.name}"
        
        from internal.config.settings import settings
        
        output_dir = settings.DATA_DIR / "motec_files" / "ldx"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / output_filename
        
        # Merge
        MotecTranslator.merge_ldx_with_parameters(
            ldx_file_path=file_path,
            parameters=parameters,
            output_path=output_path,
            merge_strategy=merge_strategy
        )
        
        return {
            "status": "success",
            "filename": output_filename,
            "path": str(output_path.relative_to(settings.BASE_DIR)),
            "message": f"Merged {len(parameters)} parameters into {output_filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error merging LDX: {str(e)}")


@app.get("/api/motec/download-ldx/{file_id}")
async def api_download_ldx_file(request: Request, file_id: str):
    """Download an LDX file by ID (for exported files)"""
    require_auth(request)
    
    # Simple implementation - assumes file_id contains path info
    # In production, you might want to store exported file metadata
    from pathlib import Path
    from internal.config.settings import settings
    
    # Try to find file in ldx directory
    ldx_dir = settings.DATA_DIR / "motec_files" / "ldx"
    filename = file_id.split("_", 1)[1] if "_" in file_id else file_id
    file_path = ldx_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="application/xml"
    )


# Parameter Defaults Management endpoints
# Parameter defaults endpoints disabled - not needed as of now
# @app.get("/api/parameter-defaults")
# @app.get("/api/parameter-defaults/{parameter_name}")
# @app.post("/api/parameter-defaults")
# @app.put("/api/parameter-defaults/{parameter_name}")
# @app.delete("/api/parameter-defaults/{parameter_name}")


@app.post("/api/reset")
async def api_reset_website(
    request: Request,
    keep_users: bool = Form(True),
    clear_files: bool = Form(False),
    clear_sessions: bool = Form(True)
):
    """
    Reset website - clear all parameters, history, queue, and optionally files/sessions
    Admin only - requires authentication
    """
    await require_role(request, settings.ROLE_ADMIN)
    
    try:
        # Reset database
        db_result = await reset_database(keep_users=keep_users)
        
        result = {
            "status": "success",
            "database": db_result
        }
        
        # Clear MoTeC file metadata if requested
        if clear_files:
            from internal.motec_file_manager import MOTEC_METADATA_FILE
            if MOTEC_METADATA_FILE.exists():
                MOTEC_METADATA_FILE.write_text("[]")
                result["files_metadata_cleared"] = True
            
            # Optionally delete uploaded files
            from pathlib import Path
            motec_dir = Path("data/motec_files")
            if motec_dir.exists():
                import shutil
                for subdir in ["ldx", "ld"]:
                    subdir_path = motec_dir / subdir
                    if subdir_path.exists():
                        for file in subdir_path.glob("*"):
                            if file.is_file() and not file.name.endswith('.bak'):
                                file.unlink()
                result["uploaded_files_deleted"] = True
        
        # Clear sessions if requested
        if clear_sessions:
            from internal.session_tracker import SESSIONS_FILE
            if SESSIONS_FILE.exists():
                SESSIONS_FILE.write_text("[]")
                result["sessions_cleared"] = True
        
        return result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error resetting website: {str(e)}")


# Car Parameters Definitions endpoints
@app.get("/api/car-parameters/definitions")
async def api_get_car_parameter_definitions(
    request: Request,
    subteam: Optional[str] = Query(None, description="Filter by subteam")
):
    """Get all car parameter definitions"""
    require_auth(request)
    
    if subteam:
        from internal.car_parameters import get_parameters_by_subteam
        definitions = get_parameters_by_subteam(subteam)
    else:
        definitions = get_all_car_parameter_definitions()
    
    return {"definitions": definitions}


@app.get("/api/car-parameters/definitions/{parameter_name}")
async def api_get_car_parameter_definition(request: Request, parameter_name: str):
    """Get definition for a specific car parameter"""
    require_auth(request)
    
    definition = get_car_parameter_definition(parameter_name)
    if not definition:
        raise HTTPException(status_code=404, detail="Car parameter definition not found")
    
    return {"definition": definition}


@app.post("/api/car-parameters/definitions")
async def api_create_car_parameter_definition(
    request: Request,
    parameter_name: str = Form(...),
    display_name: str = Form(...),
    subteam: str = Form(...),
    unit: str = Form(...),
    default_value: str = Form(...),
    min_value: Optional[str] = Form(None),
    max_value: Optional[str] = Form(None),
    motec_channel: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """Create or update a car parameter definition"""
    require_auth(request)
    
    success = add_car_parameter_definition(
        parameter_name=parameter_name,
        display_name=display_name,
        subteam=subteam,
        unit=unit,
        default_value=default_value,
        min_value=min_value,
        max_value=max_value,
        motec_channel=motec_channel,
        description=description
    )
    
    if success:
        return {"status": "success", "message": "Car parameter definition created/updated"}
    else:
        raise HTTPException(status_code=400, detail="Failed to create car parameter definition")


@app.delete("/api/car-parameters/definitions/{parameter_name}")
async def api_delete_car_parameter_definition(request: Request, parameter_name: str):
    """Delete a car parameter definition"""
    require_auth(request)
    
    success = remove_car_parameter_definition(parameter_name)
    
    if success:
        return {"status": "success", "message": "Car parameter definition deleted"}
    else:
        raise HTTPException(status_code=404, detail="Car parameter definition not found")


@app.post("/api/car-parameters/initialize")
async def api_initialize_car_parameters(request: Request):
    """Initialize car parameters in database from definitions file"""
    require_auth(request)
    
    initialized = await initialize_car_parameters_in_db()
    
    return {
        "status": "success",
        "initialized": initialized,
        "count": len(initialized),
        "message": f"Initialized {len(initialized)} car parameters in database"
    }


# Session Tracking & Comparison endpoints
@app.get("/api/sessions")
async def api_get_all_sessions(request: Request):
    """Get all sessions with their parameter snapshots and performance data"""
    require_auth(request)
    
    sessions = get_all_sessions()
    return {"sessions": sessions}


@app.get("/api/sessions/{file_id}")
async def api_get_session_by_file(request: Request, file_id: str):
    """Get session record for a specific file"""
    require_auth(request)
    
    session = get_session_by_file_id(file_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"session": session}


@app.get("/api/sessions/compare/by-parameter")
async def api_find_sessions_by_parameter(
    request: Request,
    parameter_name: str = Query(..., description="Parameter name to search for"),
    parameter_value: Optional[str] = Query(None, description="Optional: specific value to match")
):
    """
    Find sessions where a parameter had a specific value
    Example: Find all sessions where tire_pressure_fl was 20.0
    """
    require_auth(request)
    
    sessions = get_sessions_by_parameter(parameter_name, parameter_value)
    return {
        "parameter_name": parameter_name,
        "parameter_value": parameter_value,
        "sessions": sessions,
        "count": len(sessions)
    }


@app.post("/api/sessions/compare")
async def api_compare_sessions(
    request: Request,
    session_ids: List[str]
):
    """
    Compare multiple sessions to see parameter differences and performance
    Useful for analyzing: "Which parameters made us faster?"
    """
    require_auth(request)
    
    comparison = compare_sessions(session_ids)
    
    if "error" in comparison:
        raise HTTPException(status_code=400, detail=comparison["error"])
    
    return comparison


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
