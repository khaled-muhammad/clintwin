"""
Medicines API Routes
====================
Consolidated medicine endpoints with pagination, search, and alternatives.

Endpoints:
- GET /list - Get all medicines with pagination
- GET /search - Search medicines with fuzzy matching
- GET /{id} - Get medicine details
- GET /{id}/alternatives - Get alternative medicines
"""
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

from app.utils.i18n import get_language, localize_medicine, localize_medicines
from app.utils.cache import cached

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================
# Response Models
# ==================

class MedicineBasic(BaseModel):
    """Basic medicine info for lists."""
    id: str
    name: str
    name_arabic: Optional[str] = None
    display_name: str
    generic_name: Optional[str] = None
    category: Optional[str] = None
    dosage_form: Optional[str] = None
    requires_prescription: bool = False


class MedicineDetail(BaseModel):
    """Full medicine details."""
    id: str
    name: str
    name_arabic: Optional[str] = None
    display_name: str
    generic_name: Optional[str] = None
    manufacturer: Optional[str] = None
    dosage_form: Optional[str] = None
    drug_class: Optional[str] = None
    category: Optional[str] = None
    strength: Optional[str] = None
    available_strengths: List[str] = Field(default_factory=list)
    main_use: Optional[str] = None
    indications: List[str] = Field(default_factory=list)
    contraindications: List[str] = Field(default_factory=list)
    side_effects: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    adult_dosage: Optional[str] = None
    child_dosage: Optional[str] = None
    requires_prescription: bool = False
    visual: Optional[dict] = None


class PaginatedMedicines(BaseModel):
    """Paginated medicine list response."""
    success: bool = True
    medicines: List[MedicineBasic]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class SearchResult(BaseModel):
    """Search result response."""
    success: bool = True
    query: str
    results: List[MedicineBasic]
    count: int


class AlternativeMedicine(BaseModel):
    """Alternative medicine suggestion."""
    medicine: MedicineBasic
    reason: str
    reason_ar: str


# ==================
# Helper Functions  
# ==================

def _get_medicines_service():
    """Get medicine data from interaction service."""
    from app.services.interaction_checker import get_interaction_service
    return get_interaction_service()


def _fuzzy_match(query: str, text: str) -> bool:
    """Simple fuzzy matching."""
    query = query.lower().strip()
    text = text.lower()
    
    # Exact substring match
    if query in text:
        return True
    
    # Check if all query words are in text
    query_words = query.split()
    return all(word in text for word in query_words)


def _calculate_match_score(query: str, medicine: dict) -> float:
    """Calculate relevance score for search ranking."""
    query = query.lower().strip()
    score = 0.0
    
    # Exact name match
    if query == medicine.get("name", "").lower():
        score += 100
    elif query in medicine.get("name", "").lower():
        score += 50
    
    # Arabic name match
    if query in medicine.get("name_arabic", "").lower():
        score += 40
    
    # Generic name match
    if query in medicine.get("generic_name", "").lower():
        score += 30
    
    # Category match
    if query in medicine.get("category", "").lower():
        score += 10
    
    # Drug class match
    if query in medicine.get("drug_class", "").lower():
        score += 10
    
    return score


# ==================
# API Endpoints
# ==================

@router.get("/list", response_model=PaginatedMedicines)
async def list_medicines(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    prescription_only: Optional[bool] = Query(None, description="Filter by prescription requirement")
):
    """
    Get paginated list of all medicines.
    
    Supports filtering by category and prescription requirement.
    Results are localized based on Accept-Language header.
    
    Example Response:
    ```json
    {
        "success": true,
        "medicines": [
            {"id": "med_001", "name": "Panadol Extra", "display_name": "بانادول اكسترا", ...}
        ],
        "total": 16,
        "page": 1,
        "page_size": 20,
        "total_pages": 1,
        "has_next": false,
        "has_prev": false
    }
    ```
    """
    lang = get_language(request)
    service = _get_medicines_service()
    
    # Filter medicines
    medicines = service.medicines.copy()
    
    if category:
        medicines = [m for m in medicines if m.get("category") == category]
    
    if prescription_only is not None:
        medicines = [m for m in medicines if m.get("requires_prescription") == prescription_only]
    
    # Paginate
    total = len(medicines)
    total_pages = (total + page_size - 1) // page_size
    start = (page - 1) * page_size
    end = start + page_size
    page_medicines = medicines[start:end]
    
    # Localize
    localized = localize_medicines(page_medicines, lang)
    
    return PaginatedMedicines(
        medicines=[MedicineBasic(**m) for m in localized],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )


