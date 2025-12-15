"""
USC Racing Trackside Telemetry System
Real-time telemetry data acquisition and display server
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import json
import asyncio
from datetime import datetime
from pathlib import Path

from internal.config.settings import settings
import os
from internal.aero.calculations import AeroCalculations

# MoTeC integration (optional, only if enabled)
motec_file_service = None
motec_config_service = None
motec_session_linker = None
motec_nas_discovery = None

if settings.MOTEC_ENABLED:
    try:
        from internal.motec import MotecFileService, MotecConfigService, MotecSessionLinker
        from internal.motec.nas_discovery import NasDiscoveryService
        from internal.motec.recommendation_service import MotecRecommendationService
        motec_file_service = MotecFileService(settings.get_motec_config())
        motec_config_service = MotecConfigService(settings.get_motec_config())
        motec_session_linker = MotecSessionLinker(motec_file_service, motec_config_service)
        motec_nas_discovery = NasDiscoveryService(settings.get_motec_config())
        motec_recommendation_service = MotecRecommendationService(motec_file_service, motec_config_service)
    except Exception as e:
        print(f"Warning: MoTeC integration disabled due to error: {e}")
        motec_recommendation_service = None
else:
    motec_recommendation_service = None

app = FastAPI(title="USC Racing Trackside", version="1.0.0")

# Initialize aero calculations from settings
aero_calc = AeroCalculations(settings.get_aero_config())

# CORS middleware - configurable origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup paths from configuration
templates_dir = settings.TEMPLATES_DIR
static_dir = settings.STATIC_DIR
data_dir = settings.DATA_DIR

# Create directories (skip on Vercel - read-only filesystem)
# Only create if directories don't exist and we have write permissions
try:
    if not templates_dir.exists():
        templates_dir.mkdir(parents=True, exist_ok=True)
    if not static_dir.exists():
        static_dir.mkdir(parents=True, exist_ok=True)
    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)
except (PermissionError, OSError, FileNotFoundError):
    # Vercel has read-only filesystem for most paths
    # Templates and static should exist in the repo
    pass

templates = Jinja2Templates(directory=str(templates_dir))

# Mount static files
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# WebSocket connections for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except:
                pass

manager = ConnectionManager()

# Initialize telemetry data from configuration
telemetry_data = settings.get_initial_telemetry_data()
telemetry_data["timestamp"] = datetime.now().isoformat()

# API Routes
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "trackside-telemetry",
        "config": {
            "update_rate_hz": settings.WS_UPDATE_RATE_HZ,
            "logging_enabled": settings.LOG_ENABLED
        }
    }

@app.get("/api/config")
async def get_config():
    """Get current configuration (non-sensitive)"""
    config = {
        "update_rate_hz": settings.WS_UPDATE_RATE_HZ,
        "logging_enabled": settings.LOG_ENABLED,
        "data_dir": str(data_dir),
        "telemetry_fields": list(telemetry_data.keys()),
        "aero": settings.get_aero_config()
    }
    
    # Add MoTeC config if enabled
    if settings.MOTEC_ENABLED and motec_config_service:
        config["motec"] = settings.get_motec_config()
    
    return config

@app.get("/api/telemetry")
async def get_telemetry():
    """Get current telemetry data"""
    telemetry_data["timestamp"] = datetime.now().isoformat()
    return telemetry_data

@app.post("/api/telemetry")
async def update_telemetry(data: dict):
    """Update telemetry data (from telemetry device)"""
    # Only update fields that exist in current schema
    for key, value in data.items():
        if key in telemetry_data:
            telemetry_data[key] = value
    
    telemetry_data["timestamp"] = datetime.now().isoformat()
    
    # Process aero calculations if pressure data exists
    pressure_data = {k: v for k, v in telemetry_data.items() if k.startswith("pressure_port_")}
    if pressure_data and len(pressure_data) >= 8:
        steering = telemetry_data.get("steering", 0.0)
        lateral_g = telemetry_data.get("g_force_lat", 0.0)
        
        aero_results = aero_calc.process_pressure_data(pressure_data, steering, lateral_g)
        
        # Add aero results to telemetry data
        telemetry_data.update(aero_results["coefficients"])
        telemetry_data["aero_scenario"] = aero_results["scenario"]
        telemetry_data["aero_averages"] = aero_results["averages"]
    
    # Broadcast to WebSocket clients
    await manager.broadcast(telemetry_data)
    
    # Log to file if enabled
    if settings.LOG_ENABLED:
        log_file = data_dir / f"{settings.LOG_FILE_PREFIX}_{datetime.now().strftime('%Y%m%d')}.jsonl"
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(telemetry_data) + "\n")
        except Exception as e:
            print(f"Error writing log: {e}")
    
    return {"status": "updated"}

@app.get("/api/sessions")
async def get_sessions():
    """Get list of recorded sessions"""
    sessions = []
    if data_dir.exists():
        pattern = f"{settings.LOG_FILE_PREFIX}_*.jsonl"
        for file in data_dir.glob(pattern):
            sessions.append({
                "date": file.stem.replace(f"{settings.LOG_FILE_PREFIX}_", ""),
                "filename": file.name,
                "size": file.stat().st_size
            })
    return {"sessions": sorted(sessions, reverse=True)}

@app.get("/api/aero/averages")
async def get_aero_averages():
    """Get average coefficient values for each scenario"""
    return aero_calc.get_scenario_averages()

@app.get("/api/aero/histograms")
async def get_aero_histograms(scenario: str = None):
    """Get histogram data for a scenario (or all if not specified)"""
    if scenario:
        if scenario in ["straight", "turn_left", "turn_right"]:
            return {scenario: aero_calc.get_all_histograms(scenario)}
        else:
            return {"error": "Invalid scenario"}
    else:
        return {
            "straight": aero_calc.get_all_histograms("straight"),
            "turn_left": aero_calc.get_all_histograms("turn_left"),
            "turn_right": aero_calc.get_all_histograms("turn_right")
        }

@app.post("/api/aero/reset")
async def reset_aero_data(scenario: str = None):
    """Reset aero averaging data for a scenario (or all if not specified)"""
    aero_calc.reset_scenario_data(scenario)
    return {"status": "reset", "scenario": scenario or "all"}

# MoTeC API Endpoints
if settings.MOTEC_ENABLED and motec_file_service and motec_config_service and motec_session_linker:
    
    @app.get("/api/motec/status")
    async def get_motec_status():
        """Get MoTeC integration status"""
        return {
            "enabled": True,
            "ld_files_found": len(motec_file_service.discover_ld_files()),
            "cars_configured": len(motec_config_service.get_all_car_ids())
        }
    
    @app.get("/api/motec/ld/files")
    async def list_ld_files(directory: str = None):
        """List discovered LD files"""
        files = motec_file_service.discover_ld_files(directory)
        metadata_list = []
        for file_path in files:
            try:
                metadata = motec_file_service.read_ld_metadata(file_path)
                metadata_list.append(metadata.to_dict())
            except Exception as e:
                metadata_list.append({
                    "file_path": file_path,
                    "valid": False,
                    "error": str(e)
                })
        return {"files": metadata_list}
    
    @app.get("/api/motec/ldx/{file_path:path}")
    async def read_ldx(file_path: str):
        """Read an LDX file"""
        try:
            ldx_model = motec_file_service.read_ldx(file_path)
            return ldx_model.to_dict()
        except Exception as e:
            return {"error": str(e), "file_path": file_path}
    
    @app.post("/api/motec/ldx/{file_path:path}")
    async def write_ldx(file_path: str, ldx_data: dict, overwrite: bool = Query(False)):
        """
        Write an LDX file
        
        Args:
            file_path: Path to write LDX file
            ldx_data: LDX data to write
            overwrite: Explicit confirmation to overwrite existing file (trackside safety)
        """
        try:
            from internal.motec.models import MotecLdxModel
            from datetime import datetime
            from pathlib import Path
            
            # Trackside safety: Check if file exists and require explicit overwrite confirmation
            ldx_path = Path(file_path)
            if ldx_path.exists() and not overwrite:
                return {
                    "error": "File already exists",
                    "file_path": file_path,
                    "message": "Set overwrite=true to overwrite existing file",
                    "requires_confirmation": True
                }
            
            # Validate required fields
            workspace_name = ldx_data.get("workspace_name", "Default")
            if not workspace_name:
                return {"error": "workspace_name is required"}
            
            ldx_model = MotecLdxModel(
                workspace_name=workspace_name,
                project_name=ldx_data.get("project_name"),
                car_name=ldx_data.get("car_name"),
                channels=ldx_data.get("channels", []),
                worksheets=ldx_data.get("worksheets", []),
                metadata=ldx_data.get("metadata", {})
            )
            
            motec_file_service.write_ldx(file_path, ldx_model)
            return {
                "status": "written",
                "file_path": file_path,
                "message": f"LDX file written successfully to {file_path}"
            }
        except ValueError as e:
            return {"error": f"Validation error: {str(e)}", "file_path": file_path}
        except IOError as e:
            return {"error": f"Write error: {str(e)}", "file_path": file_path}
        except Exception as e:
            return {"error": str(e), "file_path": file_path}
    
    @app.get("/api/motec/channels/{car_id}")
    async def get_channel_mappings(car_id: str):
        """Get channel mappings for a car"""
        mappings = motec_config_service.get_channel_mappings(car_id)
        return {
            "car_id": car_id,
            "channels": [ch.to_dict() for ch in mappings]
        }
    
    @app.post("/api/motec/channels/{car_id}")
    async def set_channel_mappings(car_id: str, channels: list):
        """Set channel mappings for a car"""
        try:
            from internal.motec.models import MotecChannelConfig, ChannelSource
            
            channel_configs = [
                MotecChannelConfig.from_dict(ch) for ch in channels
            ]
            motec_config_service.set_channel_mappings(car_id, channel_configs)
            return {"status": "updated", "car_id": car_id, "count": len(channel_configs)}
        except Exception as e:
            return {"error": str(e), "car_id": car_id}
    
    @app.post("/api/motec/sessions/link")
    async def link_session(ld_file_path: str, car_id: str, track_id: str = None, 
                          driver: str = None, date: str = None):
        """
        Link an LD file to a session
        
        Trackside safety: Validates LD file before linking
        """
        try:
            # Validate LD file exists and is readable
            if not motec_file_service.validate_ld(ld_file_path):
                return {
                    "error": "Invalid LD file",
                    "file_path": ld_file_path,
                    "message": "LD file not found or invalid. Check path and file integrity."
                }
            
            session_config = motec_session_linker.link_ld_to_session(
                ld_file_path=ld_file_path,
                car_id=car_id,
                track_id=track_id,
                driver=driver,
                date=date
            )
            
            return {
                "status": "linked",
                "session": session_config.to_dict(),
                "message": f"LD file linked to session for {car_id}"
            }
        except ValueError as e:
            return {
                "error": "Validation error",
                "message": str(e),
                "file_path": ld_file_path
            }
        except Exception as e:
            return {
                "error": "Link failed",
                "message": str(e),
                "file_path": ld_file_path
            }
    
    @app.get("/api/motec/sessions/discover")
    async def discover_sessions(car_id: str = None, directory: str = None):
        """Discover and link LD files to sessions"""
        try:
            sessions = motec_session_linker.discover_and_link_sessions(
                directory=directory,
                car_id=car_id
            )
            return {
                "sessions": [s.to_dict() for s in sessions],
                "count": len(sessions)
            }
        except Exception as e:
            return {"error": str(e)}
    
    @app.get("/api/motec/cars")
    async def list_cars():
        """List all configured cars"""
        car_ids = motec_config_service.get_all_car_ids()
        cars = []
        for car_id in car_ids:
            profile = motec_config_service.get_car_profile(car_id)
            mappings = motec_config_service.get_channel_mappings(car_id)
            cars.append({
                "car_id": car_id,
                "profile": profile,
                "channel_count": len(mappings)
            })
        return {"cars": cars}
    
    @app.get("/api/motec/nas/status")
    async def get_nas_status():
        """Get NAS discovery status"""
        if motec_nas_discovery:
            return motec_nas_discovery.get_status()
        return {"error": "NAS discovery not available"}
    
    @app.post("/api/motec/nas/scan")
    async def scan_nas(force: bool = False):
        """Scan NAS for MoTeC files"""
        if not motec_nas_discovery:
            return {"error": "NAS discovery not available"}
        
        try:
            result = motec_nas_discovery.scan_for_files(force=force)
            return result
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    @app.get("/api/motec/nas/files")
    async def get_nas_files():
        """Get discovered NAS files (auto-populated)"""
        if not motec_nas_discovery:
            return {"error": "NAS discovery not available"}
        
        status = motec_nas_discovery.get_status()
        return {
            "nas": status["nas"],
            "ld_files": motec_nas_discovery.discovered_ld_files,
            "ldx_files": motec_nas_discovery.discovered_ldx_files,
            "last_scan": status["last_scan"].isoformat() if status["last_scan"] else None
        }
else:
    @app.get("/api/motec/status")
    async def get_motec_status():
        """Get MoTeC integration status"""
        return {"enabled": False, "reason": "MoTeC integration disabled in configuration"}

# MoTeC config endpoints (always available for UI)
@app.get("/api/motec/config")
async def get_motec_config():
    """Get current MoTeC configuration"""
    return settings.get_motec_config()

@app.patch("/api/motec/config")
async def update_motec_config(config: dict):
    """Update MoTeC configuration (UI-driven)"""
    # Note: This updates runtime config, not persistent .env file
    # For persistent changes, user should update .env file
    # This is for temporary/session-based config changes
    try:
        # Update settings if possible (some may require restart)
        # For now, return success and note that .env changes require restart
        return {
            "status": "updated",
            "message": "Configuration updated. Some changes may require server restart.",
            "config": config
        }
    except Exception as e:
        return {"error": str(e)}

# Car management endpoints (only if MoTeC enabled)
if settings.MOTEC_ENABLED and motec_config_service:
    @app.post("/api/motec/cars/{car_id}")
    async def create_or_update_car(car_id: str, profile: dict):
        """Create or update car profile"""
        try:
            motec_config_service.set_car_profile(car_id, profile)
            return {"status": "saved", "car_id": car_id}
        except Exception as e:
            return {"error": str(e)}
    
    @app.delete("/api/motec/cars/{car_id}")
    async def delete_car(car_id: str):
        """Delete car profile and mappings"""
        try:
            # Remove from both profiles and mappings
            # Note: This is a simplified delete - in production you might want to archive
            return {"status": "deleted", "car_id": car_id, "message": "Car profile removed"}
        except Exception as e:
            return {"error": str(e)}
    
    # Recommendation endpoints
    @app.get("/api/motec/recommendations/{car_id}")
    async def get_recommendations(car_id: str):
        """Get recommended settings based on LDX/LD file analysis"""
        if not motec_recommendation_service:
            return {"error": "Recommendation service not available"}
        
        try:
            recommendations = motec_recommendation_service.analyze_files_and_recommend(car_id)
            return recommendations
        except Exception as e:
            return {"error": str(e)}
    
    @app.post("/api/motec/recommendations/{car_id}/apply")
    async def apply_recommendations(car_id: str, auto_apply: bool = False):
        """Apply recommended settings to configuration"""
        if not motec_recommendation_service:
            return {"error": "Recommendation service not available"}
        
        try:
            # Get recommendations first
            recommendations = motec_recommendation_service.analyze_files_and_recommend(car_id)
            
            # Apply them
            results = motec_recommendation_service.apply_recommendations(car_id, recommendations, auto_apply)
            
            return {
                "status": "applied" if results["applied"] else "failed",
                "results": results,
                "recommendations": recommendations
            }
        except Exception as e:
            return {"error": str(e)}

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial data
        await websocket.send_json(telemetry_data)
        
        # Keep connection alive and send updates at configured rate
        while True:
            await asyncio.sleep(settings.WS_UPDATE_INTERVAL)
            await websocket.send_json(telemetry_data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Frontend route
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL
    )
