"""
Groq LLM Input Normalizer

This module uses Groq's LLama 3.1-8B-Instant model to convert natural language
user input into the structured JSON schema required by the AI models.

STRICT POLICY: 
- NEVER augment, impute, or generate data
- If a value is not explicitly provided, it MUST remain NaN
- Only extract values that are clearly stated in the user input
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("Groq package not installed. Run: pip install groq")


# Master schema with all fields initialized to NaN
MASTER_SCHEMA = {
    "age": None,
    "gender": None,
    "height": None,
    "weight": None,
    "ap_hi": None,
    "ap_lo": None,
    "cholesterol": None,
    "gluc": None,
    "smoke": None,
    "alco": None,
    "active": None,
    "hypertension": None,
    "heart_disease": None,
    "smoking_history": None,
    "bmi": None,
    "HbA1c_level": None,
    "blood_glucose_level": None
}

# Field descriptions for the LLM prompt
FIELD_DESCRIPTIONS = """
FIELD EXTRACTION RULES (EXTRACT ONLY IF EXPLICITLY MENTIONED):

1. age (number): Age in years. Only extract if explicitly stated.

2. gender: 
   - For cardiovascular: integer (1=Female, 2=Male)
   - For diabetes: string ("Female", "Male", "Other")
   - Extract the appropriate format based on context, prefer string format.

3. height (number): Height in centimeters. Convert if given in feet/inches.

4. weight (number): Weight in kilograms. Convert if given in pounds.

5. ap_hi (integer): Systolic blood pressure (the higher number in BP reading like 140/90).

6. ap_lo (integer): Diastolic blood pressure (the lower number in BP reading like 140/90).

7. cholesterol (integer 1-3): 
   - 1 = Normal
   - 2 = Above normal  
   - 3 = Well above normal
   Only extract if cholesterol level is mentioned.

8. gluc (integer 1-3): Glucose level category
   - 1 = Normal
   - 2 = Above normal
   - 3 = Well above normal
   Only extract if glucose category is mentioned.

9. smoke (integer 0-1): Current smoking status
   - 0 = No/Non-smoker
   - 1 = Yes/Smoker

10. alco (integer 0-1): Alcohol consumption
    - 0 = No
    - 1 = Yes

11. active (integer 0-1): Physical activity
    - 0 = No/Inactive/Sedentary
    - 1 = Yes/Active/Exercises

12. hypertension (integer 0-1): Has hypertension
    - 0 = No
    - 1 = Yes

13. heart_disease (integer 0-1): Has heart disease
    - 0 = No
    - 1 = Yes

14. smoking_history (string): One of: "never", "No Info", "current", "former", "ever", "not current"

15. bmi (number): Body Mass Index. Calculate from height/weight if both are given, otherwise only extract if explicitly stated.

16. HbA1c_level (number): Hemoglobin A1c level (typically 3.5-9.0).

17. blood_glucose_level (integer): Blood glucose level in mg/dL (typically 80-300).
"""

SYSTEM_PROMPT = """You are a medical data extraction assistant. Your ONLY job is to extract explicitly stated medical information from user input and convert it to a structured JSON format.

CRITICAL RULES:
1. NEVER invent, assume, or impute any data
2. NEVER fill in missing values with defaults or guesses
3. If a value is NOT explicitly mentioned, it MUST be null
4. Only extract values that are CLEARLY and EXPLICITLY stated
5. If unsure about a value, leave it as null
6. Convert units when necessary (feet to cm, pounds to kg)
7. For blood pressure like "140/90", extract ap_hi=140 and ap_lo=90

{field_descriptions}

OUTPUT FORMAT:
Return ONLY a valid JSON object with the extracted values. Use null for any field not explicitly mentioned.
Do not include any explanation or text outside the JSON.
"""

USER_PROMPT_TEMPLATE = """Extract medical information from the following user input. 
Only extract values that are EXPLICITLY stated. Leave everything else as null.