@router.get("/search", response_model=SearchResult)
async def search_medicines(
    request: Request,
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results")
):
    """
    Search medicines by name, generic name, or category.
    
    Uses fuzzy matching to handle typos and partial matches.
    Results are ranked by relevance and localized.
    
    Args:
        q: Search query (min 1 character)
        limit: Maximum number of results
        
    Example:
        GET /api/medicines/search?q=panadol
        GET /api/medicines/search?q=pain&limit=5
    """
    lang = get_language(request)
    service = _get_medicines_service()
    
    # Search and score
    scored_results = []
    for medicine in service.medicines:
        score = _calculate_match_score(q, medicine)
        if score > 0:
            scored_results.append((medicine, score))
    
    # Sort by score descending
    scored_results.sort(key=lambda x: x[1], reverse=True)
    
    # Take top results
    results = [m for m, _ in scored_results[:limit]]
    
    # Localize
    localized = localize_medicines(results, lang)
    
    return SearchResult(
        query=q,
        results=[MedicineBasic(**m) for m in localized],
        count=len(localized)
    )


@router.get("/categories")
async def get_categories(request: Request):
    """
    Get all medicine categories.
    
    Returns list of unique categories for filtering.
    """
    lang = get_language(request)
    service = _get_medicines_service()
    
    categories = set()
    for med in service.medicines:
        if med.get("category"):
            categories.add(med["category"])
    
    # Category translations
    category_names = {
        "pain_relief": {"en": "Pain Relief", "ar": "مسكنات الألم"},
        "antibiotic": {"en": "Antibiotics", "ar": "المضادات الحيوية"},
        "cardiovascular": {"en": "Cardiovascular", "ar": "أدوية القلب والأوعية"},
        "gastrointestinal": {"en": "Gastrointestinal", "ar": "أدوية الجهاز الهضمي"},
        "respiratory": {"en": "Respiratory", "ar": "أدوية الجهاز التنفسي"},
        "psychiatric": {"en": "Psychiatric", "ar": "الأدوية النفسية"}
    }
    
    result = []
    for cat in sorted(categories):
        names = category_names.get(cat, {"en": cat, "ar": cat})
        result.append({
            "id": cat,
            "name": names.get(lang, cat),
            "name_en": names.get("en", cat),
            "name_ar": names.get("ar", cat)
        })
    
    return {"categories": result, "count": len(result)}


@router.get("/{medicine_id}", response_model=MedicineDetail)
async def get_medicine_details(
    medicine_id: str,
    request: Request
):
    """
    Get full details for a specific medicine.
    
    Returns all available information including dosage,
    contraindications, side effects, and visual attributes.
    """
    lang = get_language(request)
    service = _get_medicines_service()
    
    # Find medicine
    medicine = None
    for med in service.medicines:
        if med["id"] == medicine_id:
            medicine = med
            break
    
    if not medicine:
        raise HTTPException(
            status_code=404,
            detail={
                "error_code": "MEDICINE_NOT_FOUND",
                "message": "Medicine not found" if lang == "en" else "الدواء غير موجود"
            }
        )
    
    # Localize
    localized = localize_medicine(medicine, lang)
    
    return MedicineDetail(**localized)


@router.get("/{medicine_id}/alternatives")
async def get_medicine_alternatives(
    medicine_id: str,
    request: Request,
    limit: int = Query(5, ge=1, le=20, description="Maximum alternatives")
):
    """
    Get alternative medicines for a specific drug.
    
    Returns medicines with similar indications or in the same category
    that could be considered as substitutes.
    """
    lang = get_language(request)
    service = _get_medicines_service()
    
    # Find target medicine
    target = None
    for med in service.medicines:
        if med["id"] == medicine_id:
            target = med
            break
    
    if not target:
        raise HTTPException(
            status_code=404,
            detail={
                "error_code": "MEDICINE_NOT_FOUND",
                "message": "Medicine not found" if lang == "en" else "الدواء غير موجود"
            }
        )
    
    # Find alternatives (same category, different medicine)
    alternatives = []
    target_category = target.get("category", "")
    target_indications = set(target.get("indications", []))
    
    for med in service.medicines:
        if med["id"] == medicine_id:
            continue
        
        # Same category
        if med.get("category") == target_category:
            med_indications = set(med.get("indications", []))
            common_indications = target_indications & med_indications
            
            if common_indications:
                reason = f"Similar use: {', '.join(list(common_indications)[:2])}"
                reason_ar = f"استخدام مشابه: {', '.join(list(common_indications)[:2])}"
            else:
                reason = f"Same category: {target_category}"
                reason_ar = f"نفس الفئة: {target_category}"
            
            localized_med = localize_medicine(med, lang)
            alternatives.append(AlternativeMedicine(
                medicine=MedicineBasic(**localized_med),
                reason=reason,
                reason_ar=reason_ar
            ))
            
            if len(alternatives) >= limit:
                break
    
    target_localized = localize_medicine(target, lang)
    
    return {
        "success": True,
        "medicine": MedicineBasic(**target_localized),
        "alternatives": alternatives,
        "count": len(alternatives)
    }
