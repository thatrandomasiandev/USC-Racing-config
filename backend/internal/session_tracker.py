"""
Session Tracker - Links uploaded MoTeC files to parameter snapshots
Tracks which parameters were active during each session for performance analysis
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).parent.parent.parent
SESSIONS_FILE = BASE_DIR / "data" / "sessions.json"


def ensure_sessions_file():
    """Ensure the sessions file exists"""
    SESSIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not SESSIONS_FILE.exists():
        with open(SESSIONS_FILE, 'w') as f:
            json.dump([], f)


def load_sessions() -> List[Dict[str, Any]]:
    """Load all sessions from JSON file"""
    ensure_sessions_file()
    try:
        with open(SESSIONS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_sessions(sessions: List[Dict[str, Any]]):
    """Save sessions to JSON file"""
    ensure_sessions_file()
    with open(SESSIONS_FILE, 'w') as f:
        json.dump(sessions, f, indent=2, default=str)


def create_session_from_file(
    file_id: str,
    filename: str,
    file_type: str,
    parameters_snapshot: List[Dict[str, Any]],
    session_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a session record linking an uploaded file to current parameter values
    
    Args:
        file_id: ID of uploaded file
        filename: Name of the file
        file_type: 'ldx' or 'ld'
        parameters_snapshot: Current parameter values when file was uploaded
        session_data: Extracted session data (lap times, etc.)
    
    Returns:
        Session record dictionary
    """
    sessions = load_sessions()
    
    session = {
        "session_id": f"{datetime.now().timestamp()}_{filename}",
        "file_id": file_id,
        "filename": filename,
        "file_type": file_type,
        "uploaded_at": datetime.now().isoformat(),
        "parameters_snapshot": parameters_snapshot,  # What parameters were active
        "session_data": session_data or {}  # Performance data from file
    }
    
    sessions.append(session)
    save_sessions(sessions)
    
    return session


def get_session_by_file_id(file_id: str) -> Optional[Dict[str, Any]]:
    """Get session record by file ID"""
    sessions = load_sessions()
    return next((s for s in sessions if s.get("file_id") == file_id), None)


def get_all_sessions() -> List[Dict[str, Any]]:
    """Get all sessions, sorted by upload time (newest first)"""
    sessions = load_sessions()
    return sorted(sessions, key=lambda x: x.get("uploaded_at", ""), reverse=True)


def get_sessions_by_parameter(
    parameter_name: str,
    parameter_value: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Find sessions where a specific parameter had a specific value
    Useful for comparing: "Which sessions had tire_pressure_fl = 20.0?"
    """
    sessions = get_all_sessions()
    matching_sessions = []
    
    for session in sessions:
        params = session.get("parameters_snapshot", [])
        for param in params:
            if param.get("parameter_name") == parameter_name:
                if parameter_value is None or param.get("current_value") == parameter_value:
                    matching_sessions.append(session)
                break
    
    return matching_sessions


def compare_sessions(session_ids: List[str]) -> Dict[str, Any]:
    """
    Compare multiple sessions to see parameter differences and performance
    """
    sessions = load_sessions()
    session_map = {s["session_id"]: s for s in sessions}
    
    selected_sessions = [session_map[sid] for sid in session_ids if sid in session_map]
    
    if len(selected_sessions) < 2:
        return {"error": "Need at least 2 sessions to compare"}
    
    # Extract all unique parameter names
    all_param_names = set()
    for session in selected_sessions:
        for param in session.get("parameters_snapshot", []):
            all_param_names.add(param["parameter_name"])
    
    # Compare parameter values
    parameter_comparison = {}
    for param_name in all_param_names:
        values = []
        for session in selected_sessions:
            for param in session.get("parameters_snapshot", []):
                if param["parameter_name"] == param_name:
                    values.append({
                        "session_id": session["session_id"],
                        "filename": session["filename"],
                        "value": param["current_value"]
                    })
                    break
        parameter_comparison[param_name] = values
    
    # Extract performance data for comparison
    performance_comparison = {}
    for session in selected_sessions:
        session_data = session.get("session_data", {})
        perf_key = f"{session['filename']} ({session['session_id']})"
        performance_comparison[perf_key] = session_data
    
    return {
        "sessions": selected_sessions,
        "parameter_comparison": parameter_comparison,
        "performance_comparison": performance_comparison
    }

