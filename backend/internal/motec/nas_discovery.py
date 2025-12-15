"""
NAS Discovery Service - Auto-scan and discover NAS for MoTeC files
Safe, non-blocking, trackside-friendly implementation
"""

import os
import time
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import threading
import logging

logger = logging.getLogger(__name__)


class NasDiscoveryService:
    """Service for discovering NAS and MoTeC files"""
    
    def __init__(self, config: dict):
        """
        Initialize NAS discovery service
        
        Args:
            config: Configuration dictionary from settings.get_motec_config()
        """
        self.config = config
        self.nas_base_path = config.get("nas_base_path", "")
        self.ld_glob_pattern = config.get("ld_glob_pattern", "*.ld")
        self.ldx_glob_pattern = "*.ldx"
        self.ld_scan_dir = Path(config.get("ld_scan_dir", "data/motec/ld"))
        self.ldx_output_dir = Path(config.get("ldx_output_dir", "data/motec/ldx"))
        
        # Discovery settings
        self.discovery_enabled = config.get("nas_discovery", {}).get("enabled", True)
        self.scan_on_startup = config.get("nas_discovery", {}).get("scan_on_startup", True)
        self.scan_interval_ms = config.get("nas_discovery", {}).get("scan_interval_ms", 30000)
        
        # Auto-populate settings
        self.auto_populate_enabled = config.get("auto_populate", {}).get("enabled", True)
        self.max_files_per_scan = config.get("auto_populate", {}).get("max_files_per_scan", 1000)
        self.inference_mode = config.get("auto_populate", {}).get("inference_mode", "conservative")
        
        # State
        self.nas_status: Dict = {
            "connected": False,
            "path": None,
            "last_scan": None,
            "error": None
        }
        self.discovered_ld_files: List[Dict] = []
        self.discovered_ldx_files: List[Dict] = []
        self.scan_lock = threading.Lock()
        self.scan_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Start background scanning if enabled
        if self.discovery_enabled and self.scan_on_startup:
            self.start_background_scanning()
    
    def discover_nas_path(self) -> Optional[str]:
        """
        Attempt to discover NAS path
        
        Tries multiple methods:
        1. User-configured path (takes precedence)
        2. Common NAS mount points
        3. Network shares
        
        Returns:
            NAS path if found, None otherwise
        """
        # Method 1: User-configured path (always takes precedence)
        if self.nas_base_path:
            if self._validate_nas_path(self.nas_base_path):
                return self.nas_base_path
            else:
                logger.warning(f"Configured NAS path is not accessible: {self.nas_base_path}")
        
        # Method 2: Common mount points (trackside-friendly)
        common_paths = [
            "/mnt/nas",
            "/mnt/nas/motec",
            "/media/nas",
            "/media/nas/motec",
            "/Volumes/NAS",  # macOS
            "/Volumes/NAS/motec",
        ]
        
        for path in common_paths:
            if self._validate_nas_path(path):
                logger.info(f"Auto-discovered NAS at: {path}")
                return path
        
        # Method 3: Check if scan_dir is on NAS (if it's an absolute path)
        if self.ld_scan_dir.is_absolute() and self.ld_scan_dir.exists():
            parent = self.ld_scan_dir.parent
            if self._validate_nas_path(str(parent)):
                return str(parent)
        
        return None
    
    def _validate_nas_path(self, path: str) -> bool:
        """
        Validate that a NAS path is accessible
        
        Args:
            path: Path to validate
            
        Returns:
            True if path is accessible, False otherwise
        """
        try:
            p = Path(path)
            if not p.exists():
                return False
            
            # Check if readable
            if not os.access(p, os.R_OK):
                return False
            
            # Check if it's a directory
            if not p.is_dir():
                return False
            
            return True
        except Exception as e:
            logger.debug(f"NAS path validation failed for {path}: {e}")
            return False
    
    def scan_for_files(self, force: bool = False) -> Dict:
        """
        Scan for LD and LDX files
        
        Args:
            force: Force scan even if recently scanned
            
        Returns:
            Dictionary with scan results and status
        """
        with self.scan_lock:
            # Check if we should skip scan (recently scanned)
            if not force and self.nas_status.get("last_scan"):
                last_scan_time = self.nas_status["last_scan"]
                time_since_scan = (datetime.now() - last_scan_time).total_seconds() * 1000
                if time_since_scan < (self.scan_interval_ms / 2):  # Don't scan if less than half interval
                    return {
                        "status": "cached",
                        "nas": self.nas_status,
                        "ld_files": self.discovered_ld_files,
                        "ldx_files": self.discovered_ldx_files,
                        "message": "Using cached scan results"
                    }
            
            # Discover NAS path
            nas_path = self.discover_nas_path()
            
            if not nas_path:
                self.nas_status = {
                    "connected": False,
                    "path": None,
                    "last_scan": datetime.now(),
                    "error": "NAS not found or not accessible"
                }
                return {
                    "status": "error",
                    "nas": self.nas_status,
                    "ld_files": [],
                    "ldx_files": [],
                    "message": "NAS not accessible. Check path configuration."
                }
            
            # Update NAS status
            self.nas_status = {
                "connected": True,
                "path": nas_path,
                "last_scan": datetime.now(),
                "error": None
            }
            
            # Scan for files
            try:
                ld_files = self._scan_ld_files(nas_path)
                ldx_files = self._scan_ldx_files(nas_path)
                
                self.discovered_ld_files = ld_files
                self.discovered_ldx_files = ldx_files
                
                return {
                    "status": "success",
                    "nas": self.nas_status,
                    "ld_files": ld_files,
                    "ldx_files": ldx_files,
                    "message": f"Found {len(ld_files)} LD files and {len(ldx_files)} LDX files"
                }
            except Exception as e:
                logger.error(f"Error scanning NAS: {e}")
                self.nas_status["error"] = str(e)
                return {
                    "status": "error",
                    "nas": self.nas_status,
                    "ld_files": self.discovered_ld_files,  # Keep previous results
                    "ldx_files": self.discovered_ldx_files,
                    "message": f"Scan error: {str(e)}"
                }
    
    def _scan_ld_files(self, base_path: Path) -> List[Dict]:
        """Scan for LD files"""
        ld_files = []
        base = Path(base_path)
        
        # Scan in configured scan directory
        scan_dirs = [
            base / self.ld_scan_dir.name if self.ld_scan_dir.is_relative() else self.ld_scan_dir,
            base / "ld",
            base / "data" / "ld",
            base  # Also scan root
        ]
        
        for scan_dir in scan_dirs:
            if not scan_dir.exists():
                continue
            
            try:
                pattern = self.ld_glob_pattern
                found_files = list(scan_dir.rglob(pattern))
                
                for file_path in found_files[:self.max_files_per_scan]:
                    try:
                        stat = file_path.stat()
                        ld_files.append({
                            "file_path": str(file_path),
                            "name": file_path.name,
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "suggested_session": self._infer_session_from_filename(file_path.name),
                            "suggested_car": self._infer_car_from_path(file_path),
                            "valid": True
                        })
                    except Exception as e:
                        logger.debug(f"Error processing LD file {file_path}: {e}")
                        ld_files.append({
                            "file_path": str(file_path),
                            "name": file_path.name,
                            "valid": False,
                            "error": str(e)
                        })
            except Exception as e:
                logger.warning(f"Error scanning directory {scan_dir}: {e}")
        
        return ld_files
    
    def _scan_ldx_files(self, base_path: Path) -> List[Dict]:
        """Scan for LDX files"""
        ldx_files = []
        base = Path(base_path)
        
        # Scan in configured output directory and common locations
        scan_dirs = [
            base / self.ldx_output_dir.name if self.ldx_output_dir.is_relative() else self.ldx_output_dir,
            base / "ldx",
            base / "data" / "ldx",
            base  # Also scan root
        ]
        
        for scan_dir in scan_dirs:
            if not scan_dir.exists():
                continue
            
            try:
                found_files = list(scan_dir.rglob(self.ldx_glob_pattern))
                
                for file_path in found_files[:self.max_files_per_scan]:
                    try:
                        stat = file_path.stat()
                        ldx_files.append({
                            "file_path": str(file_path),
                            "name": file_path.name,
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "suggested_car": self._infer_car_from_path(file_path),
                            "managed_by_app": self._is_managed_by_app(file_path)
                        })
                    except Exception as e:
                        logger.debug(f"Error processing LDX file {file_path}: {e}")
            except Exception as e:
                logger.warning(f"Error scanning directory {scan_dir}: {e}")
        
        return ldx_files
    
    def _infer_session_from_filename(self, filename: str) -> Optional[str]:
        """
        Infer session ID from filename
        
        Conservative inference mode:
        - Looks for date patterns: YYYYMMDD, YYYY-MM-DD
        - Looks for session identifiers: session_*, *_session_*
        
        Returns:
            Suggested session ID or None
        """
        if self.inference_mode == "conservative":
            # Only infer if pattern is very clear
            import re
            
            # Date pattern: YYYYMMDD or YYYY-MM-DD
            date_match = re.search(r'(\d{4}[-]?\d{2}[-]?\d{2})', filename)
            if date_match:
                date_str = date_match.group(1).replace('-', '')
                # Look for session identifier
                session_match = re.search(r'session[_-]?(\w+)', filename, re.IGNORECASE)
                if session_match:
                    return f"{date_str}_{session_match.group(1)}"
                return f"session_{date_str}"
            
            # Session pattern: session_XXX
            session_match = re.search(r'session[_-]?(\w+)', filename, re.IGNORECASE)
            if session_match:
                return session_match.group(1)
        
        return None
    
    def _infer_car_from_path(self, file_path: Path) -> Optional[str]:
        """
        Infer car ID from file path
        
        Conservative inference:
        - Looks for car_* directories
        - Looks for car identifiers in path
        
        Returns:
            Suggested car ID or None
        """
        if self.inference_mode == "conservative":
            import re
            
            # Check path components for car_* pattern
            for part in file_path.parts:
                car_match = re.search(r'car[_-]?(\w+)', part, re.IGNORECASE)
                if car_match:
                    return car_match.group(1)
        
        return None
    
    def _is_managed_by_app(self, file_path: Path) -> bool:
        """
        Check if LDX file is managed by this app
        
        Returns:
            True if file is in app-managed directory
        """
        # Check if file is in output directory
        try:
            file_path.resolve().relative_to(self.ldx_output_dir.resolve())
            return True
        except ValueError:
            return False
    
    def start_background_scanning(self):
        """Start background scanning thread"""
        if self.running:
            return
        
        self.running = True
        self.scan_thread = threading.Thread(target=self._background_scan_loop, daemon=True)
        self.scan_thread.start()
        logger.info("Started background NAS scanning")
    
    def stop_background_scanning(self):
        """Stop background scanning thread"""
        self.running = False
        if self.scan_thread:
            self.scan_thread.join(timeout=5)
        logger.info("Stopped background NAS scanning")
    
    def _background_scan_loop(self):
        """Background scanning loop"""
        while self.running:
            try:
                self.scan_for_files()
            except Exception as e:
                logger.error(f"Error in background scan: {e}")
            
            # Sleep for scan interval
            time.sleep(self.scan_interval_ms / 1000.0)
    
    def get_status(self) -> Dict:
        """Get current discovery status"""
        return {
            "nas": self.nas_status,
            "ld_files_count": len(self.discovered_ld_files),
            "ldx_files_count": len(self.discovered_ldx_files),
            "last_scan": self.nas_status.get("last_scan"),
            "discovery_enabled": self.discovery_enabled,
            "auto_populate_enabled": self.auto_populate_enabled
        }


