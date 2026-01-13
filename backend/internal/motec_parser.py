"""
MoTeC File Parser - Comprehensive parser for .ldx and .ld files
Handles XML-based LDX files and binary LD files
"""
import struct
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import xml.etree.ElementTree as ET
from .config.settings import settings


class MotecLdxParser:
    """Parser for MoTeC LDX (XML-based workspace) files"""
    
    @staticmethod
    def parse(file_path: Path) -> Dict[str, Any]:
        """Parse an LDX file and extract all available information"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            result = {
                "file_type": "ldx",
                "filename": file_path.name,
                "file_size": file_path.stat().st_size,
                "parsed_at": datetime.now().isoformat(),
                "version": root.get("Version", ""),
                "locale": root.get("Locale", ""),
                "default_locale": root.get("DefaultLocale", ""),
            }
            
            # Parse Details section
            details = root.find(".//Details")
            if details is not None:
                result["details"] = {}
                for string_elem in details.findall("String"):
                    key = string_elem.get("Id", "")
                    value = string_elem.get("Value", "")
                    if key:
                        result["details"][key] = value
            
            # Parse MarkerGroups and Markers
            marker_groups = root.findall(".//MarkerGroup")
            if marker_groups:
                result["marker_groups"] = []
                total_markers = 0
                for mg in marker_groups:
                    group_name = mg.get("Name", "")
                    group_index = mg.get("Index", "")
                    markers = []
                    
                    for marker in mg.findall("Marker"):
                        marker_data = {
                            "name": marker.get("Name", ""),
                            "version": marker.get("Version", ""),
                            "class_name": marker.get("ClassName", ""),
                            "flags": marker.get("Flags", ""),
                            "time": marker.get("Time", ""),
                        }
                        markers.append(marker_data)
                        total_markers += 1
                    
                    result["marker_groups"].append({
                        "name": group_name,
                        "index": group_index,
                        "marker_count": len(markers),
                        "markers": markers
                    })
                
                result["total_markers"] = total_markers
            
            # Parse Layers
            layers = root.findall(".//Layer")
            if layers:
                result["layer_count"] = len(layers)
            
            # Parse RangeBlock if present
            range_blocks = root.findall(".//RangeBlock")
            if range_blocks:
                result["has_range_block"] = True
            
            return result
            
        except Exception as e:
            return {
                "file_type": "ldx",
                "filename": file_path.name,
                "file_size": file_path.stat().st_size if file_path.exists() else 0,
                "parsed_at": datetime.now().isoformat(),
                "parse_error": str(e),
                "error_type": type(e).__name__
            }


class MotecLdParser:
    """Parser for MoTeC LD (binary logged data) files"""
    
    @staticmethod
    def _extract_strings(data: bytes, min_length: int = 3) -> List[str]:
        """Extract readable strings from binary data"""
        strings = []
        current_string = b""
        
        for byte in data:
            if 32 <= byte <= 126:  # Printable ASCII
                current_string += bytes([byte])
            else:
                if len(current_string) >= min_length:
                    try:
                        strings.append(current_string.decode('utf-8', errors='ignore').strip())
                    except:
                        pass
                current_string = b""
        
        # Add final string
        if len(current_string) >= min_length:
            try:
                strings.append(current_string.decode('utf-8', errors='ignore').strip())
            except:
                pass
        
        return strings
    
    @staticmethod
    def _parse_date_time(text: str) -> Optional[Dict[str, str]]:
        """Try to extract date and time from text"""
        # Pattern: DD/MM/YYYY HH:MM:SS
        date_pattern = r'(\d{2}/\d{2}/\d{4})'
        time_pattern = r'(\d{2}:\d{2}:\d{2})'
        
        date_match = re.search(date_pattern, text)
        time_match = re.search(time_pattern, text)
        
        result = {}
        if date_match:
            result["date"] = date_match.group(1)
        if time_match:
            result["time"] = time_match.group(1)
        
        return result if result else None
    
    @staticmethod
    def _extract_session_info(strings: List[str]) -> Dict[str, Any]:
        """Extract session information from extracted strings"""
        info = {}
        
        # Common patterns
        date_pattern = re.compile(r'\d{2}/\d{2}/\d{4}')
        time_pattern = re.compile(r'\d{2}:\d{2}:\d{2}')
        
        for s in strings:
            # Look for date
            if date_pattern.search(s) and "date" not in info:
                date_match = date_pattern.search(s)
                if date_match:
                    info["date"] = date_match.group()
            
            # Look for time
            if time_pattern.search(s) and "time" not in info:
                time_match = time_pattern.search(s)
                if time_match:
                    info["time"] = time_match.group()
            
            # Look for device/model names (common MoTeC patterns)
            if any(x in s.upper() for x in ['SCR', 'M1', 'M150', 'GPRP', 'PDM']):
                if "device_name" not in info:
                    info["device_name"] = s
            
            # Look for track names (common patterns)
            if any(x in s for x in ['Track', 'Raceway', 'Speedway', 'Circuit', 'Pomona']):
                if "track_name" not in info:
                    info["track_name"] = s
            
            # Look for driver names (usually short strings without special chars)
            if len(s) > 2 and len(s) < 30 and s.replace(' ', '').isalnum():
                # Skip dates, times, and device names
                if not (date_pattern.search(s) or time_pattern.search(s) or 
                       any(x in s.upper() for x in ['SCR', 'M1', 'GPRP', 'PDM', 'GPS'])):
                    if "driver_name" not in info or len(s) > len(info.get("driver_name", "")):
                        info["driver_name"] = s
        
        return info
    
    @staticmethod
    def parse(file_path: Path, header_size: Optional[int] = None) -> Dict[str, Any]:
        """Parse an LD file and extract metadata from header"""
        try:
            stat = file_path.stat()
            result = {
                "file_type": "ld",
                "filename": file_path.name,
                "file_size": stat.st_size,
                "parsed_at": datetime.now().isoformat(),
            }
            
            # Use configured header size
            ld_header_size = header_size or settings.MOTEC_LD_HEADER_SIZE
            
            with open(file_path, 'rb') as f:
                # Read header section
                header = f.read(ld_header_size)
                
                # Extract all readable strings from header
                strings = MotecLdParser._extract_strings(header, min_length=3)
                
                # Extract session information
                session_info = MotecLdParser._extract_session_info(strings)
                result.update(session_info)
                
                # Store raw strings for reference (limited to avoid huge output)
                result["extracted_strings"] = strings[:50]  # Limit to first 50 strings
                
                # Try to parse structured header (if we know the format)
                # MoTeC LD files typically have:
                # - File signature/version at offset 0
                # - Metadata strings at various offsets
                # - Channel definitions after header
                
                # Read first few bytes as potential file signature
                f.seek(0)
                signature = f.read(4)
                if len(signature) >= 4:
                    # Try to interpret as integers
                    try:
                        # Could be version info or file type marker
                        vals = struct.unpack('<4B', signature)
                        result["header_signature"] = [hex(v) for v in vals]
                    except:
                        pass
            
            return result
            
        except Exception as e:
            return {
                "file_type": "ld",
                "filename": file_path.name,
                "file_size": file_path.stat().st_size if file_path.exists() else 0,
                "parsed_at": datetime.now().isoformat(),
                "parse_error": str(e),
                "error_type": type(e).__name__
            }


class MotecParser:
    """Main parser interface for MoTeC files"""
    
    @staticmethod
    def parse_file(file_path: Path) -> Dict[str, Any]:
        """Parse a MoTeC file (.ldx or .ld)"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() == settings.MOTEC_LDX_EXTENSION.lower():
            return MotecLdxParser.parse(file_path)
        elif file_path.suffix.lower() == settings.MOTEC_LD_EXTENSION.lower():
            return MotecLdParser.parse(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
    
    @staticmethod
    def parse_metadata(file_path: Path) -> Dict[str, Any]:
        """Parse file and return simplified metadata for storage"""
        full_parse = MotecParser.parse_file(file_path)
        
        # Extract key metadata fields
        metadata = {
            "file_type": full_parse.get("file_type", "unknown"),
            "filename": full_parse.get("filename", ""),
            "file_size": full_parse.get("file_size", 0),
            "parsed_at": full_parse.get("parsed_at", datetime.now().isoformat()),
        }
        
        # LDX-specific metadata
        if full_parse.get("file_type") == "ldx":
            if "details" in full_parse:
                metadata.update(full_parse["details"])
            if "total_markers" in full_parse:
                metadata["total_markers"] = full_parse["total_markers"]
            if "marker_groups" in full_parse:
                metadata["marker_group_count"] = len(full_parse["marker_groups"])
        
        # LD-specific metadata
        elif full_parse.get("file_type") == "ld":
            if "date" in full_parse:
                metadata["date"] = full_parse["date"]
            if "time" in full_parse:
                metadata["time"] = full_parse["time"]
            if "driver_name" in full_parse:
                metadata["driver_name"] = full_parse["driver_name"]
            if "device_name" in full_parse:
                metadata["device_name"] = full_parse["device_name"]
            if "track_name" in full_parse:
                metadata["track_name"] = full_parse["track_name"]
        
        # Add any parse errors
        if "parse_error" in full_parse:
            metadata["parse_error"] = full_parse["parse_error"]
        
        return metadata

