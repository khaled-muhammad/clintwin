"""
Dosage Calculator API Routes
============================
Endpoints for medication dosage calculations.

Endpoints:
- POST /calculate - Calculate dosage based on patient parameters
- GET /age-categories - Get age category definitions
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

from app.services.dosage_calculator import get_dosage_service
from app.utils.i18n import get_language

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================
# Request/Response Models
# ==================

class DosageRequest(BaseModel):
    """Request for dosage calculation."""
    medicine_id: str = Field(..., description="Medicine ID")
    weight_kg: Optional[float] = Field(None, ge=0.5, le=300, description="Patient weight in kg")
    age_years: Optional[float] = Field(None, ge=0, le=120, description="Patient age in years")
    conditions: Optional[List[str]] = Field(
        default_factory=list,
        description="Special conditions: renal_impairment, hepatic_impairment, pregnancy, elderly"
    )


class DosageResponse(BaseModel):
    """Response with calculated dosage."""
    success: bool
    medicine_id: str
    medicine_name: str
    medicine_name_ar: str
    recommended_dose: str
    recommended_dose_ar: str
    calculation_method: str
    age_category: str
    is_pediatric: bool
    calculated_single_dose_mg: Optional[float] = None
    max_daily_dose_mg: Optional[float] = None
    frequency: Optional[str] = None
    frequency_ar: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    warnings_ar: List[str] = Field(default_factory=list)
    contraindications: List[str] = Field(default_factory=list)


# ==================
# API Endpoints
# ==================

@router.post("/calculate", response_model=DosageResponse)
async def calculate_dosage(
    request: Request,
    dosage_request: DosageRequest
):
    """
    Calculate recommended dosage for a medicine.
    
    Supports weight-based dosing for pediatric patients
    and adjustments for special conditions.
    
    Example Request:
    ```json
    {
        "medicine_id": "med_001",
        "weight_kg": 25,
        "age_years": 8,
        "conditions": []
    }
    ```
    
    Example Response:
    ```json
    {
        "success": true,
        "medicine_id": "med_001",
        "medicine_name": "Panadol Extra",
        "recommended_dose": "375mg every 4-6 hours",
        "calculation_method": "weight_based",
        "is_pediatric": true,
        "calculated_single_dose_mg": 375,
        "max_daily_dose_mg": 1500,
        "warnings": ["Do not exceed 8 tablets in 24 hours"]
    }
    ```
    """
    lang = get_language(request)
    service = get_dosage_service()
    
    result = service.calculate_dosage(
        medicine_id=dosage_request.medicine_id,
        weight_kg=dosage_request.weight_kg,
        age_years=dosage_request.age_years,
        conditions=dosage_request.conditions
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=404,
            detail={
                "error_code": "MEDICINE_NOT_FOUND",
                "message": result.get("error_ar" if lang == "ar" else "error")
            }
        )
    
    return DosageResponse(**result)


@router.get("/age-categories")
async def get_age_categories(request: Request):
    """
    Get age category definitions used for dosing.
    
    Returns the age ranges for each category.
    """
    lang = get_language(request)
    service = get_dosage_service()
    
    categories = []
    for key, value in service.AGE_CATEGORIES.items():
        # Arabic translations
        labels_ar = {
            "neonate": "حديث الولادة (0-1 شهر)",
            "infant": "رضيع (1-12 شهر)",
            "child": "طفل (1-12 سنة)",
            "adolescent": "مراهق (12-18 سنة)",
            "adult": "بالغ (18-65 سنة)",
            "elderly": "كبار السن (65+ سنة)"
        }
        
        categories.append({
            "id": key,
            "label": labels_ar.get(key, value["label"]) if lang == "ar" else value["label"],
            "min_years": value["min"],
            "max_years": value["max"]
        })
    
    return {"categories": categories}


@router.get("/conditions")
async def get_supported_conditions(request: Request):
    """
    Get list of supported special conditions for dosing adjustments.
    """
    lang = get_language(request)
    
    conditions = [
        {
            "id": "renal_impairment",
            "name": "قصور كلوي" if lang == "ar" else "Renal Impairment",
            "description": "يتطلب تعديل الجرعة" if lang == "ar" else "Requires dose adjustment"
        },
        {
            "id": "hepatic_impairment",
            "name": "قصور كبدي" if lang == "ar" else "Hepatic Impairment",
            "description": "يتطلب تعديل الجرعة" if lang == "ar" else "Requires dose adjustment"
        },
        {
            "id": "pregnancy",
            "name": "حمل" if lang == "ar" else "Pregnancy",
            "description": "استشر الطبيب" if lang == "ar" else "Consult physician"
        },
        {
            "id": "elderly",
            "name": "كبار السن" if lang == "ar" else "Elderly",
            "description": "قد يتطلب جرعة أقل" if lang == "ar" else "May require lower dose"
        }
    ]
    
    return {"conditions": conditions}
