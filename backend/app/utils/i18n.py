"""
Internationalization Utilities
==============================
Arabic/English translation helpers for API responses.
"""
from fastapi import Request
from typing import Dict, Any, Optional

# Response message translations
MESSAGES = {
    # Success messages
    "SESSION_STARTED": {
        "en": "Identification session started successfully",
        "ar": "تم بدء جلسة التعرف بنجاح"
    },
    "SESSION_ENDED": {
        "en": "Session ended successfully",
        "ar": "تم إنهاء الجلسة بنجاح"
    },
    "MEDICINE_IDENTIFIED": {
        "en": "Medicine identified successfully",
        "ar": "تم التعرف على الدواء بنجاح"
    },
    "NO_INTERACTIONS_FOUND": {
        "en": "No harmful interactions found. These medicines appear safe to take together.",
        "ar": "لم يتم العثور على تفاعلات ضارة. يبدو أن هذه الأدوية آمنة للتناول معاً."
    },
    "INTERACTIONS_FOUND": {
        "en": "Potential interactions found. Please review the warnings carefully.",
        "ar": "تم العثور على تفاعلات محتملة. يرجى مراجعة التحذيرات بعناية."
    },
    
    # Risk levels
    "RISK_SAFE": {
        "en": "Safe",
        "ar": "آمن"
    },
    "RISK_LOW": {
        "en": "Low Risk",
        "ar": "خطر منخفض"
    },
    "RISK_MODERATE": {
        "en": "Moderate Risk",
        "ar": "خطر متوسط"
    },
    "RISK_HIGH": {
        "en": "High Risk",
        "ar": "خطر عالي"
    },
    "RISK_CRITICAL": {
        "en": "Critical - Avoid Combination",
        "ar": "حرج - تجنب هذا المزيج"
    },
    
    # Interaction severities
    "SEVERITY_CONTRAINDICATED": {
        "en": "Contraindicated - Never use together",
        "ar": "موانع استخدام - لا تستخدم معاً أبداً"
    },
    "SEVERITY_MAJOR": {
        "en": "Major Interaction - Avoid if possible",
        "ar": "تفاعل كبير - تجنب إن أمكن"
    },
    "SEVERITY_MODERATE": {
        "en": "Moderate Interaction - Use with caution",
        "ar": "تفاعل متوسط - استخدم بحذر"
    },
    "SEVERITY_MINOR": {
        "en": "Minor Interaction - Generally safe",
        "ar": "تفاعل طفيف - آمن عموماً"
    },
    
    # User type labels
    "PHARMACY_PROFESSIONAL": {
        "en": "Pharmacy Professional",
        "ar": "صيدلي محترف"
    },
    "PATIENT_PUBLIC": {
        "en": "Patient / Public",
        "ar": "مريض / عامة الناس"
    },
    
    # Common actions
    "CONTINUE": {
        "en": "Continue",
        "ar": "متابعة"
    },
    "CANCEL": {
        "en": "Cancel",
        "ar": "إلغاء"
    },
    "RETRY": {
        "en": "Retry",
        "ar": "إعادة المحاولة"
    },
    "SEARCH": {
        "en": "Search",
        "ar": "بحث"
    },
}


def get_language(request: Request) -> str:
    """
    Get preferred language from request.
    
    Checks:
    1. Query parameter: ?lang=ar
    2. Custom header: X-Language
    3. Accept-Language header
    """
    # Check query parameter
    lang = request.query_params.get("lang")
    if lang in ("ar", "en"):
        return lang
    
    # Check custom header
    lang = request.headers.get("X-Language")
    if lang in ("ar", "en"):
        return lang
    
    # Check Accept-Language
    accept_lang = request.headers.get("Accept-Language", "")
    if "ar" in accept_lang.lower():
        return "ar"
    
    return "en"


def translate(key: str, lang: str = "en") -> str:
    """Get translated message by key."""
    if key not in MESSAGES:
        return key
    return MESSAGES[key].get(lang, MESSAGES[key].get("en", key))


def t(key: str, lang: str = "en") -> str:
    """Shorthand for translate."""
    return translate(key, lang)


def localize_response(
    data: Dict[str, Any],
    request: Request,
    message_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add localized message to response based on request language.
    
    Args:
        data: Response data dictionary
        request: FastAPI request object
        message_key: Optional key for message translation
    
    Returns:
        Data with localized message added
    """
    lang = get_language(request)
    
    if message_key:
        data["message"] = translate(message_key, lang)
        data["message_en"] = translate(message_key, "en")
        data["message_ar"] = translate(message_key, "ar")
    
    data["_locale"] = lang
    
    return data


def localize_medicine(medicine: Dict[str, Any], lang: str = "en") -> Dict[str, Any]:
    """
    Return medicine with appropriate name for language.
    
    Uses name_arabic if available and lang is 'ar'.
    """
    result = medicine.copy()
    
    if lang == "ar" and "name_arabic" in medicine and medicine["name_arabic"]:
        result["display_name"] = medicine["name_arabic"]
    else:
        result["display_name"] = medicine.get("name", "")
    
    return result


def localize_medicines(medicines: list, lang: str = "en") -> list:
    """Localize a list of medicines."""
    return [localize_medicine(m, lang) for m in medicines]
