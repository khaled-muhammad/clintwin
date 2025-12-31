"""
Image Identifier Service
========================
CNN + OCR-based medicine identification from images.

This module provides visual recognition of medicines through:
1. **CNN Classification**: Identifies medicine from visual features
2. **OCR Extraction**: Reads text from packaging (English + Arabic)
3. **Combined Analysis**: Merges CNN and OCR results for accuracy

Supported Image Types:
- Pill/tablet photos
- Medicine box/packaging
- Blister strip photos
- Bottle/syrup containers
- Prescription labels

AI Logic:
---------
1. **Preprocessing**: Resize, normalize, enhance image
2. **CNN Inference**: Run through lightweight CNN for visual classification
3. **OCR Pipeline**: Extract text using Tesseract/EasyOCR
4. **Text Matching**: Match extracted text against medicine database
5. **Confidence Fusion**: Combine CNN and OCR confidence scores
6. **Result Ranking**: Return top matches with confidence

Model Architecture (Lightweight <10MB):
- MobileNetV2 backbone (pretrained)
- Custom classification head
- Input: 224x224 RGB
- Output: Softmax over medicine classes
"""
import json
import uuid
import re
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import logging
import io
import base64

from app import config

logger = logging.getLogger(__name__)

# ==================
# Lazy Import Flags
# ==================
# These will be set to True when imports succeed
HAS_PIL = False
HAS_TF = False
HAS_EASYOCR = False
HAS_TESSERACT = False

# Try to import PIL (lightweight, usually available)
try:
    import numpy as np
    from PIL import Image
    HAS_PIL = True
except ImportError:
    np = None
    Image = None
    logger.warning("PIL/numpy not installed - using mock image processing")

# TensorFlow and EasyOCR are heavy - only import when actually needed
# They will be lazily loaded in the methods that use them