USER INPUT:
{user_input}

Return a JSON object with these fields (use null for missing values):
- age, gender, height, weight, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active
- hypertension, heart_disease, smoking_history, bmi, HbA1c_level, blood_glucose_level

JSON OUTPUT:"""


@dataclass
class NormalizerConfig:
    """Configuration for the Groq normalizer."""
    api_key: str
    model: str = "llama-3.1-8b-instant"
    temperature: float = 0.1  # Low temperature for deterministic output
    max_tokens: int = 1024


class GroqInputNormalizer:
    """
    Normalizes natural language user input into structured JSON schema
    using Groq's LLama 3.1-8B-Instant model.
    
    STRICT POLICY: Never augments data. Missing values remain NaN/null.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the normalizer.
        
        Args:
            api_key: Groq API key. If not provided, reads from GROQ_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.model = "llama-3.1-8b-instant"
        self.client = None
        
        if not GROQ_AVAILABLE:
            logger.error("Groq package not available")
            return
            
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
            logger.info("Groq client initialized successfully")
        else:
            logger.warning("No Groq API key provided. Set GROQ_API_KEY environment variable.")
    
    def get_empty_schema(self) -> Dict[str, Any]:
        """Return the master schema with all NaN values."""
        return MASTER_SCHEMA.copy()
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse the LLM response and extract JSON.
        
        Args:
            response_text: Raw response from the LLM
            
        Returns:
            Parsed JSON dict
        """
        # Try to extract JSON from the response
        text = response_text.strip()
        
        # Find JSON in the response
        start_idx = text.find('{')
        end_idx = text.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            logger.error(f"No JSON found in response: {text}")
            return self.get_empty_schema()
        
        json_str = text[start_idx:end_idx]
        
        try:
            parsed = json.loads(json_str)
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"JSON string: {json_str}")
            return self.get_empty_schema()
    
    def _validate_and_clean(self, extracted: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean the extracted data.
        Ensures only valid fields are kept and types are correct.
        
        Args:
            extracted: Raw extracted data from LLM
            
        Returns:
            Cleaned data dict
        """
        result = self.get_empty_schema()
        
        for field in MASTER_SCHEMA.keys():
            if field in extracted:
                value = extracted[field]
                
                # Skip null/None values
                if value is None or value == "null" or value == "NaN":
                    continue
                
                # Skip empty strings
                if isinstance(value, str) and value.strip() == "":
                    continue
                
                # Validate specific fields
                try:
                    if field in ["age", "height", "weight", "bmi", "HbA1c_level"]:
                        result[field] = float(value)
                    elif field in ["ap_hi", "ap_lo", "cholesterol", "gluc", "smoke", 
                                   "alco", "active", "hypertension", "heart_disease", 
                                   "blood_glucose_level"]:
                        result[field] = int(value)
                    elif field == "gender":
                        # Normalize gender to string format ("Male", "Female")
                        # The router will convert to int for cardiovascular model
                        if isinstance(value, int):
                            # Convert int (1=Female, 2=Male) to string
                            if value == 1:
                                result[field] = "Female"
                            elif value == 2:
                                result[field] = "Male"
                        elif isinstance(value, str):
                            if value.lower() in ["male", "m", "2"]:
                                result[field] = "Male"
                            elif value.lower() in ["female", "f", "1"]:
                                result[field] = "Female"
                            elif value in ["Female", "Male", "Other"]:
                                result[field] = value
                    elif field == "smoking_history":
                        valid_values = ["never", "No Info", "current", "former", "ever", "not current"]
                        if value in valid_values:
                            result[field] = value
                        elif value.lower() in [v.lower() for v in valid_values]:
                            # Match case-insensitively
                            for v in valid_values:
                                if v.lower() == value.lower():
                                    result[field] = v
                                    break
                    else:
                        result[field] = value
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid value for {field}: {value} - {e}")
                    continue
        
        return result
    
    def normalize(self, user_input: str) -> Dict[str, Any]:
        """
        Normalize natural language user input to structured JSON schema.
        
        Args:
            user_input: Natural language description of patient data
            
        Returns:
            Dict with extracted values, NaN for missing fields
        """
        if not self.client:
            logger.error("Groq client not initialized. Cannot normalize.")
            return {
                "error": "Groq client not initialized. Provide API key.",
                "schema": self.get_empty_schema()
            }
        
        # Build prompts
        system_prompt = SYSTEM_PROMPT.format(field_descriptions=FIELD_DESCRIPTIONS)
        user_prompt = USER_PROMPT_TEMPLATE.format(user_input=user_input)
        
        try:
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistent output
                max_tokens=1024
            )
            
            # Extract response text
            response_text = response.choices[0].message.content
            logger.info(f"LLM Response: {response_text}")
            
            # Parse and validate
            extracted = self._parse_llm_response(response_text)
            cleaned = self._validate_and_clean(extracted)
            
            return {
                "success": True,
                "normalized_data": cleaned,
                "raw_input": user_input
            }
            
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            return {
                "success": False,
                "error": str(e),
                "normalized_data": self.get_empty_schema(),
                "raw_input": user_input
            }
    
    def normalize_and_route(self, user_input: str, router) -> Dict[str, Any]:
        """
        Normalize user input and route to appropriate model.
        
        Args:
            user_input: Natural language patient data
            router: MainSwarmRouter instance
            
        Returns:
            Prediction result or validation error
        """
        # First normalize the input
        normalized = self.normalize(user_input)
        
        if not normalized.get("success", False):
            return {
                "error": f"Normalization failed: {normalized.get('error')}",
                "normalized_data": normalized.get("normalized_data")
            }
        
        # Get the normalized data (with None for missing values)
        data = normalized["normalized_data"]
        
        # Filter out None values before routing
        filtered_data = {k: v for k, v in data.items() if v is not None}
        
        # Route to models
        result = router.route(filtered_data)
        
        # Add normalization info to result
        result["normalization"] = {
            "raw_input": user_input,
            "extracted_fields": filtered_data,
            "missing_fields": [k for k, v in data.items() if v is None]
        }
        
        return result


