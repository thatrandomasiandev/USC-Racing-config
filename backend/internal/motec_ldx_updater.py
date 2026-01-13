"""
MoTeC LDX Updater - Updates specific parameter values in existing LDX files
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Dict, Any
import hashlib
import os
import time
from datetime import datetime
from .motec_parser import MotecParser


class MotecLdxUpdater:
    """Update parameter values in existing LDX files"""
    
    @staticmethod
    def _get_file_hash(file_path: Path) -> str:
        """Get SHA256 hash of file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            return f"ERROR: {e}"
    
    @staticmethod
    def _get_file_stats(file_path: Path) -> Dict[str, Any]:
        """Get file statistics for debugging"""
        try:
            stat = file_path.stat()
            return {
                "exists": file_path.exists(),
                "size": stat.st_size if file_path.exists() else 0,
                "mtime": stat.st_mtime if file_path.exists() else 0,
                "mtime_str": datetime.fromtimestamp(stat.st_mtime).isoformat() if file_path.exists() else "N/A",
                "readable": os.access(file_path, os.R_OK) if file_path.exists() else False,
                "writable": os.access(file_path, os.W_OK) if file_path.exists() else False,
                "absolute_path": str(file_path.resolve()),
                "hash": MotecLdxUpdater._get_file_hash(file_path) if file_path.exists() else "N/A"
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def update_parameter_in_ldx(
        file_path: Path,
        parameter_name: str,
        new_value: str,
        comment: Optional[str] = None
    ) -> bool:
        """
        Update a specific parameter value in an existing LDX file
        
        Args:
            file_path: Path to the LDX file
            parameter_name: Name of the parameter (e.g., "ldx_details_Fastest_Time", "ldx_math_ID_scale")
            new_value: New value to set
            comment: Optional comment to include in documentation
        
        Returns:
            True if update was successful, False otherwise
        """
        # Resolve absolute path (follow symlinks)
        file_path = file_path.resolve()
        
        # Log BEFORE state
        print(f"[LDX_UPDATER] === UPDATE START ===")
        print(f"[LDX_UPDATER] Parameter: {parameter_name}")
        print(f"[LDX_UPDATER] New value: {new_value}")
        
        before_stats = MotecLdxUpdater._get_file_stats(file_path)
        print(f"[LDX_UPDATER] BEFORE - Path: {before_stats.get('absolute_path')}")
        print(f"[LDX_UPDATER] BEFORE - Exists: {before_stats.get('exists')}")
        print(f"[LDX_UPDATER] BEFORE - Size: {before_stats.get('size')} bytes")
        print(f"[LDX_UPDATER] BEFORE - mtime: {before_stats.get('mtime_str')}")
        print(f"[LDX_UPDATER] BEFORE - Hash: {before_stats.get('hash')[:16]}...")
        print(f"[LDX_UPDATER] BEFORE - Readable: {before_stats.get('readable')}, Writable: {before_stats.get('writable')}")
        
        try:
            if not file_path.exists():
                print(f"[LDX_UPDATER] ERROR: File does not exist: {file_path}")
                return False
            
            # Parse the XML
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Get original content hash for comparison
            original_content = ET.tostring(root, encoding='unicode')
            original_hash = hashlib.sha256(original_content.encode()).hexdigest()
            
            # Determine parameter type and update accordingly
            if parameter_name.startswith("ldx_details_"):
                # Update Details String element
                original_id = parameter_name.replace("ldx_details_", "").replace("_", " ")
                updated = MotecLdxUpdater._update_details_string(root, original_id, new_value)
            
            elif parameter_name.startswith("ldx_math_"):
                # Update MathItem
                # Parse: ldx_math_ID_scale or ldx_math_ID_offset
                parts = parameter_name.replace("ldx_math_", "").split("_")
                if len(parts) >= 2:
                    # Last part is the field (scale/offset), rest is ID
                    field = parts[-1]
                    item_id = "_".join(parts[:-1])
                    updated = MotecLdxUpdater._update_math_item(root, item_id, field, new_value)
                else:
                    updated = False
            
            elif parameter_name.startswith("ldx_desc_"):
                # Update Descriptor
                # Parse: ldx_desc_ID_dps
                parts = parameter_name.replace("ldx_desc_", "").split("_")
                if len(parts) >= 2:
                    field = parts[-1]
                    desc_id = "_".join(parts[:-1])
                    updated = MotecLdxUpdater._update_descriptor(root, desc_id, field, new_value)
                else:
                    updated = False
            
            else:
                # Car parameter or other parameter - auto-document in Details section
                # Check if this is a car parameter and should be documented
                updated = MotecLdxUpdater._update_or_add_details_documentation(
                    root, parameter_name, new_value, comment
                )
            
            if updated:
                print(f"[LDX_UPDATER] Parameter found and XML updated")
                
                # Create backup first
                backup_path = file_path.with_suffix(file_path.suffix + '.bak')
                if not backup_path.exists():
                    import shutil
                    shutil.copy2(file_path, backup_path)
                    print(f"[LDX_UPDATER] Backup created: {backup_path}")
                else:
                    print(f"[LDX_UPDATER] Backup already exists: {backup_path}")
                
                # Format XML properly
                try:
                    ET.indent(tree, space=" ", level=0)
                except AttributeError:
                    # Python < 3.9 doesn't have ET.indent
                    pass
                
                # Generate new XML content
                new_content = ET.tostring(root, encoding='unicode')
                new_hash = hashlib.sha256(new_content.encode()).hexdigest()
                
                print(f"[LDX_UPDATER] Original content hash: {original_hash[:16]}...")
                print(f"[LDX_UPDATER] New content hash: {new_hash[:16]}...")
                
                if original_hash == new_hash:
                    print(f"[LDX_UPDATER] WARNING: Content hash unchanged - no actual changes produced!")
                    print(f"[LDX_UPDATER] This may mean the parameter was not found or value unchanged")
                
                # Atomic write: Write to temporary file first, then replace
                temp_path = file_path.with_suffix(file_path.suffix + '.tmp')
                print(f"[LDX_UPDATER] Writing to temp file: {temp_path}")
                
                # Write XML with proper formatting
                with open(temp_path, 'wb') as f:
                    xml_bytes = ET.tostring(root, encoding='utf-8', xml_declaration=True)
                    f.write(xml_bytes)
                    f.flush()
                    os.fsync(f.fileno())  # Force write to disk
                
                print(f"[LDX_UPDATER] Temp file written, size: {temp_path.stat().st_size} bytes")
                
                # Atomic replace
                os.replace(temp_path, file_path)
                print(f"[LDX_UPDATER] Atomic replace completed: {temp_path} -> {file_path}")
                
                # Verify AFTER write
                time.sleep(0.1)  # Brief pause to ensure filesystem sync
                after_stats = MotecLdxUpdater._get_file_stats(file_path)
                print(f"[LDX_UPDATER] AFTER - Size: {after_stats.get('size')} bytes")
                print(f"[LDX_UPDATER] AFTER - mtime: {after_stats.get('mtime_str')}")
                print(f"[LDX_UPDATER] AFTER - Hash: {after_stats.get('hash')[:16]}...")
                
                # Verify the change is actually in the file
                try:
                    verify_tree = ET.parse(file_path)
                    verify_root = verify_tree.getroot()
                    
                    # Check if our change is actually there
                    if parameter_name.startswith("ldx_details_"):
                        original_id = parameter_name.replace("ldx_details_", "").replace("_", " ")
                        details = verify_root.find(".//Details")
                        if details is not None:
                            for string_elem in details.findall("String"):
                                if string_elem.get("Id") == original_id:
                                    actual_value = string_elem.get("Value", "")
                                    print(f"[LDX_UPDATER] VERIFICATION - Found '{original_id}' in file with value: '{actual_value}'")
                                    if actual_value == str(new_value):
                                        print(f"[LDX_UPDATER] ✓ VERIFIED: Value matches expected new value")
                                    else:
                                        print(f"[LDX_UPDATER] ✗ MISMATCH: Expected '{new_value}', got '{actual_value}'")
                    elif parameter_name.startswith("ldx_math_"):
                        parts = parameter_name.replace("ldx_math_", "").split("_")
                        if len(parts) >= 2:
                            field = parts[-1]
                            item_id = "_".join(parts[:-1])
                            item_id_with_spaces = item_id.replace("_", " ")
                            math_items = verify_root.find(".//MathItems")
                            if math_items is not None:
                                for math_item in math_items.findall("MathScaleOffset"):
                                    ldx_id = math_item.get("Id", "")
                                    if ldx_id == item_id or ldx_id == item_id_with_spaces:
                                        if field in ["scale", "Scale"]:
                                            actual_value = math_item.get("Scale", "")
                                        else:
                                            actual_value = math_item.get("Offset", "")
                                        print(f"[LDX_UPDATER] VERIFICATION - Found '{item_id}' ({field}) with value: '{actual_value}'")
                                        if actual_value == str(new_value):
                                            print(f"[LDX_UPDATER] ✓ VERIFIED: Value matches expected new value")
                                        else:
                                            print(f"[LDX_UPDATER] ✗ MISMATCH: Expected '{new_value}', got '{actual_value}'")
                except Exception as verify_err:
                    print(f"[LDX_UPDATER] WARNING: Could not verify change: {verify_err}")
                
                print(f"[LDX_UPDATER] === UPDATE COMPLETE ===")
                return True
            else:
                print(f"[LDX_UPDATER] Parameter not found in XML structure")
                print(f"[LDX_UPDATER] === UPDATE FAILED (parameter not found) ===")
                return False
            
        except Exception as e:
            import traceback
            print(f"[LDX_UPDATER] ERROR updating LDX file:")
            print(f"[LDX_UPDATER] Exception: {e}")
            print(f"[LDX_UPDATER] Traceback:")
            traceback.print_exc()
            print(f"[LDX_UPDATER] === UPDATE FAILED (exception) ===")
            return False
    
    @staticmethod
    def _update_details_string(root: ET.Element, string_id: str, new_value: str) -> bool:
        """Update a Details String element"""
        # Find Details section
        details = root.find(".//Details")
        if details is None:
            return False
        
        # Find the String element with matching Id
        for string_elem in details.findall("String"):
            if string_elem.get("Id") == string_id:
                string_elem.set("Value", str(new_value))
                return True
        
        return False
    
    @staticmethod
    def _update_math_item(root: ET.Element, item_id: str, field: str, new_value: str) -> bool:
        """Update a MathItem (Scale or Offset)"""
        # Find MathItems section
        math_items = root.find(".//MathItems")
        if math_items is None:
            return False
        
        # Convert item_id from underscore format to space format for matching
        # LDX files use spaces, parameters use underscores
        item_id_with_spaces = item_id.replace("_", " ")
        
        # Find the MathScaleOffset element with matching Id
        for math_item in math_items.findall("MathScaleOffset"):
            ldx_id = math_item.get("Id", "")
            # Match either format (spaces or underscores)
            if ldx_id == item_id or ldx_id == item_id_with_spaces:
                if field in ["scale", "Scale"]:
                    math_item.set("Scale", str(new_value))
                    return True
                elif field in ["offset", "Offset"]:
                    math_item.set("Offset", str(new_value))
                    return True
        
        return False
    
    @staticmethod
    def _update_descriptor(root: ET.Element, desc_id: str, field: str, new_value: str) -> bool:
        """Update a Descriptor (DisplayDPS, etc.)"""
        # Find Descriptors section
        descriptors = root.find(".//Descriptors")
        if descriptors is None:
            return False
        
        # Find the Descriptor element with matching Id
        for desc in descriptors.findall("Descriptor"):
            if desc.get("Id") == desc_id:
                if field in ["dps", "DisplayDPS"]:
                    desc.set("DisplayDPS", str(new_value))
                    return True
                elif field in ["unit", "DisplayUnit"]:
                    desc.set("DisplayUnit", str(new_value))
                    return True
        
        return False
    
    @staticmethod
    def _update_or_add_details_documentation(
        root: ET.Element,
        parameter_name: str,
        new_value: str,
        comment: Optional[str] = None
    ) -> bool:
        """
        Update or add a Details String element for car parameter documentation
        
        Args:
            root: XML root element
            parameter_name: Parameter name (e.g., "brake_bias")
            new_value: New value to document
            comment: Optional comment to include
        
        Returns:
            True if updated/added, False otherwise
        """
        try:
            # Try to get car parameter definition to get display name
            from .car_parameters import get_car_parameter_definition
            defn = get_car_parameter_definition(parameter_name)
            
            if defn:
                # Use display_name as the Details String Id
                details_id = defn.get("display_name")
                if not details_id:
                    # Fallback if display_name is missing
                    details_id = parameter_name.replace("_", " ").title()
                
                unit = defn.get("unit", "")
                
                # Format value with unit if provided (but don't double-add if value already has unit)
                formatted_value = str(new_value)
                if unit and formatted_value:
                    # Check if value already contains the unit
                    if unit.lower() not in formatted_value.lower():
                        formatted_value = f"{formatted_value} {unit}".strip()
            else:
                # Fallback: convert parameter_name to readable format
                details_id = parameter_name.replace("_", " ").title()
                formatted_value = str(new_value)
            
            # Add comment if provided
            if comment and comment.strip():
                formatted_value = f"{formatted_value} ({comment.strip()})"
            
            # Find or create Layers section
            layers = root.find(".//Layers")
            if layers is None:
                # Create Layers section
                layers = ET.SubElement(root, "Layers")
            
            # Find or create Details section
            details = layers.find(".//Details")
            if details is None:
                # Create Details section
                details = ET.SubElement(layers, "Details")
            
            # Check if String with this Id already exists
            existing_string = None
            for string_elem in details.findall("String"):
                if string_elem.get("Id") == details_id:
                    existing_string = string_elem
                    break
            
            if existing_string is not None:
                # Update existing String
                existing_string.set("Value", formatted_value)
                print(f"[LDX_UPDATER] Updated Details documentation: '{details_id}' = '{formatted_value}'")
            else:
                # Create new String element
                new_string = ET.SubElement(details, "String")
                new_string.set("Id", details_id)
                new_string.set("Value", formatted_value)
                print(f"[LDX_UPDATER] Added Details documentation: '{details_id}' = '{formatted_value}'")
            
            return True
            
        except Exception as e:
            print(f"[LDX_UPDATER] Error adding Details documentation: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def ldx_file_contains_parameter(file_path: Path, parameter_name: str) -> bool:
        """
        Check if an LDX file contains a specific parameter
        
        Args:
            file_path: Path to the LDX file
            parameter_name: Name of the parameter to check for
        
        Returns:
            True if the file contains the parameter, False otherwise
        """
        try:
            if not file_path.exists():
                return False
            
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Check based on parameter type
            if parameter_name.startswith("ldx_details_"):
                # Check Details section
                original_id = parameter_name.replace("ldx_details_", "").replace("_", " ")
                details = root.find(".//Details")
                if details is not None:
                    for string_elem in details.findall("String"):
                        if string_elem.get("Id") == original_id:
                            return True
            
            elif parameter_name.startswith("ldx_math_"):
                # Check MathItems section
                parts = parameter_name.replace("ldx_math_", "").split("_")
                if len(parts) >= 2:
                    item_id = "_".join(parts[:-1])
                    item_id_with_spaces = item_id.replace("_", " ")
                    math_items = root.find(".//MathItems")
                    if math_items is not None:
                        for math_item in math_items.findall("MathScaleOffset"):
                            ldx_id = math_item.get("Id", "")
                            # Match either format (spaces or underscores)
                            if ldx_id == item_id or ldx_id == item_id_with_spaces:
                                return True
            
            elif parameter_name.startswith("ldx_desc_"):
                # Check Descriptors section
                parts = parameter_name.replace("ldx_desc_", "").split("_")
                if len(parts) >= 2:
                    desc_id = "_".join(parts[:-1])
                    desc_id_with_spaces = desc_id.replace("_", " ")
                    descriptors = root.find(".//Descriptors")
                    if descriptors is not None:
                        for desc in descriptors.findall("Descriptor"):
                            ldx_id = desc.get("Id", "")
                            # Match either format (spaces or underscores)
                            if ldx_id == desc_id or ldx_id == desc_id_with_spaces:
                                return True
            
            else:
                # For car parameters, we'll always try to document them
                # Check if it's a car parameter
                try:
                    from .car_parameters import get_car_parameter_definition
                    defn = get_car_parameter_definition(parameter_name)
                    if defn:
                        # This is a car parameter that should be documented
                        return True
                except Exception:
                    pass
            
            return False
            
        except Exception as e:
            print(f"Error checking if LDX file contains parameter: {e}")
            return False

