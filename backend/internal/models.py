"""
Pydantic models for parameter management system
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Parameter(BaseModel):
    """Current parameter state"""
    id: Optional[int] = None
    parameter_name: str
    subteam: str
    current_value: str
    updated_at: str
    updated_by: str
    
    class Config:
        from_attributes = True


class ParameterUpdate(BaseModel):
    """Form submission for updating a parameter"""
    parameter_name: str = Field(..., min_length=1, description="Parameter name")
    subteam: str = Field(..., min_length=1, description="Subteam name")
    new_value: str = Field(..., description="New parameter value")
    comment: Optional[str] = Field(None, description="Optional comment about the change")
    queue: bool = Field(False, description="Whether to add to queue for admin approval")
    
    class Config:
        json_schema_extra = {
            "example": {
                "parameter_name": "max_rpm",
                "subteam": "Engine",
                "new_value": "8500",
                "comment": "Increased for testing",
                "queue": False
            }
        }


class ParameterHistory(BaseModel):
    """Audit trail entry"""
    id: int
    parameter_id: int
    parameter_name: str
    subteam: str
    prior_value: Optional[str]
    new_value: str
    updated_by: str
    updated_at: str
    comment: Optional[str] = None
    form_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class QueueItem(BaseModel):
    """Queue item for pending parameter changes"""
    id: int
    parameter_name: str
    subteam: str
    new_value: str
    current_value: Optional[str]
    submitted_by: str
    submitted_at: str
    comment: Optional[str] = None
    status: str
    form_id: str
    
    class Config:
        from_attributes = True


class User(BaseModel):
    """User with role"""
    id: int
    username: str
    role: str
    subteam: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """Create user request"""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    role: str = Field("user", description="Role: admin, user")
    subteam: str = Field(..., min_length=1, description="Subteam assignment (required)")


class Car(BaseModel):
    """Car identification"""
    id: int
    car_identifier: str
    display_name: Optional[str] = None
    created_at: str
    last_seen_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class CarCreate(BaseModel):
    """Create car request"""
    car_identifier: str = Field(..., min_length=1, description="Unique car identifier")
    display_name: Optional[str] = Field(None, description="Display name for the car")


class CarParameterDefinition(BaseModel):
    """Car parameter definition with link key support"""
    parameter_name: str = Field(..., description="Snake case parameter name (for backward compatibility)")
    display_name: str = Field(..., description="Human-readable display name")
    subteam: str = Field(..., description="Subteam name")
    unit: str = Field(..., description="Unit of measurement")
    default_value: str = Field(..., description="Default value")
    min_value: Optional[str] = Field(None, description="Minimum allowed value")
    max_value: Optional[str] = Field(None, description="Maximum allowed value")
    motec_channel: Optional[str] = Field(None, description="MoTeC channel name")
    description: Optional[str] = Field(None, description="Description text")
    link_key: Optional[str] = Field(None, description="Link key identifier (composite key)")
    tab: Optional[str] = Field(None, description="Tab/category name")
    inject_type: Optional[str] = Field(None, description="Inject type: Constant or Comment")
    variable_name: Optional[str] = Field(None, description="Variable name from CSV")
    type: Optional[str] = Field(None, description="Parameter type: int, float, string, dropdown")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "parameter_name": "damper_fl_hs_rebound",
                "display_name": "FL HS Rebound",
                "subteam": "Suspension",
                "tab": "Damper",
                "link_key": "suspension_damper_fl_hs_rebound",
                "unit": "turns",
                "default_value": "0",
                "type": "int",
                "inject_type": "Constant"
            }
        }
