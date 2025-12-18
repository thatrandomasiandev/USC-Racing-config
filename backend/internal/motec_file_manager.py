"""
MoTeC File Manager - Handles .ldx and .ld file uploads and storage
Lightweight file management for parameter system
"""
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from .motec_parser import MotecParser

BASE_DIR = Path(__file__).parent.parent.parent
MOTEC_FILES_DIR = BASE_DIR / "data" / "motec_files"
MOTEC_METADATA_FILE = BASE_DIR / "data" / "motec_files_metadata.json"

# Ensure directories exist
MOTEC_FILES_DIR.mkdir(parents=True, exist_ok=True)
(MOTEC_FILES_DIR / "ldx").mkdir(exist_ok=True)
(MOTEC_FILES_DIR / "ld").mkdir(exist_ok=True)


def load_metadata() -> List[Dict[str, Any]]:
    """Load file metadata from JSON"""
    if not MOTEC_METADATA_FILE.exists():
        return []
    
    try:
        with open(MOTEC_METADATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Ensure we return a list
            if not isinstance(data, list):
                print(f"Warning: Metadata file contains non-list data, returning empty list")
                return []
            return data
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in metadata file: {e}")
        # Return empty list instead of crashing
        return []
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error loading metadata: {e}")
        # Return empty list to prevent crashes
        return []


def save_metadata(metadata: List[Dict[str, Any]]):
    """Save file metadata to JSON"""
    try:
        # Ensure directory exists
        MOTEC_METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(MOTEC_METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, default=str)
    except Exception as e:
        print(f"Error saving metadata: {e}")
        raise


def parse_ldx_metadata(file_path: Path) -> Dict[str, Any]:
    """Parse metadata from LDX file using comprehensive parser"""
    try:
        # Use the comprehensive parser
        parsed = MotecParser.parse_metadata(file_path)
        parsed["uploaded_at"] = datetime.now().isoformat()
        return parsed
    except Exception as e:
        return {
            "file_type": "ldx",
            "filename": file_path.name,
            "file_size": file_path.stat().st_size if file_path.exists() else 0,
            "uploaded_at": datetime.now().isoformat(),
            "parse_error": str(e)
        }


def parse_ld_metadata(file_path: Path) -> Dict[str, Any]:
    """Parse metadata from LD file using comprehensive parser"""
    try:
        # Use the comprehensive parser
        parsed = MotecParser.parse_metadata(file_path)
        parsed["uploaded_at"] = datetime.now().isoformat()
        return parsed
    except Exception as e:
        return {
            "file_type": "ld",
            "filename": file_path.name,
            "file_size": file_path.stat().st_size if file_path.exists() else 0,
            "uploaded_at": datetime.now().isoformat(),
            "parse_error": str(e)
        }


def save_uploaded_file(file_content: bytes, filename: str, file_type: str) -> Dict[str, Any]:
    """Save uploaded file and return metadata"""
    # Determine subdirectory
    subdir = "ldx" if filename.lower().endswith('.ldx') else "ld"
    if file_type == "ldx":
        subdir = "ldx"
    elif file_type == "ld":
        subdir = "ld"
    else:
        # Infer from extension
        if filename.lower().endswith('.ldx'):
            subdir = "ldx"
        else:
            subdir = "ld"
    
    # Save file
    save_path = MOTEC_FILES_DIR / subdir / filename
    with open(save_path, 'wb') as f:
        f.write(file_content)
    
    # Parse metadata
    if file_type == "ldx" or filename.lower().endswith('.ldx'):
        metadata = parse_ldx_metadata(save_path)
    else:
        metadata = parse_ld_metadata(save_path)
    
    metadata["file_path"] = str(save_path.relative_to(BASE_DIR))
    metadata["id"] = f"{datetime.now().timestamp()}_{filename}"
    
    # Save to metadata file
    all_metadata = load_metadata()
    all_metadata.append(metadata)
    save_metadata(all_metadata)
    
    return metadata


def get_all_files() -> List[Dict[str, Any]]:
    """Get all uploaded MoTeC files"""
    return load_metadata()


def get_file_by_id(file_id: str) -> Optional[Dict[str, Any]]:
    """Get file metadata by ID"""
    all_files = load_metadata()
    for file_meta in all_files:
        if file_meta.get("id") == file_id:
            return file_meta
    return None


def delete_file(file_id: str) -> bool:
    """Delete file and its metadata"""
    all_files = load_metadata()
    file_meta = None
    remaining_files = []
    
    for f in all_files:
        if f.get("id") == file_id:
            file_meta = f
        else:
            remaining_files.append(f)
    
    if file_meta:
        # Delete actual file
        file_path_str = file_meta.get("file_path")
        if file_path_str:
            file_path = BASE_DIR / file_path_str
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception:
                    pass  # File might already be deleted
        
        # Update metadata
        save_metadata(remaining_files)
        return True
    
    return False


def get_file_path(file_id: str) -> Optional[Path]:
    """Get full path to file by ID"""
    file_meta = get_file_by_id(file_id)
    if file_meta and file_meta.get("file_path"):
        return BASE_DIR / file_meta["file_path"]
    return None

