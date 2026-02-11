"""
JSON Transformer API - Modifies JSON according to natural language instructions.

This backend receives a JSON payload with:
1. The original JSON data
2. Natural language instructions on what to change

It uses Groq (primary) or Ollama (fallback) to interpret the instructions,
applies the changes while preserving the original structure, and returns the modified JSON.

Run with:
    uvicorn json_transformer_api:app --host 0.0.0.0 --port 8002 --reload
"""

import os
import copy
import json
import httpx
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

# ============================================================
# LLM Configuration (from environment variables)
# ============================================================
# Groq Configuration (Primary)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3-32b")

# Ollama Configuration (Fallback)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")

# ============================================================
# Pydantic Models for JSON Transformation
# ============================================================

class FieldTransformation(BaseModel):
    """Defines a single field transformation."""
    field_path: str = Field(
        ..., 
        description="Dot-notation path to the field (e.g., 'observations.0.heartrate' or 'patient_id')"
    )
    new_value: Any = Field(
        ..., 
        description="The new value to set for this field"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "field_path": "observations.0.heartrate",
                "new_value": 100
            }
        }
    }


class TransformationInstruction(BaseModel):
    """Instructions for transforming the JSON."""
    transformations: List[FieldTransformation] = Field(
        default=[],
        description="List of field transformations to apply"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "transformations": [
                    {"field_path": "patient_id", "new_value": "P002"},
                    {"field_path": "observations.0.heartrate", "new_value": 100}
                ]
            }
        }
    }


class Observation(BaseModel):
    """Single observation of patient vitals - matches sepsis model input."""
    heartrate: float = Field(..., ge=0, le=300, description="Heart rate (bpm)")
    sysbp: float = Field(..., ge=0, le=300, description="Systolic BP (mmHg)")
    diasbp: float = Field(..., ge=0, le=200, description="Diastolic BP (mmHg)")
    meanbp: float = Field(..., ge=0, le=250, description="Mean BP (mmHg)")
    resprate: float = Field(..., ge=0, le=100, description="Respiratory rate")
    tempc: float = Field(..., ge=30, le=45, description="Temperature (°C)")
    spo2: float = Field(..., ge=0, le=100, description="SpO2 (%)")
    glucose: float = Field(..., ge=0, le=1000, description="Glucose (mg/dL)")
    age: float = Field(..., ge=0, le=150, description="Age (years)")
    gender: int = Field(..., ge=0, le=1, description="Gender (0=F, 1=M)")


class PatientData(BaseModel):
    """Patient data structure matching sepsis prediction input."""
    patient_id: str = Field(..., description="Patient identifier")
    observations: List[Observation] = Field(..., min_length=1)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "patient_id": "P001",
                "observations": [{
                    "heartrate": 95, "sysbp": 110, "diasbp": 70, "meanbp": 83,
                    "resprate": 24, "tempc": 38.5, "spo2": 94, "glucose": 140,
                    "age": 72, "gender": 1
                }]
            }
        }
    }


class TransformRequest(BaseModel):
    """
    Main request body for JSON transformation.
    Contains the original data and instructions on how to modify it.
    """
    original_data: PatientData = Field(
        ..., 
        description="The original JSON data to transform"
    )
    instructions: TransformationInstruction = Field(
        ..., 
        description="Instructions on how to transform the data"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "original_data": {
                    "patient_id": "P001",
                    "observations": [{
                        "heartrate": 95, "sysbp": 110, "diasbp": 70, "meanbp": 83,
                        "resprate": 24, "tempc": 38.5, "spo2": 94, "glucose": 140,
                        "age": 72, "gender": 1
                    }]
                },
                "instructions": {
                    "transformations": [
                        {"field_path": "patient_id", "new_value": "P002"},
                        {"field_path": "observations.0.heartrate", "new_value": 100},
                        {"field_path": "observations.0.tempc", "new_value": 37.5}
                    ]
                }
            }
        }
    }


