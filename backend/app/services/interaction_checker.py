"""
Drug Interaction Checker Service
================================
Check for harmful drug-drug interactions.

This module provides medication safety verification by:
1. Checking direct drug-drug interactions
2. Checking drug class interactions
3. Identifying contraindicated combinations
4. Suggesting safer alternatives

Interaction Severity Levels:
- CONTRAINDICATED: Must never be combined
- MAJOR: Serious harm possible, avoid combination
- MODERATE: May require dose adjustment or monitoring
- MINOR: Minimal clinical significance

AI Logic:
---------
1. **Direct Matching**: Check if specific drugs have known interactions
2. **Group Matching**: Check drug class interactions (e.g., all NSAIDs + anticoagulants)
3. **Severity Assessment**: Prioritize by clinical significance
4. **Alternative Suggestion**: Find safer substitute drugs
5. **Risk Scoring**: Calculate overall risk level
"""
import json
from typing import List, Dict, Optional, Set, Tuple
from pathlib import Path
import logging
from enum import Enum

from app import config
from app.models.interaction import InteractionSeverity

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Overall risk assessment levels."""
    CRITICAL = "critical"  # Contains contraindicated combination
    HIGH = "high"  # Contains major interaction
    MODERATE = "moderate"  # Contains moderate interaction
    LOW = "low"  # Minor or no interactions
    SAFE = "safe"  # No interactions found


class InteractionCheckerService:
    """
    Service for checking drug-drug interactions.
    
    Verifies medication safety by checking for known interactions
    between drugs and drug classes, providing warnings and alternatives.
    """
    
    def __init__(self):
        """Initialize the Interaction Checker service."""
        self.medicines = self._load_medicines()
        self.interactions = self._load_interactions()
        
        # Build lookup indices for fast searching
        self.medicine_by_id = {m["id"]: m for m in self.medicines}
        self.medicine_by_name = {m["name"].lower(): m for m in self.medicines}
        
        # Build interaction lookup by drug and drug group
        self.interaction_by_drug = self._build_interaction_index()
        
        logger.info(
            f"InteractionCheckerService initialized with "
            f"{len(self.medicines)} medicines and {len(self.interactions)} interactions"
        )
    
    def _load_medicines(self) -> List[Dict]:
        """Load medicine database."""
        try:
            with open(config.MEDICINES_DB_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("medicines", [])
        except Exception as e:
            logger.error(f"Error loading medicines: {e}")
            return []
    
    def _load_interactions(self) -> List[Dict]:
        """Load interaction database."""
        try:
            with open(config.INTERACTIONS_DB_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("interactions", [])
        except Exception as e:
            logger.error(f"Error loading interactions: {e}")
            return []
    
    def _build_interaction_index(self) -> Dict[str, List[Dict]]:
        """
        Build index for fast interaction lookup.
        
        Maps drug names and groups to their interactions.
        """
        index = {}
        
        for interaction in self.interactions:
            # Index by drug_a
            drug_a = interaction.get("drug_a", "").lower()
            if drug_a:
                if drug_a not in index:
                    index[drug_a] = []
                index[drug_a].append(interaction)
            
            # Index by drug_a_group
            group_a = interaction.get("drug_a_group", "").lower()
            if group_a:
                if group_a not in index:
                    index[group_a] = []
                index[group_a].append(interaction)
            
            # Index by drug_b
            drug_b = interaction.get("drug_b", "").lower()
            if drug_b:
                if drug_b not in index:
                    index[drug_b] = []
                index[drug_b].append(interaction)
            
            # Index by drug_b_group
            group_b = interaction.get("drug_b_group", "").lower()
            if group_b:
                if group_b not in index:
                    index[group_b] = []
                index[group_b].append(interaction)
        
        return index
    
    def _get_medicine_groups(self, medicine: Dict) -> Set[str]:
        """
        Get all interaction groups for a medicine.
        
        Args:
            medicine: Medicine dictionary
            
        Returns:
            Set of group names (lowercase)
        """
        groups = set()
        
        # From interaction_groups field
        for group in medicine.get("interaction_groups", []):
            groups.add(group.lower())
        
        # Also add drug class as a group
        drug_class = medicine.get("drug_class", "")
        if drug_class:
            groups.add(drug_class.lower())
        
        # Add category
        category = medicine.get("category", "")
        if category:
            groups.add(category.lower())
        
        return groups
    
    def _find_interactions(
        self,
        medicine_a: Dict,
        medicine_b: Dict,
        include_groups: bool = True
    ) -> List[Dict]:
        """
        Find interactions between two medicines.
        
        Checks:
        1. Direct drug-to-drug interaction
        2. Drug-to-group interaction
        3. Group-to-group interaction
        
        Args:
            medicine_a: First medicine
            medicine_b: Second medicine
            include_groups: Whether to check group-level interactions
            
        Returns:
            List of matching interactions
        """
        found_interactions = []
        seen_ids = set()
        
        # Get names and groups
        name_a = medicine_a["name"].lower()
        name_b = medicine_b["name"].lower()
        groups_a = self._get_medicine_groups(medicine_a) if include_groups else set()
        groups_b = self._get_medicine_groups(medicine_b) if include_groups else set()
        
        # Search terms for medicine A
        search_terms_a = {name_a} | groups_a
        search_terms_b = {name_b} | groups_b
        
        # Check interactions from A's perspective
        for term in search_terms_a:
            if term in self.interaction_by_drug:
                for interaction in self.interaction_by_drug[term]:
                    if interaction["id"] in seen_ids:
                        continue
                    
                    # Check if the other drug matches medicine B
                    other_drug = interaction.get("drug_b", "").lower()
                    other_group = interaction.get("drug_b_group", "").lower()
                    
                    if other_drug in search_terms_b or other_group in search_terms_b:
                        found_interactions.append(interaction)
                        seen_ids.add(interaction["id"])
        
        # Check interactions from B's perspective (symmetry)
        for term in search_terms_b:
            if term in self.interaction_by_drug:
                for interaction in self.interaction_by_drug[term]:
                    if interaction["id"] in seen_ids:
                        continue
                    
                    other_drug = interaction.get("drug_b", "").lower()
                    other_group = interaction.get("drug_b_group", "").lower()
                    
                    if other_drug in search_terms_a or other_group in search_terms_a:
                        found_interactions.append(interaction)
                        seen_ids.add(interaction["id"])
        
        return found_interactions
    
    def _calculate_risk_level(self, interactions: List[Dict]) -> RiskLevel:
        """
        Calculate overall risk level from list of interactions.
        
        Args:
            interactions: List of found interactions
            
        Returns:
            RiskLevel enum value
        """
        if not interactions:
            return RiskLevel.SAFE
        
        # Check for highest severity
        severities = [i.get("severity", "unknown") for i in interactions]
        
        if "contraindicated" in severities:
            return RiskLevel.CRITICAL
        elif "major" in severities:
            return RiskLevel.HIGH
        elif "moderate" in severities:
            return RiskLevel.MODERATE
        elif "minor" in severities:
            return RiskLevel.LOW
        else:
            return RiskLevel.LOW
    
    def _find_alternatives(
        self,
        medicine: Dict,
        interacting_medicine: Dict,
        interaction: Dict
    ) -> List[Dict]:
        """
        Find safer alternative medicines.
        
        Looks for medicines with similar use but not interacting
        with the other medicine.
        
        Args:
            medicine: Medicine to find alternative for
            interacting_medicine: Medicine it interacts with
            interaction: The interaction information
            
        Returns:
            List of alternative medicines
        """
        alternatives = []
        
        # First check if interaction specifies alternatives
        specified_alternatives = interaction.get("alternatives", [])
        if specified_alternatives:
            for alt_name in specified_alternatives:
                alt_lower = alt_name.lower()
                if alt_lower in self.medicine_by_name:
                    alternatives.append(self.medicine_by_name[alt_lower])
        
        # If no specified alternatives, find by category
        if not alternatives:
            target_category = medicine.get("category")
            target_use = medicine.get("main_use", "").lower()
            
            for med in self.medicines:
                # Skip the original medicine
                if med["id"] == medicine["id"]:
                    continue
                
                # Check if same category/use
                if (med.get("category") == target_category or 
                    target_use in med.get("main_use", "").lower()):
                    
                    # Check if this alternative interacts with the other medicine
                    alt_interactions = self._find_interactions(med, interacting_medicine)
                    
                    # Only suggest if no major interactions
                    severities = [i.get("severity") for i in alt_interactions]
                    if "contraindicated" not in severities and "major" not in severities:
                        alternatives.append(med)
                        
                        if len(alternatives) >= 3:
                            break
        
        return alternatives[:3]
    
    def _generate_warnings(
        self,
        interactions: List[Dict],
        medicines: List[Dict]
    ) -> List[Dict]:
        """
        Generate user-friendly warning messages.
        
        Args:
            interactions: List of found interactions
            medicines: List of medicines involved
            
        Returns:
            List of warning dictionaries
        """
        warnings = []
        
        # Sort by severity (most severe first)
        severity_order = {
            "contraindicated": 0,
            "major": 1,
            "moderate": 2,
            "minor": 3,
            "unknown": 4
        }
        
        sorted_interactions = sorted(
            interactions,
            key=lambda x: severity_order.get(x.get("severity", "unknown"), 5)
        )
        
        for interaction in sorted_interactions:
            severity = interaction.get("severity", "unknown")
            
            # Generate title based on severity
            if severity == "contraindicated":
                title = "⛔ CONTRAINDICATED - DO NOT COMBINE"
            elif severity == "major":
                title = "🔴 Major Interaction Warning"
            elif severity == "moderate":
                title = "🟡 Moderate Interaction"
            else:
                title = "🟢 Minor Interaction"
            
            warnings.append({
                "severity": severity,
                "title": title,
                "drugs_involved": [interaction.get("drug_a"), interaction.get("drug_b")],
                "message": interaction.get("description", ""),
                "clinical_effects": interaction.get("clinical_effects", []),
                "symptoms_to_watch": interaction.get("symptoms", []),
                "recommendation": interaction.get("recommendation", ""),
                "monitoring": interaction.get("monitoring"),
                "evidence_level": interaction.get("evidence_level", "moderate")
            })
        
        return warnings
    
    def _generate_summary(
        self,
        risk_level: RiskLevel,
        interactions: List[Dict],
        medicines: List[Dict]
    ) -> str:
        """
        Generate human-readable summary of interaction check.
        
        Args:
            risk_level: Calculated risk level
            interactions: List of found interactions
            medicines: List of medicines checked
            
        Returns:
            Summary string
        """
        medicine_names = [m["name"] for m in medicines]
        
        if risk_level == RiskLevel.SAFE:
            return f"No known interactions found between {', '.join(medicine_names)}. " \
                   f"These medications appear safe to take together, but always consult " \
                   f"your pharmacist or doctor."
        
        elif risk_level == RiskLevel.CRITICAL:
            return f"⛔ CRITICAL: These medicines should NOT be taken together. " \
                   f"A contraindicated combination was found. Please consult your " \
                   f"doctor immediately for an alternative medication."
        
        elif risk_level == RiskLevel.HIGH:
            return f"🔴 HIGH RISK: Major interaction(s) found between these medicines. " \
                   f"Taking them together could cause serious harm. Consult your " \
                   f"doctor before continuing."
        
        elif risk_level == RiskLevel.MODERATE:
            return f"🟡 MODERATE RISK: Interaction(s) found that may require dose " \
                   f"adjustment or monitoring. Discuss with your doctor or pharmacist."
        
        else:
            return f"🟢 LOW RISK: Minor interaction(s) found. Generally safe but " \
                   f"be aware of potential effects listed below."
    
    # ==================
    # Public API Methods
    # ==================
    
    def check_interactions(
        self,
        medicine_ids: List[str],
        include_groups: bool = True
    ) -> Dict:
        """
        Check interactions between multiple medicines.
        
        This is the main entry point for interaction checking.
        Checks all pairs of medicines for known interactions.
        
        Args:
            medicine_ids: List of medicine IDs to check
            include_groups: Whether to check drug class interactions
            
        Returns:
            Comprehensive interaction check result
        """
        # Get medicines from IDs
        medicines = []
        not_found = []
        
        for med_id in medicine_ids:
            if med_id in self.medicine_by_id:
                medicines.append(self.medicine_by_id[med_id])
            elif med_id.lower() in self.medicine_by_name:
                medicines.append(self.medicine_by_name[med_id.lower()])
            else:
                not_found.append(med_id)
        
        if not_found:
            logger.warning(f"Medicines not found: {not_found}")
        
        if len(medicines) < 2:
            return {
                "success": True,
                "medicines_checked": [m["name"] for m in medicines],
                "interactions_found": [],
                "warnings": [],
                "risk_level": RiskLevel.SAFE.value,
                "summary": "Need at least 2 medicines to check for interactions.",
                "safe_alternatives": []
            }
        
        # Check all pairs
        all_interactions = []
        checked_pairs = set()
        
        for i, med_a in enumerate(medicines):
            for med_b in medicines[i+1:]:
                pair_key = tuple(sorted([med_a["id"], med_b["id"]]))
                if pair_key in checked_pairs:
                    continue
                checked_pairs.add(pair_key)
                
                interactions = self._find_interactions(med_a, med_b, include_groups)
                
                for interaction in interactions:
                    # Add medicine info to interaction
                    interaction["medicines_involved"] = [med_a["name"], med_b["name"]]
                    all_interactions.append(interaction)
        
        # Calculate risk
        risk_level = self._calculate_risk_level(all_interactions)
        
        # Generate warnings
        warnings = self._generate_warnings(all_interactions, medicines)
        
        # Find alternatives for high-risk interactions
        alternatives = []
        for interaction in all_interactions:
            if interaction.get("severity") in ["contraindicated", "major"]:
                for med in medicines:
                    med_groups = self._get_medicine_groups(med)
                    drug_a_terms = {
                        interaction.get("drug_a", "").lower(),
                        interaction.get("drug_a_group", "").lower()
                    }
                    
                    if med["name"].lower() in drug_a_terms or med_groups & drug_a_terms:
                        # Find the other medicine
                        other_meds = [m for m in medicines if m["id"] != med["id"]]
                        if other_meds:
                            alts = self._find_alternatives(med, other_meds[0], interaction)
                            for alt in alts:
                                alternatives.append({
                                    "for_medicine": med["name"],
                                    "alternative": {
                                        "name": alt["name"],
                                        "generic_name": alt.get("generic_name"),
                                        "category": alt.get("category")
                                    },
                                    "reason": f"Safer alternative that doesn't interact with {other_meds[0]['name']}"
                                })
        
        # Generate summary
        summary = self._generate_summary(risk_level, all_interactions, medicines)
        
        return {
            "success": True,
            "medicines_checked": [m["name"] for m in medicines],
            "interactions_found": [
                {
                    "id": i.get("id"),
                    "drugs_involved": i.get("medicines_involved", []),
                    "severity": i.get("severity"),
                    "description": i.get("description"),
                    "recommendation": i.get("recommendation")
                }
                for i in all_interactions
            ],
            "warnings": warnings,
            "has_contraindicated": risk_level == RiskLevel.CRITICAL,
            "has_major": risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH],
            "risk_level": risk_level.value,
            "summary": summary,
            "safe_alternatives": alternatives
        }
    
    def check_by_names(
        self,
        medicine_names: List[str],
        include_groups: bool = True
    ) -> Dict:
        """
        Check interactions by medicine names.
        
        Convenience method that accepts names instead of IDs.
        
        Args:
            medicine_names: List of medicine names
            include_groups: Whether to check drug class interactions
            
        Returns:
            Interaction check result
        """
        # Convert names to IDs
        medicine_ids = []
        
        for name in medicine_names:
            name_lower = name.lower()
            if name_lower in self.medicine_by_name:
                medicine_ids.append(self.medicine_by_name[name_lower]["id"])
            else:
                # Try partial match
                for med_name, med in self.medicine_by_name.items():
                    if name_lower in med_name or med_name in name_lower:
                        medicine_ids.append(med["id"])
                        break
        
        return self.check_interactions(medicine_ids, include_groups)
    
    def check_single_drug(self, medicine_id: str) -> Dict:
        """
        Get all known interactions for a single medicine.
        
        Useful for showing potential interactions before adding
        to patient's medication list.
        
        Args:
            medicine_id: Medicine ID to check
            
        Returns:
            List of all potential interactions
        """
        if medicine_id not in self.medicine_by_id:
            if medicine_id.lower() not in self.medicine_by_name:
                return {
                    "success": False,
                    "error": f"Medicine not found: {medicine_id}"
                }
            medicine = self.medicine_by_name[medicine_id.lower()]
        else:
            medicine = self.medicine_by_id[medicine_id]
        
        # Get all groups for this medicine
        groups = self._get_medicine_groups(medicine)
        search_terms = {medicine["name"].lower()} | groups
        
        # Find all interactions
        all_interactions = []
        seen_ids = set()
        
        for term in search_terms:
            if term in self.interaction_by_drug:
                for interaction in self.interaction_by_drug[term]:
                    if interaction["id"] not in seen_ids:
                        all_interactions.append(interaction)
                        seen_ids.add(interaction["id"])
        
        # Group by severity
        by_severity = {
            "contraindicated": [],
            "major": [],
            "moderate": [],
            "minor": []
        }
        
        for interaction in all_interactions:
            severity = interaction.get("severity", "minor")
            if severity in by_severity:
                by_severity[severity].append({
                    "interacts_with": (
                        interaction.get("drug_b") 
                        if interaction.get("drug_a", "").lower() in search_terms 
                        else interaction.get("drug_a")
                    ),
                    "severity": severity,
                    "description": interaction.get("description"),
                    "recommendation": interaction.get("recommendation")
                })
        
        return {
            "success": True,
            "medicine": medicine["name"],
            "drug_groups": list(groups),
            "total_interactions": len(all_interactions),
            "interactions_by_severity": by_severity,
            "caution_with": [
                i["interacts_with"] 
                for i in by_severity["contraindicated"] + by_severity["major"]
            ]
        }
    
    def get_all_medicines(self) -> List[Dict]:
        """Get list of all medicines for selection UI."""
        return [
            {
                "id": m["id"],
                "name": m["name"],
                "generic_name": m.get("generic_name"),
                "category": m.get("category"),
                "requires_prescription": m.get("requires_prescription", True)
            }
            for m in self.medicines
        ]


# Singleton instance
_interaction_service: Optional[InteractionCheckerService] = None


def get_interaction_service() -> InteractionCheckerService:
    """Get or create the Interaction Checker service singleton."""
    global _interaction_service
    if _interaction_service is None:
        _interaction_service = InteractionCheckerService()
    return _interaction_service
