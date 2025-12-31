"""
Medicine Data Models
====================
Pydantic models for medicine data with visual attributes
for Pill Akinator identification.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class DosageForm(str, Enum):
    """Possible medicine dosage forms."""
    TABLET = "tablet"
    CAPSULE = "capsule"
    SYRUP = "syrup"
    SUSPENSION = "suspension"
    INJECTION = "injection"
    CREAM = "cream"
    GEL = "gel"
    DROPS = "drops"
    INHALER = "inhaler"
    SUPPOSITORY = "suppository"
    POWDER = "powder"
    OTHER = "other"


class BoxColor(str, Enum):
    """Primary box/packaging colors."""
    WHITE = "white"
    BLUE = "blue"
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    PURPLE = "purple"
    PINK = "pink"
    BLACK = "black"
    SILVER = "silver"
    GOLD = "gold"
    BROWN = "brown"
    MULTICOLOR = "multicolor"


class TabletShape(str, Enum):
    """Tablet/pill shapes."""
    ROUND = "round"
    OVAL = "oval"
    OBLONG = "oblong"
    CAPSULE_SHAPED = "capsule_shaped"
    SQUARE = "square"
    DIAMOND = "diamond"
    TRIANGLE = "triangle"
    HEXAGON = "hexagon"
    HEART = "heart"
    OTHER = "other"


class LiquidColor(str, Enum):
    """Colors for liquid medications (syrups, suspensions)."""
    CLEAR = "clear"
    WHITE = "white"
    PINK = "pink"
    RED = "red"
    ORANGE = "orange"
    YELLOW = "yellow"
    GREEN = "green"
    BROWN = "brown"
    PURPLE = "purple"


class MedicineVisualAttributes(BaseModel):
    """
    Visual attributes used by Pill Akinator for identification.
    These are what users can remember/describe from visual memory.
    """
    # Box/Package attributes
    box_primary_color: BoxColor = Field(..., description="Primary color of the medicine box")
    box_secondary_color: Optional[BoxColor] = Field(None, description="Secondary color if any")
    has_stripe_design: bool = Field(False, description="Does the box have stripe patterns?")
    has_logo: bool = Field(True, description="Does the box have a visible brand logo?")
    logo_description: Optional[str] = Field(None, description="Brief description of logo if notable")
    
    # Text attributes (what user might remember)
    prominent_word: str = Field(..., description="Most prominent/memorable word on packaging")
    has_arabic_text: bool = Field(True, description="Does packaging have Arabic text?")
    has_english_text: bool = Field(True, description="Does packaging have English text?")
    text_color: Optional[str] = Field(None, description="Color of main text")
    
    # Pill/Tablet attributes (if applicable)
    tablet_shape: Optional[TabletShape] = Field(None, description="Shape of the tablet/pill")
    tablet_color: Optional[str] = Field(None, description="Color of the tablet/pill")
    has_imprint: bool = Field(False, description="Does tablet have text/number imprint?")
    imprint_text: Optional[str] = Field(None, description="Text imprinted on tablet")
    is_scored: bool = Field(False, description="Does tablet have a score line for splitting?")
    is_coated: bool = Field(False, description="Is tablet film-coated (shiny)?")
    
    # Strip attributes
    strip_color: Optional[str] = Field(None, description="Color of blister strip")
    pills_per_strip: Optional[int] = Field(None, description="Number of pills visible per strip")
    
    # Liquid attributes (for syrups/suspensions)
    liquid_color: Optional[LiquidColor] = Field(None, description="Color of liquid medicine")
    bottle_shape: Optional[str] = Field(None, description="Shape of bottle (round, square, etc.)")


class Medicine(BaseModel):
    """
    Complete medicine information model.
    Combines identification, medical, and visual data.
    """
    # Identification
    id: str = Field(..., description="Unique medicine identifier")
    name: str = Field(..., description="Medicine brand name")
    name_arabic: Optional[str] = Field(None, description="Arabic name if available")
    generic_name: str = Field(..., description="Generic/active ingredient name")
    manufacturer: str = Field(..., description="Pharmaceutical company")
    
    # Classification
    dosage_form: DosageForm = Field(..., description="Form of the medicine")
    drug_class: str = Field(..., description="Therapeutic drug class")
    category: str = Field(..., description="General category (pain relief, antibiotic, etc.)")
    
    # Dosage Information
    strength: str = Field(..., description="Medicine strength (e.g., 500mg)")
    available_strengths: List[str] = Field(default_factory=list, description="All available strengths")
    
    # Medical Information
    main_use: str = Field(..., description="Primary indication/use")
    indications: List[str] = Field(default_factory=list, description="All indications")
    contraindications: List[str] = Field(default_factory=list, description="Contraindications")
    side_effects: List[str] = Field(default_factory=list, description="Common side effects")
    warnings: List[str] = Field(default_factory=list, description="Important warnings")
    
    # Dosage Guidelines
    adult_dosage: Optional[str] = Field(None, description="Adult dosage instructions")
    child_dosage: Optional[str] = Field(None, description="Pediatric dosage if applicable")
    
    # Regulatory
    requires_prescription: bool = Field(True, description="Is prescription required?")
    schedule: Optional[str] = Field(None, description="Drug schedule if controlled")
    
    # Identifiers
    barcode: Optional[str] = Field(None, description="Product barcode")
    ndc: Optional[str] = Field(None, description="National Drug Code if applicable")
    
    # Visual attributes for Akinator
    visual: MedicineVisualAttributes = Field(..., description="Visual identification attributes")
    
    # Images
    product_image: Optional[str] = Field(None, description="URL to product image")
    
    # Interaction groups for checking
    interaction_groups: List[str] = Field(default_factory=list, description="Drug interaction categories")

    class Config:
        use_enum_values = True


class MedicineSearchResult(BaseModel):
    """Result from medicine identification."""
    medicine: Medicine
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    match_reasons: List[str] = Field(default_factory=list, description="Why this medicine matched")


class MCQQuestion(BaseModel):
    """
    MCQ Question generated by Pill Akinator.
    JSON structure for LLM-generated questions.
    """
    question_id: str = Field(..., description="Unique question identifier")
    question_text: str = Field(..., description="The question to ask the user")
    options: List[str] = Field(..., min_length=2, max_length=6, description="Answer options")
    field_target: str = Field(..., description="Which visual attribute this question targets")
    confidence_before: float = Field(..., ge=0, le=1, description="Confidence before this question")
    confidence_after_expected: float = Field(..., ge=0, le=1, description="Expected confidence after answer")


class MCQAnswer(BaseModel):
    """User's answer to an MCQ."""
    question_id: str
    selected_option: str
    session_id: str


class AkinatorSession(BaseModel):
    """Tracks state of a Pill Akinator session."""
    session_id: str
    questions_asked: int = 0
    current_confidence: float = 0.0
    answers_history: List[dict] = Field(default_factory=list)
    remaining_candidates: List[str] = Field(default_factory=list)
    identified_medicine: Optional[Medicine] = None
    is_complete: bool = False