class GenericTransformRequest(BaseModel):
    """
    Generic request for transforming any JSON structure.
    Use this when you want to transform arbitrary JSON.
    """
    original_data: Dict[str, Any] = Field(
        ..., 
        description="The original JSON data to transform (any structure)"
    )
    instructions: TransformationInstruction = Field(
        ..., 
        description="Instructions on how to transform the data"
    )


class TransformResponse(BaseModel):
    """Response containing the transformed data."""
    success: bool = Field(..., description="Whether transformation was successful")
    transformed_data: Dict[str, Any] = Field(..., description="The transformed JSON data")
    changes_applied: List[str] = Field(
        default=[], 
        description="List of changes that were applied"
    )
    timestamp: str = Field(..., description="Timestamp of transformation")
    model_used: Optional[str] = Field(None, description="LLM model used for interpretation (if NL)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "transformed_data": {
                    "patient_id": "P002",
                    "observations": [{
                        "heartrate": 100, "sysbp": 110, "diasbp": 70, "meanbp": 83,
                        "resprate": 24, "tempc": 37.5, "spo2": 94, "glucose": 140,
                        "age": 72, "gender": 1
                    }]
                },
                "changes_applied": [
                    "patient_id: P001 -> P002",
                    "observations.0.heartrate: 95 -> 100",
                    "observations.0.tempc: 38.5 -> 37.5"
                ],
                "timestamp": "2026-02-11T12:00:00",
                "model_used": "qwen/qwen3-32b"
            }
        }
    }


class NaturalLanguageTransformRequest(BaseModel):
    """
    Request for transforming JSON using natural language instructions.
    The LLM will interpret the instructions and apply appropriate changes.
    """
    original_data: PatientData = Field(
        ..., 
        description="The original JSON data to transform"
    )
    instructions: str = Field(
        ..., 
        description="Natural language instructions describing what changes to make"
    )
    use_ollama: bool = Field(
        False, 
        description="Force use of Ollama instead of Groq"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "original_data": {
                    "patient_id": "P001",
                    "observations": [{
                        "heartrate": 95, "sysbp": 110, "diasbp": 70, "meanbp": 83,
                        "resprate": 24, "tempc": 38.5, "spo2": 94, "glucose": 140,
                        "age": 72, "gender": 1
                    }]
                },
                "instructions": "Change the patient ID to P002, increase the heart rate by 10, and set the temperature to normal (37.0)"
            }
        }
    }


class GenericNLTransformRequest(BaseModel):
    """
    Generic request for transforming any JSON using natural language.
    """
    original_data: Dict[str, Any] = Field(
        ..., 
        description="The original JSON data to transform (any structure)"
    )
    instructions: str = Field(
        ..., 
        description="Natural language instructions describing what changes to make"
    )
    use_ollama: bool = Field(
        False, 
        description="Force use of Ollama instead of Groq"
    )


