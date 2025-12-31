"""
Dosage Calculator Service
=========================
Weight-based and age-appropriate dosage calculations.
"""
from typing import Dict, Optional, List, Any
import logging
import json
from pathlib import Path

from app import config

logger = logging.getLogger(__name__)


class DosageCalculatorService:
    """
    Service for calculating appropriate medication dosages.
    
    Provides weight-based, age-appropriate dosing with
    consideration for special conditions.
    """
    
    # Age categories
    AGE_CATEGORIES = {
        "neonate": {"min": 0, "max": 0.083, "label": "Neonate (0-1 month)"},
        "infant": {"min": 0.083, "max": 1, "label": "Infant (1-12 months)"},
        "child": {"min": 1, "max": 12, "label": "Child (1-12 years)"},
        "adolescent": {"min": 12, "max": 18, "label": "Adolescent (12-18 years)"},
        "adult": {"min": 18, "max": 65, "label": "Adult (18-65 years)"},
        "elderly": {"min": 65, "max": 999, "label": "Elderly (65+ years)"}
    }
    
    # Common dosing rules per medicine category
    DOSING_RULES = {
        "pain_relief": {
            "paracetamol": {
                "child_mg_per_kg": 15,
                "child_max_daily": 60,  # mg/kg/day
                "adult_single": "500-1000mg",
                "adult_max_daily": 4000,  # mg/day
                "frequency": "every 4-6 hours",
                "frequency_ar": "كل 4-6 ساعات"
            },
            "ibuprofen": {
                "child_mg_per_kg": 10,
                "child_max_daily": 40,
                "adult_single": "200-400mg",
                "adult_max_daily": 1200,
                "frequency": "every 6-8 hours",
                "frequency_ar": "كل 6-8 ساعات",
                "warning": "Take with food",
                "warning_ar": "يؤخذ مع الطعام"
            }
        },
        "antibiotic": {
            "amoxicillin": {
                "child_mg_per_kg": 25,
                "child_max_daily": 80,
                "adult_single": "500mg",
                "adult_max_daily": 3000,
                "frequency": "every 8 hours",
                "frequency_ar": "كل 8 ساعات"
            }
        }
    }
    
    def __init__(self):
        self.medicines = self._load_medicines()
    
    def _load_medicines(self) -> List[Dict]:
        """Load medicine database."""
        try:
            with open(config.MEDICINES_DB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("medicines", [])
        except Exception as e:
            logger.error(f"Failed to load medicines: {e}")
            return []
    
    def get_age_category(self, age_years: float) -> str:
        """Determine age category."""
        for category, bounds in self.AGE_CATEGORIES.items():
            if bounds["min"] <= age_years < bounds["max"]:
                return category
        return "adult"
    
    def calculate_dosage(
        self,
        medicine_id: str,
        weight_kg: Optional[float] = None,
        age_years: Optional[float] = None,
        conditions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Calculate recommended dosage for a medicine.
        
        Args:
            medicine_id: Medicine ID
            weight_kg: Patient weight in kg
            age_years: Patient age in years
            conditions: List of conditions (e.g., "renal_impairment")
        
        Returns:
            Dosage calculation result
        """
        # Find medicine
        medicine = None
        for med in self.medicines:
            if med["id"] == medicine_id:
                medicine = med
                break
        
        if not medicine:
            return {
                "success": False,
                "error": "Medicine not found",
                "error_ar": "الدواء غير موجود"
            }
        
        # Determine patient category
        age_category = self.get_age_category(age_years) if age_years else "adult"
        is_pediatric = age_category in ["neonate", "infant", "child", "adolescent"]
        
        # Get standard dosage from medicine
        result = {
            "success": True,
            "medicine_id": medicine_id,
            "medicine_name": medicine["name"],
            "medicine_name_ar": medicine.get("name_arabic", medicine["name"]),
            "age_category": age_category,
            "is_pediatric": is_pediatric
        }
        
        # Adult dosage
        if not is_pediatric:
            result["recommended_dose"] = medicine.get("adult_dosage", "Consult physician")
            result["recommended_dose_ar"] = medicine.get("adult_dosage", "استشر الطبيب")
            result["calculation_method"] = "standard_adult"
        else:
            # Pediatric - try weight-based if available
            child_dosage = medicine.get("child_dosage", "")
            
            if weight_kg and age_years:
                # Check if we have specific dosing rules
                category = medicine.get("category", "")
                generic = medicine.get("generic_name", "").lower()
                
                # Look for matching dosing rule
                dose_rule = None
                if category in self.DOSING_RULES:
                    for drug, rule in self.DOSING_RULES[category].items():
                        if drug in generic:
                            dose_rule = rule
                            break
                
                if dose_rule:
                    mg_per_kg = dose_rule["child_mg_per_kg"]
                    calculated_dose = weight_kg * mg_per_kg
                    max_daily = weight_kg * dose_rule["child_max_daily"]
                    
                    result["calculated_single_dose_mg"] = round(calculated_dose, 1)
                    result["max_daily_dose_mg"] = round(max_daily, 1)
                    result["frequency"] = dose_rule["frequency"]
                    result["frequency_ar"] = dose_rule.get("frequency_ar", dose_rule["frequency"])
                    result["calculation_method"] = "weight_based"
                    result["recommended_dose"] = f"{round(calculated_dose)}mg {dose_rule['frequency']}"
                    result["recommended_dose_ar"] = f"{round(calculated_dose)}مجم {dose_rule.get('frequency_ar', '')}"
                    
                    if "warning" in dose_rule:
                        result["warning"] = dose_rule["warning"]
                        result["warning_ar"] = dose_rule.get("warning_ar", dose_rule["warning"])
                else:
                    result["recommended_dose"] = child_dosage or "Consult physician for pediatric dosing"
                    result["recommended_dose_ar"] = child_dosage or "استشر الطبيب لجرعة الأطفال"
                    result["calculation_method"] = "standard_pediatric"
            else:
                result["recommended_dose"] = child_dosage or "Consult physician"
                result["recommended_dose_ar"] = child_dosage or "استشر الطبيب"
                result["calculation_method"] = "standard_pediatric"
        
        # Add warnings based on conditions
        warnings = list(medicine.get("warnings", []))
        warnings_ar = []
        
        if conditions:
            if "renal_impairment" in conditions:
                warnings.append("Adjust dose for kidney function - consult physician")
                warnings_ar.append("يجب تعديل الجرعة حسب وظائف الكلى - استشر الطبيب")
            if "hepatic_impairment" in conditions:
                warnings.append("Adjust dose for liver function - consult physician")
                warnings_ar.append("يجب تعديل الجرعة حسب وظائف الكبد - استشر الطبيب")
            if "pregnancy" in conditions:
                warnings.append("Consult physician before use during pregnancy")
                warnings_ar.append("استشر الطبيب قبل الاستخدام أثناء الحمل")
            if "elderly" in conditions or age_category == "elderly":
                warnings.append("Consider lower initial dose for elderly patients")
                warnings_ar.append("يُنصح ببدء جرعة أقل لكبار السن")
        
        result["warnings"] = warnings
        result["warnings_ar"] = warnings_ar
        
        # Add contraindications
        result["contraindications"] = medicine.get("contraindications", [])
        
        return result


# Singleton instance
_dosage_service: Optional[DosageCalculatorService] = None


def get_dosage_service() -> DosageCalculatorService:
    """Get or create dosage calculator service instance."""
    global _dosage_service
    if _dosage_service is None:
        _dosage_service = DosageCalculatorService()
    return _dosage_service
