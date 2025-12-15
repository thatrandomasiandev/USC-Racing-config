"""
Optional Rust parser integration for MoTeC files
Falls back to Python implementation if Rust parser not available
"""

from pathlib import Path
from typing import Optional
from .models import MotecLdxModel, MotecLdMetadata
from datetime import datetime

# Try to import Rust parser
try:
    import motec_parser
    RUST_PARSER_AVAILABLE = True
except ImportError:
    RUST_PARSER_AVAILABLE = False
    motec_parser = None


def read_ldx_rust(file_path: Path) -> Optional[MotecLdxModel]:
    """
    Read LDX file using Rust parser (if available)
    
    Args:
        file_path: Path to LDX file
        
    Returns:
        MotecLdxModel if successful, None if parser not available
    """
    if not RUST_PARSER_AVAILABLE:
        return None
    
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        
        ldx = motec_parser.parse_ldx(data)
        
        # Convert Rust LdxFile to Python MotecLdxModel
        stat = file_path.stat()
        created = datetime.fromtimestamp(stat.st_ctime)
        modified = datetime.fromtimestamp(stat.st_mtime)
        
        return MotecLdxModel(
            workspace_name=ldx.workspace_name,
            project_name=ldx.project_name,
            car_name=ldx.car_name,
            channels=[
                {
                    "name": ch.name,
                    "units": ch.units or "",
                    "source": ch.source or "CAN",
                    "scaling": ch.scaling,
                    "math": ch.math
                }
                for ch in ldx.channels
            ],
            worksheets=[
                {
                    "name": ws.name,
                    "type": ws.worksheet_type or "",
                    "channels": [ref.name for ref in ws.channel_refs]
                }
                for ws in ldx.worksheets
            ],
            metadata={
                item.key: item.value
                for item in ldx.metadata
            },
            created=created,
            modified=modified
        )
    except Exception as e:
        print(f"Warning: Rust parser failed, falling back to Python: {e}")
        return None


def read_ld_metadata_rust(file_path: Path) -> Optional[MotecLdMetadata]:
    """
    Read LD file metadata using Rust parser (if available)
    Fast header-only parsing without loading full file
    
    Args:
        file_path: Path to LD file
        
    Returns:
        MotecLdMetadata if successful, None if parser not available
    """
    if not RUST_PARSER_AVAILABLE:
        return None
    
    try:
        with open(file_path, 'rb') as f:
            # Only read header (first 512 bytes for fast parsing)
            data = f.read(512)
        
        metadata = motec_parser.parse_ld_metadata(data)
        
        stat = file_path.stat()
        
        return MotecLdMetadata(
            file_path=str(file_path),
            file_size=metadata.file_size,
            sample_rate=metadata.sample_rate,
            start_time=datetime.fromtimestamp(stat.st_mtime),
            channels=metadata.channel_names,
            valid=metadata.valid
        )
    except Exception as e:
        print(f"Warning: Rust parser failed, falling back to Python: {e}")
        return None