# ============================================================
# FastAPI App
# ============================================================
app = FastAPI(
    title="JSON Transformer API",
    description="Transforms JSON data according to instructions while preserving structure",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Helper Functions
# ============================================================

def get_nested_value(data: dict, path: str) -> Any:
    """
    Get a value from a nested dictionary using dot notation.
    Supports array indices like 'observations.0.heartrate'
    """
    keys = path.split('.')
    current = data
    
    for key in keys:
        if isinstance(current, dict):
            if key not in current:
                raise KeyError(f"Key '{key}' not found in path '{path}'")
            current = current[key]
        elif isinstance(current, list):
            try:
                idx = int(key)
                if idx < 0 or idx >= len(current):
                    raise IndexError(f"Index {idx} out of range for path '{path}'")
                current = current[idx]
            except ValueError:
                raise ValueError(f"Expected array index but got '{key}' in path '{path}'")
        else:
            raise TypeError(f"Cannot navigate into {type(current).__name__} at path '{path}'")
    
    return current


def set_nested_value(data: dict, path: str, value: Any) -> Any:
    """
    Set a value in a nested dictionary using dot notation.
    Supports array indices like 'observations.0.heartrate'
    Returns the old value.
    """
    keys = path.split('.')
    current = data
    
    # Navigate to the parent of the target
    for key in keys[:-1]:
        if isinstance(current, dict):
            if key not in current:
                raise KeyError(f"Key '{key}' not found in path '{path}'")
            current = current[key]
        elif isinstance(current, list):
            try:
                idx = int(key)
                if idx < 0 or idx >= len(current):
                    raise IndexError(f"Index {idx} out of range for path '{path}'")
                current = current[idx]
            except ValueError:
                raise ValueError(f"Expected array index but got '{key}' in path '{path}'")
        else:
            raise TypeError(f"Cannot navigate into {type(current).__name__} at path '{path}'")
    
    # Set the value
    final_key = keys[-1]
    if isinstance(current, dict):
        if final_key not in current:
            raise KeyError(f"Key '{final_key}' not found - cannot add new keys (structure must be preserved)")
        old_value = current[final_key]
        current[final_key] = value
        return old_value
    elif isinstance(current, list):
        try:
            idx = int(final_key)
            if idx < 0 or idx >= len(current):
                raise IndexError(f"Index {idx} out of range")
            old_value = current[idx]
            current[idx] = value
            return old_value
        except ValueError:
            raise ValueError(f"Expected array index but got '{final_key}'")
    else:
        raise TypeError(f"Cannot set value in {type(current).__name__}")


def apply_transformations(data: dict, instructions: TransformationInstruction) -> tuple[dict, List[str]]:
    """
    Apply all transformations to the data.
    Returns the modified data and a list of changes applied.
    """
    # Deep copy to avoid modifying original
    result = copy.deepcopy(data)
    changes = []
    
    for transformation in instructions.transformations:
        path = transformation.field_path
        new_value = transformation.new_value
        
        try:
            old_value = set_nested_value(result, path, new_value)
            changes.append(f"{path}: {old_value} -> {new_value}")
        except (KeyError, IndexError, ValueError, TypeError) as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to apply transformation at '{path}': {str(e)}"
            )
    
    return result, changes


# ============================================================
# LLM Integration for Natural Language Processing
# ============================================================

def get_json_transform_prompt(original_json: dict, instructions: str) -> tuple[str, str]:
    """
    Create the system and user prompts for JSON transformation.
    """
    system_prompt = """You are a JSON transformation assistant. Your task is to modify JSON data according to natural language instructions.

CRITICAL RULES:
1. You MUST preserve the exact structure of the JSON - do not add or remove keys
2. Only modify the VALUES of existing fields as instructed
3. Return ONLY the modified JSON, no explanations, no markdown, no code blocks
4. Ensure all values maintain their correct types (numbers stay numbers, strings stay strings)
5. If a field is not mentioned in the instructions, keep it unchanged
6. ALWAYS apply the requested changes - do not skip any instruction

CRITICAL - TEMPERATURE HANDLING:
- The tempc field stores temperature in CELSIUS with valid range 30-45°C
- If user gives a temperature value > 45, they likely mean FAHRENHEIT - you MUST convert it!
- Fahrenheit to Celsius: C = (F - 32) × 5/9
- Examples: 90°F = 32.2°C, 97°F = 36.1°C, 98.6°F = 37°C, 100°F = 37.8°C, 102°F = 38.9°C, 104°F = 40°C
- If the value is between 30-45, use it directly as Celsius
- If the value is > 45, ALWAYS convert from Fahrenheit to Celsius

RELATIVE CHANGES:
- "increase by X" means add X to current value
- "decrease by X" or "lower by X" means subtract X from current value
- "set to X" or "change to X" means replace with X exactly

The JSON structure for patient data is:
- patient_id: string (patient identifier)
- observations: array of objects, each containing:
  - heartrate: number (0-300 bpm)
  - sysbp: number (0-300 mmHg) - systolic blood pressure
  - diasbp: number (0-200 mmHg) - diastolic blood pressure
  - meanbp: number (0-250 mmHg) - mean blood pressure
  - resprate: number (0-100) - respiratory rate
  - tempc: number (30-45 °C) - body temperature IN CELSIUS - convert from F if > 45!
  - spo2: number (0-100 %) - oxygen saturation
  - glucose: number (0-1000 mg/dL)
  - age: number (0-150 years)
  - gender: integer (0=Female, 1=Male)

OUTPUT: Return ONLY the raw JSON object. No markdown, no code fences, no explanation."""

    user_prompt = f"""Original JSON:
{json.dumps(original_json, indent=2)}

Instructions: {instructions}

REMINDER: If temperature value > 45, convert from Fahrenheit to Celsius!
Apply ALL the requested changes and return the modified JSON:"""

    return system_prompt, user_prompt


