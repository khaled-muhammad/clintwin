"""
History API Routes
==================
Scan history, favorites, and medication reminders.

Endpoints:
- POST /scans - Record a new scan
- GET /scans - Get scan history
- POST /favorites - Add favorite
- GET /favorites - Get favorites
- DELETE /favorites/{id} - Remove favorite
- POST /reminders - Create reminder
- GET /reminders - Get reminders
"""
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid
import logging

from app.models.history import ScanHistoryItem, FavoriteItem, MedicationReminder, ScanType, ReminderFrequency
from app.utils.i18n import get_language

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================
# In-Memory Storage (Replace with DB in production)
# ==================
_scan_history: List[ScanHistoryItem] = []
_favorites: List[FavoriteItem] = []
_reminders: List[MedicationReminder] = []


# ==================
# Request Models
# ==================

class RecordScanRequest(BaseModel):
    """Request to record a scan."""
    medicine_id: str
    medicine_name: str
    medicine_name_ar: Optional[str] = None
    scan_type: ScanType = ScanType.IMAGE
    confidence: float = Field(1.0, ge=0, le=1)


class AddFavoriteRequest(BaseModel):
    """Request to add a favorite."""
    medicine_id: str
    medicine_name: str
    medicine_name_ar: Optional[str] = None
    notes: Optional[str] = None


class CreateReminderRequest(BaseModel):
    """Request to create a reminder."""
    medicine_id: str
    medicine_name: str
    dosage: str = "1 tablet"
    frequency: ReminderFrequency = ReminderFrequency.ONCE_DAILY
    times: List[str] = Field(default_factory=lambda: ["09:00"])
    end_date: Optional[datetime] = None
    notes: Optional[str] = None


# ==================
# Scan History Endpoints
# ==================

@router.post("/scans")
async def record_scan(
    request: Request,
    scan: RecordScanRequest
):
    """
    Record a new medicine scan/identification.
    
    Called after successful medicine identification to track history.
    """
    lang = get_language(request)
    
    item = ScanHistoryItem(
        id=str(uuid.uuid4())[:8],
        medicine_id=scan.medicine_id,
        medicine_name=scan.medicine_name,
        medicine_name_ar=scan.medicine_name_ar,
        scan_type=scan.scan_type,
        confidence=scan.confidence
    )
    
    _scan_history.insert(0, item)  # Add to front (most recent first)
    
    # Keep only last 100 items
    if len(_scan_history) > 100:
        _scan_history.pop()
    
    return {
        "success": True,
        "message": "تم تسجيل المسح" if lang == "ar" else "Scan recorded",
        "scan_id": item.id
    }


@router.get("/scans")
async def get_scan_history(
    request: Request,
    limit: int = Query(20, ge=1, le=100),
    scan_type: Optional[ScanType] = None
):
    """
    Get scan history.
    
    Returns recent medicine identifications, optionally filtered by type.
    """
    lang = get_language(request)
    
    items = _scan_history
    
    if scan_type:
        items = [i for i in items if i.scan_type == scan_type]
    
    items = items[:limit]
    
    return {
        "success": True,
        "scans": [
            {
                "id": i.id,
                "medicine_id": i.medicine_id,
                "display_name": i.medicine_name_ar if lang == "ar" and i.medicine_name_ar else i.medicine_name,
                "medicine_name": i.medicine_name,
                "medicine_name_ar": i.medicine_name_ar,
                "scan_type": i.scan_type.value,
                "confidence": i.confidence,
                "timestamp": i.timestamp.isoformat()
            }
            for i in items
        ],
        "count": len(items)
    }


@router.delete("/scans")
async def clear_scan_history(request: Request):
    """Clear all scan history."""
    lang = get_language(request)
    
    _scan_history.clear()
    
    return {
        "success": True,
        "message": "تم مسح السجل" if lang == "ar" else "History cleared"
    }


# ==================
# Favorites Endpoints
# ==================

@router.post("/favorites")
async def add_favorite(
    request: Request,
    favorite: AddFavoriteRequest
):
    """
    Add a medicine to favorites.
    
    Allows users to bookmark medicines for quick access.
    """
    lang = get_language(request)
    
    # Check if already favorited
    for f in _favorites:
        if f.medicine_id == favorite.medicine_id:
            return {
                "success": False,
                "message": "الدواء موجود بالفعل في المفضلة" if lang == "ar" else "Medicine already in favorites",
                "favorite_id": f.id
            }
    
    item = FavoriteItem(
        id=str(uuid.uuid4())[:8],
        medicine_id=favorite.medicine_id,
        medicine_name=favorite.medicine_name,
        medicine_name_ar=favorite.medicine_name_ar,
        notes=favorite.notes
    )
    
    _favorites.insert(0, item)
    
    return {
        "success": True,
        "message": "تمت الإضافة إلى المفضلة" if lang == "ar" else "Added to favorites",
        "favorite_id": item.id
    }


