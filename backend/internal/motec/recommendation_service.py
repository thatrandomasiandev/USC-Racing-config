"""
MoTeC Recommendation Service
Analyzes LDX and LD files to provide recommended settings and configurations
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
import re

from .file_service import MotecFileService
from .config_service import MotecConfigService
from .models import MotecChannelConfig, ChannelSource


class MotecRecommendationService:
    """Service for analyzing MoTeC files and generating recommendations"""
    
    def __init__(self, file_service: MotecFileService, config_service: MotecConfigService):
        """
        Initialize recommendation service
        
        Args:
            file_service: MotecFileService instance
            config_service: MotecConfigService instance
        """
        self.file_service = file_service
        self.config_service = config_service
        self.config = file_service.config
    
    def analyze_files_and_recommend(self, car_id: Optional[str] = None) -> Dict:
        """
        Analyze available LDX and LD files and generate comprehensive recommendations
        
        Args:
            car_id: Optional car ID to focus analysis on
            
        Returns:
            Dictionary with recommendations for:
            - Channel mappings
            - Car profiles
            - Optimal settings
            - Missing channels
            - Data quality issues
        """
        recommendations = {
            "car_id": car_id or "default",
            "timestamp": datetime.now().isoformat(),
            "channel_mappings": [],
            "car_profile": {},
            "missing_channels": [],
            "data_quality": {},
            "optimal_settings": {},
            "confidence": "medium"
        }
        
        # Discover files
        ld_files = self.file_service.discover_ld_files()
        ldx_files = self._discover_ldx_files()
        
        if not ld_files and not ldx_files:
            recommendations["confidence"] = "low"
            recommendations["message"] = "No LDX or LD files found. Cannot generate recommendations."
            return recommendations
        
        # Analyze LDX files for channel configurations
        ldx_channels = self._analyze_ldx_channels(ldx_files)
        
        # Analyze LD files for actual data availability
        ld_analysis = self._analyze_ld_files(ld_files[:10])  # Limit to first 10 for performance
        
        # Generate channel mapping recommendations
        recommendations["channel_mappings"] = self._recommend_channel_mappings(
            ldx_channels, ld_analysis, car_id
        )
        
        # Generate car profile recommendations
        recommendations["car_profile"] = self._recommend_car_profile(
            ld_files, ldx_files, car_id
        )
        
        # Identify missing channels
        recommendations["missing_channels"] = self._identify_missing_channels(
            ldx_channels, ld_analysis
        )
        
        # Data quality assessment
        recommendations["data_quality"] = self._assess_data_quality(ld_files, ldx_files)
        
        # Optimal settings recommendations
        recommendations["optimal_settings"] = self._recommend_optimal_settings(
            ld_analysis, ldx_channels
        )
        
        # Calculate confidence level
        recommendations["confidence"] = self._calculate_confidence(
            len(ld_files), len(ldx_files), recommendations
        )
        
        return recommendations
    
    def _discover_ldx_files(self) -> List[str]:
        """Discover LDX files in configured directories"""
        ldx_files = []
        output_dir = Path(self.config.get("ldx_output_dir", "data/motec/ldx"))
        
        # Check output directory
        if output_dir.exists():
            for ldx_file in output_dir.glob("*.ldx"):
                if ldx_file.is_file():
                    ldx_files.append(str(ldx_file))
        
        # Check NAS if configured
        nas_base = self.file_service.nas_base_path
        if nas_base and nas_base.exists():
            for ldx_file in nas_base.rglob("*.ldx"):
                if ldx_file.is_file() and str(ldx_file) not in ldx_files:
                    ldx_files.append(str(ldx_file))
        
        return sorted(ldx_files)
    
    def _analyze_ldx_channels(self, ldx_files: List[str]) -> Dict:
        """Analyze channels from LDX files"""
        all_channels = {}
        channel_frequency = {}
        
        for ldx_path in ldx_files[:5]:  # Limit analysis to first 5 files
            try:
                ldx_model = self.file_service.read_ldx(ldx_path)
                
                for channel in ldx_model.channels:
                    ch_name = channel.get("name", "").lower()
                    if not ch_name:
                        continue
                    
                    # Track frequency
                    channel_frequency[ch_name] = channel_frequency.get(ch_name, 0) + 1
                    
                    # Store channel details
                    if ch_name not in all_channels:
                        all_channels[ch_name] = {
                            "name": channel.get("name", ""),
                            "units": channel.get("units", ""),
                            "source": channel.get("source", "CAN"),
                            "scaling": channel.get("scaling"),
                            "math": channel.get("math"),
                            "frequency": 0,
                            "files": []
                        }
                    
                    all_channels[ch_name]["frequency"] = channel_frequency[ch_name]
                    all_channels[ch_name]["files"].append(ldx_path)
            except Exception as e:
                continue
        
        return all_channels
    
    def _analyze_ld_files(self, ld_files: List[str]) -> Dict:
        """Analyze LD files for data patterns and availability"""
        analysis = {
            "total_files": len(ld_files),
            "valid_files": 0,
            "common_patterns": {},
            "suggested_channels": [],
            "file_metadata": []
        }
        
        for ld_path in ld_files:
            try:
                metadata = self.file_service.read_ld_metadata(ld_path)
                if metadata.valid:
                    analysis["valid_files"] += 1
                    analysis["file_metadata"].append({
                        "path": ld_path,
                        "size": metadata.file_size,
                        "channels": metadata.channels or []
                    })
            except Exception:
                continue
        
        # Infer common channel patterns from filenames and paths
        analysis["suggested_channels"] = self._infer_channels_from_files(ld_files)
        
        return analysis
    
    def _infer_channels_from_files(self, ld_files: List[str]) -> List[str]:
        """Infer likely channel names from file patterns"""
        suggested = []
        
        # Common MoTeC channel patterns
        common_channels = [
            "speed", "rpm", "throttle", "brake", "steering",
            "g_force_lat", "g_force_long", "g_force_vert",
            "oil_temp", "water_temp", "oil_pressure",
            "fuel_level", "fuel_pressure",
            "lap_time", "sector_time",
            "pressure_port_1", "pressure_port_2", "pressure_port_3",
            "pressure_port_4", "pressure_port_5", "pressure_port_6",
            "pressure_port_7", "pressure_port_8"
        ]
        
        # Check if files suggest these channels exist
        for ch in common_channels:
            # Simple heuristic: if we have multiple LD files, likely channels exist
            if len(ld_files) > 0:
                suggested.append(ch)
        
        return suggested
    
    def _recommend_channel_mappings(self, ldx_channels: Dict, ld_analysis: Dict, car_id: Optional[str]) -> List[Dict]:
        """Generate recommended channel mappings"""
        recommendations = []
        
        # Standard internal channel names (from telemetry schema)
        # Expanded with MoTeC DTC standard channels
        internal_channels = {
            "speed": "Speed",
            "rpm": "RPM",
            "throttle": "Throttle",
            "brake": "Brake",
            "steering": "Steering",
            "g_force_lat": "Lateral G",
            "g_force_long": "Longitudinal G",
            "oil_temp": "Engine Oil Temperature",
            "water_temp": "Water Temperature",
            "oil_pressure": "Oil Pressure",
            "fuel_level": "Fuel Level",
            "fuel_pressure": "Fuel Pressure",
            "lap_time": "Lap Time",
            "sector_time": "Sector Time",
            "gbox_oil_temp": "Gearbox Oil Temperature",
            "diff_oil_temp": "Differential Oil Temperature",
            "reference_lap": "Reference Lap Time",
            "gain_loss": "Gain/Loss"
        }
        
        # Map LDX channels to internal channels
        for internal_name, display_name in internal_channels.items():
            # Try to find matching LDX channel
            motec_name = self._find_matching_motec_channel(internal_name, ldx_channels)
            
            if motec_name:
                ldx_ch = ldx_channels[motec_name]
                recommendations.append({
                    "internal_name": internal_name,
                    "motec_name": ldx_ch["name"],
                    "units": ldx_ch.get("units", self._infer_units(internal_name)),
                    "source": ldx_ch.get("source", "CAN"),
                    "scaling": ldx_ch.get("scaling"),
                    "math_expression": ldx_ch.get("math"),
                    "enabled": True,
                    "confidence": "high" if ldx_ch["frequency"] > 1 else "medium",
                    "reason": f"Found in {ldx_ch['frequency']} LDX file(s)"
                })
            else:
                # Suggest based on naming patterns
                suggested_motec = self._suggest_motec_name(internal_name)
                recommendations.append({
                    "internal_name": internal_name,
                    "motec_name": suggested_motec,
                    "units": self._infer_units(internal_name),
                    "source": "CAN",
                    "enabled": True,
                    "confidence": "low",
                    "reason": "Suggested based on naming convention"
                })
        
        return recommendations
    
    def _find_matching_motec_channel(self, internal_name: str, ldx_channels: Dict) -> Optional[str]:
        """Find matching MoTeC channel name for internal channel"""
        # Try exact match first
        internal_lower = internal_name.lower()
        if internal_lower in ldx_channels:
            return internal_lower
        
        # Try variations
        variations = [
            internal_lower.replace("_", ""),
            internal_lower.replace("_", " "),
            internal_lower.replace("_", "-"),
        ]
        
        for variation in variations:
            for motec_name in ldx_channels.keys():
                if variation in motec_name.lower() or motec_name.lower() in variation:
                    return motec_name
        
        return None
    
    def _suggest_motec_name(self, internal_name: str) -> str:
        """Suggest MoTeC channel name based on internal name
        
        Uses MoTeC DTC Color Displays standard naming conventions
        Reference: https://www.motec.com.au/hessian/uploads/2015_DTC_Colour_Displays_v2_0_d7cc55fc75.pdf
        """
        # MoTeC DTC standard channel naming conventions
        name_map = {
            "speed": "Speed",
            "rpm": "RPMx1000",
            "throttle": "Throttle Position",
            "brake": "Brake Pressure",
            "steering": "Steering Angle",
            "g_force_lat": "Lateral G",
            "g_force_long": "Longitudinal G",
            "oil_temp": "ENGINE OIL TMP",  # MoTeC standard: ENGINE OIL TMP
            "water_temp": "WATER TMP",  # MoTeC standard: WATER TMP
            "oil_pressure": "OIL PRESS",  # MoTeC standard: OIL PRESS
            "fuel_level": "Fuel Level",
            "fuel_pressure": "FUEL PRESS",  # MoTeC standard: FUEL PRESS
            "lap_time": "RUNNING LAP",  # MoTeC standard: RUNNING LAP
            "sector_time": "Sector Time",
            "gbox_oil_temp": "GBOX OIL TMP",  # MoTeC standard: GBOX OIL TMP
            "diff_oil_temp": "DIFF OIL TMP",  # MoTeC standard: DIFF OIL TMP
            "reference_lap": "REFERENCE LAP",  # MoTeC standard: REFERENCE LAP
            "gain_loss": "GAIN/LOSS"  # MoTeC standard: GAIN/LOSS
        }
        
        # Check exact match first
        if internal_name in name_map:
            return name_map[internal_name]
        
        # Convert internal naming to MoTeC convention
        # MoTeC often uses UPPERCASE for temperatures and pressures
        parts = internal_name.split("_")
        
        # Special handling for temperature channels (MoTeC uses TMP)
        if "temp" in internal_name.lower() or "temperature" in internal_name.lower():
            # Extract component name
            component = parts[0].upper() if parts else ""
            if component == "OIL":
                return "ENGINE OIL TMP"
            elif component == "WATER":
                return "WATER TMP"
            elif component == "GBOX" or component == "GEARBOX":
                return "GBOX OIL TMP"
            elif component == "DIFF" or component == "DIFFERENTIAL":
                return "DIFF OIL TMP"
            else:
                return f"{component} TMP"
        
        # Special handling for pressure channels (MoTeC uses PRESS)
        if "pressure" in internal_name.lower() or "press" in internal_name.lower():
            component = parts[0].upper() if parts else ""
            if component == "OIL":
                return "OIL PRESS"
            elif component == "FUEL":
                return "FUEL PRESS"
            else:
                return f"{component} PRESS"
        
        # Default: Title Case
        motec_name = " ".join(word.capitalize() for word in parts)
        return motec_name
    
    def _infer_units(self, channel_name: str) -> str:
        """Infer units for a channel based on name"""
        units_map = {
            "speed": "mph",
            "rpm": "rpm",
            "throttle": "%",
            "brake": "%",
            "steering": "deg",
            "g_force_lat": "g",
            "g_force_long": "g",
            "oil_temp": "°F",
            "water_temp": "°F",
            "oil_pressure": "psi",
            "fuel_level": "%",
            "lap_time": "s",
            "sector_time": "s"
        }
        
        return units_map.get(channel_name, "")
    
    def _recommend_car_profile(self, ld_files: List[str], ldx_files: List[str], car_id: Optional[str]) -> Dict:
        """Generate recommended car profile"""
        profile = {
            "car_id": car_id or "default",
            "name": "",
            "class": "",
            "year": None,
            "default_track": "",
            "default_driver": ""
        }
        
        # Infer from file paths
        if ld_files:
            first_file = Path(ld_files[0])
            # Try to extract car info from path
            path_parts = first_file.parts
            for part in path_parts:
                if "car" in part.lower():
                    profile["name"] = part.replace("car_", "").replace("car-", "").title()
                    break
        
        # Infer from LDX files
        if ldx_files:
            try:
                ldx_model = self.file_service.read_ldx(ldx_files[0])
                if ldx_model.car_name:
                    profile["name"] = ldx_model.car_name
                if ldx_model.project_name:
                    profile["class"] = ldx_model.project_name
            except Exception:
                pass
        
        return profile
    
    def _identify_missing_channels(self, ldx_channels: Dict, ld_analysis: Dict) -> List[str]:
        """Identify channels that should exist but don't"""
        required_channels = [
            "speed", "rpm", "throttle", "brake", "steering",
            "g_force_lat", "oil_temp", "water_temp"
        ]
        
        missing = []
        ldx_channel_names = {ch.lower() for ch in ldx_channels.keys()}
        
        for req_ch in required_channels:
            found = False
            for ldx_ch in ldx_channel_names:
                if req_ch in ldx_ch or ldx_ch in req_ch:
                    found = True
                    break
            if not found:
                missing.append(req_ch)
        
        return missing
    
    def _assess_data_quality(self, ld_files: List[str], ldx_files: List[str]) -> Dict:
        """Assess data quality of files"""
        quality = {
            "ld_files_count": len(ld_files),
            "ldx_files_count": len(ldx_files),
            "issues": [],
            "warnings": [],
            "score": 100
        }
        
        if len(ld_files) == 0:
            quality["issues"].append("No LD files found")
            quality["score"] -= 30
        
        if len(ldx_files) == 0:
            quality["warnings"].append("No LDX files found - channel mappings may be incomplete")
            quality["score"] -= 20
        
        if len(ld_files) > 0 and len(ldx_files) == 0:
            quality["warnings"].append("LD files exist but no LDX configuration files found")
            quality["score"] -= 15
        
        return quality
    
    def _recommend_optimal_settings(self, ld_analysis: Dict, ldx_channels: Dict) -> Dict:
        """Recommend optimal settings based on analysis"""
        ld_count = ld_analysis.get("total_files", 0)
        ldx_count = len(ldx_channels)
        
        settings = {
            "auto_generate_ldx": ld_count > ldx_count if ld_count > 0 else False,
            "overwrite_policy": "ifSafe",
            "suggested_update_rate": 10.0,
            "channel_count": len(ldx_channels)
        }
        
        return settings
    
    def _calculate_confidence(self, ld_count: int, ldx_count: int, recommendations: Dict) -> str:
        """Calculate confidence level of recommendations"""
        if ld_count == 0 and ldx_count == 0:
            return "low"
        
        if ld_count > 5 and ldx_count > 2:
            return "high"
        
        if ld_count > 0 or ldx_count > 0:
            return "medium"
        
        return "low"
    
    def apply_recommendations(self, car_id: str, recommendations: Dict, auto_apply: bool = False) -> Dict:
        """
        Apply recommendations to configuration
        
        Args:
            car_id: Car ID to apply recommendations to
            recommendations: Recommendations dictionary from analyze_files_and_recommend
            auto_apply: If True, automatically apply without confirmation
            
        Returns:
            Dictionary with application results
        """
        results = {
            "applied": False,
            "channels_applied": 0,
            "profile_applied": False,
            "errors": []
        }
        
        try:
            # Apply channel mappings
            if recommendations.get("channel_mappings"):
                channels = []
                for rec in recommendations["channel_mappings"]:
                    try:
                        channel = MotecChannelConfig(
                            internal_name=rec["internal_name"],
                            motec_name=rec["motec_name"],
                            units=rec["units"],
                            source=ChannelSource(rec.get("source", "CAN")),
                            scaling=rec.get("scaling"),
                            math_expression=rec.get("math_expression"),
                            enabled=rec.get("enabled", True),
                            description=f"Auto-recommended: {rec.get('reason', '')}"
                        )
                        channels.append(channel)
                    except Exception as e:
                        results["errors"].append(f"Error creating channel {rec.get('internal_name')}: {e}")
                
                if channels:
                    self.config_service.set_channel_mappings(car_id, channels)
                    results["channels_applied"] = len(channels)
            
            # Apply car profile
            if recommendations.get("car_profile"):
                profile = recommendations["car_profile"]
                self.config_service.set_car_profile(car_id, profile)
                results["profile_applied"] = True
            
            results["applied"] = True
            
        except Exception as e:
            results["errors"].append(f"Error applying recommendations: {e}")
        
        return results

