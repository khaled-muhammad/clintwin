"""
Drug Interaction Checker API Routes
===================================
Endpoints for checking drug-drug interactions.

Endpoints:
- POST /check - Check interactions between medicines
- GET /medicine/{id}/interactions - Get all interactions for a medicine
- GET /medicines - Get list of all medicines for selection
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional

from app.services.interaction_checker import get_interaction_service

router = APIRouter()


# ==================
# Request/Response Models
# ==================

class InteractionCheckRequest(BaseModel):
    """Request to check interactions between medicines."""
    medicine_ids: List[str] = Field(
        ..., 
        min_length=1,
        description="List of medicine IDs or names to check"
    )
    include_groups: bool = Field(
        True, 
        description="Include drug class interactions"
    )


class InteractionWarning(BaseModel):
    """A specific interaction warning."""
    severity: str
    title: str
    drugs_involved: List[str]
    message: str
    recommendation: str
    clinical_effects: List[str] = Field(default_factory=list)
    symptoms_to_watch: List[str] = Field(default_factory=list)
    monitoring: Optional[str] = None


class InteractionCheckResponse(BaseModel):
    """Response from interaction check."""
    success: bool
    medicines_checked: List[str]
    interactions_found: List[dict]
    warnings: List[InteractionWarning]
    has_contraindicated: bool = Field(False, description="Contains contraindicated combination")
    has_major: bool = Field(False, description="Contains major interaction")
    risk_level: str = Field(..., description="Overall risk: safe/low/moderate/high/critical")
    summary: str = Field(..., description="Human-readable summary")
    safe_alternatives: List[dict] = Field(default_factory=list)


class MedicineInteractionsResponse(BaseModel):
    """Response with all interactions for a single medicine."""
    success: bool
    medicine: str
    drug_groups: List[str]
    total_interactions: int
    interactions_by_severity: dict
    caution_with: List[str] = Field(default_factory=list, description="Drugs to use with caution")


class MedicineListItem(BaseModel):
    """Medicine item for selection list."""
    id: str
    name: str
    generic_name: Optional[str]
    category: Optional[str]
    requires_prescription: bool = True


# ==================
# API Endpoints
# ==================

@router.post("/check", response_model=InteractionCheckResponse)
async def check_interactions(request: InteractionCheckRequest):
    """
    Check for drug interactions between multiple medicines.
    
    Checks all pairs of provided medicines for known interactions,
    including drug class interactions if enabled.
    
    Args:
        request: Medicine IDs/names and options
        
    Returns:
        Comprehensive interaction check result
        
    Example Request:
    ```json
    {
        "medicine_ids": ["med_002", "med_004"],
        "include_groups": true
    }
    ```
    
    Example Response:
    ```json
    {
        "success": true,
        "medicines_checked": ["Brufen 400", "Cataflam 50"],
        "interactions_found": [{
            "id": "int_006",
            "drugs_involved": ["Brufen 400", "Cataflam 50"],
            "severity": "major",
            "description": "Using multiple NSAIDs together...",
            "recommendation": "Never use more than one NSAID at a time"
        }],
        "warnings": [{
            "severity": "major",
            "title": "🔴 Major Interaction Warning",
            "drugs_involved": ["NSAIDs", "NSAIDs"],
            "message": "Using multiple NSAIDs together significantly increases...",
            "recommendation": "Never use more than one NSAID at a time"
        }],
        "has_contraindicated": false,
        "has_major": true,
        "risk_level": "high",
        "summary": "🔴 HIGH RISK: Major interaction(s) found...",
        "safe_alternatives": [{
            "for_medicine": "Brufen 400",
            "alternative": {"name": "Panadol Extra", ...},
            "reason": "Safer alternative..."
        }]
    }
    ```
    """
    service = get_interaction_service()
    
    if len(request.medicine_ids) < 1:
        raise HTTPException(
            status_code=400, 
            detail="At least one medicine ID is required"
        )
    
    try:
        result = service.check_interactions(
            request.medicine_ids,
            request.include_groups
        )
        return InteractionCheckResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interaction check failed: {str(e)}")


@router.post("/check-by-names")
async def check_interactions_by_names(
    medicine_names: List[str] = Query(..., description="Medicine names to check")
):
    """
    Check interactions by medicine names.
    
    Convenience endpoint that accepts names instead of IDs.
    
    Args:
        medicine_names: List of medicine names
        
    Returns:
        Interaction check result
    """
    service = get_interaction_service()
    
    if len(medicine_names) < 2:
        return {
            "success": True,
            "message": "Need at least 2 medicines to check interactions",
            "medicines_checked": medicine_names,
            "risk_level": "safe"
        }
    
    try:
        result = service.check_by_names(medicine_names)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interaction check failed: {str(e)}")


@router.get("/medicine/{medicine_id}/interactions", response_model=MedicineInteractionsResponse)
async def get_medicine_interactions(medicine_id: str):
    """
    Get all known interactions for a single medicine.
    
    Returns all potential interactions, useful for showing
    warnings when adding a medicine to a patient's list.
    
    Args:
        medicine_id: Medicine ID or name
        
    Returns:
        All known interactions grouped by severity
        
    Example Response:
    ```json
    {
        "success": true,
        "medicine": "Brufen 400",
        "drug_groups": ["NSAIDs", "painkillers"],
        "total_interactions": 5,
        "interactions_by_severity": {
            "contraindicated": [],
            "major": [{
                "interacts_with": "Warfarin",
                "severity": "major",
                "description": "NSAIDs increase bleeding risk..."
            }],
            "moderate": [...],
            "minor": [...]
        },
        "caution_with": ["Warfarin", "Alcohol"]
    }
    ```
    """
    service = get_interaction_service()
    
    try:
        result = service.check_single_drug(medicine_id)
        
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error", "Medicine not found"))
        
        return MedicineInteractionsResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get interactions: {str(e)}")


@router.get("/medicines", response_model=List[MedicineListItem])
async def get_medicines_list():
    """
    Get list of all medicines for selection UI.
    
    Returns a simplified list suitable for dropdown/autocomplete
    selection in the interaction checker UI.
    
    Returns:
        List of medicines with basic info
    """
    service = get_interaction_service()
    
    try:
        medicines = service.get_all_medicines()
        return [MedicineListItem(**m) for m in medicines]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get medicines: {str(e)}")


@router.get("/medicines/search")
async def search_medicines(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Max results")
):
    """
    Search medicines by name.
    
    Returns medicines matching the search query for autocomplete.
    
    Args:
        q: Search query string
        limit: Maximum number of results
        
    Returns:
        Matching medicines
    """
    service = get_interaction_service()
    query = q.lower()
    
    matches = []
    for med in service.medicines:
        # Search in name, generic name, and category
        if (query in med["name"].lower() or
            query in med.get("generic_name", "").lower() or
            query in med.get("category", "").lower()):
            matches.append({
                "id": med["id"],
                "name": med["name"],
                "generic_name": med.get("generic_name"),
                "category": med.get("category")
            })
            if len(matches) >= limit:
                break
    
    return {"query": q, "results": matches, "count": len(matches)}


@router.get("/severity-levels")
async def get_severity_levels():
    """
    Get information about interaction severity levels.
    
    Useful for displaying legends/help in the UI.
    
    Returns:
        Severity level descriptions
    """
    return {
        "levels": [
            {
                "level": "contraindicated",
                "emoji": "⛔",
                "color": "#DC2626",
                "title": "Contraindicated",
                "description": "These medicines should NEVER be taken together. Combination is absolutely prohibited due to severe risk."
            },
            {
                "level": "major",
                "emoji": "🔴",
                "color": "#EF4444",
                "title": "Major Interaction",
                "description": "High risk of serious harm. Avoid this combination unless no alternative exists and close monitoring is available."
            },
            {
                "level": "moderate",
                "emoji": "🟡",
                "color": "#F59E0B",
                "title": "Moderate Interaction",
                "description": "May require dose adjustment or monitoring. Discuss with your doctor or pharmacist."
            },
            {
                "level": "minor",
                "emoji": "🟢",
                "color": "#10B981",
                "title": "Minor Interaction",
                "description": "Minimal clinical significance. Generally safe but be aware of potential effects."
            },
            {
                "level": "safe",
                "emoji": "✅",
                "color": "#059669",
                "title": "No Known Interaction",
                "description": "No documented interaction. These medicines appear safe to take together."
            }
        ]
    }
