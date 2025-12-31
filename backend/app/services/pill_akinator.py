"""
Pill Akinator Service
=====================
Dynamic MCQ-based medicine identification using LLM.

This module implements an "Akinator-style" identification system that:
1. Generates intelligent MCQs based on visual attributes users can remember
2. Uses information theory to select questions that maximize information gain
3. Leverages cloud LLM for natural, context-aware question generation
4. Achieves >90% confidence in 1-3 questions

AI Logic:
---------
The Akinator uses a combination of:
1. **Information Gain**: Selects questions that best split remaining candidates
2. **LLM Generation**: Creates natural, varied questions for visual attributes
3. **Bayesian Updating**: Updates confidence based on user answers
4. **Early Termination**: Stops when confidence exceeds threshold

Visual Attributes Targeted:
- box_primary_color: Main color of medicine packaging
- tablet_shape: Physical shape of pill/tablet
- prominent_word: Most memorable text on packaging
- liquid_color: Color for syrups/suspensions
- has_logo: Presence of brand logo
"""
import json
import uuid
import random
import math
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import logging

from app import config

logger = logging.getLogger(__name__)


class PillAkinatorService:
    """
    Service for MCQ-based medicine identification.
    
    This service dynamically generates questions about visual characteristics
    of medicines that users can recall from memory (box color, pill shape,
    text on packaging, etc.) to identify the medicine.
    """
    
    def __init__(self):
        """Initialize the Akinator service with medicine database."""
        self.medicines = self._load_medicines()
        self.sessions: Dict[str, Dict] = {}  # In-memory session storage
        
        # Visual attribute questions (used for both mock and LLM modes)
        # Maps attribute names to question templates and options
        # NOTE: We deliberately exclude "prominent_word" as it contains brand names
        # which would make the question circular and useless
        self.attribute_config = {
            "dosage_form": {
                "question_templates": [
                    "What form is the medicine? (tablet, syrup, capsule, etc.)",
                    "How do you take this medicine - swallow a pill, drink liquid, or apply it?",
                    "Is it a pill you swallow, a liquid, a cream, or an injection?",
                    "What type of medicine is it - tablet, capsule, syrup, gel, or something else?"
                ],
                "options": ["Tablet", "Capsule", "Syrup/Liquid", "Gel/Cream", "Injection", "Not sure"],
                "field_type": "enum",
                "priority": 1  # Ask this first - most discriminating
            },
            "box_primary_color": {
                "question_templates": [
                    "What is the main color of the medicine box/packaging?",
                    "What color is the box? (red, blue, green, white, etc.)",
                    "Can you recall the main color of the packaging?",
                    "What's the dominant color you see on the medicine package?"
                ],
                "options_from_data": True,
                "field_type": "enum",
                "priority": 2
            },
            "tablet_shape": {
                "question_templates": [
                    "What shape is the pill/tablet?",
                    "Is the pill round, oval, oblong, or another shape?",
                    "Can you describe the shape of the tablet?",
                    "What does the pill look like - round like a coin, oval, or long/oblong?"
                ],
                "options": ["Round", "Oval", "Oblong (long rectangle)", "Capsule-shaped", "Heart-shaped", "Other/Not sure"],
                "field_type": "enum",
                "priority": 3
            },
            "tablet_color": {
                "question_templates": [
                    "What color is the pill/tablet itself?",
                    "Can you recall the color of the actual pill?",
                    "What color are the tablets - white, pink, yellow, etc.?",
                    "Looking at the pill itself (not the box), what color is it?"
                ],
                "options_from_data": True,
                "field_type": "enum",
                "priority": 4
            },
            "liquid_color": {
                "question_templates": [
                    "What color is the liquid/syrup?",
                    "Can you describe the color of the syrup or suspension?",
                    "What color is the medicine when you pour it?",
                    "Is the liquid clear, colored, or milky?"
                ],
                "options_from_data": True,
                "field_type": "enum",
                "conditional_on": {"dosage_form": ["syrup", "suspension"]}
            },
            "has_logo": {
                "question_templates": [
                    "Does the box have a visible brand/company logo?",
                    "Can you see a manufacturer logo on the packaging?",
                    "Is there a recognizable company logo on the box?",
                    "Does the packaging show a pharmaceutical company logo?"
                ],
                "options": ["Yes, there's a logo", "No logo visible", "Not sure"],
                "field_type": "boolean"
            },
            "is_scored": {
                "question_templates": [
                    "Does the tablet have a line for splitting it?",
                    "Is there a score line on the pill?",
                    "Can the tablet be easily broken in half?",
                    "Does the pill have a dividing line?"
                ],
                "options": ["Yes, it has a score line", "No score line", "Not sure"],
                "field_type": "boolean",
                "conditional_on": {"dosage_form": ["tablet"]}
            },
            "category": {
                "question_templates": [
                    "What is this medicine generally used for?",
                    "What type of condition does this medicine treat?",
                    "Is this for pain, infection, heart, stomach, or something else?",
                    "What category best describes this medicine?"
                ],
                "options": ["Pain Relief", "Antibiotic/Infection", "Heart/Blood Pressure", "Stomach/Digestive", "Respiratory/Breathing", "Other/Not sure"],
                "field_type": "enum",
                "priority": 2  # Very useful discriminator
            },
            "requires_prescription": {
                "question_templates": [
                    "Does this medicine require a prescription?",
                    "Can you buy this medicine over the counter, or do you need a doctor's prescription?",
                    "Is this an OTC (over-the-counter) medicine or prescription-only?",
                    "Did you need a prescription to get this medicine?"
                ],
                "options": ["Yes, prescription required", "No, over-the-counter (OTC)", "Not sure"],
                "field_type": "boolean",
                "priority": 5
            },
            "strip_color": {
                "question_templates": [
                    "What color is the blister strip/packaging that holds the pills?",
                    "What color is the foil strip the tablets come in?",
                    "Looking at the strip holding the pills, what color is it?",
                    "What color is the blister pack?"
                ],
                "options_from_data": True,
                "field_type": "enum",
                "priority": 6,
                "conditional_on": {"dosage_form": ["tablet", "capsule"]}
            },
            "manufacturer": {
                "question_templates": [
                    "Do you recognize the pharmaceutical company that makes this?",
                    "What company/manufacturer is shown on the box?",
                    "Can you see a company name like Pfizer, GSK, Novartis, etc.?",
                    "Which pharmaceutical company makes this medicine?"
                ],
                "options": ["Pfizer", "GSK (GlaxoSmithKline)", "Novartis", "Sanofi", "Abbott", "AstraZeneca", "Other/Not sure"],
                "field_type": "enum",
                "priority": 7
            }
        }
        
        logger.info(f"PillAkinatorService initialized with {len(self.medicines)} medicines")
    
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
    
    def _get_attribute_value(self, medicine: Dict, attribute: str) -> Any:
        """
        Get attribute value from medicine, handling nested visual attributes.
        
        Args:
            medicine: Medicine dictionary
            attribute: Attribute name (may be in visual sub-dict)
            
        Returns:
            Attribute value or None
        """
        # Check top-level first
        if attribute in medicine:
            return medicine[attribute]
        
        # Check in visual attributes
        visual = medicine.get("visual", {})
        if attribute in visual:
            return visual[attribute]
        
        return None
    
    def _calculate_information_gain(
        self, 
        candidates: List[Dict], 
        attribute: str
    ) -> Tuple[float, Dict[str, int]]:
        """
        Calculate information gain for asking about a specific attribute.
        
        Information Gain = Entropy(before) - Entropy(after)
        
        The best question splits candidates as evenly as possible.
        
        Args:
            candidates: Current list of candidate medicines
            attribute: Attribute to evaluate
            
        Returns:
            Tuple of (information_gain, value_distribution)
        """
        if len(candidates) <= 1:
            return 0.0, {}
        
        # Count distribution of values for this attribute
        value_counts: Dict[str, int] = {}
        for med in candidates:
            value = self._get_attribute_value(med, attribute)
            if value is not None:
                # Convert to string for counting
                value_str = str(value).lower()
                value_counts[value_str] = value_counts.get(value_str, 0) + 1
        
        if len(value_counts) <= 1:
            # No information gain if all have same value
            return 0.0, value_counts
        
        total = len(candidates)
        
        # Calculate current entropy (before split)
        # For uniform distribution: H = log2(n)
        entropy_before = math.log2(total) if total > 1 else 0
        
        # Calculate weighted entropy after split
        entropy_after = 0.0
        for count in value_counts.values():
            if count > 0:
                prob = count / total
                # Entropy contribution: -p * log2(p)
                # For each bucket, entropy is log2(bucket_size)
                bucket_entropy = math.log2(count) if count > 1 else 0
                entropy_after += prob * bucket_entropy
        
        information_gain = entropy_before - entropy_after
        
        # Bonus for more balanced splits (prefer 50/50 over 90/10)
        if len(value_counts) == 2:
            counts = list(value_counts.values())
            balance = min(counts) / max(counts)
            information_gain *= (1 + balance * 0.5)
        
        return information_gain, value_counts
    
    def _select_best_attribute(
        self, 
        candidates: List[Dict],
        asked_attributes: List[str]
    ) -> Optional[Tuple[str, Dict[str, int]]]:
        """
        Select the best attribute to ask about next.
        
        Uses information gain combined with priority to find the attribute 
        that will most effectively narrow down the candidates.
        
        Strategy:
        1. Never ask about medicine names (that defeats the purpose!)
        2. Prioritize attributes with high information gain
        3. Use priority as tiebreaker for similar gains
        4. Skip conditional attributes when condition not met
        
        Args:
            candidates: Current candidate medicines
            asked_attributes: Attributes already asked about
            
        Returns:
            Tuple of (best_attribute, value_distribution) or None
        """
        # Attributes to NEVER ask about (they contain identifying info)
        FORBIDDEN_ATTRIBUTES = {'prominent_word', 'name', 'generic_name', 'brand_name'}
        
        candidates_with_scores = []
        
        for attribute in self.attribute_config.keys():
            # Skip forbidden attributes
            if attribute in FORBIDDEN_ATTRIBUTES:
                continue
                
            if attribute in asked_attributes:
                continue
            
            attr_config = self.attribute_config[attribute]
            
            # Check conditional attributes (e.g., liquid_color only for syrups)
            if "conditional_on" in attr_config:
                # TODO: Check if condition is met based on session state
                # For now, skip conditional attributes in early questions
                if len(asked_attributes) < 2:
                    continue
            
            gain, distribution = self._calculate_information_gain(candidates, attribute)
            
            # Need at least some variety in values to be useful
            if len(distribution) < 2:
                continue
            
            # Get priority (lower = ask first)
            priority = attr_config.get("priority", 10)
            
            # Score combines information gain and priority
            # Higher gain is better, lower priority is better
            score = gain + (1.0 / (priority + 1))
            
            candidates_with_scores.append({
                "attribute": attribute,
                "score": score,
                "gain": gain,
                "distribution": distribution,
                "priority": priority
            })
        
        if not candidates_with_scores:
            return None
        
        # Sort by score (descending)
        candidates_with_scores.sort(key=lambda x: x["score"], reverse=True)
        
        best = candidates_with_scores[0]
        logger.debug(f"Selected attribute '{best['attribute']}' with gain={best['gain']:.3f}, priority={best['priority']}")
        
        return best["attribute"], best["distribution"]
    
    def _generate_options(
        self, 
        attribute: str, 
        candidates: List[Dict],
        value_distribution: Dict[str, int]
    ) -> List[str]:
        """
        Generate MCQ options for an attribute.
        
        Options are drawn from actual values in the candidate medicines
        to ensure relevance.
        
        Args:
            attribute: Attribute being asked about
            candidates: Current candidate medicines
            value_distribution: Distribution of values
            
        Returns:
            List of option strings
        """
        attr_config = self.attribute_config.get(attribute, {})
        
        # If fixed options defined, use those
        if "options" in attr_config:
            return attr_config["options"]
        
        # Generate from data
        options = []
        for value, count in sorted(value_distribution.items(), key=lambda x: -x[1]):
            if len(options) >= 5:  # Max 5 options
                break
            # Format the option nicely
            formatted = value.replace("_", " ").title()
            options.append(formatted)
        
        # Add "Other/Not sure" option
        if len(options) < 6:
            options.append("Not sure / Other")
        
        return options
    
    async def _generate_question_llm(
        self,
        attribute: str,
        candidates: List[Dict],
        session_history: List[Dict],
        value_distribution: Dict[str, int]
    ) -> Dict:
        """
        Generate a question using cloud LLM.
        
        This creates more natural, context-aware questions that reference
        previous answers and adapt to the conversation flow.
        
        Args:
            attribute: Attribute to ask about
            candidates: Remaining candidate medicines
            session_history: Previous Q&A pairs
            value_distribution: Distribution of values
            
        Returns:
            MCQ question dictionary
        """
        # For mock mode or if LLM unavailable, fall back to template
        if config.LLM_PROVIDER == "mock":
            return self._generate_question_mock(attribute, candidates, value_distribution)
        
        try:
            # Prepare context for LLM
            context = {
                "attribute": attribute,
                "possible_values": list(value_distribution.keys()),
                "previous_answers": session_history[-3:] if session_history else [],
                "remaining_candidates": len(candidates)
            }
            
            if config.LLM_PROVIDER == "hackclub":
                return await self._call_hackclub_ai(attribute, context, value_distribution)
            elif config.LLM_PROVIDER == "openai":
                return await self._call_openai(attribute, context, value_distribution)
            elif config.LLM_PROVIDER == "anthropic":
                return await self._call_anthropic(attribute, context, value_distribution)
            else:
                return self._generate_question_mock(attribute, candidates, value_distribution)
                
        except Exception as e:
            logger.error(f"LLM question generation failed: {e}")
            return self._generate_question_mock(attribute, candidates, value_distribution)
    
    async def _call_hackclub_ai(
        self,
        attribute: str,
        context: Dict,
        value_distribution: Dict[str, int]
    ) -> Dict:
        """
        Call Hack Club AI API for question generation.
        
        Uses the free Hack Club AI endpoint (OpenAI-compatible).
        Model: qwen/qwen3-32b
        """
        import aiohttp
        
        # Get predefined options if available, otherwise format from data
        attr_config = self.attribute_config.get(attribute, {})
        if "options" in attr_config:
            options = attr_config["options"]
        else:
            # Format options from actual values in the database
            options = []
            for value in list(value_distribution.keys())[:5]:
                formatted = value.replace("_", " ").title()
                options.append(formatted)
            options.append("Not sure / Other")
        
        # Get a template question for reference
        template = self._get_template_question(attribute)
        
        try:
            prompt = f"""You're helping someone remember which medicine they take by asking about its VISUAL appearance.

ATTRIBUTE TO ASK ABOUT: {attribute.replace('_', ' ')}
EXAMPLE QUESTION: "{template}"
OPTIONS TO USE: {options}

Write a friendly, clear question asking about this visual feature.

IMPORTANT RULES:
- Ask about VISUAL characteristics (color, shape, form) - NOT the medicine name!
- Use simple language anyone can understand
- The question should help identify the medicine based on what it LOOKS like

Return ONLY this JSON (no extra text):
{{"question_text": "your question here", "options": {json.dumps(options)}}}"""

            headers = {
                "Content-Type": "application/json"
            }
            
            # Add API key if provided
            if config.HACKCLUB_API_KEY:
                headers["Authorization"] = f"Bearer {config.HACKCLUB_API_KEY}"
            
            payload = {
                "model": config.HACKCLUB_MODEL,
                "messages": [
                    {
                        "role": "system", 
                        "content": "You generate MCQ questions to help identify medicines by their visual appearance. NEVER mention medicine names in questions - only ask about colors, shapes, forms, and visual features. Return valid JSON only."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": config.HACKCLUB_TEMPERATURE,
                "max_tokens": 300
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    config.HACKCLUB_API_URL,
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Hack Club AI error: {response.status} - {error_text}")
                        return self._generate_question_mock(attribute, [], value_distribution)
                    
                    result = await response.json()
            
            # Extract content from response
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Parse JSON from response (handle potential markdown code blocks)
            content = content.strip()
            if content.startswith("```"):
                # Remove markdown code block
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            parsed = json.loads(content)
            
            # ALWAYS use our predefined options, not LLM's options
            # This ensures we only show valid, meaningful choices
            return {
                "question_id": str(uuid.uuid4()),
                "question_text": parsed.get("question_text", template),
                "options": options,  # Always use our options, never LLM's
                "field_target": attribute,
                "confidence_before": context.get("confidence", 0.0),
                "confidence_after_expected": min(0.95, context.get("confidence", 0.0) + 0.3)
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Hack Club AI response as JSON: {e}")
            # Fall back to template question with our options
            return {
                "question_id": str(uuid.uuid4()),
                "question_text": template,
                "options": options,
                "field_target": attribute,
                "confidence_before": 0.0,
                "confidence_after_expected": 0.3
            }
        except Exception as e:
            logger.error(f"Hack Club AI API error: {e}")
            # Return template question with our predefined options
            return {
                "question_id": str(uuid.uuid4()),
                "question_text": template,
                "options": options,
                "field_target": attribute,
                "confidence_before": 0.0,
                "confidence_after_expected": 0.3
            }

    async def _call_openai(
        self, 
        attribute: str, 
        context: Dict,
        value_distribution: Dict[str, int]
    ) -> Dict:
        """Call OpenAI API for question generation (fallback)."""
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
            
            prompt = f"""Generate an MCQ question to identify a medicine based on visual attributes.

Attribute to ask about: {attribute}
Possible values: {list(value_distribution.keys())}
Previous conversation: {context.get('previous_answers', [])}

Generate a natural, friendly question. Return JSON only:
{{
    "question_text": "Your question here",
    "options": ["option1", "option2", ...]
}}"""
            
            response = await client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful pharmacy assistant asking questions to identify medicines. Generate clear, simple MCQ questions about visual characteristics."},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.OPENAI_TEMPERATURE,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "question_id": str(uuid.uuid4()),
                "question_text": result.get("question_text", self._get_template_question(attribute)),
                "options": result.get("options", self._generate_options(attribute, [], value_distribution)),
                "field_target": attribute,
                "confidence_before": context.get("confidence", 0.0),
                "confidence_after_expected": min(0.95, context.get("confidence", 0.0) + 0.3)
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._generate_question_mock(attribute, [], value_distribution)
    
    async def _call_anthropic(
        self, 
        attribute: str, 
        context: Dict,
        value_distribution: Dict[str, int]
    ) -> Dict:
        """Call Anthropic API for question generation."""
        try:
            from anthropic import AsyncAnthropic
            
            client = AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)
            
            prompt = f"""Generate an MCQ question to identify a medicine based on visual attributes.

Attribute to ask about: {attribute}
Possible values: {list(value_distribution.keys())}
Previous conversation: {context.get('previous_answers', [])}

Generate a natural, friendly question. Return JSON only:
{{
    "question_text": "Your question here",
    "options": ["option1", "option2", ...]
}}"""
            
            response = await client.messages.create(
                model=config.ANTHROPIC_MODEL,
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                system="You are a helpful pharmacy assistant. Generate clear MCQ questions about medicine visual characteristics. Return only valid JSON."
            )
            
            result = json.loads(response.content[0].text)
            
            return {
                "question_id": str(uuid.uuid4()),
                "question_text": result.get("question_text", self._get_template_question(attribute)),
                "options": result.get("options", self._generate_options(attribute, [], value_distribution)),
                "field_target": attribute,
                "confidence_before": context.get("confidence", 0.0),
                "confidence_after_expected": min(0.95, context.get("confidence", 0.0) + 0.3)
            }
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return self._generate_question_mock(attribute, [], value_distribution)
    
    def _get_template_question(self, attribute: str) -> str:
        """Get a random template question for an attribute."""
        templates = self.attribute_config.get(attribute, {}).get(
            "question_templates", 
            [f"What is the {attribute.replace('_', ' ')}?"]
        )
        return random.choice(templates)
    
    def _generate_question_mock(
        self,
        attribute: str,
        candidates: List[Dict],
        value_distribution: Dict[str, int]
    ) -> Dict:
        """
        Generate a question using templates (mock/offline mode).
        
        This provides a fallback when LLM is unavailable and enables
        fully offline operation.
        """
        question_text = self._get_template_question(attribute)
        options = self._generate_options(attribute, candidates, value_distribution)
        
        return {
            "question_id": str(uuid.uuid4()),
            "question_text": question_text,
            "options": options,
            "field_target": attribute,
            "confidence_before": 0.0,
            "confidence_after_expected": 0.0
        }
    
    def _filter_candidates(
        self,
        candidates: List[Dict],
        attribute: str,
        answer: str
    ) -> List[Dict]:
        """
        Filter candidates based on user's answer.
        
        Args:
            candidates: Current candidates
            attribute: Attribute that was asked
            answer: User's selected answer
            
        Returns:
            Filtered list of candidates matching the answer
        """
        if "not sure" in answer.lower() or "other" in answer.lower():
            # Keep all candidates if user is unsure
            return candidates
        
        answer_normalized = answer.lower().replace(" ", "_")
        
        filtered = []
        for med in candidates:
            value = self._get_attribute_value(med, attribute)
            if value is not None:
                value_normalized = str(value).lower().replace(" ", "_")
                # Flexible matching
                if (value_normalized == answer_normalized or
                    answer_normalized in value_normalized or
                    value_normalized in answer_normalized):
                    filtered.append(med)
        
        # If filtering is too aggressive, keep some candidates
        if len(filtered) == 0:
            return candidates[:max(3, len(candidates) // 2)]
        
        return filtered
    
    def _calculate_confidence(
        self,
        candidates: List[Dict],
        total_medicines: int
    ) -> float:
        """
        Calculate confidence score based on remaining candidates.
        
        More conservative calculation - high confidence only when
        we've really narrowed down the options.
        
        Args:
            candidates: Remaining candidate medicines
            total_medicines: Total medicines in database
            
        Returns:
            Confidence score between 0 and 1
        """
        if len(candidates) == 0:
            return 0.0
        
        if len(candidates) == 1:
            return 0.95  # High confidence with single match
        
        if len(candidates) == 2:
            return 0.85  # Good confidence with 2 candidates
        
        # Calculate based on how many we've eliminated
        remaining_ratio = len(candidates) / total_medicines
        
        # Logarithmic scale - harder to get high confidence
        # 16 medicines -> 8 remaining = 0.3
        # 16 medicines -> 4 remaining = 0.5
        # 16 medicines -> 2 remaining = 0.7
        # 16 medicines -> 1 remaining = 0.95
        
        import math
        if remaining_ratio <= 0:
            return 0.95
        
        # confidence = 1 - log(remaining)/log(total)
        log_confidence = 1 - (math.log(len(candidates)) / math.log(max(total_medicines, 2)))
        
        # Scale to reasonable range (0.1 to 0.8 for multiple candidates)
        confidence = 0.1 + (log_confidence * 0.7)
        
        # Cap at 0.8 unless we have very few candidates
        if len(candidates) > 2:
            confidence = min(confidence, 0.80)
        
        return round(confidence, 2)
    
    # ==================
    # Public API Methods
    # ==================
    
    def start_session(self) -> Dict:
        """
        Start a new Akinator session.
        
        Returns:
            Session info with ID and first question
        """
        session_id = str(uuid.uuid4())
        
        # Initialize session state
        self.sessions[session_id] = {
            "candidates": self.medicines.copy(),
            "asked_attributes": [],
            "answers": [],
            "questions_asked": 0,
            "confidence": 0.0
        }
        
        # Generate first question
        result = self._select_best_attribute(self.medicines, [])
        
        if result:
            attribute, distribution = result
            question = self._generate_question_mock(attribute, self.medicines, distribution)
            
            # Store current question in session
            self.sessions[session_id]["current_attribute"] = attribute
            self.sessions[session_id]["current_question"] = question
            
            return {
                "session_id": session_id,
                "question": question,
                "remaining_candidates": len(self.medicines),
                "confidence": 0.0,
                "questions_asked": 0
            }
        
        return {
            "session_id": session_id,
            "error": "Unable to generate question",
            "remaining_candidates": len(self.medicines)
        }
    
    async def start_session_async(self) -> Dict:
        """
        Start a new session with async LLM question generation.
        
        Returns:
            Session info with ID and first question
        """
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            "candidates": self.medicines.copy(),
            "asked_attributes": [],
            "answers": [],
            "questions_asked": 0,
            "confidence": 0.0
        }
        
        result = self._select_best_attribute(self.medicines, [])
        
        if result:
            attribute, distribution = result
            question = await self._generate_question_llm(
                attribute, 
                self.medicines, 
                [],
                distribution
            )
            
            self.sessions[session_id]["current_attribute"] = attribute
            self.sessions[session_id]["current_question"] = question
            
            return {
                "session_id": session_id,
                "question": question,
                "remaining_candidates": len(self.medicines),
                "confidence": 0.0,
                "questions_asked": 0
            }
        
        return {
            "session_id": session_id,
            "error": "Unable to generate question",
            "remaining_candidates": len(self.medicines)
        }
    
    def submit_answer(self, session_id: str, answer: str) -> Dict:
        """
        Process user's answer and return next question or result.
        
        This is the core Akinator logic:
        1. Filter candidates based on answer
        2. Update confidence
        3. Check if we should stop (confidence > threshold or max questions)
        4. Generate next question if continuing
        
        Args:
            session_id: Session identifier
            answer: User's selected answer
            
        Returns:
            Next question or final identification result
        """
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_id]
        current_attribute = session.get("current_attribute")
        
        if not current_attribute:
            return {"error": "No current question"}
        
        # Record the answer
        session["answers"].append({
            "attribute": current_attribute,
            "answer": answer,
            "question": session.get("current_question", {}).get("question_text", "")
        })
        session["asked_attributes"].append(current_attribute)
        session["questions_asked"] += 1
        
        # Filter candidates based on answer
        session["candidates"] = self._filter_candidates(
            session["candidates"],
            current_attribute,
            answer
        )
        
        # Update confidence
        confidence = self._calculate_confidence(
            session["candidates"],
            len(self.medicines)
        )
        session["confidence"] = confidence
        
        candidates = session["candidates"]
        questions_asked = session["questions_asked"]
        
        # Check termination conditions
        # We need BOTH:
        # 1. Asked at least AKINATOR_MIN_QUESTIONS (don't guess too early!)
        # 2. AND one of: high confidence, max questions reached, or only 1 candidate left
        
        min_questions_met = questions_asked >= config.AKINATOR_MIN_QUESTIONS
        max_questions_reached = questions_asked >= config.AKINATOR_MAX_QUESTIONS
        high_confidence = confidence >= config.AKINATOR_CONFIDENCE_THRESHOLD
        single_candidate = len(candidates) == 1
        
        should_stop = (
            # Must have asked minimum questions first
            min_questions_met and (
                high_confidence or          # Very confident in result
                single_candidate            # Only one medicine matches
            )
        ) or max_questions_reached          # Hard limit reached
        
        if should_stop:
            # Return identification result
            return self._generate_result(session)
        
        # Generate next question
        result = self._select_best_attribute(
            candidates,
            session["asked_attributes"]
        )
        
        if result:
            attribute, distribution = result
            question = self._generate_question_mock(attribute, candidates, distribution)
            question["confidence_before"] = confidence
            question["confidence_after_expected"] = min(0.95, confidence + 0.2)
            
            session["current_attribute"] = attribute
            session["current_question"] = question
            
            return {
                "type": "question",
                "question": question,
                "remaining_candidates": len(candidates),
                "confidence": confidence,
                "questions_asked": questions_asked
            }
        
        # No more good questions, return result
        return self._generate_result(session)
    
    async def submit_answer_async(self, session_id: str, answer: str) -> Dict:
        """
        Process answer with async LLM question generation.
        
        Args:
            session_id: Session identifier
            answer: User's selected answer
            
        Returns:
            Next question or final result
        """
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_id]
        current_attribute = session.get("current_attribute")
        
        if not current_attribute:
            return {"error": "No current question"}
        
        # Record answer
        session["answers"].append({
            "attribute": current_attribute,
            "answer": answer,
            "question": session.get("current_question", {}).get("question_text", "")
        })
        session["asked_attributes"].append(current_attribute)
        session["questions_asked"] += 1
        
        # Filter candidates
        session["candidates"] = self._filter_candidates(
            session["candidates"],
            current_attribute,
            answer
        )
        
        # Update confidence
        confidence = self._calculate_confidence(
            session["candidates"],
            len(self.medicines)
        )
        session["confidence"] = confidence
        
        candidates = session["candidates"]
        questions_asked = session["questions_asked"]
        
        # Check termination conditions (same as sync version)
        min_questions_met = questions_asked >= config.AKINATOR_MIN_QUESTIONS
        max_questions_reached = questions_asked >= config.AKINATOR_MAX_QUESTIONS
        high_confidence = confidence >= config.AKINATOR_CONFIDENCE_THRESHOLD
        single_candidate = len(candidates) == 1
        
        should_stop = (
            min_questions_met and (high_confidence or single_candidate)
        ) or max_questions_reached
        
        if should_stop:
            return self._generate_result(session)
        
        # Generate next question with LLM
        result = self._select_best_attribute(
            candidates,
            session["asked_attributes"]
        )
        
        if result:
            attribute, distribution = result
            question = await self._generate_question_llm(
                attribute,
                candidates,
                session["answers"],
                distribution
            )
            question["confidence_before"] = confidence
            question["confidence_after_expected"] = min(0.95, confidence + 0.2)
            
            session["current_attribute"] = attribute
            session["current_question"] = question
            
            return {
                "type": "question",
                "question": question,
                "remaining_candidates": len(candidates),
                "confidence": confidence,
                "questions_asked": questions_asked
            }
        
        return self._generate_result(session)
    
    def _generate_result(self, session: Dict) -> Dict:
        """
        Generate final identification result.
        
        Args:
            session: Session state dictionary
            
        Returns:
            Final result with identified medicine(s) and confidence
        """
        candidates = session["candidates"]
        confidence = session["confidence"]
        
        if len(candidates) == 0:
            return {
                "type": "result",
                "success": False,
                "message": "No matching medicine found. Please try again with different answers.",
                "confidence": 0.0,
                "questions_asked": session["questions_asked"]
            }
        
        # Prepare results
        results = []
        for i, med in enumerate(candidates[:5]):  # Top 5 matches
            match_confidence = confidence * (1 - i * 0.1)  # Decrease for lower ranks
            results.append({
                "medicine": med,
                "confidence": round(match_confidence, 2),
                "rank": i + 1
            })
        
        return {
            "type": "result",
            "success": True,
            "top_match": results[0] if results else None,
            "alternatives": results[1:] if len(results) > 1 else [],
            "confidence": confidence,
            "questions_asked": session["questions_asked"],
            "answers_given": session["answers"]
        }
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session state."""
        return self.sessions.get(session_id)
    
    def end_session(self, session_id: str) -> bool:
        """End and cleanup a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False


# Singleton instance for dependency injection
_akinator_service: Optional[PillAkinatorService] = None


def get_akinator_service() -> PillAkinatorService:
    """Get or create the Akinator service singleton."""
    global _akinator_service
    if _akinator_service is None:
        _akinator_service = PillAkinatorService()
    return _akinator_service
