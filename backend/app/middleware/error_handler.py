"""
Error Handler Middleware
========================
Structured error handling with Arabic/English support.
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional, Dict, Any
import logging
import traceback

logger = logging.getLogger(__name__)


class ClinTwinError(Exception):
    """Base exception for ClinTwin application."""
    
    def __init__(
        self,
        message: str,
        message_ar: str,
        error_code: str = "GENERAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.message_ar = message_ar
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class ValidationError(ClinTwinError):
    """Validation error with bilingual messages."""
    
    def __init__(self, message: str, message_ar: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            message_ar=message_ar,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )


class NotFoundError(ClinTwinError):
    """Resource not found error."""
    
    def __init__(self, resource: str, resource_ar: str):
        super().__init__(
            message=f"{resource} not found",
            message_ar=f"{resource_ar} غير موجود",
            error_code="NOT_FOUND",
            status_code=404
        )


class RateLimitError(ClinTwinError):
    """Rate limit exceeded error."""
    
    def __init__(self, retry_after: int = 60):
        super().__init__(
            message=f"Rate limit exceeded. Try again in {retry_after} seconds.",
            message_ar=f"تم تجاوز الحد المسموح. حاول مرة أخرى بعد {retry_after} ثانية.",
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={"retry_after": retry_after}
        )


class ServiceUnavailableError(ClinTwinError):
    """Service temporarily unavailable."""
    
    def __init__(self, service: str, service_ar: str):
        super().__init__(
            message=f"{service} service is temporarily unavailable",
            message_ar=f"خدمة {service_ar} غير متاحة مؤقتاً",
            error_code="SERVICE_UNAVAILABLE",
            status_code=503
        )


# Error messages for common scenarios
ERROR_MESSAGES = {
    "INVALID_SESSION": {
        "en": "Invalid or expired session",
        "ar": "جلسة غير صالحة أو منتهية الصلاحية"
    },
    "MEDICINE_NOT_FOUND": {
        "en": "Medicine not found in database",
        "ar": "الدواء غير موجود في قاعدة البيانات"
    },
    "INVALID_IMAGE": {
        "en": "Invalid or unsupported image format",
        "ar": "تنسيق صورة غير صالح أو غير مدعوم"
    },
    "LLM_ERROR": {
        "en": "AI service temporarily unavailable",
        "ar": "خدمة الذكاء الاصطناعي غير متاحة مؤقتاً"
    },
    "INTERACTION_CHECK_FAILED": {
        "en": "Failed to check drug interactions",
        "ar": "فشل في فحص التفاعلات الدوائية"
    },
    "INTERNAL_ERROR": {
        "en": "An unexpected error occurred",
        "ar": "حدث خطأ غير متوقع"
    }
}


def get_accept_language(request: Request) -> str:
    """Extract preferred language from Accept-Language header."""
    accept_lang = request.headers.get("Accept-Language", "en")
    if "ar" in accept_lang.lower():
        return "ar"
    return "en"


def create_error_response(
    error_code: str,
    message: str,
    message_ar: str,
    status_code: int = 500,
    details: Optional[Dict] = None,
    language: str = "en"
) -> Dict[str, Any]:
    """Create structured error response."""
    response = {
        "success": False,
        "error_code": error_code,
        "message": message_ar if language == "ar" else message,
        "message_en": message,
        "message_ar": message_ar
    }
    if details:
        response["details"] = details
    return response


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Global error handler middleware.
    
    Catches all exceptions and returns structured bilingual responses.
    """
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
            
        except ClinTwinError as e:
            logger.warning(f"Application error: {e.error_code} - {e.message}")
            language = get_accept_language(request)
            
            return JSONResponse(
                status_code=e.status_code,
                content=create_error_response(
                    error_code=e.error_code,
                    message=e.message,
                    message_ar=e.message_ar,
                    status_code=e.status_code,
                    details=e.details,
                    language=language
                )
            )
            
        except HTTPException as e:
            logger.warning(f"HTTP exception: {e.status_code} - {e.detail}")
            language = get_accept_language(request)
            
            # Try to find Arabic translation
            message_ar = ERROR_MESSAGES.get("INTERNAL_ERROR", {}).get("ar", str(e.detail))
            
            return JSONResponse(
                status_code=e.status_code,
                content=create_error_response(
                    error_code="HTTP_ERROR",
                    message=str(e.detail),
                    message_ar=message_ar,
                    status_code=e.status_code,
                    language=language
                )
            )
            
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}\n{traceback.format_exc()}")
            language = get_accept_language(request)
            
            return JSONResponse(
                status_code=500,
                content=create_error_response(
                    error_code="INTERNAL_ERROR",
                    message=ERROR_MESSAGES["INTERNAL_ERROR"]["en"],
                    message_ar=ERROR_MESSAGES["INTERNAL_ERROR"]["ar"],
                    status_code=500,
                    language=language
                )
            )