class ImageIdentifierService:
    """
    Service for image-based medicine identification.
    
    Combines CNN visual classification with OCR text extraction
    to accurately identify medicines from photos.
    """
    
    def __init__(self):
        """Initialize the Image Identifier service."""
        self.medicines = self._load_medicines()
        self.medicine_names = [m["name"].lower() for m in self.medicines]
        self.medicine_index = {m["name"].lower(): m for m in self.medicines}
        
        # Initialize CNN model (will use mock if not available)
        # Note: CNN loading is deferred until first use to speed up startup
        self.cnn_model = None
        self._cnn_loaded = False
        self.class_labels = [m["name"] for m in self.medicines]
        
        # Initialize OCR reader (deferred until first use)
        self.ocr_reader = None
        self._ocr_loaded = False
        
        logger.info(f"ImageIdentifierService initialized with {len(self.medicines)} medicines")
        logger.info("CNN and OCR will be loaded on first use (lazy loading)")
    
    def _ensure_cnn_loaded(self):
        """Ensure CNN model is loaded (lazy loading)."""
        if not self._cnn_loaded:
            self.cnn_model = self._load_cnn_model()
            self._cnn_loaded = True
    
    def _ensure_ocr_loaded(self):
        """Ensure OCR reader is loaded (lazy loading)."""
        if not self._ocr_loaded:
            self.ocr_reader = self._init_ocr()
            self._ocr_loaded = True
    
    def _load_medicines(self) -> List[Dict]:
        """Load medicine database from JSON file."""
        try:
            with open(config.MEDICINES_DB_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("medicines", [])
        except FileNotFoundError:
            logger.warning(f"Medicines file not found: {config.MEDICINES_DB_PATH}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing medicines JSON: {e}")
            return []
    
    def _load_cnn_model(self) -> Any:
        """
        Load or create CNN model for medicine classification.
        
        If a trained model exists, load it.
        Otherwise, return None to use mock mode.
        
        Model Architecture:
        - Base: MobileNetV2 (lightweight, fast inference)
        - Head: GlobalAveragePooling -> Dense(256) -> Dropout -> Dense(num_classes)
        - Total size: ~8MB
        """
        global HAS_TF
        
        # Try lazy import of TensorFlow
        try:
            import tensorflow as tf
            from tensorflow import keras
            HAS_TF = True
        except ImportError:
            logger.info("TensorFlow not available - using mock CNN")
            return None
        
        model_path = config.CNN_MODEL_PATH
        
        if model_path.exists():
            try:
                model = keras.models.load_model(str(model_path))
                logger.info(f"Loaded CNN model from {model_path}")
                return model
            except Exception as e:
                logger.error(f"Error loading CNN model: {e}")
                return None
        
        # Create mock/placeholder model structure for demo
        logger.info("No trained model found - will use text matching for demo")
        return None
    
    def _init_ocr(self) -> Any:
        """
        Initialize OCR reader for English and Arabic text.
        
        Tries EasyOCR first (better Arabic support), falls back to Tesseract.
        OCR libraries are loaded lazily to avoid startup issues.
        """
        global HAS_EASYOCR, HAS_TESSERACT
        
        # Try EasyOCR (lazy import - it's heavy)
        try:
            import easyocr
            HAS_EASYOCR = True
            reader = easyocr.Reader(['en', 'ar'], gpu=False)
            logger.info("EasyOCR initialized for English + Arabic")
            return reader
        except ImportError:
            logger.info("EasyOCR not installed")
        except Exception as e:
            logger.error(f"EasyOCR init error: {e}")
        
        # Try Tesseract (lazy import)
        try:
            import pytesseract
            HAS_TESSERACT = True
            logger.info("Using Tesseract OCR")
            return "tesseract"
        except ImportError:
            logger.info("Pytesseract not installed")
        
        logger.warning("No OCR available - using text matching only")
        return None
    
    def _preprocess_image(self, image_data: bytes) -> Optional[Any]:
        """
        Preprocess image for CNN input.
        
        Steps:
        1. Load image from bytes
        2. Resize to model input size (224x224)
        3. Normalize pixel values to [0, 1]
        4. Add batch dimension
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Preprocessed numpy array or None if error
        """
        if not HAS_PIL:
            return None
        
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize to model input size
            image = image.resize(config.CNN_INPUT_SIZE, Image.Resampling.LANCZOS)
            
            if HAS_TF:
                # Convert to numpy array
                img_array = np.array(image, dtype=np.float32)
                
                # Normalize to [0, 1]
                img_array = img_array / 255.0
                
                # Add batch dimension
                img_array = np.expand_dims(img_array, axis=0)
                
                return img_array
            
            return image
            
        except Exception as e:
            logger.error(f"Image preprocessing error: {e}")
            return None
    
    def _run_cnn_inference(self, preprocessed_image: Any) -> List[Tuple[str, float]]:
        """
        Run CNN inference on preprocessed image.
        
        Args:
            preprocessed_image: Preprocessed numpy array
            
        Returns:
            List of (medicine_name, confidence) tuples, sorted by confidence
        """
        # Ensure CNN is loaded
        self._ensure_cnn_loaded()
        
        if self.cnn_model is None or preprocessed_image is None:
            # Return empty for mock mode
            return []
        
        try:
            # Run prediction
            predictions = self.cnn_model.predict(preprocessed_image, verbose=0)[0]
            
            # Get top predictions
            if np is not None:
                top_indices = np.argsort(predictions)[::-1][:5]
            else:
                return []
            
            results = []
            for idx in top_indices:
                if idx < len(self.class_labels):
                    name = self.class_labels[idx]
                    confidence = float(predictions[idx])
                    if confidence >= 0.1:  # Minimum threshold
                        results.append((name, confidence))
            
            return results
            
        except Exception as e:
            logger.error(f"CNN inference error: {e}")
            return []
    
    def _extract_text_ocr(self, image_data: bytes) -> List[Dict]:
        """
        Extract text from image using OCR.
        
        Supports English and Arabic text extraction.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            List of extracted text items with confidence
        """
        extracted = []
        
        if self.ocr_reader is None:
            # No OCR available - return empty
            return extracted
        
        try:
            if HAS_PIL and Image is not None:
                image = Image.open(io.BytesIO(image_data))
                
                if isinstance(self.ocr_reader, str) and self.ocr_reader == "tesseract":
                    # Tesseract OCR
                    import pytesseract
                    text = pytesseract.image_to_string(image, lang='eng+ara')
                    for line in text.split('\n'):
                        line = line.strip()
                        if line and len(line) > 2:
                            extracted.append({
                                "text": line,
                                "confidence": 0.8,
                                "source": "tesseract"
                            })
                else:
                    # EasyOCR
                    if np is not None:
                        results = self.ocr_reader.readtext(np.array(image))
                        for (bbox, text, conf) in results:
                            if text and len(text) > 2:
                                extracted.append({
                                    "text": text,
                                    "confidence": conf,
                                    "source": "easyocr",
                                    "bbox": bbox
                                })
            
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
        
        return extracted
    
    def _match_text_to_medicines(
        self, 
        extracted_texts: List[Dict]
    ) -> List[Tuple[Dict, float, str]]:
        """
        Match extracted OCR text to medicine database.
        
        Uses fuzzy matching to handle OCR errors.
        
        Args:
            extracted_texts: List of OCR results
            
        Returns:
            List of (medicine, confidence, matched_text) tuples
        """
        matches = []
        
        for text_item in extracted_texts:
            text = text_item["text"].lower().strip()
            ocr_confidence = text_item["confidence"]
            
            # Direct match check
            for med_name, medicine in self.medicine_index.items():
                # Check if medicine name or prominent word matches
                prominent = medicine.get("visual", {}).get("prominent_word", "").lower()
                generic = medicine.get("generic_name", "").lower()
                
                match_score = 0.0
                matched_text = ""
                
                # Exact match
                if med_name in text or text in med_name:
                    match_score = 0.95
                    matched_text = med_name
                elif prominent and (prominent in text or text in prominent):
                    match_score = 0.90
                    matched_text = prominent
                elif generic and (generic in text or text in generic):
                    match_score = 0.85
                    matched_text = generic
                else:
                    # Partial match - check for word overlap
                    med_words = set(med_name.split())
                    text_words = set(text.split())
                    overlap = med_words & text_words
                    if overlap:
                        match_score = 0.5 * (len(overlap) / len(med_words))
                        matched_text = " ".join(overlap)
                
                if match_score > 0:
                    # Combine with OCR confidence
                    combined_confidence = match_score * ocr_confidence
                    matches.append((medicine, combined_confidence, matched_text))
        
        # Sort by confidence and remove duplicates
        matches.sort(key=lambda x: x[1], reverse=True)
        
        seen_ids = set()
        unique_matches = []
        for med, conf, text in matches:
            if med["id"] not in seen_ids:
                seen_ids.add(med["id"])
                unique_matches.append((med, conf, text))
        
        return unique_matches[:5]  # Top 5
    
    def _extract_barcode(self, image_data: bytes) -> Optional[str]:
        """
        Attempt to extract barcode from image.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Barcode string or None
        """
        # Barcode extraction would require pyzbar or similar
        # For demo, return None
        return None
    
    def _lookup_barcode(self, barcode: str) -> Optional[Dict]:
        """
        Look up medicine by barcode.
        
        Args:
            barcode: Barcode string
            
        Returns:
            Medicine dict or None
        """
        for medicine in self.medicines:
            if medicine.get("barcode") == barcode:
                return medicine
        return None
    
    def _fuse_results(
        self,
        cnn_results: List[Tuple[str, float]],
        ocr_matches: List[Tuple[Dict, float, str]]
    ) -> List[Dict]:
        """
        Fuse CNN and OCR results for final predictions.
        
        Strategy:
        1. If both agree on top match, boost confidence
        2. If disagree, weight by individual confidences
        3. Include unique matches from both
        
        Args:
            cnn_results: CNN predictions (name, confidence)
            ocr_matches: OCR matches (medicine, confidence, text)
            
        Returns:
            Fused results list
        """
        fused = {}
        
        # Add CNN results
        for name, conf in cnn_results:
            name_lower = name.lower()
            if name_lower in self.medicine_index:
                med = self.medicine_index[name_lower]
                fused[med["id"]] = {
                    "medicine": med,
                    "cnn_confidence": conf,
                    "ocr_confidence": 0.0,
                    "matched_text": "",
                    "sources": ["cnn"]
                }
        
        # Add/merge OCR results
        for med, conf, text in ocr_matches:
            med_id = med["id"]
            if med_id in fused:
                # Merge with existing CNN result
                fused[med_id]["ocr_confidence"] = conf
                fused[med_id]["matched_text"] = text
                fused[med_id]["sources"].append("ocr")
            else:
                fused[med_id] = {
                    "medicine": med,
                    "cnn_confidence": 0.0,
                    "ocr_confidence": conf,
                    "matched_text": text,
                    "sources": ["ocr"]
                }
        
        # Calculate final confidence
        results = []
        for med_id, data in fused.items():
            cnn_conf = data["cnn_confidence"]
            ocr_conf = data["ocr_confidence"]
            
            # Weighted fusion
            if cnn_conf > 0 and ocr_conf > 0:
                # Both agree - boost confidence
                final_conf = 0.6 * max(cnn_conf, ocr_conf) + 0.4 * min(cnn_conf, ocr_conf) + 0.1
            elif cnn_conf > 0:
                final_conf = cnn_conf * 0.8
            else:
                final_conf = ocr_conf * 0.9
            
            final_conf = min(0.98, final_conf)
            
            results.append({
                "medicine": data["medicine"],
                "confidence": round(final_conf, 2),
                "sources": data["sources"],
                "matched_text": data["matched_text"]
            })
        
        # Sort by confidence
        results.sort(key=lambda x: x["confidence"], reverse=True)
        
        return results[:5]
    
    def _extract_medicine_info(self, medicine: Dict) -> Dict:
        """
        Extract full medicine information for display.
        
        Args:
            medicine: Medicine dictionary
            
        Returns:
            Formatted medicine info
        """
        return {
            "id": medicine.get("id"),
            "name": medicine.get("name"),
            "name_arabic": medicine.get("name_arabic"),
            "generic_name": medicine.get("generic_name"),
            "manufacturer": medicine.get("manufacturer"),
            "dosage_form": medicine.get("dosage_form"),
            "strength": medicine.get("strength"),
            "drug_class": medicine.get("drug_class"),
            "category": medicine.get("category"),
            "main_use": medicine.get("main_use"),
            "indications": medicine.get("indications", []),
            "contraindications": medicine.get("contraindications", []),
            "side_effects": medicine.get("side_effects", []),
            "warnings": medicine.get("warnings", []),
            "adult_dosage": medicine.get("adult_dosage"),
            "child_dosage": medicine.get("child_dosage"),
            "requires_prescription": medicine.get("requires_prescription", True),
            "product_image": medicine.get("product_image"),
            "barcode": medicine.get("barcode")
        }
    
    # ==================
    # Public API Methods
    # ==================
    
    async def identify_image(self, image_data: bytes) -> Dict:
        """
        Identify medicine from image.
        
        This is the main entry point for image identification.
        Combines CNN classification and OCR text extraction.
        
        Args:
            image_data: Raw image bytes (JPEG, PNG, etc.)
            
        Returns:
            Identification result with medicine info and confidence
        """
        request_id = str(uuid.uuid4())
        
        try:
            # Step 1: Preprocess image for CNN
            preprocessed = self._preprocess_image(image_data)
            
            # Step 2: Run CNN inference (lazy loads CNN if available)
            cnn_results = self._run_cnn_inference(preprocessed)
            
            # Step 3: Extract text via OCR (lazy loads OCR if available)
            self._ensure_ocr_loaded()
            ocr_texts = self._extract_text_ocr(image_data)
            
            # Step 4: Match OCR text to medicines
            ocr_matches = self._match_text_to_medicines(ocr_texts)
            
            # Step 5: Try barcode lookup
            barcode = self._extract_barcode(image_data)
            barcode_match = None
            if barcode:
                barcode_match = self._lookup_barcode(barcode)
            
            # Step 6: Fuse results
            fused_results = self._fuse_results(cnn_results, ocr_matches)
            
            # If barcode matched, prioritize it
            if barcode_match:
                fused_results.insert(0, {
                    "medicine": barcode_match,
                    "confidence": 0.99,
                    "sources": ["barcode"],
                    "matched_text": barcode
                })
            
            # Generate response
            if fused_results:
                top_result = fused_results[0]
                return {
                    "request_id": request_id,
                    "success": True,
                    "top_match": {
                        "medicine": self._extract_medicine_info(top_result["medicine"]),
                        "confidence": top_result["confidence"],
                        "identification_sources": top_result["sources"]
                    },
                    "alternatives": [
                        {
                            "medicine": self._extract_medicine_info(r["medicine"]),
                            "confidence": r["confidence"],
                            "identification_sources": r["sources"]
                        }
                        for r in fused_results[1:]
                    ],
                    "extracted_text": [t["text"] for t in ocr_texts[:5]],
                    "ocr_available": self.ocr_reader is not None,
                    "cnn_available": self.cnn_model is not None
                }
            
            # No matches found
            return {
                "request_id": request_id,
                "success": False,
                "message": "Could not identify medicine from image. Please try a clearer photo.",
                "extracted_text": [t["text"] for t in ocr_texts[:5]],
                "suggestions": [
                    "Ensure good lighting",
                    "Include the medicine name in the photo",
                    "Try a photo of the box front"
                ]
            }
            
        except Exception as e:
            logger.error(f"Image identification error: {e}")
            return {
                "request_id": request_id,
                "success": False,
                "error": str(e),
                "message": "An error occurred during image processing"
            }
    
    def identify_image_sync(self, image_data: bytes) -> Dict:
        """
        Synchronous version of identify_image.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Identification result
        """
        import asyncio
        return asyncio.run(self.identify_image(image_data))
    
    def extract_info_only(self, image_data: bytes) -> Dict:
        """
        Extract text information from image without identification.
        
        Useful for reading dosage, warnings, etc. from packaging.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Extracted text information
        """
        try:
            # Ensure OCR is loaded
            self._ensure_ocr_loaded()
            ocr_texts = self._extract_text_ocr(image_data)
            
            # Try to categorize extracted text
            categorized = {
                "medicine_name": [],
                "dosage": [],
                "warnings": [],
                "ingredients": [],
                "other": []
            }
            
            # Simple categorization based on keywords
            for text_item in ocr_texts:
                text = text_item["text"]
                text_lower = text.lower()
                
                if any(word in text_lower for word in ["mg", "ml", "dose", "dosage"]):
                    categorized["dosage"].append(text)
                elif any(word in text_lower for word in ["warning", "caution", "تحذير"]):
                    categorized["warnings"].append(text)
                elif any(word in text_lower for word in ["active", "ingredient", "contains"]):
                    categorized["ingredients"].append(text)
                elif text_lower in self.medicine_names:
                    categorized["medicine_name"].append(text)
                else:
                    categorized["other"].append(text)
            
            return {
                "success": True,
                "extracted_text": categorized,
                "raw_text": [t["text"] for t in ocr_texts],
                "text_count": len(ocr_texts)
            }
            
        except Exception as e:
            logger.error(f"Text extraction error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported image formats."""
        return ["jpeg", "jpg", "png", "gif", "bmp", "webp"]
    
    def get_max_image_size(self) -> int:
        """Get maximum supported image size in bytes."""
        return 10 * 1024 * 1024  # 10MB


# Singleton instance
_image_service: Optional[ImageIdentifierService] = None


def get_image_service() -> ImageIdentifierService:
    """Get or create the Image Identifier service singleton."""
    global _image_service
    if _image_service is None:
        _image_service = ImageIdentifierService()
    return _image_service
