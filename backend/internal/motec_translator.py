"""
MoTeC Translator - Bidirectional translation between .ldx files and Admin Console parameters
Converts LDX XML data to parameter format and vice versa
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from .motec_parser import MotecParser, MotecLdxParser


class MotecTranslator:
    """Bidirectional translator between LDX files and Admin Console parameters"""
    
    @staticmethod
    def extract_math_items(ldx_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Extract MathItems from parsed LDX data (if available)"""
        # This would need to be added to the parser first
        # For now, return empty dict
        return {}
    
    @staticmethod
    def extract_descriptors(ldx_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Extract Descriptors from parsed LDX data (if available)"""
        # This would need to be added to the parser first
        # For now, return empty dict
        return {}
    
    @staticmethod
    def ldx_to_parameters(
        file_path: Path,
        subteam: Optional[str] = None,
        default_updated_by: str = "system",
        include_details: bool = True,
        include_math_items: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Convert LDX file to list of parameters for admin console
        
        Args:
            file_path: Path to .ldx file
            subteam: Subteam name to assign to parameters
            default_updated_by: Username for parameter updates
            include_details: Include Details String elements as parameters
            include_math_items: Include MathItems as parameters
        
        Returns:
            List of parameter dictionaries with keys:
            - parameter_name: str
            - subteam: str
            - current_value: str
            - updated_at: str
            - updated_by: str
        """
        try:
            # Parse the LDX file
            ldx_data = MotecParser.parse_file(file_path)
            
            if ldx_data.get("parse_error"):
                raise ValueError(f"Error parsing LDX file: {ldx_data['parse_error']}")
            
            parameters = []
            now = datetime.now().isoformat()
            
            # Convert Details String elements to parameters
            if include_details and "details" in ldx_data:
                for key, value in ldx_data["details"].items():
                    # Create parameter-friendly name (replace spaces, special chars)
                    param_name = f"ldx_details_{key.replace(' ', '_').replace('/', '_')}"
                    
                    parameters.append({
                        "parameter_name": param_name,
                        "subteam": param_subteam,
                        "current_value": str(value),
                        "updated_at": now,
                        "updated_by": default_updated_by,
                        "_source": "ldx_details",
                        "_original_id": key
                    })
            
            # Extract MathItems if available (need to parse XML directly for now)
            if include_math_items:
                try:
                    tree = ET.parse(file_path)
                    root = tree.getroot()
                    
                    # Find MathItems
                    math_items = root.findall(".//MathItems/MathScaleOffset")
                    for math_item in math_items:
                        item_id = math_item.get("Id", "")
                        if not item_id:
                            continue
                        
                        scale = math_item.get("Scale", "1")
                        offset = math_item.get("Offset", "0")
                        unit = math_item.get("Unit", "")
                        
                        # Create parameter for scale
                        param_name_scale = f"ldx_math_{item_id.replace(' ', '_').replace('/', '_')}_scale"
                        parameters.append({
                            "parameter_name": param_name_scale,
                            "subteam": param_subteam,
                            "current_value": str(scale),
                            "updated_at": now,
                            "updated_by": default_updated_by,
                            "_source": "ldx_math",
                            "_original_id": item_id,
                            "_field": "scale",
                            "_unit": unit
                        })
                        
                        # Create parameter for offset
                        param_name_offset = f"ldx_math_{item_id.replace(' ', '_').replace('/', '_')}_offset"
                        parameters.append({
                            "parameter_name": param_name_offset,
                            "subteam": param_subteam,
                            "current_value": str(offset),
                            "updated_at": now,
                            "updated_by": default_updated_by,
                            "_source": "ldx_math",
                            "_original_id": item_id,
                            "_field": "offset",
                            "_unit": unit
                        })
                except Exception as e:
                    # MathItems parsing is optional, don't fail if it errors
                    pass
            
            # Extract Descriptors if available
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                
                descriptors = root.findall(".//Descriptors/Descriptor")
                for desc in descriptors:
                    desc_id = desc.get("Id", "")
                    if not desc_id:
                        continue
                    
                    display_unit = desc.get("DisplayUnit", "")
                    display_dps = desc.get("DisplayDPS", "")
                    
                    if display_dps:
                        param_name_dps = f"ldx_desc_{desc_id.replace(' ', '_')}_dps"
                        parameters.append({
                            "parameter_name": param_name_dps,
                            "subteam": param_subteam,
                            "current_value": str(display_dps),
                            "updated_at": now,
                            "updated_by": default_updated_by,
                            "_source": "ldx_descriptor",
                            "_original_id": desc_id,
                            "_field": "display_dps",
                            "_unit": display_unit
                        })
            except Exception:
                # Descriptors parsing is optional
                pass
            
            return parameters
            
        except Exception as e:
            raise ValueError(f"Error converting LDX to parameters: {str(e)}")
    
    @staticmethod
    def parameters_to_ldx(
        parameters: List[Dict[str, Any]],
        output_path: Path,
        locale: str = "English_United States.1252",
        default_locale: str = "C",
        version: str = "1.6",
        preserve_markers: bool = False,
        marker_groups: Optional[List[Dict[str, Any]]] = None
    ) -> Path:
        """
        Convert parameters from admin console to LDX file
        
        Args:
            parameters: List of parameter dictionaries (from database)
            output_path: Path where LDX file should be written
            locale: LDX locale setting
            default_locale: LDX default locale setting
            version: LDX version
            preserve_markers: If True, preserve markers from template LDX
            marker_groups: Optional marker groups to include
        
        Returns:
            Path to created LDX file
        """
        # Create root element
        root = ET.Element("LDXFile")
        root.set("Locale", locale)
        root.set("DefaultLocale", default_locale)
        root.set("Version", version)
        
        # Organize parameters by source type
        details_params = []
        math_params = {}
        descriptor_params = {}
        
        for param in parameters:
            source = param.get("_source", "")
            param_name = param.get("parameter_name", "")
            value = param.get("current_value", param.get("new_value", ""))
            
            if source == "ldx_details" or param_name.startswith("ldx_details_"):
                # Extract original ID
                original_id = param.get("_original_id", "")
                if not original_id:
                    # Try to reconstruct from parameter name
                    original_id = param_name.replace("ldx_details_", "").replace("_", " ")
                
                details_params.append({
                    "id": original_id,
                    "value": value
                })
            
            elif source == "ldx_math" or param_name.startswith("ldx_math_"):
                original_id = param.get("_original_id", "")
                field = param.get("_field", "")
                unit = param.get("_unit", "")
                
                if original_id not in math_params:
                    math_params[original_id] = {
                        "unit": unit,
                        "scale": "1",
                        "offset": "0"
                    }
                
                if field == "scale":
                    math_params[original_id]["scale"] = value
                elif field == "offset":
                    math_params[original_id]["offset"] = value
            
            elif source == "ldx_descriptor" or param_name.startswith("ldx_desc_"):
                original_id = param.get("_original_id", "")
                field = param.get("_field", "")
                unit = param.get("_unit", "")
                
                if original_id not in descriptor_params:
                    descriptor_params[original_id] = {
                        "display_unit": unit,
                        "display_dps": "4"
                    }
                
                if field == "display_dps":
                    descriptor_params[original_id]["display_dps"] = value
        
        # Create Layers element
        layers = ET.SubElement(root, "Layers")
        layer = ET.SubElement(layers, "Layer")
        
        # Add MarkerBlock if we have markers
        if preserve_markers and marker_groups:
            marker_block = ET.SubElement(layer, "MarkerBlock")
            for mg in marker_groups:
                marker_group = ET.SubElement(marker_block, "MarkerGroup")
                marker_group.set("Name", mg.get("name", ""))
                marker_group.set("Index", str(mg.get("index", "")))
                
                for marker in mg.get("markers", []):
                    marker_elem = ET.SubElement(marker_group, "Marker")
                    marker_elem.set("Version", marker.get("version", "100"))
                    marker_elem.set("ClassName", marker.get("class_name", ""))
                    marker_elem.set("Name", marker.get("name", ""))
                    marker_elem.set("Flags", marker.get("flags", ""))
                    marker_elem.set("Time", marker.get("time", ""))
        
        # Add RangeBlock
        ET.SubElement(layer, "RangeBlock")
        
        # Add Details section if we have details parameters
        if details_params:
            details = ET.SubElement(layers, "Details")
            for detail in details_params:
                string_elem = ET.SubElement(details, "String")
                string_elem.set("Id", detail["id"])
                string_elem.set("Value", detail["value"])
        
        # Add Maths section if we have math parameters
        if math_params:
            maths = ET.SubElement(root, "Maths")
            maths.set("Id", "Local")
            maths.set("Flags", "1208")
            math_items = ET.SubElement(maths, "MathItems")
            
            for item_id, math_data in math_params.items():
                math_item = ET.SubElement(math_items, "MathScaleOffset")
                math_item.set("Id", item_id)
                math_item.set("SampleRate", "0")
                math_item.set("Unit", math_data.get("unit", ""))
                math_item.set("EngineFlags", "7")
                math_item.set("Scale", math_data.get("scale", "1"))
                math_item.set("Offset", math_data.get("offset", "0"))
        
        # Add Descriptors section if we have descriptor parameters
        if descriptor_params:
            descriptors = ET.SubElement(root, "Descriptors")
            for desc_id, desc_data in descriptor_params.items():
                desc = ET.SubElement(descriptors, "Descriptor")
                desc.set("Id", desc_id)
                desc.set("DisplayUnit", desc_data.get("display_unit", ""))
                desc.set("DisplayDPS", desc_data.get("display_dps", "4"))
                desc.set("DisplayColorIndex", "2")
                desc.set("Interpolate", "1")
        
        # Create XML tree and write to file
        tree = ET.ElementTree(root)
        
        # Indent XML (ET.indent available in Python 3.9+)
        try:
            ET.indent(tree, space=" ", level=0)
        except AttributeError:
            # Python < 3.9 doesn't have ET.indent, use manual formatting
            pass
        
        # Write with XML declaration
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tree.write(
            output_path,
            encoding="utf-8",
            xml_declaration=True
        )
        
        return output_path
    
    @staticmethod
    def merge_ldx_with_parameters(
        ldx_file_path: Path,
        parameters: List[Dict[str, Any]],
        output_path: Path,
        merge_strategy: str = "parameters_override"
    ) -> Path:
        """
        Merge existing LDX file with parameters from admin console
        
        Args:
            ldx_file_path: Path to existing LDX file
            parameters: Parameters from admin console
            output_path: Path for merged LDX file
            merge_strategy: "parameters_override" or "ldx_override" or "merge"
        
        Returns:
            Path to merged LDX file
        """
        # Parse existing LDX
        ldx_data = MotecParser.parse_file(ldx_file_path)
        
        # Extract markers from original if we want to preserve them
        marker_groups = ldx_data.get("marker_groups", []) if merge_strategy != "parameters_override" else None
        
        # Get locale/version from original
        locale = ldx_data.get("locale", "English_United States.1252")
        version = ldx_data.get("version", "1.6")
        
        # Convert parameters to LDX, preserving structure from original
        return MotecTranslator.parameters_to_ldx(
            parameters=parameters,
            output_path=output_path,
            locale=locale,
            version=version,
            preserve_markers=(marker_groups is not None),
            marker_groups=marker_groups
        )