async def call_groq_api(system_prompt: str, user_prompt: str) -> Optional[dict]:
    """Call Groq API to interpret natural language and return transformed JSON."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{GROQ_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.1,  # Low temperature for consistent JSON output
                    "max_tokens": 2000
                }
            )
            
            if response.status_code != 200:
                error_text = response.text
                print(f"Groq API error: {response.status_code} - {error_text}")
                return None
            
            data = response.json()
            print(f"Groq response received, model: {GROQ_MODEL}")
            
            content = data["choices"][0]["message"]["content"]
            print(f"Raw content (first 200 chars): {content[:200] if len(content) > 200 else content}")
            
            # Clean up the response - remove markdown code blocks if present
            content = content.strip()
            
            # Handle <think> tags from some models
            if "<think>" in content:
                # Remove everything between <think> and </think>
                import re
                content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
                content = content.strip()
            
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Parse JSON
            return json.loads(content)
            
    except json.JSONDecodeError as e:
        print(f"Groq JSON parse error: {str(e)}")
        print(f"Content that failed to parse: {content[:500] if 'content' in dir() else 'N/A'}")
        return None
    except Exception as e:
        print(f"Groq error: {str(e)}")
        return None


async def call_ollama_api(system_prompt: str, user_prompt: str) -> Optional[dict]:
    """Call Ollama API as fallback."""
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 2000
                    }
                }
            )
            
            if response.status_code != 200:
                print(f"Ollama API error: {response.status_code}")
                return None
            
            data = response.json()
            content = data.get("response", "")
            
            # Clean up the response
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            return json.loads(content)
            
    except json.JSONDecodeError as e:
        print(f"Ollama JSON parse error: {str(e)}")
        return None
    except httpx.ConnectError:
        print("Could not connect to Ollama")
        return None
    except Exception as e:
        print(f"Ollama error: {str(e)}")
        return None


async def transform_with_llm(original_data: dict, instructions: str, use_ollama: bool = False) -> tuple[Optional[dict], str]:
    """
    Use LLM to interpret natural language instructions and transform JSON.
    Returns (transformed_data, model_used) or (None, error_message).
    """
    system_prompt, user_prompt = get_json_transform_prompt(original_data, instructions)
    
    if use_ollama:
        # Force Ollama
        result = await call_ollama_api(system_prompt, user_prompt)
        if result:
            return result, OLLAMA_MODEL
        return None, "Ollama failed to process the request"
    
    # Try Groq first
    result = await call_groq_api(system_prompt, user_prompt)
    if result:
        return result, GROQ_MODEL
    
    # Fallback to Ollama
    print("Groq failed, falling back to Ollama...")
    result = await call_ollama_api(system_prompt, user_prompt)
    if result:
        return result, OLLAMA_MODEL
    
    return None, "Both Groq and Ollama failed to process the request"


def compute_changes(original: dict, transformed: dict, prefix: str = "") -> List[str]:
    """
    Compute the list of changes between original and transformed data.
    """
    changes = []
    
    for key in original:
        current_path = f"{prefix}{key}" if prefix else key
        
        if key not in transformed:
            continue
            
        old_val = original[key]
        new_val = transformed[key]
        
        if isinstance(old_val, dict) and isinstance(new_val, dict):
            changes.extend(compute_changes(old_val, new_val, f"{current_path}."))
        elif isinstance(old_val, list) and isinstance(new_val, list):
            for i, (old_item, new_item) in enumerate(zip(old_val, new_val)):
                if isinstance(old_item, dict) and isinstance(new_item, dict):
                    changes.extend(compute_changes(old_item, new_item, f"{current_path}.{i}."))
                elif old_item != new_item:
                    changes.append(f"{current_path}.{i}: {old_item} -> {new_item}")
        elif old_val != new_val:
            changes.append(f"{current_path}: {old_val} -> {new_val}")
    
    return changes


# ============================================================
# API Endpoints
# ============================================================

@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "service": "JSON Transformer API",
        "version": "2.0.0",
        "description": "Transforms JSON data using natural language or explicit instructions",
        "llm_config": {
            "primary": f"Groq ({GROQ_MODEL})",
            "fallback": f"Ollama ({OLLAMA_MODEL})"
        },
        "endpoints": {
            "POST /transform/nl": "Transform patient data using natural language (Groq/Ollama)",
            "POST /transform/nl/generic": "Transform any JSON using natural language",
            "POST /transform": "Transform patient data (explicit field paths)",
            "POST /transform/generic": "Transform any JSON (explicit field paths)",
            "GET /schema": "Get the expected JSON schema",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/schema")
async def get_schema():
    """
    Returns the expected JSON schema for patient data.
    This schema must be followed for validated transformations.
    """
    return {
        "patient_data_schema": PatientData.model_json_schema(),
        "observation_schema": Observation.model_json_schema(),
        "transform_request_schema": TransformRequest.model_json_schema(),
        "example_request": {
            "original_data": {
                "patient_id": "P001",
                "observations": [{
                    "heartrate": 95.0,
                    "sysbp": 110.0,
                    "diasbp": 70.0,
                    "meanbp": 83.0,
                    "resprate": 24.0,
                    "tempc": 38.5,
                    "spo2": 94.0,
                    "glucose": 140.0,
                    "age": 72.0,
                    "gender": 1
                }]
            },
            "instructions": {
                "transformations": [
                    {"field_path": "patient_id", "new_value": "P002"},
                    {"field_path": "observations.0.heartrate", "new_value": 100}
                ]
            }
        }
    }


@app.post("/transform", response_model=TransformResponse)
async def transform_patient_data(request: TransformRequest):
    """
    Transform patient data according to instructions.
    
    This endpoint validates both input and output against the PatientData schema,
    ensuring the structure is preserved and values are within valid ranges.
    
    **Path notation examples:**
    - `patient_id` - Top-level field
    - `observations.0.heartrate` - First observation's heartrate
    - `observations.1.tempc` - Second observation's temperature
    """
    try:
        # Convert Pydantic model to dict for manipulation
        data_dict = request.original_data.model_dump()
        
        # Apply transformations
        transformed_dict, changes = apply_transformations(data_dict, request.instructions)
        
        # Validate the transformed data still matches the schema
        try:
            validated = PatientData(**transformed_dict)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Transformed data does not match schema: {str(e)}"
            )
        
        return TransformResponse(
            success=True,
            transformed_data=validated.model_dump(),
            changes_applied=changes,
            timestamp=datetime.now().isoformat(),
            model_used=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Transformation failed: {str(e)}"
        )


@app.post("/transform/generic", response_model=TransformResponse)
async def transform_generic_json(request: GenericTransformRequest):
    """
    Transform any JSON structure according to instructions.
    
    This endpoint does NOT validate against a specific schema - 
    it simply applies the transformations to whatever JSON you provide.
    
    Use this when you need flexibility with the JSON structure.
    
    **Path notation examples:**
    - `name` - Top-level field
    - `address.city` - Nested field
    - `items.0.price` - First item's price in an array
    - `data.users.2.email` - Deeply nested field
    """
    try:
        # Apply transformations
        transformed_dict, changes = apply_transformations(
            request.original_data, 
            request.instructions
        )
        
        return TransformResponse(
            success=True,
            transformed_data=transformed_dict,
            changes_applied=changes,
            timestamp=datetime.now().isoformat(),
            model_used=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Transformation failed: {str(e)}"
        )


# ============================================================
# Natural Language Endpoints (Groq/Ollama)
# ============================================================

@app.post("/transform/nl", response_model=TransformResponse)
async def transform_patient_data_nl(request: NaturalLanguageTransformRequest):
    """
    Transform patient data using natural language instructions.
    
    Uses Groq (primary) or Ollama (fallback) to interpret your instructions
    and apply the appropriate changes to the JSON.
    
    **Example instructions:**
    - "Change the patient ID to P002"
    - "Increase heart rate by 10 and set temperature to normal"
    - "Make the patient female and 5 years younger"
    - "Set all vital signs to critical levels"
    """
    try:
        # Convert Pydantic model to dict
        data_dict = request.original_data.model_dump()
        
        # Use LLM to transform
        transformed_dict, model_used = await transform_with_llm(
            data_dict, 
            request.instructions,
            use_ollama=request.use_ollama
        )
        
        if transformed_dict is None:
            raise HTTPException(
                status_code=500,
                detail=f"LLM failed to process request: {model_used}"
            )
        
        # Validate the transformed data against schema
        try:
            validated = PatientData(**transformed_dict)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"LLM output does not match schema: {str(e)}. The model may have misunderstood the instructions."
            )
        
        # Compute changes
        changes = compute_changes(data_dict, validated.model_dump())
        
        return TransformResponse(
            success=True,
            transformed_data=validated.model_dump(),
            changes_applied=changes,
            timestamp=datetime.now().isoformat(),
            model_used=model_used
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Transformation failed: {str(e)}"
        )


@app.post("/transform/nl/generic", response_model=TransformResponse)
async def transform_generic_nl(request: GenericNLTransformRequest):
    """
    Transform any JSON structure using natural language instructions.
    
    Uses Groq (primary) or Ollama (fallback) to interpret your instructions.
    No schema validation is performed on the output.
    
    **Example instructions:**
    - "Change all prices to 50% of their current value"
    - "Update the user's name to John Doe"
    - "Set status to inactive for all items"
    """
    try:
        # Use LLM to transform
        transformed_dict, model_used = await transform_with_llm(
            request.original_data, 
            request.instructions,
            use_ollama=request.use_ollama
        )
        
        if transformed_dict is None:
            raise HTTPException(
                status_code=500,
                detail=f"LLM failed to process request: {model_used}"
            )
        
        # Compute changes
        changes = compute_changes(request.original_data, transformed_dict)
        
        return TransformResponse(
            success=True,
            transformed_data=transformed_dict,
            changes_applied=changes,
            timestamp=datetime.now().isoformat(),
            model_used=model_used
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Transformation failed: {str(e)}"
        )


@app.post("/validate")
async def validate_patient_data(data: PatientData):
    """
    Validate patient data against the schema without transforming.
    Returns the validated and normalized data.
    """
    return {
        "valid": True,
        "data": data.model_dump(),
        "timestamp": datetime.now().isoformat()
    }


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting JSON Transformer API on port 8002...")
    print("📚 API docs available at: http://localhost:8002/docs")
    uvicorn.run(app, host="0.0.0.0", port=8002)
