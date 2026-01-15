"""
Quick test script for CSV import functionality
Run this to test the CSV import with your Config Variables CSV file
"""
import sys
from pathlib import Path

# Add backend to path
BACKEND_DIR = Path(__file__).parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from internal.csv_parameter_importer import import_csv_file, import_csv_content, generate_link_key
from internal.car_parameters import get_all_car_parameter_definitions, get_car_parameter_definition_by_link_key

def test_link_key_generation():
    """Test link key generation"""
    print("Testing link key generation...")
    
    test_cases = [
        ("Suspension", "Damper", "FL HS Rebound", "suspension_damper_fl_hs_rebound"),
        ("Powertrain", "", "Fuel added", "powertrain_fuel_added"),
        ("Ergo", "", "Brake Bias", "ergo_brake_bias"),
        ("Suspension", "CCT", "FL Toe", "suspension_cct_fl_toe"),
    ]
    
    for subteam, tab, var_name, expected in test_cases:
        result = generate_link_key(subteam, tab, var_name)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {subteam} | {tab or '(empty)'} | {var_name}")
        print(f"      Expected: {expected}")
        print(f"      Got:      {result}")
        if result != expected:
            print(f"      ⚠️  Mismatch!")
        print()
    
    print()

def test_csv_import(csv_path):
    """Test CSV import"""
    csv_file = Path(csv_path)
    
    if not csv_file.exists():
        print(f"❌ CSV file not found: {csv_path}")
        return
    
    print(f"📄 Importing CSV: {csv_file}")
    print()
    
    # Import CSV
    results = import_csv_file(csv_file, overwrite_existing=False)
    
    print("📊 Import Results:")
    print(f"  Created: {results['created']}")
    print(f"  Updated: {results['updated']}")
    print(f"  Skipped: {results['skipped']}")
    print(f"  Total rows: {results['total_rows']}")
    
    if results['errors']:
        print(f"\n⚠️  Errors ({len(results['errors'])}):")
        for error in results['errors'][:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(results['errors']) > 10:
            print(f"  ... and {len(results['errors']) - 10} more errors")
    else:
        print("\n✅ No errors!")
    
    print()
    
    # Show some sample definitions
    print("📋 Sample imported definitions (first 5):")
    all_defs = get_all_car_parameter_definitions()
    for i, defn in enumerate(all_defs[:5], 1):
        link_key = defn.get('link_key', 'N/A')
        display_name = defn.get('display_name', defn.get('parameter_name', 'N/A'))
        subteam = defn.get('subteam', 'N/A')
        tab = defn.get('tab', '')
        print(f"  {i}. [{link_key}]")
        print(f"     Display: {display_name}")
        print(f"     Subteam: {subteam}, Tab: {tab or '(none)'}")
        print()
    
    # Test lookup by link key
    if results['created'] > 0 or results['updated'] > 0:
        print("🔍 Testing lookup by link key...")
        test_link_key = "suspension_damper_fl_hs_rebound"
        found = get_car_parameter_definition_by_link_key(test_link_key)
        if found:
            print(f"  ✓ Found definition by link_key: {test_link_key}")
            print(f"    Parameter: {found.get('parameter_name')}")
            print(f"    Display: {found.get('display_name')}")
        else:
            print(f"  ✗ Not found by link_key: {test_link_key}")
            print("     (This might be okay if the CSV structure is different)")
        print()

if __name__ == "__main__":
    print("=" * 60)
    print("CSV Import Test Script")
    print("=" * 60)
    print()
    
    # Test 1: Link key generation
    test_link_key_generation()
    
    # Test 2: CSV import
    # Default path - change this to your CSV file path
    csv_path = r"C:\Users\josht\Downloads\Config Variables - Sheet1.csv"
    
    # Check if CSV exists at default path, otherwise ask for path
    if not Path(csv_path).exists():
        print(f"⚠️  CSV not found at default path: {csv_path}")
        print("Please update the csv_path variable in this script to point to your CSV file.")
        print()
        # Try alternative path
        csv_path = Path(__file__).parent / "Config Variables - Sheet1.csv"
        if csv_path.exists():
            print(f"Found CSV at: {csv_path}")
        else:
            print("Please provide the CSV file path.")
            sys.exit(1)
    
    test_csv_import(csv_path)
    
    print("=" * 60)
    print("✅ Test complete!")
    print("=" * 60)
