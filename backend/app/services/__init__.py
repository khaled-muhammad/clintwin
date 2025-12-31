"""
ClinTwin Services
=================
Core business logic for each module.

Services are imported lazily to avoid loading heavy dependencies
(TensorFlow, EasyOCR, etc.) at startup.
"""

def get_pill_akinator_service():
    """Get Pill Akinator service (lazy import)."""
    from app.services.pill_akinator import get_akinator_service
    return get_akinator_service()

def get_image_identifier_service():
    """Get Image Identifier service (lazy import)."""
    from app.services.image_identifier import get_image_service
    return get_image_service()

def get_interaction_checker_service():
    """Get Interaction Checker service (lazy import)."""
    from app.services.interaction_checker import get_interaction_service
    return get_interaction_service()

__all__ = [
    "get_pill_akinator_service",
    "get_image_identifier_service", 
    "get_interaction_checker_service"
]
