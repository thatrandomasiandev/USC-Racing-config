"""
MoTeC file service for reading and writing LDX and LD files
Handles parsing, validation, and file operations
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
import struct

from .models import MotecLdxModel, MotecLdMetadata


class MotecFileService:
    """Service for MoTeC LDX and LD file operations"""
    
    def __init__(self, config: dict):
        """
        Initialize MoTeC file service
        
        Args:
            config: Configuration dictionary from settings.get_motec_config()
        """
        self.config = config
        self.nas_base_path = Path(config.get("nas_base_path", "")) if config.get("nas_base_path") else None
        self.ldx_template_dir = Path(config.get("ldx_template_dir", "config/motec/templates"))
        self.ldx_output_dir = Path(config.get("ldx_output_dir", "data/motec/ldx"))
        self.ld_scan_dir = Path(config.get("ld_scan_dir", "data/motec/ld"))
        
        # Create directories if they don't exist
        self.ldx_template_dir.mkdir(parents=True, exist_ok=True)
        self.ldx_output_dir.mkdir(parents=True, exist_ok=True)
        self.ld_scan_dir.mkdir(parents=True, exist_ok=True)
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve path, checking NAS base path if configured"""
        path_obj = Path(path)
        if path_obj.is_absolute():
            return path_obj
        
        # If NAS base path is configured, try there first
        if self.nas_base_path and self.nas_base_path.exists():
            nas_path = self.nas_base_path / path
            if nas_path.exists():
                return nas_path
        
        # Fall back to relative path
        return Path(path)
    
    def read_ldx(self, path: str) -> MotecLdxModel:
        """
        Read and parse a MoTeC LDX file
        
        Uses Rust parser if available (faster), falls back to Python XML parser.
        
        Args:
            path: Path to LDX file
            
        Returns:
            MotecLdxModel with parsed data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is invalid
        """
        file_path = self._resolve_path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"LDX file not found: {path}")
        
        # Try Rust parser first (faster)
        try:
            from .rust_parser import read_ldx_rust
            rust_result = read_ldx_rust(file_path)
            if rust_result:
                return rust_result
        except ImportError:
            pass  # Rust parser not available, continue with Python
        
        try:
            # LDX files are XML-based
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract workspace/project information
            workspace_name = root.get("Workspace", "Default")
            project_name = root.get("Project", None)
            car_name = root.get("Car", None)
            
            # Parse channels
            channels = []
            for channel_elem in root.findall(".//Channel"):
                channel_data = {
                    "name": channel_elem.get("Name", ""),
                    "units": channel_elem.get("Units", ""),
                    "source": channel_elem.get("Source", "CAN"),
                    "scaling": channel_elem.get("Scaling", None),
                    "math": channel_elem.findtext("Math", None)
                }
                channels.append(channel_data)
            
            # Parse worksheets (if present)
            worksheets = []
            for worksheet_elem in root.findall(".//Worksheet"):
                worksheet_data = {
                    "name": worksheet_elem.get("Name", ""),
                    "type": worksheet_elem.get("Type", ""),
                    "channels": [ch.get("Name") for ch in worksheet_elem.findall(".//Channel")]
                }
                worksheets.append(worksheet_data)
            
            # Extract metadata
            metadata = {}
            for meta_elem in root.findall(".//Metadata"):
                key = meta_elem.get("Key", "")
                value = meta_elem.get("Value", "")
                if key:
                    metadata[key] = value
            
            # Get file timestamps
            stat = file_path.stat()
            created = datetime.fromtimestamp(stat.st_ctime)
            modified = datetime.fromtimestamp(stat.st_mtime)
            
            return MotecLdxModel(
                workspace_name=workspace_name,
                project_name=project_name,
                car_name=car_name,
                channels=channels,
                worksheets=worksheets,
                metadata=metadata,
                created=created,
                modified=modified
            )
            
        except ET.ParseError as e:
            raise ValueError(f"Invalid LDX XML format: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing LDX file: {e}")
    
    def write_ldx(self, path: str, model: MotecLdxModel) -> None:
        """
        Write a MotecLdxModel to an LDX file
        
        Uses safe write pattern: write to temp file first, then replace.
        This prevents corruption if write fails partway through.
        
        Args:
            path: Output path for LDX file
            model: MotecLdxModel to write
            
        Raises:
            ValueError: If validation fails
            IOError: If file write fails
        """
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Validate model before writing
        if not model.workspace_name:
            raise ValueError("Workspace name is required")
        
        # Use temp file for safe writing
        temp_path = file_path.with_suffix('.ldx.tmp')
        
        # Create XML structure
        root = ET.Element("Workspace")
        root.set("Name", model.workspace_name)
        
        if model.project_name:
            root.set("Project", model.project_name)
        if model.car_name:
            root.set("Car", model.car_name)
        
        # Add channels
        channels_elem = ET.SubElement(root, "Channels")
        for channel in model.channels:
            ch_elem = ET.SubElement(channels_elem, "Channel")
            ch_elem.set("Name", channel.get("name", ""))
            ch_elem.set("Units", channel.get("units", ""))
            ch_elem.set("Source", channel.get("source", "CAN"))
            if channel.get("scaling"):
                ch_elem.set("Scaling", str(channel["scaling"]))
            if channel.get("math"):
                math_elem = ET.SubElement(ch_elem, "Math")
                math_elem.text = channel["math"]
        
        # Add worksheets
        if model.worksheets:
            worksheets_elem = ET.SubElement(root, "Worksheets")
            for worksheet in model.worksheets:
                ws_elem = ET.SubElement(worksheets_elem, "Worksheet")
                ws_elem.set("Name", worksheet.get("name", ""))
                ws_elem.set("Type", worksheet.get("type", ""))
                for ch_name in worksheet.get("channels", []):
                    ch_ref = ET.SubElement(ws_elem, "ChannelRef")
                    ch_ref.set("Name", ch_name)
        
        # Add metadata
        if model.metadata:
            metadata_elem = ET.SubElement(root, "Metadata")
            for key, value in model.metadata.items():
                meta_item = ET.SubElement(metadata_elem, "Item")
                meta_item.set("Key", key)
                meta_item.set("Value", str(value))
        
        # Write to temp file first (safe write pattern)
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        try:
            tree.write(temp_path, encoding="utf-8", xml_declaration=True)
            
            # Validate temp file can be read back
            try:
                ET.parse(temp_path)
            except ET.ParseError as e:
                temp_path.unlink(missing_ok=True)  # Clean up invalid temp file
                raise ValueError(f"Generated LDX file is invalid: {e}")
            
            # Replace original with temp file (atomic operation)
            if file_path.exists():
                file_path.unlink()
            temp_path.replace(file_path)
            
        except Exception as e:
            # Clean up temp file on error
            temp_path.unlink(missing_ok=True)
            raise IOError(f"Failed to write LDX file: {e}")
    
    def read_ld_metadata(self, path: str) -> MotecLdMetadata:
        """
        Read metadata from a MoTeC LD file
        
        LD files are binary format. This extracts basic metadata without
        reading the entire file.
        
        Uses Rust parser if available (faster header-only parsing).
        
        Args:
            path: Path to LD file
            
        Returns:
            MotecLdMetadata with file information
        """
        file_path = self._resolve_path(path)
        
        metadata = MotecLdMetadata(
            file_path=str(file_path),
            file_size=0,
            valid=False
        )
        
        if not file_path.exists():
            metadata.error = f"LD file not found: {path}"
            return metadata
        
        # Try Rust parser first (faster, header-only)
        try:
            from .rust_parser import read_ld_metadata_rust
            rust_result = read_ld_metadata_rust(file_path)
            if rust_result:
                return rust_result
        except ImportError:
            pass  # Rust parser not available, continue with Python
        
        try:
            stat = file_path.stat()
            metadata.file_size = stat.st_size
            
            # LD files have a header structure
            # This is a simplified parser - full implementation would need
            # MoTeC LD file format specification
            with open(file_path, "rb") as f:
                # Read header (first 512 bytes typically contain metadata)
                header = f.read(512)
                
                # Try to extract basic info
                # Note: Actual LD format parsing requires MoTeC documentation
                # This is a placeholder that can be extended
                
                # For now, mark as valid if file exists and has reasonable size
                if metadata.file_size > 0:
                    metadata.valid = True
                    metadata.start_time = datetime.fromtimestamp(stat.st_mtime)
                    
                    # Try to extract channel names from header if possible
                    # This would require full LD format knowledge
                    # Placeholder: empty channels list
                    metadata.channels = []
            
        except Exception as e:
            metadata.error = f"Error reading LD file: {str(e)}"
            metadata.valid = False
        
        return metadata
    
    def validate_ld(self, path: str) -> bool:
        """
        Validate that an LD file exists and is readable
        
        Args:
            path: Path to LD file
            
        Returns:
            True if file is valid, False otherwise
        """
        file_path = self._resolve_path(path)
        
        if not file_path.exists():
            return False
        
        if not file_path.is_file():
            return False
        
        # Check file size (LD files should have minimum size)
        if file_path.stat().st_size < 512:
            return False
        
        return True
    
    def discover_ld_files(self, directory: Optional[str] = None, pattern: Optional[str] = None) -> List[str]:
        """
        Discover LD files in a directory
        
        Args:
            directory: Directory to scan (defaults to configured scan dir)
            pattern: Glob pattern (defaults to configured pattern)
            
        Returns:
            List of LD file paths
        """
        scan_dir = Path(directory) if directory else self.ld_scan_dir
        glob_pattern = pattern or self.config.get("ld_glob_pattern", "*.ld")
        
        if not scan_dir.exists():
            return []
        
        # Also check NAS path if configured
        ld_files = []
        
        # Scan configured directory
        for ld_file in scan_dir.glob(glob_pattern):
            if ld_file.is_file():
                ld_files.append(str(ld_file))
        
        # Scan NAS if configured
        if self.nas_base_path and self.nas_base_path.exists():
            nas_scan_dir = self.nas_base_path / scan_dir.name if scan_dir.is_relative_to(Path.cwd()) else self.nas_base_path
            if nas_scan_dir.exists():
                for ld_file in nas_scan_dir.glob(glob_pattern):
                    if ld_file.is_file() and str(ld_file) not in ld_files:
                        ld_files.append(str(ld_file))
        
        return sorted(ld_files)