@router.get("/favorites")
async def get_favorites(request: Request):
    """Get all favorited medicines."""
    lang = get_language(request)
    
    return {
        "success": True,
        "favorites": [
            {
                "id": f.id,
                "medicine_id": f.medicine_id,
                "display_name": f.medicine_name_ar if lang == "ar" and f.medicine_name_ar else f.medicine_name,
                "medicine_name": f.medicine_name,
                "medicine_name_ar": f.medicine_name_ar,
                "notes": f.notes,
                "created_at": f.created_at.isoformat()
            }
            for f in _favorites
        ],
        "count": len(_favorites)
    }


@router.delete("/favorites/{favorite_id}")
async def remove_favorite(
    favorite_id: str,
    request: Request
):
    """Remove a medicine from favorites."""
    lang = get_language(request)
    
    for i, f in enumerate(_favorites):
        if f.id == favorite_id:
            _favorites.pop(i)
            return {
                "success": True,
                "message": "تمت الإزالة من المفضلة" if lang == "ar" else "Removed from favorites"
            }
    
    raise HTTPException(
        status_code=404,
        detail={
            "error_code": "NOT_FOUND",
            "message": "المفضلة غير موجودة" if lang == "ar" else "Favorite not found"
        }
    )


# ==================
# Reminders Endpoints
# ==================

@router.post("/reminders")
async def create_reminder(
    request: Request,
    reminder: CreateReminderRequest
):
    """
    Create a medication reminder.
    
    Sets up a schedule for medication reminders.
    """
    lang = get_language(request)
    
    item = MedicationReminder(
        id=str(uuid.uuid4())[:8],
        medicine_id=reminder.medicine_id,
        medicine_name=reminder.medicine_name,
        dosage=reminder.dosage,
        frequency=reminder.frequency,
        times=reminder.times,
        end_date=reminder.end_date,
        notes=reminder.notes
    )
    
    _reminders.append(item)
    
    return {
        "success": True,
        "message": "تم إنشاء التذكير" if lang == "ar" else "Reminder created",
        "reminder_id": item.id
    }


@router.get("/reminders")
async def get_reminders(
    request: Request,
    active_only: bool = Query(True, description="Only return active reminders")
):
    """Get medication reminders."""
    lang = get_language(request)
    
    items = _reminders
    if active_only:
        items = [r for r in items if r.is_active]
    
    # Frequency labels
    freq_labels = {
        "once_daily": {"en": "Once daily", "ar": "مرة يومياً"},
        "twice_daily": {"en": "Twice daily", "ar": "مرتين يومياً"},
        "three_times_daily": {"en": "Three times daily", "ar": "ثلاث مرات يومياً"},
        "four_times_daily": {"en": "Four times daily", "ar": "أربع مرات يومياً"},
        "as_needed": {"en": "As needed", "ar": "عند الحاجة"},
        "custom": {"en": "Custom", "ar": "مخصص"}
    }
    
    return {
        "success": True,
        "reminders": [
            {
                "id": r.id,
                "medicine_id": r.medicine_id,
                "medicine_name": r.medicine_name,
                "dosage": r.dosage,
                "frequency": r.frequency.value,
                "frequency_label": freq_labels.get(r.frequency.value, {}).get(lang, r.frequency.value),
                "times": r.times,
                "start_date": r.start_date.isoformat(),
                "end_date": r.end_date.isoformat() if r.end_date else None,
                "is_active": r.is_active,
                "notes": r.notes
            }
            for r in items
        ],
        "count": len(items)
    }


@router.delete("/reminders/{reminder_id}")
async def delete_reminder(
    reminder_id: str,
    request: Request
):
    """Delete a medication reminder."""
    lang = get_language(request)
    
    for i, r in enumerate(_reminders):
        if r.id == reminder_id:
            _reminders.pop(i)
            return {
                "success": True,
                "message": "تم حذف التذكير" if lang == "ar" else "Reminder deleted"
            }
    
    raise HTTPException(
        status_code=404,
        detail={
            "error_code": "NOT_FOUND",
            "message": "التذكير غير موجود" if lang == "ar" else "Reminder not found"
        }
    )


@router.patch("/reminders/{reminder_id}/toggle")
async def toggle_reminder(
    reminder_id: str,
    request: Request
):
    """Toggle a reminder's active status."""
    lang = get_language(request)
    
    for r in _reminders:
        if r.id == reminder_id:
            r.is_active = not r.is_active
            status = "مفعل" if r.is_active else "متوقف"
            status_en = "activated" if r.is_active else "deactivated"
            
            return {
                "success": True,
                "message": f"التذكير {status}" if lang == "ar" else f"Reminder {status_en}",
                "is_active": r.is_active
            }
    
    raise HTTPException(
        status_code=404,
        detail={
            "error_code": "NOT_FOUND", 
            "message": "التذكير غير موجود" if lang == "ar" else "Reminder not found"
        }
    )
