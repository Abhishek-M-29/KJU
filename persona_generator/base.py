"""
Base Classes for Persona Generation
Defines core data structures used across the persona generator
"""

import uuid
import random
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum


class Gender(Enum):
    MALE = "M"
    FEMALE = "F"


class Race(Enum):
    WHITE = "white"
    BLACK = "black"
    ASIAN = "asian"
    HISPANIC = "hispanic"
    NATIVE = "native"
    OTHER = "other"


class MaritalStatus(Enum):
    SINGLE = "S"
    MARRIED = "M"
    DIVORCED = "D"
    WIDOWED = "W"


@dataclass
class Demographics:
    """Patient demographic information"""
    first_name: str
    last_name: str
    gender: Gender
    birth_date: date
    race: Race
    marital_status: MaritalStatus
    address: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    county: str = ""
    lat: float = 0.0
    lon: float = 0.0
    healthcare_expenses: float = 0.0
    healthcare_coverage: float = 0.0
    income: int = 0
    
    @property
    def age(self) -> int:
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


@dataclass
class VitalSigns:
    """Single vital signs measurement"""
    measurement_date: datetime
    systolic_bp: int
    diastolic_bp: int
    heart_rate: int
    respiratory_rate: int
    temperature: float  # Celsius
    oxygen_saturation: float
    height_cm: float
    weight_kg: float
    
    @property
    def bmi(self) -> float:
        if self.height_cm > 0:
            return round(self.weight_kg / ((self.height_cm / 100) ** 2), 1)
        return 0.0
    
    @property
    def map(self) -> float:
        """Mean Arterial Pressure"""
        return round((self.systolic_bp + 2 * self.diastolic_bp) / 3, 1)


@dataclass
class LabResult:
    """Single lab result"""
    test_date: datetime
    test_code: str
    test_name: str
    value: float
    unit: str
    reference_low: Optional[float] = None
    reference_high: Optional[float] = None
    
    @property
    def is_abnormal(self) -> bool:
        if self.reference_low and self.value < self.reference_low:
            return True
        if self.reference_high and self.value > self.reference_high:
            return True
        return False


@dataclass
class Condition:
    """Medical condition"""
    code: str
    description: str
    start_date: date
    stop_date: Optional[date] = None
    is_active: bool = True
    category: str = "encounter-diagnosis"


@dataclass
class Medication:
    """Medication prescription"""
    code: str
    description: str
    start_datetime: datetime
    stop_datetime: Optional[datetime] = None
    is_active: bool = True
    reason_code: Optional[str] = None
    reason_description: Optional[str] = None
    dosage: str = ""
    frequency: str = ""


@dataclass
class Allergy:
    """Allergy record"""
    code: str
    description: str
    start_date: date
    stop_date: Optional[date] = None
    is_active: bool = True
    reaction: str = ""
    severity: str = "moderate"


@dataclass
class Encounter:
    """Healthcare encounter"""
    encounter_id: str
    encounter_class: str  # ambulatory, emergency, inpatient, etc.
    encounter_type: str
    start_datetime: datetime
    stop_datetime: datetime
    reason_code: Optional[str] = None
    reason_description: Optional[str] = None
    provider: str = ""
    organization: str = ""
    payer: str = ""
    base_cost: float = 0.0
    total_claim_cost: float = 0.0
    payer_coverage: float = 0.0


@dataclass
class Procedure:
    """Medical procedure"""
    code: str
    description: str
    performed_date: datetime
    reason_code: Optional[str] = None
    reason_description: Optional[str] = None
    base_cost: float = 0.0


@dataclass
class Immunization:
    """Vaccination record"""
    code: str
    description: str
    administered_date: datetime
    base_cost: float = 0.0


@dataclass
class CarePlan:
    """Care plan"""
    code: str
    description: str
    start_date: date
    stop_date: Optional[date] = None
    is_active: bool = True
    reason_code: Optional[str] = None
    reason_description: Optional[str] = None


@dataclass
class FamilyHistory:
    """Family medical history item"""
    relation: str  # mother, father, sibling, etc.
    condition: str
    age_at_onset: Optional[int] = None
    deceased: bool = False
    age_at_death: Optional[int] = None


@dataclass
class SocialHistory:
    """Social/lifestyle factors"""
    smoking_status: str = "never"  # never, former, current
    packs_per_day: float = 0.0
    years_smoked: int = 0
    alcohol_use: str = "none"  # none, social, moderate, heavy
    drinks_per_week: int = 0
    drug_use: str = "none"
    exercise_frequency: str = "none"  # none, rarely, weekly, daily
    exercise_minutes_per_week: int = 0
    diet_quality: str = "average"  # poor, average, good, excellent
    occupation: str = ""
    education_level: str = ""
    living_situation: str = ""  # alone, with family, assisted living, etc.
    stress_level: str = "moderate"  # low, moderate, high


