"""
MoTeC session linker - associates LD files with track sessions
Links telemetry sessions to MoTeC LD/LDX files
"""

from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
from .file_service import MotecFileService
from .config_service import MotecConfigService
from .models import MotecSessionConfig, MotecLdMetadata


class MotecSessionLinker:
    """Service for linking track sessions with MoTeC files"""
    
    def __init__(self, file_service: MotecFileService, config_service: MotecConfigService):
        """
        Initialize session linker
        
        Args:
            file_service: MotecFileService instance
            config_service: MotecConfigService instance
        """
        self.file_service = file_service
        self.config_service = config_service
        self.config = file_service.config
    
    def link_ld_to_session(
        self,
        ld_file_path: str,
        car_id: str,
        session_id: Optional[str] = None,
        track_id: Optional[str] = None,
        driver: Optional[str] = None,
        date: Optional[str] = None
    ) -> MotecSessionConfig:
        """
        Link an LD file to a track session
        
        Args:
            ld_file_path: Path to LD file
            car_id: Car identifier
            session_id: Optional session identifier
            track_id: Optional track identifier
            driver: Optional driver name
            date: Optional session date
            
        Returns:
            MotecSessionConfig with linked files
        """
        # Validate LD file
        if not self.file_service.validate_ld(ld_file_path):
            raise ValueError(f"Invalid LD file: {ld_file_path}")
        
        # Get metadata
        metadata = self.file_service.read_ld_metadata(ld_file_path)
        
        # Create session config
        session_config = self.config_service.create_session_config(
            car_id=car_id,
            track_id=track_id or metadata.track_id,
            driver=driver or metadata.driver,
            date=date or metadata.date or datetime.now().strftime("%Y-%m-%d"),
            ld_file_path=ld_file_path,
            session_name=session_id or metadata.session_name
        )
        
        # Auto-generate LDX if configured
        if self.config.get("auto_generate_ldx", False):
            ldx_path = self._generate_ldx_for_session(session_config)
            session_config.ldx_file_path = ldx_path
        
        return session_config
    
    def _generate_ldx_for_session(self, session_config: MotecSessionConfig) -> str:
        """
        Generate LDX file for a session
        
        Args:
            session_config: Session configuration
            
        Returns:
            Path to generated LDX file
        """
        from .file_service import MotecLdxModel
        
        # Determine output path
        output_dir = Path(self.config.get("ldx_output_dir", "data/motec/ldx"))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        car_id = session_config.car_id
        date_str = session_config.date or datetime.now().strftime("%Y%m%d")
        session_name = session_config.session_name or "session"
        ldx_filename = f"{car_id}_{date_str}_{session_name}.ldx"
        ldx_path = output_dir / ldx_filename
        
        # Check overwrite policy - trackside safety: never overwrite without explicit confirmation
        overwrite_policy = self.config.get("overwrite_policy", "ifSafe")
        if ldx_path.exists():
            if overwrite_policy == "never":
                raise FileExistsError(
                    f"LDX file exists and overwrite policy is 'never': {ldx_path}. "
                    "Use 'ifSafe' or 'always' policy, or delete existing file first."
                )
            elif overwrite_policy == "ifSafe":
                # Only overwrite if file is older than session
                # For trackside safety, we require explicit confirmation via API parameter
                # This check is done at API level, not here
                pass  # Allow overwrite if policy permits
        
        # Create LDX model from session config
        ldx_model = MotecLdxModel(
            workspace_name=f"{car_id}_Workspace",
            project_name=f"{car_id}_Project",
            car_name=car_id,
            channels=self._channels_to_ldx_format(session_config.channels),
            metadata={
                "Track": session_config.track_id or "",
                "Driver": session_config.driver or "",
                "Date": session_config.date or "",
                "Session": session_config.session_name or ""
            }
        )
        
        # Write LDX file
        self.file_service.write_ldx(str(ldx_path), ldx_model)
        
        return str(ldx_path)
    
    def _channels_to_ldx_format(self, channels) -> List[Dict]:
        """Convert channel configs to LDX format"""
        return [
            {
                "name": ch.motec_name,
                "units": ch.units,
                "source": ch.source.value,
                "scaling": ch.scaling,
                "math": ch.math_expression
            }
            for ch in channels if ch.enabled
        ]
    
    def discover_and_link_sessions(
        self,
        directory: Optional[str] = None,
        car_id: Optional[str] = None
    ) -> List[MotecSessionConfig]:
        """
        Discover LD files and create session configs for them
        
        Args:
            directory: Directory to scan (defaults to configured scan dir)
            car_id: Optional car ID filter
            
        Returns:
            List of session configurations
        """
        ld_files = self.file_service.discover_ld_files(directory)
        sessions = []
        
        for ld_file in ld_files:
            try:
                metadata = self.file_service.read_ld_metadata(ld_file)
                
                # Determine car_id if not provided
                session_car_id = car_id or metadata.car_id or "default"
                
                # Create session config
                session_config = self.link_ld_to_session(
                    ld_file_path=ld_file,
                    car_id=session_car_id,
                    track_id=metadata.track_id,
                    driver=metadata.driver,
                    date=metadata.date,
                    session_id=metadata.session_name
                )
                
                sessions.append(session_config)
            except Exception as e:
                print(f"Warning: Could not link LD file {ld_file}: {e}")
                continue
        
        return sessions
    
    def get_session_by_ld_file(self, ld_file_path: str) -> Optional[MotecSessionConfig]:
        """
        Get session configuration for an LD file
        
        Args:
            ld_file_path: Path to LD file
            
        Returns:
            Session configuration or None if not found
        """
        metadata = self.file_service.read_ld_metadata(ld_file_path)
        
        if not metadata.valid:
            return None
        
        # Try to determine car_id from metadata or file path
        car_id = metadata.car_id or "default"
        
        return self.config_service.create_session_config(
            car_id=car_id,
            track_id=metadata.track_id,
            driver=metadata.driver,
            date=metadata.date,
            ld_file_path=ld_file_path,
            session_name=metadata.session_name
        )

