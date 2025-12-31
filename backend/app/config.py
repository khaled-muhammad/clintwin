"""
ClinTwin Configuration
======================
Central configuration for API keys, paths, and settings.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ====================
# Path Configuration
# ====================
BASE_DIR = Path(__file__).parent.parent
APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
ML_MODELS_DIR = BASE_DIR / "ml_models"

# ====================
# API Configuration
# ====================
# Hack Club AI API (free, OpenAI-compatible endpoint)
HACKCLUB_API_URL = "https://ai.hackclub.com/proxy/v1/chat/completions"
HACKCLUB_API_KEY = os.getenv("HACKCLUB_API_KEY", "")  # Optional, may work without key

# Legacy API keys (optional, for fallback)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ====================
# LLM Configuration
# ====================
# Which LLM provider to use for Pill Akinator: "hackclub", "openai", "anthropic", or "mock"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "hackclub")  # Default to Hack Club AI

# Hack Club AI settings (recommended - free!)
HACKCLUB_MODEL = os.getenv("HACKCLUB_MODEL", "qwen/qwen3-32b")
HACKCLUB_TEMPERATURE = 0.3

# OpenAI settings (fallback)
OPENAI_MODEL = "gpt-4-turbo-preview"
OPENAI_TEMPERATURE = 0.3

# Anthropic settings (fallback)
ANTHROPIC_MODEL = "claude-3-sonnet-20240229"
ANTHROPIC_TEMPERATURE = 0.3

# ====================
# Pill Akinator Settings
# ====================
AKINATOR_MIN_QUESTIONS = 3       # Minimum questions before we can suggest (avoid guessing too early)
AKINATOR_MAX_QUESTIONS = 8       # Maximum questions before forcing a guess
AKINATOR_CONFIDENCE_THRESHOLD = 0.92  # Stop when confidence exceeds this (high = more certain)

# ====================
# Image Identifier Settings
# ====================
CNN_MODEL_PATH = ML_MODELS_DIR / "medicine_cnn.h5"
CNN_INPUT_SIZE = (224, 224)
CNN_CONFIDENCE_THRESHOLD = 0.7

# OCR Settings
OCR_LANGUAGES = ["en", "ar"]  # English and Arabic
TESSERACT_PATH = os.getenv("TESSERACT_PATH", None)  # Optional custom path

# ====================
# Database Paths
# ====================
MEDICINES_DB_PATH = DATA_DIR / "medicines.json"
INTERACTIONS_DB_PATH = DATA_DIR / "interactions.json"

# ====================
# Server Settings
# ====================
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
