"""
Image Identifier API Routes
===========================
Endpoints for image-based medicine identification.

Endpoints:
- POST /upload - Upload image for identification
- POST /extract - Extract text/info from image only
- GET /formats - Get supported image formats
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, List
import base64

from app.services.image_identifier import get_image_service

router = APIRouter()


# ==================
# Request/Response Models
# ==================

class IdentificationResult(BaseModel):
    """Response from image identification."""
    request_id: str = Field(..., description="Unique request identifier")
    success: bool = Field(..., description="Whether identification succeeded")
    top_match: Optional[dict] = Field(None, description="Best matching medicine with details")
    alternatives: List[dict] = Field(default_factory=list, description="Alternative matches")
    extracted_text: List[str] = Field(default_factory=list, description="Text extracted from image")
    message: Optional[str] = Field(None, description="Status message or error")


class ExtractionResult(BaseModel):
    """Response from text extraction only."""
    success: bool
    extracted_text: dict = Field(default_factory=dict, description="Categorized extracted text")
    raw_text: List[str] = Field(default_factory=list, description="All extracted text")
    text_count: int = Field(0, description="Number of text items found")


class Base64ImageRequest(BaseModel):
    """Request with base64-encoded image."""
    image_data: str = Field(..., description="Base64-encoded image data")
    image_format: str = Field("jpeg", description="Image format (jpeg, png, etc.)")


# ==================
# API Endpoints
# ==================

@router.post("/upload", response_model=IdentificationResult)
async def upload_image(file: UploadFile = File(...)):
    """
    Upload an image for medicine identification.
    
    Accepts a medicine image (pill, box, strip, bottle, syrup) and
    uses CNN + OCR to identify the medicine.
    
    Supported formats: JPEG, PNG, GIF, BMP, WebP
    Maximum size: 10MB
    
    Args:
        file: Uploaded image file
        
    Returns:
        Identification result with medicine info and confidence
        
    Example Response:
    ```json
    {
        "request_id": "uuid",
        "success": true,
        "top_match": {
            "medicine": {
                "id": "med_001",
                "name": "Panadol Extra",
                "generic_name": "Paracetamol + Caffeine",
                "dosage_form": "tablet",
                "main_use": "Pain relief and fever",
                "warnings": ["Do not exceed 8 tablets/day"],
                ...
            },
            "confidence": 0.92,
            "identification_sources": ["cnn", "ocr"]
        },
        "alternatives": [...],
        "extracted_text": ["PANADOL", "500mg", "GSK"]
    }
    ```
    """
    service = get_image_service()
    
    # Validate file type
    if not file.content_type:
        raise HTTPException(status_code=400, detail="Could not determine file type")
    
    content_type = file.content_type.lower()
    if not any(fmt in content_type for fmt in ["jpeg", "jpg", "png", "gif", "bmp", "webp"]):
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported image format: {content_type}. Supported: JPEG, PNG, GIF, BMP, WebP"
        )
    
    # Read file
    try:
        image_data = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
    
    # Check size
    if len(image_data) > service.get_max_image_size():
        raise HTTPException(
            status_code=400, 
            detail=f"Image too large. Maximum size: {service.get_max_image_size() // (1024*1024)}MB"
        )
    
    # Identify
    try:
        result = await service.identify_image(image_data)
        return IdentificationResult(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Identification failed: {str(e)}")


@router.post("/identify-base64", response_model=IdentificationResult)
async def identify_base64_image(request: Base64ImageRequest):
    """
    Identify medicine from base64-encoded image.
    
    Alternative to file upload for web/mobile clients that
    prefer to send images as base64 strings.
    
    Args:
        request: Base64-encoded image data
        
    Returns:
        Identification result
    """
    service = get_image_service()
    
    # Decode base64
    try:
        # Remove data URL prefix if present
        image_b64 = request.image_data
        if "," in image_b64:
            image_b64 = image_b64.split(",")[1]
        
        image_data = base64.b64decode(image_b64)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 data: {str(e)}")
    
    # Check size
    if len(image_data) > service.get_max_image_size():
        raise HTTPException(status_code=400, detail="Image too large")
    
    # Identify
    try:
        result = await service.identify_image(image_data)
        return IdentificationResult(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Identification failed: {str(e)}")


@router.post("/extract", response_model=ExtractionResult)
async def extract_text(file: UploadFile = File(...)):
    """
    Extract text information from medicine image without identification.
    
    Useful for reading dosage, warnings, ingredients, etc.
    from packaging when identification is not needed.
    
    Args:
        file: Uploaded image file
        
    Returns:
        Categorized extracted text
        
    Example Response:
    ```json
    {
        "success": true,
        "extracted_text": {
            "medicine_name": ["Panadol Extra"],
            "dosage": ["500mg", "Take 1-2 tablets"],
            "warnings": ["Do not exceed..."],
            "ingredients": ["Paracetamol", "Caffeine"],
            "other": ["GSK", "Made in Egypt"]
        },
        "raw_text": [...],
        "text_count": 12
    }
    ```
    """
    service = get_image_service()
    
    try:
        image_data = await file.read()
        result = service.extract_info_only(image_data)
        return ExtractionResult(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.get("/formats")
async def get_supported_formats():
    """
    Get list of supported image formats and constraints.
    
    Returns:
        Supported formats and size limits
    """
    service = get_image_service()
    
    return {
        "supported_formats": service.get_supported_formats(),
        "max_size_bytes": service.get_max_image_size(),
        "max_size_mb": service.get_max_image_size() // (1024 * 1024),
        "recommended_resolution": "640x480 minimum, 1920x1080 optimal",
        "tips": [
            "Ensure good lighting",
            "Include the medicine name in the frame",
            "For pills, photograph against a contrasting background",
            "Box front typically provides best identification"
        ]
    }


@router.post("/capture")
async def capture_from_camera(
    image_data: str = Form(...),
    source: str = Form("camera")
):
    """
    Identify from camera capture (for mobile/web camera).
    
    Receives image data from camera capture as base64.
    
    Args:
        image_data: Base64-encoded captured image
        source: Capture source (camera/gallery)
        
    Returns:
        Identification result
    """
    service = get_image_service()
    
    try:
        # Remove data URL prefix if present
        if "," in image_data:
            image_data = image_data.split(",")[1]
        
        decoded = base64.b64decode(image_data)
        result = await service.identify_image(decoded)
        
        result["capture_source"] = source
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Capture processing failed: {str(e)}")
