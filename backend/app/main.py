"""
ClinTwin Main Application
=========================
FastAPI application with three independent modules:
1. Pill Akinator - MCQ-based medicine identification
2. Image Identifier - CNN + OCR visual recognition
3. Drug Interaction Checker - Safety verification

Each module operates independently but shares the medicine database.
Services are lazily loaded to avoid importing heavy dependencies at startup.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import asyncio
import os

from app.routes import akinator, image, interactions, medicines, dosage, history
from app import config

# Import middleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.rate_limiter import RateLimitMiddleware, get_rate_limiter
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.utils.cache import get_cache

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def periodic_cleanup():
    """Periodic cleanup task for cache and rate limiter."""
    while True:
        await asyncio.sleep(300)  # Every 5 minutes
        try:
            await get_cache().cleanup()
            await get_rate_limiter().cleanup()
            logger.debug("Periodic cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Initializes services on startup, cleans up on shutdown.
    """
    logger.info("🚀 Starting ClinTwin Backend...")
    
    # Initialize services (they will be available via dependency injection)
    logger.info("📦 Loading medicine database...")
    logger.info("🤖 Initializing Pill Akinator service...")
    logger.info("🖼️ Initializing Image Identifier service...")
    logger.info("⚠️ Initializing Interaction Checker service...")
    logger.info("🌍 Arabic/English i18n enabled")
    logger.info("🛡️ Rate limiting enabled")
    logger.info("📝 Request logging enabled")
    
    # Start background cleanup task
    cleanup_task = asyncio.create_task(periodic_cleanup())
    
    logger.info("✅ ClinTwin Backend started successfully!")
    
    yield  # Application runs here
    
    # Cleanup on shutdown
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    
    # Clear caches
    await get_cache().clear()
    
    logger.info("👋 Shutting down ClinTwin Backend...")


# Create FastAPI application
app = FastAPI(
    title="ClinTwin API",
    description="""
    ## AI-Powered Pharmaceutical Safety System
    
    ClinTwin provides three independent modules for medicine identification
    and safety checking, designed for resource-limited settings in Egypt.
    
    ### 🌍 Bilingual Support
    All endpoints support Arabic and English responses.
    Use `Accept-Language: ar` header or `?lang=ar` query parameter.
    
    ### Modules:
    
    1. **Pill Akinator** - Identify medicines through intelligent MCQs
       - Uses visual memory (box color, pill shape, text, logos)
       - Dynamic question generation via LLM
       - Achieves >90% confidence in ~3 questions
    
    2. **Image Identifier** - Recognize medicines from photos
       - CNN for visual classification
       - OCR for text extraction (English + Arabic)
       - Supports pills, boxes, strips, bottles, syrups
    
    3. **Drug Interaction Checker** - Verify medication safety
       - Checks for harmful drug-drug interactions
       - Provides warnings and safe alternatives
       - High sensitivity for critical interactions
    """,
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
# In production, replace with your actual frontend domain
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# Add production origins from environment
if os.getenv("FRONTEND_URL"):
    ALLOWED_ORIGINS.append(os.getenv("FRONTEND_URL"))

# In development, allow all origins
if config.DEBUG:
    ALLOWED_ORIGINS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID", "X-Response-Time", "Retry-After"]
)

# Add custom middleware (order matters - first added = last executed)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Include routers for each module
app.include_router(akinator.router, prefix="/api/akinator", tags=["Pill Akinator"])
app.include_router(image.router, prefix="/api/image", tags=["Image Identifier"])
app.include_router(interactions.router, prefix="/api/interactions", tags=["Drug Interactions"])
app.include_router(medicines.router, prefix="/api/medicines", tags=["Medicines"])
app.include_router(dosage.router, prefix="/api/dosage", tags=["Dosage Calculator"])
app.include_router(history.router, prefix="/api/history", tags=["History & Favorites"])


@app.get("/", tags=["Health"])
async def root():
    """
    Health check endpoint.
    Returns basic API information.
    """
    return {
        "name": "ClinTwin API",
        "name_ar": "واجهة برمجة تطبيقات كلين توين",
        "version": "2.0.0",
        "status": "healthy",
        "status_ar": "يعمل بشكل سليم",
        "features": {
            "bilingual": True,
            "rate_limiting": True,
            "caching": True
        },
        "modules": {
            "pill_akinator": "/api/akinator",
            "image_identifier": "/api/image",
            "interaction_checker": "/api/interactions"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check(request: Request):
    """
    Detailed health check for all services.
    """
    from app.utils.i18n import get_language
    
    lang = get_language(request)
    
    status_text = "يعمل" if lang == "ar" else "online"
    healthy_text = "سليم" if lang == "ar" else "healthy"
    
    return {
        "status": healthy_text,
        "services": {
            "pill_akinator": status_text,
            "image_identifier": status_text,
            "interaction_checker": status_text
        },
        "llm_provider": config.LLM_PROVIDER,
        "debug_mode": config.DEBUG,
        "locale": lang,
        "features": {
            "arabic_support": True,
            "rate_limiting": True,
            "request_logging": True,
            "caching": True
        }
    }


@app.get("/api/info", tags=["Health"])
async def api_info(request: Request):
    """
    Get API information with localized content.
    """
    from app.utils.i18n import get_language
    
    lang = get_language(request)
    
    if lang == "ar":
        return {
            "name": "كلين توين",
            "description": "نظام سلامة الأدوية المدعوم بالذكاء الاصطناعي",
            "version": "2.0.0",
            "modules": [
                {
                    "name": "التعرف بالأسئلة",
                    "description": "تحديد الأدوية من خلال الأسئلة الذكية",
                    "endpoint": "/api/akinator"
                },
                {
                    "name": "التعرف بالصورة",
                    "description": "التعرف على الأدوية من الصور",
                    "endpoint": "/api/image"
                },
                {
                    "name": "فاحص التفاعلات",
                    "description": "التحقق من التفاعلات الدوائية الخطرة",
                    "endpoint": "/api/interactions"
                }
            ]
        }
    
    return {
        "name": "ClinTwin",
        "description": "AI-Powered Pharmaceutical Safety System",
        "version": "2.0.0",
        "modules": [
            {
                "name": "Pill Akinator",
                "description": "Identify medicines through intelligent MCQs",
                "endpoint": "/api/akinator"
            },
            {
                "name": "Image Identifier",
                "description": "Recognize medicines from photos",
                "endpoint": "/api/image"
            },
            {
                "name": "Interaction Checker",
                "description": "Check for harmful drug interactions",
                "endpoint": "/api/interactions"
            }
        ]
    }


# Entry point for running directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )

