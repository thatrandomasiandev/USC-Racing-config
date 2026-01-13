"""
Queue Auto Applier - Automatically applies queued parameter changes to MoTeC files
When a car returns and data is pulled, this module injects all pending queue items
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from .database import get_queue, process_queue_item, get_parameter, update_parameter
from .motec_ldx_updater import MotecLdxUpdater
from .config.settings import settings


async def auto_apply_queued_changes_to_file(
    file_path: Path,
    car_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Automatically apply all pending queue items to an uploaded MoTeC file
    
    This is called when a car returns and data is pulled. All queued changes
    that were made while the car was on track are automatically injected.
    
    Args:
        file_path: Path to the uploaded LDX file
        car_id: Optional car identifier to filter queue items
    
    Returns:
        Dictionary with:
        - applied_count: Number of queue items applied
        - failed_count: Number of queue items that failed
        - applied_items: List of applied queue items
        - failed_items: List of failed queue items with errors
    """
    # Only process LDX files (not LD files)
    if not file_path.exists() or file_path.suffix.lower() != settings.MOTEC_LDX_EXTENSION.lower():
        return {
            "applied_count": 0,
            "failed_count": 0,
            "applied_items": [],
            "failed_items": [],
            "message": "Only LDX files can be updated with queued changes"
        }
    
    # Get all pending queue items (optionally filtered by car)
    queue_items = await get_queue(status=settings.QUEUE_STATUS_PENDING, car_id=car_id)
    
    if not queue_items:
        return {
            "applied_count": 0,
            "failed_count": 0,
            "applied_items": [],
            "failed_items": [],
            "message": "No pending queue items to apply"
        }
    
    applied_items = []
    failed_items = []
    
    # Process each queue item
    for item in queue_items:
        try:
            parameter_name = item["parameter_name"]
            new_value = item["new_value"]
            comment = item.get("comment")
            form_id = item["form_id"]
            
            # Apply change to LDX file
            success = MotecLdxUpdater.update_parameter_in_ldx(
                file_path=file_path,
                parameter_name=parameter_name,
                new_value=new_value,
                comment=comment
            )
            
            if success:
                # Update parameter in database
                # Check if parameter exists
                existing = await get_parameter(parameter_name)
                
                if existing:
                    # Update existing parameter
                    await update_parameter(
                        parameter_name=parameter_name,
                        subteam=item["subteam"],
                        new_value=new_value,
                        updated_by=item["submitted_by"],
                        comment=comment or f"Auto-applied from queue (queued by {item['submitted_by']})",
                        form_id=form_id
                    )
                else:
                    # Create new parameter
                    await update_parameter(
                        parameter_name=parameter_name,
                        subteam=item["subteam"],
                        new_value=new_value,
                        updated_by=item["submitted_by"],
                        comment=comment or f"Auto-applied from queue (queued by {item['submitted_by']})",
                        form_id=form_id
                    )
                
                # Mark queue item as auto-applied (using process_queue_item with special status)
                # We'll update the status directly to "auto-applied"
                from .database import get_db
                db = await get_db()
                try:
                    await db.execute(
                        f"UPDATE parameter_queue SET status = '{settings.QUEUE_STATUS_AUTO_APPLIED}' WHERE form_id = ?",
                        (form_id,)
                    )
                    await db.commit()
                finally:
                    await db.close()
                
                applied_items.append({
                    "form_id": form_id,
                    "parameter_name": parameter_name,
                    "new_value": new_value,
                    "submitted_by": item["submitted_by"]
                })
            else:
                # LDX update failed
                failed_items.append({
                    "form_id": form_id,
                    "parameter_name": parameter_name,
                    "error": "Failed to update parameter in LDX file"
                })
        
        except Exception as e:
            # Error processing this queue item
            failed_items.append({
                "form_id": item.get("form_id", "unknown"),
                "parameter_name": item.get("parameter_name", "unknown"),
                "error": str(e)
            })
    
    return {
        "applied_count": len(applied_items),
        "failed_count": len(failed_items),
        "applied_items": applied_items,
        "failed_items": failed_items,
        "message": f"Applied {len(applied_items)} queued changes, {len(failed_items)} failed"
    }
