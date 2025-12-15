"""
MoTeC configuration service for channel mappings and car profiles
Manages the mapping between internal telemetry channels and MoTeC i2 channels
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from .models import MotecChannelConfig, MotecSessionConfig, ChannelSource


class MotecConfigService:
    """Service for managing MoTeC channel mappings and car profiles"""
    
    def __init__(self, config: dict):
        """
        Initialize MoTeC config service
        
        Args:
            config: Configuration dictionary from settings.get_motec_config()
        """
        self.config = config
        self.channel_mappings_file = Path(config.get("channel_mappings_file", "config/motec/channel_mappings.json"))
        self.car_profiles_file = Path(config.get("car_profiles_file", "config/motec/car_profiles.json"))
        
        # Create directories if needed
        self.channel_mappings_file.parent.mkdir(parents=True, exist_ok=True)
        self.car_profiles_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load mappings
        self._channel_mappings: Dict[str, List[MotecChannelConfig]] = {}
        self._car_profiles: Dict[str, dict] = {}
        self._load_mappings()
        self._load_car_profiles()
    
    def _load_mappings(self) -> None:
        """Load channel mappings from file"""
        if self.channel_mappings_file.exists():
            try:
                with open(self.channel_mappings_file, "r") as f:
                    data = json.load(f)
                    for car_id, channels in data.items():
                        self._channel_mappings[car_id] = [
                            MotecChannelConfig.from_dict(ch) for ch in channels
                        ]
            except Exception as e:
                print(f"Warning: Could not load channel mappings: {e}")
                self._channel_mappings = {}
        else:
            # Create default empty mappings
            self._save_mappings()
    
    def _save_mappings(self) -> None:
        """Save channel mappings to file"""
        data = {
            car_id: [ch.to_dict() for ch in channels]
            for car_id, channels in self._channel_mappings.items()
        }
        with open(self.channel_mappings_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def _load_car_profiles(self) -> None:
        """Load car profiles from file"""
        if self.car_profiles_file.exists():
            try:
                with open(self.car_profiles_file, "r") as f:
                    self._car_profiles = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load car profiles: {e}")
                self._car_profiles = {}
        else:
            # Create default empty profiles
            self._save_car_profiles()
    
    def _save_car_profiles(self) -> None:
        """Save car profiles to file"""
        with open(self.car_profiles_file, "w") as f:
            json.dump(self._car_profiles, f, indent=2)
    
    def get_channel_mappings(self, car_id: str) -> List[MotecChannelConfig]:
        """
        Get channel mappings for a specific car
        
        Args:
            car_id: Car identifier
            
        Returns:
            List of channel configurations
        """
        return self._channel_mappings.get(car_id, [])
    
    def set_channel_mappings(self, car_id: str, channels: List[MotecChannelConfig]) -> None:
        """
        Set channel mappings for a car
        
        Args:
            car_id: Car identifier
            channels: List of channel configurations
        """
        self._channel_mappings[car_id] = channels
        self._save_mappings()
    
    def add_channel_mapping(self, car_id: str, channel: MotecChannelConfig) -> None:
        """
        Add a single channel mapping for a car
        
        Args:
            car_id: Car identifier
            channel: Channel configuration to add
        """
        if car_id not in self._channel_mappings:
            self._channel_mappings[car_id] = []
        
        # Check if channel already exists (by internal name)
        existing = [ch for ch in self._channel_mappings[car_id] 
                   if ch.internal_name == channel.internal_name]
        if existing:
            # Update existing
            idx = self._channel_mappings[car_id].index(existing[0])
            self._channel_mappings[car_id][idx] = channel
        else:
            # Add new
            self._channel_mappings[car_id].append(channel)
        
        self._save_mappings()
    
    def remove_channel_mapping(self, car_id: str, internal_name: str) -> bool:
        """
        Remove a channel mapping
        
        Args:
            car_id: Car identifier
            internal_name: Internal channel name to remove
            
        Returns:
            True if removed, False if not found
        """
        if car_id not in self._channel_mappings:
            return False
        
        original_count = len(self._channel_mappings[car_id])
        self._channel_mappings[car_id] = [
            ch for ch in self._channel_mappings[car_id]
            if ch.internal_name != internal_name
        ]
        
        if len(self._channel_mappings[car_id]) < original_count:
            self._save_mappings()
            return True
        return False
    
    def get_car_profile(self, car_id: str) -> Optional[dict]:
        """
        Get car profile configuration
        
        Args:
            car_id: Car identifier
            
        Returns:
            Car profile dictionary or None
        """
        return self._car_profiles.get(car_id)
    
    def set_car_profile(self, car_id: str, profile: dict) -> None:
        """
        Set car profile configuration
        
        Args:
            car_id: Car identifier
            profile: Profile dictionary
        """
        self._car_profiles[car_id] = profile
        self._save_car_profiles()
    
    def map_internal_to_motec(self, car_id: str, internal_name: str) -> Optional[str]:
        """
        Map internal channel name to MoTeC channel name
        
        Args:
            car_id: Car identifier
            internal_name: Internal channel name
            
        Returns:
            MoTeC channel name or None if not found
        """
        mappings = self.get_channel_mappings(car_id)
        for mapping in mappings:
            if mapping.internal_name == internal_name and mapping.enabled:
                return mapping.motec_name
        return None
    
    def map_motec_to_internal(self, car_id: str, motec_name: str) -> Optional[str]:
        """
        Map MoTeC channel name to internal channel name
        
        Args:
            car_id: Car identifier
            motec_name: MoTeC channel name
            
        Returns:
            Internal channel name or None if not found
        """
        mappings = self.get_channel_mappings(car_id)
        for mapping in mappings:
            if mapping.motec_name == motec_name and mapping.enabled:
                return mapping.internal_name
        return None
    
    def create_session_config(self, car_id: str, **kwargs) -> MotecSessionConfig:
        """
        Create a session configuration for a car with default mappings
        
        Args:
            car_id: Car identifier
            **kwargs: Additional session parameters (track_id, driver, date, etc.)
            
        Returns:
            MotecSessionConfig with channels from mappings
        """
        channels = self.get_channel_mappings(car_id)
        
        return MotecSessionConfig(
            car_id=car_id,
            channels=channels,
            **kwargs
        )
    
    def get_all_car_ids(self) -> List[str]:
        """Get list of all configured car IDs"""
        return sorted(set(list(self._channel_mappings.keys()) + list(self._car_profiles.keys())))


