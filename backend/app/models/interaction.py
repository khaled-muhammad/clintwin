"""
Drug Interaction Models
=======================
Models for drug-drug interaction checking.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class InteractionSeverity(str, Enum):
    """Severity levels for drug interactions."""
    CONTRAINDICATED = "contraindicated"  # Must never be combined
    MAJOR = "major"  # Serious harm possible, avoid combination
    MODERATE = "moderate"  # May require dose adjustment or monitoring
    MINOR = "minor"  # Minimal clinical significance
    UNKNOWN = "unknown"  # Interaction possible but not well documented


class InteractionMechanism(str, Enum):
    """How drugs interact."""
    PHARMACOKINETIC = "pharmacokinetic"  # Affects absorption, distribution, metabolism, excretion
    PHARMACODYNAMIC = "pharmacodynamic"  # Affects drug action at target site
    ADDITIVE = "additive"  # Combined effects add up
    SYNERGISTIC = "synergistic"  # Combined effect greater than sum
    ANTAGONISTIC = "antagonistic"  # One drug reduces effect of another
    UNKNOWN = "unknown"


class DrugInteraction(BaseModel):
    """
    Represents an interaction between two drugs or drug groups.
    """
    id: str = Field(..., description="Unique interaction identifier")
    
    # Interacting entities (can be specific drugs or drug classes)
    drug_a: str = Field(..., description="First drug/drug class")
    drug_a_group: Optional[str] = Field(None, description="Drug group for first drug")
    drug_b: str = Field(..., description="Second drug/drug class")
    drug_b_group: Optional[str] = Field(None, description="Drug group for second drug")
    
    # Interaction details
    severity: InteractionSeverity = Field(..., description="How serious is this interaction")
    mechanism: InteractionMechanism = Field(InteractionMechanism.UNKNOWN, description="How drugs interact")
    
    # Clinical information
    description: str = Field(..., description="Description of the interaction")
    clinical_effects: List[str] = Field(default_factory=list, description="What can happen")
    symptoms: List[str] = Field(default_factory=list, description="Symptoms to watch for")
    
    # Recommendations
    recommendation: str = Field(..., description="What to do about this interaction")
    alternatives: List[str] = Field(default_factory=list, description="Safer alternative drugs")
    monitoring: Optional[str] = Field(None, description="What to monitor if used together")
    
    # Evidence
    evidence_level: str = Field("moderate", description="How well documented (high/moderate/low)")
    references: List[str] = Field(default_factory=list, description="Scientific references")

    class Config:
        use_enum_values = True


class InteractionCheckRequest(BaseModel):
    """Request to check interactions between medicines."""
    medicine_ids: List[str] = Field(..., min_length=1, description="List of medicine IDs to check")
    include_groups: bool = Field(True, description="Also check drug class interactions")


class InteractionCheckResult(BaseModel):
    """Result of interaction check."""
    medicines_checked: List[str] = Field(..., description="Medicines that were checked")
    interactions_found: List[DrugInteraction] = Field(default_factory=list)
    has_contraindicated: bool = Field(False, description="Are there any contraindicated combinations?")
    has_major: bool = Field(False, description="Are there any major interactions?")
    overall_risk: str = Field("low", description="Overall risk assessment: low/moderate/high/critical")
    summary: str = Field("", description="Human-readable summary of findings")
    safe_alternatives: List[dict] = Field(default_factory=list, description="Suggested safer alternatives")


class InteractionWarning(BaseModel):
    """A specific warning to display to user."""
    severity: InteractionSeverity
    title: str
    message: str
    drugs_involved: List[str]
    action_required: str
