"""
MoTeC i2 data models for LDX and LD files
"""

from typing import Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ChannelSource(str, Enum):
    """Source type for MoTeC channels"""
    CAN = "CAN"
    DERIVED = "derived"
    CALCULATED = "calculated"
    ANALOG = "analog"
    DIGITAL = "digital"


@dataclass
class MotecChannelConfig:
    """Configuration for a single MoTeC channel mapping"""
    internal_name: str  # Our app's channel name
    motec_name: str  # MoTeC i2 channel name
    units: str
    source: ChannelSource
    scaling: Optional[Dict[str, Union[float, str]]] = None
    math_expression: Optional[str] = None
    enabled: bool = True
    description: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "internal_name": self.internal_name,
            "motec_name": self.motec_name,
            "units": self.units,
            "source": self.source.value,
            "scaling": self.scaling,
            "math_expression": self.math_expression,
            "enabled": self.enabled,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "MotecChannelConfig":
        """Create from dictionary"""
        return cls(
            internal_name=data["internal_name"],
            motec_name=data["motec_name"],
            units=data["units"],
            source=ChannelSource(data.get("source", "CAN")),
            scaling=data.get("scaling"),
            math_expression=data.get("math_expression"),
            enabled=data.get("enabled", True),
            description=data.get("description")
        )


@dataclass
class MotecSessionConfig:
    """Configuration for a MoTeC session"""
    car_id: str
    track_id: Optional[str] = None
    driver: Optional[str] = None
    date: Optional[str] = None
    ld_file_path: Optional[str] = None
    ldx_file_path: Optional[str] = None
    channels: List[MotecChannelConfig] = field(default_factory=list)
    session_name: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "car_id": self.car_id,
            "track_id": self.track_id,
            "driver": self.driver,
            "date": self.date,
            "ld_file_path": self.ld_file_path,
            "ldx_file_path": self.ldx_file_path,
            "channels": [ch.to_dict() for ch in self.channels],
            "session_name": self.session_name
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "MotecSessionConfig":
        """Create from dictionary"""
        return cls(
            car_id=data["car_id"],
            track_id=data.get("track_id"),
            driver=data.get("driver"),
            date=data.get("date"),
            ld_file_path=data.get("ld_file_path"),
            ldx_file_path=data.get("ldx_file_path"),
            channels=[MotecChannelConfig.from_dict(ch) for ch in data.get("channels", [])],
            session_name=data.get("session_name")
        )


@dataclass
class MotecLdxModel:
    """Model representing a MoTeC LDX configuration file"""
    workspace_name: str
    project_name: Optional[str] = None
    car_name: Optional[str] = None
    channels: List[Dict] = field(default_factory=list)
    worksheets: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "workspace_name": self.workspace_name,
            "project_name": self.project_name,
            "car_name": self.car_name,
            "channels": self.channels,
            "worksheets": self.worksheets,
            "metadata": self.metadata,
            "created": self.created.isoformat() if self.created else None,
            "modified": self.modified.isoformat() if self.modified else None
        }


@dataclass
class MotecLdMetadata:
    """Metadata extracted from a MoTeC LD log file"""
    file_path: str
    file_size: int
    duration: Optional[float] = None  # seconds
    sample_rate: Optional[float] = None  # Hz
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    channels: List[str] = field(default_factory=list)
    car_id: Optional[str] = None
    track_id: Optional[str] = None
    driver: Optional[str] = None
    session_name: Optional[str] = None
    valid: bool = False
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "file_path": self.file_path,
            "file_size": self.file_size,
            "duration": self.duration,
            "sample_rate": self.sample_rate,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "channels": self.channels,
            "car_id": self.car_id,
            "track_id": self.track_id,
            "driver": self.driver,
            "session_name": self.session_name,
            "valid": self.valid,
            "error": self.error
        }


