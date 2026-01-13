"""
Parse Config Variables PDF and generate car_parameters.json
"""
import PyPDF2
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
PDF_PATH = BASE_DIR / "Config Variables - Sheet1.pdf"
OUTPUT_PATH = BASE_DIR / "data" / "car_parameters.json"

def parse_pdf():
    """Parse PDF and extract all config variables"""
    with open(PDF_PATH, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text() + '\n'
    
    lines = text.split('\n')
    parameters = []
    
    # Skip header
    for line in lines[1:]:
        line = line.strip()
        if not line or line.startswith('Subteam'):
            continue
        
        # Parse pattern: Subteam Tab VariableName Type Constant Unit/Description
        # Example: "Suspension Damper FL HS Rebound Int Constant HS is meaured..."
        # Example: "Suspension CCT FL Toe Foat? expected value of -5 to 5 Constant Degrees"
        
        # Find subteam (first word that's one of these)
        subteams = ['Suspension', 'Powertrain', 'Ergo', 'DAQ', 'Aero', 'Egro']
        subteam = None
        for st in subteams:
            if line.startswith(st):
                subteam = st
                line = line[len(st):].strip()
                break
        
        if not subteam:
            continue
        
        # Find tab/category (next word before variable name starts)
        tabs = ['Damper', 'CCT', 'Parameters', 'Temp', 'Tires', 'sound', 'Brake', 'Rear', 'Front', 'Special', 'Rear']
        tab = None
        for t in tabs:
            if line.startswith(t):
                tab = t
                line = line[len(t):].strip()
                break
        
        # Now extract variable name, type, and description
        # Look for type indicators
        var_type = None
        type_patterns = [
            (r'\bInt\b', 'int'),
            (r'\bfloat\b', 'float'),
            (r'\bFoat\?', 'float'),  # typo in PDF
            (r'\bString\b', 'string'),
            (r'\bstring\b', 'string'),
            (r'drop down', 'dropdown'),
        ]
        
        for pattern, dtype in type_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                var_type = dtype
                break
        
        # Extract variable name (everything before type)
        var_name_match = re.match(r'^(.+?)(?:\s+(?:Int|float|Foat|String|string|drop\s+down))', line, re.IGNORECASE)
        if not var_name_match:
            # Try without type if not found
            var_name_match = re.match(r'^(.+?)(?:\s+Constant)', line)
        
        var_name_full = var_name_match.group(1).strip() if var_name_match else line.split('Constant')[0].strip()
        var_name_full = var_name_full.replace('?', '').strip()
        
        # Extract unit
        unit = ""
        unit_patterns = [
            (r'\bDegrees?\b', 'deg'),
            (r'\blbs?\b', 'lbs'),
            (r'\bPSI\b', 'psi'),
            (r'\bdBc?\b', 'dB'),
            (r'%\b', '%'),
            (r'\bin\b(?!\w)', 'in'),  # 'in' but not 'inside' or 'constant'
        ]
        
        for pattern, u in unit_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                unit = u
                break
        
        # Extract min/max from "expected value of -5 to 5" or "-15 to 15"
        min_val = None
        max_val = None
        range_match = re.search(r'(-?\d+(?:\.\d+)?)\s+to\s+(-?\d+(?:\.\d+)?)', line)
        if range_match:
            min_val = range_match.group(1)
            max_val = range_match.group(2)
        
        # Create parameter name (snake_case)
        # Clean variable name
        param_name_base = var_name_full.lower().replace(' ', '_').replace('/', '_')
        param_name_base = re.sub(r'[^a-z0-9_]', '_', param_name_base)
        param_name_base = re.sub(r'_+', '_', param_name_base).strip('_')
        
        # Add tab prefix if we have one
        if tab:
            tab_prefix = tab.lower().replace(' ', '_')
            param_name = f"{tab_prefix}_{param_name_base}"
        else:
            param_name = param_name_base
        
        # Create display name
        display_name = var_name_full.replace('?', '').strip()
        
        # Get default value based on type
        default_value = "0" if var_type in ['int', 'float'] else ""
        
        # Extract description (everything after "Constant")
        description = ""
        if 'Constant' in line:
            desc_part = line.split('Constant', 1)[1] if 'Constant' in line else ""
            # Clean up description
            desc_part = desc_part.strip()
            # Remove unit mentions
            for u_word in ['Degrees', 'degrees', 'lbs', 'PSI', 'psi', 'dB', 'in']:
                desc_part = re.sub(rf'\b{u_word}\b', '', desc_part, flags=re.IGNORECASE)
            # Remove range info
            desc_part = re.sub(r'expected value of.*?Constant', '', desc_part, flags=re.IGNORECASE)
            desc_part = re.sub(r'-?\d+\s+to\s+-?\d+', '', desc_part)
            desc_part = re.sub(r'\s+', ' ', desc_part).strip()
            description = desc_part[:200]
        
        param = {
            "parameter_name": param_name,
            "display_name": display_name,
            "subteam": subteam,
            "unit": unit,
            "default_value": default_value,
            "min_value": min_val or "",
            "max_value": max_val or "",
            "motec_channel": None,
            "description": description
        }
        
        parameters.append(param)
    
    return parameters

if __name__ == "__main__":
    params = parse_pdf()
    
    output = {
        "description": "Car parameters to track - definitions from Config Variables PDF",
        "version": "1.0",
        "parameters": params
    }
    
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Generated {len(params)} parameters in {OUTPUT_PATH}")