# Convenience functions
_normalizer_instance: Optional[GroqInputNormalizer] = None


def get_normalizer(api_key: Optional[str] = None) -> GroqInputNormalizer:
    """Get or create the normalizer instance."""
    global _normalizer_instance
    if _normalizer_instance is None or api_key:
        _normalizer_instance = GroqInputNormalizer(api_key)
    return _normalizer_instance


def normalize_input(user_input: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to normalize user input.
    
    Args:
        user_input: Natural language patient description
        api_key: Optional Groq API key
        
    Returns:
        Normalized data dict
    """
    normalizer = get_normalizer(api_key)
    return normalizer.normalize(user_input)


if __name__ == "__main__":
    # Test the normalizer
    print("=" * 60)
    print("  GROQ INPUT NORMALIZER - TEST")
    print("=" * 60)
    
    # Check if API key is set
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("\n⚠️  GROQ_API_KEY not set. Please set it:")
        print("   export GROQ_API_KEY='your-api-key-here'")
        print("\nShowing empty schema:")
        print(json.dumps(MASTER_SCHEMA, indent=2))
    else:
        normalizer = GroqInputNormalizer(api_key)
        
        # Test input
        test_input = """
        Patient is a 55 year old male, height 170cm, weight 85kg. 
        Blood pressure is 150/95. He has high cholesterol and is a smoker.
        He doesn't drink alcohol but is physically inactive.
        """
        
        print(f"\nTest Input:\n{test_input}")
        print("\nNormalizing...")
        
        result = normalizer.normalize(test_input)
        print("\nResult:")
        print(json.dumps(result, indent=2))
