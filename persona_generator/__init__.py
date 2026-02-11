# Persona Generator Package
# Synthea-level detailed patient persona generation system

from .base import PersonaBase, Demographics, VitalSigns, LabResult
from .conditions import ConditionTemplates, CONDITION_CATALOG
from .medications import MedicationTemplates, MEDICATION_CATALOG
from .generator import PersonaGenerator
from .database import DatabaseManager

__all__ = [
    'PersonaBase',
    'Demographics', 
    'VitalSigns',
    'LabResult',
    'ConditionTemplates',
    'CONDITION_CATALOG',
    'MedicationTemplates',
    'MEDICATION_CATALOG',
    'PersonaGenerator',
    'DatabaseManager'
]


def initialize_persona_counter():
    """
    Initialize the persona_id counter from the database.
    Call this once at startup to ensure new personas get correct IDs.
    """
    try:
        db = DatabaseManager()
        max_id = db.get_max_persona_id()
        PersonaBase.set_starting_persona_id(max_id + 1)
        db.close()
        return max_id + 1
    except Exception as e:
        print(f"Warning: Could not initialize persona counter: {e}")
        return 1


def get_persona(persona_id: int) -> dict:
    """
    Get a persona by its numeric ID.
    
    Args:
        persona_id: The numeric persona ID (1, 2, 3, ...)
        
    Returns:
        Dictionary with full persona data from Patient_Data table
    """
    db = DatabaseManager()
    try:
        return db.get_persona_by_id(persona_id)
    finally:
        db.close()


def list_all_personas(limit: int = 100) -> list:
    """
    List all personas with basic info.
    
    Args:
        limit: Maximum number of personas to return
        
    Returns:
        List of persona dictionaries with basic info
    """
    db = DatabaseManager()
    try:
        return db.list_personas(limit)
    finally:
        db.close()