@dataclass
class AIFeatures:
    """Features for AI/ML model inference"""
    diabetes_risk_score: int = 1  # 1-10
    cardiovascular_risk_score: int = 1  # 1-10
    sepsis_risk_score: int = 1  # 1-10
    readmission_risk_score: int = 1  # 1-10
    mortality_risk_score: int = 1  # 1-10
    
    # Derived features
    has_diabetes: bool = False
    has_hypertension: bool = False
    has_heart_disease: bool = False
    has_ckd: bool = False
    has_copd: bool = False
    
    # Lifestyle features
    is_smoker: bool = False
    is_obese: bool = False
    is_sedentary: bool = False
    
    # Lab flags
    has_abnormal_hba1c: bool = False
    has_abnormal_lipids: bool = False
    has_abnormal_kidney: bool = False


class PersonaBase:
    """
    Base class for a complete patient persona
    Aggregates all patient data into a single entity
    """
    
    # Class variable to track next persona_id
    _next_persona_id: int = 1
    
    def __init__(self, demographics: Demographics, persona_id: Optional[int] = None):
        self.id: str = str(uuid.uuid4())
        self.persona_id: Optional[int] = persona_id  # Numeric ID for easy lookup (1, 2, 3, ...)
        self.demographics = demographics
        self.conditions: List[Condition] = []
        self.medications: List[Medication] = []
        self.allergies: List[Allergy] = []
        self.encounters: List[Encounter] = []
        self.procedures: List[Procedure] = []
        self.immunizations: List[Immunization] = []
        self.care_plans: List[CarePlan] = []
        self.vital_signs_history: List[VitalSigns] = []
        self.lab_results: List[LabResult] = []
        self.family_history: List[FamilyHistory] = []
        self.social_history: Optional[SocialHistory] = None
        self.ai_features: Optional[AIFeatures] = None
        self.narrative: str = ""
        self.clinical_summary: str = ""
    
    @classmethod
    def set_starting_persona_id(cls, start_id: int):
        """Set the starting persona_id for new personas"""
        cls._next_persona_id = start_id
    
    @classmethod
    def get_next_persona_id(cls) -> int:
        """Get and increment the next persona_id"""
        current_id = cls._next_persona_id
        cls._next_persona_id += 1
        return current_id
    
    def assign_persona_id(self):
        """Assign a persona_id if not already set"""
        if self.persona_id is None:
            self.persona_id = PersonaBase.get_next_persona_id()
        
    @property
    def active_conditions(self) -> List[Condition]:
        return [c for c in self.conditions if c.is_active]
    
    @property
    def active_medications(self) -> List[Medication]:
        return [m for m in self.medications if m.is_active]
    
    @property
    def latest_vitals(self) -> Optional[VitalSigns]:
        if self.vital_signs_history:
            return sorted(self.vital_signs_history, 
                         key=lambda v: v.measurement_date)[-1]
        return None
    
    @property
    def latest_labs(self) -> Dict[str, LabResult]:
        """Returns most recent value for each lab test"""
        latest = {}
        for lab in sorted(self.lab_results, key=lambda l: l.test_date):
            latest[lab.test_code] = lab
        return latest
    
    def add_condition(self, condition: Condition):
        self.conditions.append(condition)
        
    def add_medication(self, medication: Medication):
        self.medications.append(medication)
        
    def add_allergy(self, allergy: Allergy):
        self.allergies.append(allergy)
        
    def add_encounter(self, encounter: Encounter):
        self.encounters.append(encounter)
        
    def add_vital_signs(self, vitals: VitalSigns):
        self.vital_signs_history.append(vitals)
        
    def add_lab_result(self, lab: LabResult):
        self.lab_results.append(lab)
        
    def add_family_history(self, fh: FamilyHistory):
        self.family_history.append(fh)
        
    def set_social_history(self, sh: SocialHistory):
        self.social_history = sh
        
    def calculate_ai_features(self):
        """Calculate AI/ML features based on patient data"""
        features = AIFeatures()
        
        # Check conditions
        condition_codes = [c.code for c in self.active_conditions]
        condition_descs = [c.description.lower() for c in self.active_conditions]
        
        features.has_diabetes = any('diabetes' in d or 'E11' in c or 'E10' in c 
                                    for c, d in zip(condition_codes, condition_descs))
        features.has_hypertension = any('hypertension' in d or 'I10' in c 
                                        for c, d in zip(condition_codes, condition_descs))
        features.has_heart_disease = any(any(x in d for x in ['heart failure', 'coronary', 'mi ', 'myocardial', 'atrial fib']) 
                                         for d in condition_descs)
        features.has_ckd = any('kidney' in d or 'N18' in c 
                               for c, d in zip(condition_codes, condition_descs))
        features.has_copd = any('copd' in d or 'J44' in c 
                                for c, d in zip(condition_codes, condition_descs))
        
        # Check lifestyle
        if self.social_history:
            features.is_smoker = self.social_history.smoking_status == "current"
            features.is_sedentary = self.social_history.exercise_frequency in ["none", "rarely"]
        
        # Check vitals for obesity
        if self.latest_vitals:
            features.is_obese = self.latest_vitals.bmi >= 30
        
        # Check labs
        latest = self.latest_labs
        if 'HBA1C' in latest:
            features.has_abnormal_hba1c = latest['HBA1C'].value >= 6.5
        if 'CREATININE' in latest:
            features.has_abnormal_kidney = latest['CREATININE'].value > 1.3
        if 'LDL' in latest:
            features.has_abnormal_lipids = latest['LDL'].value > 130
        
        # Calculate risk scores
        # Diabetes risk
        d_score = 1
        if features.has_diabetes:
            d_score = 8
            if features.has_abnormal_hba1c:
                d_score += 1
            if features.is_obese:
                d_score += 1
        elif features.has_abnormal_hba1c:
            d_score = 5
        elif features.is_obese:
            d_score += 2
        if features.is_sedentary:
            d_score += 1
        features.diabetes_risk_score = min(10, max(1, d_score))
        
        # Cardiovascular risk
        cv_score = 1
        if features.has_heart_disease:
            cv_score = 8
        if features.has_hypertension:
            cv_score += 2
        if features.has_abnormal_lipids:
            cv_score += 2
        if features.has_diabetes:
            cv_score += 1
        if features.is_smoker:
            cv_score += 2
        if features.has_ckd:
            cv_score += 1
        features.cardiovascular_risk_score = min(10, max(1, cv_score))
        
        # Sepsis risk (higher for immunocompromised, elderly, multiple comorbidities)
        s_score = 1
        if self.demographics.age > 65:
            s_score += 2
        if len(self.active_conditions) > 3:
            s_score += 2
        if features.has_ckd:
            s_score += 2
        if features.has_diabetes:
            s_score += 1
        features.sepsis_risk_score = min(10, max(1, s_score))
        
        # Readmission risk
        r_score = 1
        if len(self.encounters) > 10:
            r_score += 2
        if features.has_heart_disease:
            r_score += 2
        if len(self.active_medications) > 5:
            r_score += 1
        if self.demographics.age > 75:
            r_score += 2
        features.readmission_risk_score = min(10, max(1, r_score))
        
        # Mortality risk
        m_score = 1
        if self.demographics.age > 80:
            m_score += 3
        elif self.demographics.age > 70:
            m_score += 2
        if features.has_heart_disease:
            m_score += 2
        if features.has_ckd:
            m_score += 2
        if features.has_copd:
            m_score += 1
        features.mortality_risk_score = min(10, max(1, m_score))
        
        self.ai_features = features
        return features
    
    def generate_narrative(self) -> str:
        """Generate a clinical narrative summary"""
        parts = []
        
        # Demographics
        parts.append(f"{self.demographics.full_name} is a {self.demographics.age}-year-old "
                    f"{self.demographics.race.value} {self.demographics.gender.value.lower()} "
                    f"({self.demographics.marital_status.value}).")
        
        # Chief conditions
        if self.active_conditions:
            conditions_str = ", ".join([c.description for c in self.active_conditions[:5]])
            parts.append(f"Active medical conditions include: {conditions_str}.")
        
        # Current medications
        if self.active_medications:
            meds_str = ", ".join([m.description.split()[0] for m in self.active_medications[:5]])
            parts.append(f"Current medications: {meds_str}.")
        
        # Allergies
        if self.allergies:
            allergies_str = ", ".join([a.description for a in self.allergies])
            parts.append(f"Allergies: {allergies_str}.")
        
        # Latest vitals
        if self.latest_vitals:
            v = self.latest_vitals
            parts.append(f"Latest vitals: BP {v.systolic_bp}/{v.diastolic_bp} mmHg, "
                        f"HR {v.heart_rate} bpm, BMI {v.bmi}.")
        
        # Social history
        if self.social_history:
            sh = self.social_history
            if sh.smoking_status != "never":
                parts.append(f"Smoking history: {sh.smoking_status} smoker.")
            if sh.occupation:
                parts.append(f"Occupation: {sh.occupation}.")
        
        # Family history summary
        if self.family_history:
            fh_conditions = [f.condition for f in self.family_history]
            if fh_conditions:
                parts.append(f"Family history notable for: {', '.join(fh_conditions[:3])}.")
        
        self.narrative = " ".join(parts)
        return self.narrative
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert persona to dictionary for database insertion"""
        return {
            'id': self.id,
            'persona_id': self.persona_id,
            'first_name': self.demographics.first_name,
            'last_name': self.demographics.last_name,
            'gender': self.demographics.gender.value,
            'birth_date': self.demographics.birth_date.isoformat(),
            'race': self.demographics.race.value,
            'marital_status': self.demographics.marital_status.value,
            'address': self.demographics.address,
            'city': self.demographics.city,
            'state': self.demographics.state,
            'zip_code': self.demographics.zip_code,
            'lat': self.demographics.lat,
            'lon': self.demographics.lon,
            'healthcare_expenses': self.demographics.healthcare_expenses,
            'healthcare_coverage': self.demographics.healthcare_coverage,
            'income': self.demographics.income,
            'conditions': [vars(c) for c in self.conditions],
            'medications': [vars(m) for m in self.medications],
            'allergies': [vars(a) for a in self.allergies],
            'vitals': [vars(v) for v in self.vital_signs_history],
            'labs': [vars(l) for l in self.lab_results],
            'ai_features': vars(self.ai_features) if self.ai_features else None,
            'narrative': self.narrative
        }
