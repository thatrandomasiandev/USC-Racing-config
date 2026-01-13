#!/usr/bin/env python3
"""
Reset Website - Clear all data
Run this script to reset the website to a clean state
"""
import asyncio
from pathlib import Path
import json
from backend.internal.database import reset_database
from backend.internal.motec_file_manager import MOTEC_METADATA_FILE
from backend.internal.session_tracker import SESSIONS_FILE

async def reset_all(delete_files=False):
    print("🔄 Resetting website...")
    if delete_files:
        print("⚠️  DELETE FILES mode: Will delete uploaded LDX/LD files!")
    print()
    
    # Reset database
    print("Clearing database...")
    db_result = await reset_database(keep_users=True)
    print(f"  ✓ Deleted {db_result['parameters_deleted']} parameters")
    print(f"  ✓ Deleted {db_result['history_deleted']} history entries")
    print(f"  ✓ Deleted {db_result['queue_deleted']} queue items")
    print(f"  ✓ Users: {db_result['users_deleted']}")
    print()
    
    # Clear file metadata
    print("Clearing MoTeC file metadata...")
    if MOTEC_METADATA_FILE.exists():
        MOTEC_METADATA_FILE.write_text("[]")
        print(f"  ✓ Cleared {MOTEC_METADATA_FILE}")
    else:
        print(f"  - No metadata file found")
    print()
    
    # Clear sessions
    print("Clearing sessions...")
    if SESSIONS_FILE.exists():
        SESSIONS_FILE.write_text("[]")
        print(f"  ✓ Cleared {SESSIONS_FILE}")
    else:
        print(f"  - No sessions file found")
    print()
    
    # Delete uploaded files if requested
    if delete_files:
        print("Deleting uploaded LDX/LD files...")
        from pathlib import Path
        motec_dir = Path("data/motec_files")
        deleted_count = 0
        
        for subdir in ["ldx", "ld"]:
            subdir_path = motec_dir / subdir
            if subdir_path.exists():
                for file in subdir_path.glob("*"):
                    if file.is_file() and not file.name.endswith('.bak'):
                        file.unlink()
                        deleted_count += 1
                        print(f"  ✓ Deleted {file.name}")
        
        print(f"  ✓ Deleted {deleted_count} files total")
        print()
    else:
        print("Note: Uploaded LDX/LD files are NOT deleted.")
        print("      To delete them, run: python3 reset_website.py --delete-files")
        print()
    
    print("✅ Website reset complete!")

if __name__ == "__main__":
    import sys
    delete_files = "--delete-files" in sys.argv or "-d" in sys.argv
    asyncio.run(reset_all(delete_files=delete_files))
