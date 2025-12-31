"""
History Models
==============
Data models for scan history and favorites.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ScanType(str, Enum):
    """Type of scan/identification."""
    IMAGE = "image"
    AKINATOR = "akinator"
    BARCODE = "barcode"


class ScanHistoryItem(BaseModel):
    """Record of a medicine identification."""
    id: str = Field(..., description="Unique scan ID")
    user_id: str = Field(default="anonymous", description="User identifier")
    medicine_id: str = Field(..., description="Identified medicine ID")
    medicine_name: str = Field(..., description="Medicine name")
    medicine_name_ar: Optional[str] = Field(None, description="Arabic name")
    scan_type: ScanType = Field(..., description="How medicine was identified")
    confidence: float = Field(..., ge=0, le=1, description="Identification confidence")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FavoriteItem(BaseModel):
    """User's saved/bookmarked medicine."""
    id: str = Field(..., description="Favorite entry ID")
    user_id: str = Field(default="anonymous", description="User identifier")
    medicine_id: str = Field(..., description="Medicine ID")
    medicine_name: str = Field(..., description="Medicine name")
    medicine_name_ar: Optional[str] = Field(None, description="Arabic name")
    notes: Optional[str] = Field(None, description="User notes")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ReminderFrequency(str, Enum):
    """Medication reminder frequency."""
    ONCE_DAILY = "once_daily"
    TWICE_DAILY = "twice_daily"
    THREE_TIMES_DAILY = "three_times_daily"
    FOUR_TIMES_DAILY = "four_times_daily"
    AS_NEEDED = "as_needed"
    CUSTOM = "custom"


class MedicationReminder(BaseModel):
    """Medication reminder schedule."""
    id: str = Field(..., description="Reminder ID")
    user_id: str = Field(default="anonymous", description="User identifier")
    medicine_id: str = Field(..., description="Medicine ID")
    medicine_name: str = Field(..., description="Medicine name")
    dosage: str = Field(..., description="Dosage amount")
    frequency: ReminderFrequency = Field(..., description="How often to take")
    times: List[str] = Field(default_factory=list, description="Times of day (HH:MM)")
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = Field(None, description="End date if limited course")
    is_active: bool = Field(True, description="Whether reminder is active")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
