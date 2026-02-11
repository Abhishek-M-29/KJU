"""
Persona Generator
Main class for generating randomized Synthea-level patient personas
"""

import random
import uuid
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass

from .base import (
    PersonaBase, Demographics, VitalSigns, LabResult, 
    Condition, Medication, Allergy, Encounter, FamilyHistory, 
    SocialHistory, AIFeatures, Gender, Race, MaritalStatus
)
from .conditions import CONDITION_CATALOG, ConditionTemplates, ConditionCategory, VitalPattern, LabPattern
from .medications import MEDICATION_CATALOG, MedicationTemplates


# ============================================================
# NAME AND DEMOGRAPHIC DATA
# ============================================================

FIRST_NAMES_MALE = [
    "James", "Michael", "Robert", "David", "William", "Richard", "Joseph", "Thomas",
    "Christopher", "Charles", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven",
    "Paul", "Andrew", "Joshua", "Kenneth", "Kevin", "Brian", "George", "Timothy",
    "Ronald", "Edward", "Jason", "Jeffrey", "Ryan", "Jacob", "Gary", "Nicholas",
    "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon", "Benjamin",
    "Samuel", "Raymond", "Gregory", "Frank", "Alexander", "Patrick", "Jack", "Dennis",
    "Jerry", "Tyler", "Aaron", "Jose", "Adam", "Nathan", "Henry", "Douglas", "Zachary",
    "Peter", "Kyle", "Noah", "Ethan", "Jeremy", "Walter", "Christian", "Keith", "Roger",
    "Terry", "Austin", "Sean", "Gerald", "Carl", "Harold", "Dylan", "Arthur", "Lawrence",
    "Jordan", "Jesse", "Bryan", "Billy", "Bruce", "Gabriel", "Joe", "Logan", "Albert",
    "Willie", "Alan", "Eugene", "Russell", "Vincent", "Philip", "Bobby", "Johnny", "Bradley",
    # Diverse names
    "Miguel", "Carlos", "Luis", "Juan", "Francisco", "Antonio", "Manuel", "Jorge", "Pedro",
    "Jamal", "Darnell", "DeShawn", "Terrell", "Marcus", "Andre", "Malik", "Tyrone", "Jerome",
    "Wei", "Chen", "Hiroshi", "Takeshi", "Raj", "Vikram", "Amir", "Mohammed", "Omar",
    "Sergei", "Nikolai", "Andrei", "Giovanni", "Marco", "Luca", "Pierre", "Jean", "Hans"
]

FIRST_NAMES_FEMALE = [
    "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan", "Jessica",
    "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra", "Ashley", "Kimberly",
    "Emily", "Donna", "Michelle", "Dorothy", "Carol", "Amanda", "Melissa", "Deborah",
    "Stephanie", "Rebecca", "Sharon", "Laura", "Cynthia", "Kathleen", "Amy", "Angela",
    "Shirley", "Anna", "Brenda", "Pamela", "Emma", "Nicole", "Helen", "Samantha", "Katherine",
    "Christine", "Debra", "Rachel", "Carolyn", "Janet", "Catherine", "Maria", "Heather",
    "Diane", "Ruth", "Julie", "Olivia", "Joyce", "Virginia", "Victoria", "Kelly", "Lauren",
    "Christina", "Joan", "Evelyn", "Judith", "Megan", "Andrea", "Cheryl", "Hannah", "Jacqueline",
    "Martha", "Gloria", "Teresa", "Ann", "Sara", "Madison", "Frances", "Kathryn", "Janice",
    "Jean", "Abigail", "Alice", "Judy", "Sophia", "Grace", "Denise", "Amber", "Doris",
    "Marilyn", "Danielle", "Beverly", "Isabella", "Theresa", "Diana", "Natalie", "Brittany",
    # Diverse names
    "Rosa", "Carmen", "Lucia", "Sofia", "Elena", "Isabella", "Gabriela", "Ana", "Maria",
    "Aaliyah", "Imani", "Keisha", "Latoya", "Ebony", "Jasmine", "Destiny", "Tanya",
    "Mei", "Yuki", "Priya", "Lakshmi", "Fatima", "Aisha", "Zara", "Nadia", "Leila",
    "Olga", "Natasha", "Svetlana", "Francesca", "Chiara", "Amélie", "Marie", "Ingrid"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Turner", "Phillips", "Evans", "Parker", "Collins", "Edwards",
    "Stewart", "Morris", "Murphy", "Cook", "Rogers", "Morgan", "Peterson", "Cooper",
    "Reed", "Bailey", "Bell", "Gomez", "Kelly", "Howard", "Ward", "Cox", "Diaz",
    "Richardson", "Wood", "Watson", "Brooks", "Bennett", "Gray", "James", "Reyes",
    "Cruz", "Hughes", "Price", "Myers", "Long", "Foster", "Sanders", "Ross", "Morales",
    # Diverse surnames
    "Chen", "Wang", "Li", "Zhang", "Liu", "Kim", "Park", "Choi", "Tanaka", "Yamamoto",
    "Patel", "Shah", "Singh", "Kumar", "Sharma", "Gupta", "Khan", "Ali", "Hassan",
    "Ivanov", "Petrov", "Kowalski", "Müller", "Schmidt", "Rossi", "Bianchi", "Dubois",
    "O'Brien", "O'Connor", "McCarthy", "Sullivan", "Brennan", "Nakamura", "Johansson"
]

CITIES_BY_STATE = {
    "California": ["Los Angeles", "San Diego", "San Francisco", "San Jose", "Oakland", "Sacramento", "Fresno"],
    "Texas": ["Houston", "San Antonio", "Dallas", "Austin", "Fort Worth", "El Paso", "Arlington"],
    "Florida": ["Miami", "Orlando", "Tampa", "Jacksonville", "Fort Lauderdale", "St. Petersburg"],
    "New York": ["New York City", "Buffalo", "Rochester", "Albany", "Syracuse", "Yonkers"],
    "Illinois": ["Chicago", "Aurora", "Naperville", "Rockford", "Springfield", "Peoria"],
    "Pennsylvania": ["Philadelphia", "Pittsburgh", "Allentown", "Erie", "Reading", "Scranton"],
    "Ohio": ["Columbus", "Cleveland", "Cincinnati", "Toledo", "Akron", "Dayton"],
    "Georgia": ["Atlanta", "Augusta", "Columbus", "Savannah", "Athens", "Macon"],
    "North Carolina": ["Charlotte", "Raleigh", "Greensboro", "Durham", "Winston-Salem"],
    "Michigan": ["Detroit", "Grand Rapids", "Warren", "Ann Arbor", "Lansing", "Flint"],
    "Arizona": ["Phoenix", "Tucson", "Mesa", "Chandler", "Scottsdale", "Gilbert"],
    "Washington": ["Seattle", "Spokane", "Tacoma", "Vancouver", "Bellevue", "Kent"],
    "Massachusetts": ["Boston", "Worcester", "Springfield", "Cambridge", "Lowell"],
    "Colorado": ["Denver", "Colorado Springs", "Aurora", "Fort Collins", "Boulder"],
    "Virginia": ["Virginia Beach", "Norfolk", "Richmond", "Newport News", "Alexandria"]
}

STREET_NAMES = [
    "Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Pine St", "Elm St", "Washington Ave",
    "Park Blvd", "Lake Dr", "Forest Way", "River Rd", "Hill St", "Valley View",
    "Sunset Blvd", "Meadow Ln", "Spring St", "Garden Way", "Ocean Dr", "Mountain View",
    "Cherry Ln", "Birch St", "Walnut Ave", "Willow Dr", "Chestnut St", "Hickory Ln"
]

OCCUPATIONS = [
    "Software Engineer", "Registered Nurse", "Teacher", "Accountant", "Sales Manager",
    "Administrative Assistant", "Customer Service Rep", "Truck Driver", "Retail Associate",
    "Construction Worker", "Electrician", "Plumber", "Mechanic", "Chef", "Waiter/Waitress",
    "Lawyer", "Physician", "Pharmacist", "Dentist", "Veterinarian", "Psychologist",
    "Social Worker", "Police Officer", "Firefighter", "Military Personnel", "Security Guard",
    "Real Estate Agent", "Financial Advisor", "Bank Teller", "Insurance Agent",
    "Marketing Manager", "Graphic Designer", "Web Developer", "Data Analyst", "IT Support",
    "Human Resources", "Project Manager", "Consultant", "Entrepreneur", "Farmer",
    "Retired", "Disabled", "Homemaker", "Student", "Unemployed"
]

ALLERGIES_CATALOG = {
    "penicillin": ("Z88.0", "Allergy status to penicillin", "rash", "moderate"),
    "sulfa": ("Z88.2", "Allergy status to sulfonamides", "rash", "moderate"),
    "aspirin": ("Z88.6", "Allergy status to analgesic agent", "gi upset", "mild"),
    "nsaid": ("Z88.6", "Allergy status to NSAIDs", "gi bleeding", "severe"),
    "ace_inhibitor": ("Z88.8", "Allergy to ACE inhibitors", "angioedema", "severe"),
    "latex": ("Z91.040", "Latex allergy status", "contact dermatitis", "moderate"),
    "shellfish": ("Z91.013", "Allergy to shellfish", "anaphylaxis", "severe"),
    "peanut": ("Z91.010", "Allergy to peanuts", "anaphylaxis", "severe"),
    "tree_nuts": ("Z91.010", "Allergy to tree nuts", "anaphylaxis", "severe"),
    "eggs": ("Z91.012", "Allergy to eggs", "hives", "moderate"),
    "milk": ("Z91.011", "Allergy to dairy", "gi upset", "mild"),
    "wheat": ("Z91.012", "Allergy to wheat", "gi upset", "mild"),
    "soy": ("Z91.013", "Allergy to soy", "rash", "mild"),
    "fish": ("Z91.013", "Allergy to fish", "hives", "moderate"),
    "bee_sting": ("Z91.030", "Bee venom allergy", "anaphylaxis", "severe"),
    "iodine_contrast": ("Z91.041", "Allergy to iodinated contrast", "rash", "moderate"),
    "codeine": ("Z88.5", "Allergy to opioid", "nausea", "mild"),
    "morphine": ("Z88.5", "Allergy to opioid", "itching", "mild"),
    "cephalosporin": ("Z88.1", "Allergy to cephalosporins", "rash", "moderate"),
    "fluoroquinolone": ("Z88.8", "Allergy to fluoroquinolones", "tendon pain", "moderate"),
    "tetracycline": ("Z88.1", "Allergy to tetracycline", "rash", "mild"),
    "erythromycin": ("Z88.1", "Allergy to macrolides", "gi upset", "mild"),
    "metformin": ("Z88.8", "Allergy to metformin", "gi upset", "mild"),
    "statin": ("Z88.8", "Allergy to statins", "myalgia", "moderate"),
    "lisinopril": ("Z88.8", "Allergy to lisinopril", "cough", "mild"),
}

FAMILY_CONDITIONS = [
    "Type 2 diabetes", "Hypertension", "Heart disease", "Stroke", "Cancer (breast)",
    "Cancer (colon)", "Cancer (prostate)", "Cancer (lung)", "Alzheimer's disease",
    "Parkinson's disease", "Depression", "Anxiety", "Bipolar disorder", "Schizophrenia",
    "Asthma", "COPD", "Kidney disease", "Liver disease", "Thyroid disease",
    "Rheumatoid arthritis", "Lupus", "Multiple sclerosis", "Osteoporosis",
    "Obesity", "Alcoholism", "Drug addiction"
]


# ============================================================
# PERSONA PROFILE PRESETS
# ============================================================

@dataclass
class PersonaProfile:
    """Preset profile for generating a specific type of persona"""
    name: str
    description: str
    age_range: Tuple[int, int]
    gender_weights: Dict[str, float]  # {"M": 0.5, "F": 0.5}
    primary_conditions: List[str]  # Must have these
    secondary_conditions: List[str]  # May have some of these
    excluded_conditions: List[str]  # Cannot have these
    smoking_probability: float
    obesity_probability: float
    comorbidity_count: Tuple[int, int]  # (min, max) additional conditions
    medication_adherence: float  # 0-1, affects how many meds they're on
    encounter_frequency: str  # "low", "moderate", "high", "very_high"
    socioeconomic_level: str  # "low", "middle", "high"


# Predefined profiles for common patient types
PERSONA_PROFILES = {
    "healthy_young": PersonaProfile(
        name="Healthy Young Adult",
        description="Young adult with minimal health issues",
        age_range=(18, 35),
        gender_weights={"M": 0.5, "F": 0.5},
        primary_conditions=[],
        secondary_conditions=["generalized_anxiety", "major_depression", "asthma", "migraine", "acne"],
        excluded_conditions=["heart_failure_systolic", "ckd_stage4", "copd", "type2_diabetes"],
        smoking_probability=0.15,
        obesity_probability=0.20,
        comorbidity_count=(0, 2),
        medication_adherence=0.8,
        encounter_frequency="low",
        socioeconomic_level="middle"
    ),
    
    "healthy_middle_aged": PersonaProfile(
        name="Healthy Middle-Aged",
        description="Middle-aged adult with controlled risk factors",
        age_range=(40, 55),
        gender_weights={"M": 0.5, "F": 0.5},
        primary_conditions=[],
        secondary_conditions=["essential_hypertension", "hyperlipidemia", "prediabetes", "obesity", "gerd"],
        excluded_conditions=["heart_failure_systolic", "ckd_stage4", "copd_severe"],
        smoking_probability=0.10,
        obesity_probability=0.35,
        comorbidity_count=(0, 3),
        medication_adherence=0.85,
        encounter_frequency="low",
        socioeconomic_level="middle"
    ),
    
    "healthy_elderly": PersonaProfile(
        name="Healthy Elderly",
        description="Well-maintained elderly patient",
        age_range=(70, 90),
        gender_weights={"M": 0.4, "F": 0.6},
        primary_conditions=["essential_hypertension"],
        secondary_conditions=["hyperlipidemia", "osteoarthritis", "osteoporosis", "hypothyroidism", "gerd"],
        excluded_conditions=["heart_failure_systolic", "ckd_stage5", "copd_severe", "alzheimers"],
        smoking_probability=0.05,
        obesity_probability=0.25,
        comorbidity_count=(1, 4),
        medication_adherence=0.90,
        encounter_frequency="moderate",
        socioeconomic_level="middle"
    ),
    
    "diabetic_controlled": PersonaProfile(
        name="Controlled Diabetic",
        description="Type 2 diabetic with good control",
        age_range=(45, 75),
        gender_weights={"M": 0.55, "F": 0.45},
        primary_conditions=["type2_diabetes"],
        secondary_conditions=["essential_hypertension", "hyperlipidemia", "obesity", "gerd"],
        excluded_conditions=["ckd_stage5", "diabetic_nephropathy"],
        smoking_probability=0.10,
        obesity_probability=0.60,
        comorbidity_count=(2, 4),
        medication_adherence=0.85,
        encounter_frequency="moderate",
        socioeconomic_level="middle"
    ),
    
    "diabetic_uncontrolled": PersonaProfile(
        name="Uncontrolled Diabetic",
        description="Type 2 diabetic with complications",
        age_range=(50, 80),
        gender_weights={"M": 0.55, "F": 0.45},
        primary_conditions=["type2_diabetes_with_complications"],
        secondary_conditions=["diabetic_nephropathy", "diabetic_neuropathy", "ckd_stage3", "coronary_artery_disease"],
        excluded_conditions=[],
        smoking_probability=0.15,
        obesity_probability=0.70,
        comorbidity_count=(3, 6),
        medication_adherence=0.60,
        encounter_frequency="high",
        socioeconomic_level="low"
    ),
    
    "type1_diabetic": PersonaProfile(
        name="Type 1 Diabetic",
        description="Insulin-dependent diabetic",
        age_range=(18, 60),
        gender_weights={"M": 0.5, "F": 0.5},
        primary_conditions=["type1_diabetes"],
        secondary_conditions=["hypothyroidism", "celiac_disease", "generalized_anxiety"],
        excluded_conditions=["type2_diabetes", "obesity"],
        smoking_probability=0.08,
        obesity_probability=0.15,
        comorbidity_count=(0, 2),
        medication_adherence=0.90,
        encounter_frequency="moderate",
        socioeconomic_level="middle"
    ),
    
    "cardiovascular_high_risk": PersonaProfile(
        name="High Cardiovascular Risk",
        description="Multiple cardiac risk factors",
        age_range=(50, 75),
        gender_weights={"M": 0.65, "F": 0.35},
        primary_conditions=["coronary_artery_disease", "essential_hypertension"],
        secondary_conditions=["hyperlipidemia", "type2_diabetes", "prior_mi", "peripheral_vascular_disease"],
        excluded_conditions=[],
        smoking_probability=0.25,
        obesity_probability=0.50,
        comorbidity_count=(3, 5),
        medication_adherence=0.70,
        encounter_frequency="high",
        socioeconomic_level="middle"
    ),
    
    "heart_failure": PersonaProfile(
        name="Heart Failure Patient",
        description="Systolic heart failure with reduced EF",
        age_range=(55, 85),
        gender_weights={"M": 0.60, "F": 0.40},
        primary_conditions=["heart_failure_systolic"],
        secondary_conditions=["atrial_fibrillation", "ckd_stage3", "type2_diabetes", "anemia_ckd"],
        excluded_conditions=[],
        smoking_probability=0.10,
        obesity_probability=0.40,
        comorbidity_count=(3, 6),
        medication_adherence=0.75,
        encounter_frequency="very_high",
        socioeconomic_level="low"
    ),
    
    "atrial_fibrillation": PersonaProfile(
        name="Atrial Fibrillation",
        description="AFib on anticoagulation",
        age_range=(60, 85),
        gender_weights={"M": 0.55, "F": 0.45},
        primary_conditions=["atrial_fibrillation"],
        secondary_conditions=["essential_hypertension", "heart_failure_preserved", "sleep_apnea", "type2_diabetes"],
        excluded_conditions=[],
        smoking_probability=0.08,
        obesity_probability=0.45,
        comorbidity_count=(2, 4),
        medication_adherence=0.85,
        encounter_frequency="moderate",
        socioeconomic_level="middle"
    ),
    
    "post_stroke": PersonaProfile(
        name="Post-Stroke Patient",
        description="History of ischemic stroke",
        age_range=(60, 85),
        gender_weights={"M": 0.55, "F": 0.45},
        primary_conditions=["stroke_ischemic"],
        secondary_conditions=["atrial_fibrillation", "essential_hypertension", "type2_diabetes", "major_depression"],
        excluded_conditions=[],
        smoking_probability=0.05,
        obesity_probability=0.35,
        comorbidity_count=(3, 5),
        medication_adherence=0.80,
        encounter_frequency="high",
        socioeconomic_level="middle"
    ),
    
    "copd_moderate": PersonaProfile(
        name="COPD Moderate",
        description="COPD with moderate airflow limitation",
        age_range=(55, 80),
        gender_weights={"M": 0.55, "F": 0.45},
        primary_conditions=["copd"],
        secondary_conditions=["essential_hypertension", "coronary_artery_disease", "osteoporosis", "major_depression"],
        excluded_conditions=[],
        smoking_probability=0.40,  # Many are former smokers
        obesity_probability=0.25,
        comorbidity_count=(2, 4),
        medication_adherence=0.70,
        encounter_frequency="moderate",
        socioeconomic_level="low"
    ),
    
    "copd_severe": PersonaProfile(
        name="COPD Severe",
        description="Advanced COPD on home oxygen",
        age_range=(60, 85),
        gender_weights={"M": 0.55, "F": 0.45},
        primary_conditions=["copd_severe"],
        secondary_conditions=["heart_failure_systolic", "pulmonary_hypertension", "osteoporosis", "anxiety"],
        excluded_conditions=[],
        smoking_probability=0.20,
        obesity_probability=0.15,  # Often underweight
        comorbidity_count=(3, 5),
        medication_adherence=0.75,
        encounter_frequency="very_high",
        socioeconomic_level="low"
    ),
    
    "ckd_stage3": PersonaProfile(
        name="CKD Stage 3",
        description="Moderate chronic kidney disease",
        age_range=(55, 80),
        gender_weights={"M": 0.55, "F": 0.45},
        primary_conditions=["ckd_stage3"],
        secondary_conditions=["type2_diabetes", "essential_hypertension", "anemia_ckd", "gout"],
        excluded_conditions=["ckd_stage5"],
        smoking_probability=0.10,
        obesity_probability=0.40,
        comorbidity_count=(2, 4),
        medication_adherence=0.75,
        encounter_frequency="moderate",
        socioeconomic_level="middle"
    ),
    
    "ckd_stage4": PersonaProfile(
        name="CKD Stage 4",
        description="Severe CKD approaching dialysis",
        age_range=(55, 80),
        gender_weights={"M": 0.55, "F": 0.45},
        primary_conditions=["ckd_stage4"],
        secondary_conditions=["type2_diabetes", "essential_hypertension", "anemia_ckd", "secondary_hyperparathyroidism"],
        excluded_conditions=[],
        smoking_probability=0.05,
        obesity_probability=0.35,
        comorbidity_count=(3, 5),
        medication_adherence=0.80,
        encounter_frequency="high",
        socioeconomic_level="middle"
    ),
    
    "rheumatoid_arthritis": PersonaProfile(
        name="Rheumatoid Arthritis",
        description="RA on DMARDs",
        age_range=(35, 70),
        gender_weights={"M": 0.25, "F": 0.75},
        primary_conditions=["rheumatoid_arthritis"],
        secondary_conditions=["osteoporosis", "major_depression", "coronary_artery_disease"],
        excluded_conditions=[],
        smoking_probability=0.15,
        obesity_probability=0.30,
        comorbidity_count=(1, 3),
        medication_adherence=0.85,
        encounter_frequency="moderate",
        socioeconomic_level="middle"
    ),
    
    "lupus": PersonaProfile(
        name="Systemic Lupus",
        description="SLE patient",
        age_range=(20, 55),
        gender_weights={"M": 0.10, "F": 0.90},
        primary_conditions=["lupus"],
        secondary_conditions=["ckd_stage3", "major_depression", "fibromyalgia"],
        excluded_conditions=[],
        smoking_probability=0.10,
        obesity_probability=0.25,
        comorbidity_count=(1, 3),
        medication_adherence=0.80,
        encounter_frequency="moderate",
        socioeconomic_level="middle"
    ),
    
    "cirrhosis": PersonaProfile(
        name="Cirrhosis",
        description="Liver cirrhosis",
        age_range=(45, 75),
        gender_weights={"M": 0.70, "F": 0.30},
        primary_conditions=["cirrhosis"],
        secondary_conditions=["type2_diabetes", "ckd_stage3", "hepatic_encephalopathy"],
        excluded_conditions=[],
        smoking_probability=0.25,
        obesity_probability=0.30,
        comorbidity_count=(2, 4),
        medication_adherence=0.65,
        encounter_frequency="high",
        socioeconomic_level="low"
    ),
    
    "depression_anxiety": PersonaProfile(
        name="Depression/Anxiety",
        description="Primary psychiatric condition",
        age_range=(20, 65),
        gender_weights={"M": 0.40, "F": 0.60},
        primary_conditions=["major_depression_recurrent", "generalized_anxiety"],
        secondary_conditions=["insomnia", "migraine", "ibs", "fibromyalgia"],
        excluded_conditions=["schizophrenia", "bipolar_disorder"],
        smoking_probability=0.25,
        obesity_probability=0.35,
        comorbidity_count=(1, 3),
        medication_adherence=0.70,
        encounter_frequency="moderate",
        socioeconomic_level="middle"
    ),
    
    "bipolar": PersonaProfile(
        name="Bipolar Disorder",
        description="Bipolar I or II",
        age_range=(18, 55),
        gender_weights={"M": 0.50, "F": 0.50},
        primary_conditions=["bipolar_disorder"],
        secondary_conditions=["generalized_anxiety", "substance_use", "obesity", "type2_diabetes"],
        excluded_conditions=["schizophrenia"],
        smoking_probability=0.35,
        obesity_probability=0.45,
        comorbidity_count=(1, 3),
        medication_adherence=0.55,
        encounter_frequency="moderate",
        socioeconomic_level="low"
    ),
    
    "schizophrenia": PersonaProfile(
        name="Schizophrenia",
        description="Chronic schizophrenia",
        age_range=(25, 65),
        gender_weights={"M": 0.55, "F": 0.45},
        primary_conditions=["schizophrenia"],
        secondary_conditions=["type2_diabetes", "hyperlipidemia", "obesity", "copd"],
        excluded_conditions=[],
        smoking_probability=0.60,
        obesity_probability=0.50,
        comorbidity_count=(2, 4),
        medication_adherence=0.50,
        encounter_frequency="moderate",
        socioeconomic_level="low"
    ),
    
    "hiv_controlled": PersonaProfile(
        name="HIV Controlled",
        description="HIV on ART with undetectable viral load",
        age_range=(25, 65),
        gender_weights={"M": 0.70, "F": 0.30},
        primary_conditions=["hiv_controlled"],
        secondary_conditions=["hyperlipidemia", "ckd_stage3", "major_depression", "osteoporosis"],
        excluded_conditions=[],
        smoking_probability=0.25,
        obesity_probability=0.20,
        comorbidity_count=(1, 3),
        medication_adherence=0.90,
        encounter_frequency="moderate",
        socioeconomic_level="middle"
    ),
    
    "cancer_survivor": PersonaProfile(
        name="Cancer Survivor",
        description="History of cancer, in remission",
        age_range=(45, 80),
        gender_weights={"M": 0.45, "F": 0.55},
        primary_conditions=["breast_cancer_history"],  # Will be randomized
        secondary_conditions=["major_depression", "generalized_anxiety", "osteoporosis", "neuropathy"],
        excluded_conditions=[],
        smoking_probability=0.05,
        obesity_probability=0.30,
        comorbidity_count=(1, 3),
        medication_adherence=0.90,
        encounter_frequency="moderate",
        socioeconomic_level="middle"
    ),
    
    "metabolic_syndrome": PersonaProfile(
        name="Metabolic Syndrome",
        description="Obesity with metabolic complications",
        age_range=(35, 65),
        gender_weights={"M": 0.50, "F": 0.50},
        primary_conditions=["obesity", "prediabetes"],
        secondary_conditions=["essential_hypertension", "hyperlipidemia", "sleep_apnea", "nash", "gerd"],
        excluded_conditions=["ckd_stage4"],
        smoking_probability=0.15,
        obesity_probability=0.95,
        comorbidity_count=(3, 5),
        medication_adherence=0.60,
        encounter_frequency="moderate",
        socioeconomic_level="low"
    ),
    
    "sepsis_risk_high": PersonaProfile(
        name="High Sepsis Risk",
        description="Multiple risk factors for sepsis",
        age_range=(60, 90),
        gender_weights={"M": 0.50, "F": 0.50},
        primary_conditions=["ckd_stage4", "type2_diabetes_with_complications"],
        secondary_conditions=["heart_failure_systolic", "cirrhosis", "malnutrition", "immunosuppression"],
        excluded_conditions=[],
        smoking_probability=0.10,
        obesity_probability=0.30,
        comorbidity_count=(4, 7),
        medication_adherence=0.65,
        encounter_frequency="very_high",
        socioeconomic_level="low"
    ),
    
    "frail_elderly": PersonaProfile(
        name="Frail Elderly",
        description="Multiple comorbidities, high care needs",
        age_range=(80, 95),
        gender_weights={"M": 0.35, "F": 0.65},
        primary_conditions=["essential_hypertension", "osteoarthritis"],
        secondary_conditions=["heart_failure_preserved", "ckd_stage3", "osteoporosis", "alzheimers", "anemia_ckd"],
        excluded_conditions=[],
        smoking_probability=0.02,
        obesity_probability=0.20,
        comorbidity_count=(4, 7),
        medication_adherence=0.80,
        encounter_frequency="very_high",
        socioeconomic_level="middle"
    ),
}


class PersonaGenerator:
    """
    Main generator class for creating randomized patient personas
    """
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize generator with optional random seed for reproducibility"""
        if seed is not None:
            random.seed(seed)
        
        self.generated_count = 0
        
    def generate(self, 
                 profile: Optional[str] = None,
                 count: int = 1,
                 custom_profile: Optional[PersonaProfile] = None) -> List[PersonaBase]:
        """
        Generate one or more personas
        
        Args:
            profile: Name of predefined profile (e.g., "diabetic_controlled")
            count: Number of personas to generate
            custom_profile: Custom PersonaProfile object
            
        Returns:
            List of PersonaBase objects
        """
        personas = []
        
        for _ in range(count):
            if custom_profile:
                persona = self._generate_from_profile(custom_profile)
            elif profile and profile in PERSONA_PROFILES:
                persona = self._generate_from_profile(PERSONA_PROFILES[profile])
            else:
                # Random profile
                profile_key = random.choice(list(PERSONA_PROFILES.keys()))
                persona = self._generate_from_profile(PERSONA_PROFILES[profile_key])
            
            personas.append(persona)
            self.generated_count += 1
        
        return personas
    
    def generate_random(self, count: int = 1) -> List[PersonaBase]:
        """Generate random personas from random profiles"""
        return self.generate(count=count)
    
    def generate_diverse_set(self, count: int = 10) -> List[PersonaBase]:
        """Generate a diverse set of personas from different profiles"""
        profile_keys = list(PERSONA_PROFILES.keys())
        personas = []
        
        # Ensure diversity by cycling through profiles
        for i in range(count):
            profile_key = profile_keys[i % len(profile_keys)]
            persona = self._generate_from_profile(PERSONA_PROFILES[profile_key])
            personas.append(persona)
            self.generated_count += 1
        
        return personas
    
    def _generate_from_profile(self, profile: PersonaProfile) -> PersonaBase:
        """Generate a single persona from a profile"""
        
        # 1. Generate demographics
        demographics = self._generate_demographics(profile)
        
        # Create base persona
        persona = PersonaBase(demographics)
        
        # 2. Generate social history (affects other choices)
        social_history = self._generate_social_history(profile, demographics)
        persona.set_social_history(social_history)
        
        # 3. Generate conditions
        conditions = self._generate_conditions(profile, demographics)
        for condition in conditions:
            persona.add_condition(condition)
        
        # 4. Generate medications based on conditions
        medications = self._generate_medications(conditions, profile)
        for medication in medications:
            persona.add_medication(medication)
        
        # 5. Generate allergies
        allergies = self._generate_allergies()
        for allergy in allergies:
            persona.add_allergy(allergy)
        
        # 6. Generate family history
        family_history = self._generate_family_history(conditions)
        for fh in family_history:
            persona.add_family_history(fh)
        
        # 7. Generate vital signs history (time series)
        vitals_history = self._generate_vitals_history(profile, conditions, social_history)
        for vitals in vitals_history:
            persona.add_vital_signs(vitals)
        
        # 8. Generate lab results history (time series)
        labs_history = self._generate_labs_history(conditions)
        for lab in labs_history:
            persona.add_lab_result(lab)
        
        # 9. Generate encounters
        encounters = self._generate_encounters(profile, conditions)
        for encounter in encounters:
            persona.add_encounter(encounter)
        
        # 10. Calculate AI features
        persona.calculate_ai_features()
        
        # 11. Generate narrative
        persona.generate_narrative()
        
        return persona
    
    def _generate_demographics(self, profile: PersonaProfile) -> Demographics:
        """Generate demographic information"""
        
        # Gender
        gender = Gender.MALE if random.random() < profile.gender_weights.get("M", 0.5) else Gender.FEMALE
        
        # Name
        if gender == Gender.MALE:
            first_name = random.choice(FIRST_NAMES_MALE)
        else:
            first_name = random.choice(FIRST_NAMES_FEMALE)
        last_name = random.choice(LAST_NAMES)
        
        # Age and birth date
        age = random.randint(profile.age_range[0], profile.age_range[1])
        today = date.today()
        birth_year = today.year - age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)  # Safe for all months
        birth_date = date(birth_year, birth_month, birth_day)
        
        # Race (roughly US demographics with some variation)
        race_weights = {
            Race.WHITE: 0.60,
            Race.BLACK: 0.13,
            Race.HISPANIC: 0.18,
            Race.ASIAN: 0.06,
            Race.OTHER: 0.03
        }
        race = random.choices(list(race_weights.keys()), 
                              weights=list(race_weights.values()))[0]
        
        # Marital status (age-dependent)
        if age < 25:
            marital = MaritalStatus.SINGLE
        elif age < 40:
            marital = random.choices(
                [MaritalStatus.SINGLE, MaritalStatus.MARRIED, MaritalStatus.DIVORCED],
                weights=[0.4, 0.5, 0.1]
            )[0]
        elif age < 65:
            marital = random.choices(
                [MaritalStatus.SINGLE, MaritalStatus.MARRIED, MaritalStatus.DIVORCED, MaritalStatus.WIDOWED],
                weights=[0.15, 0.55, 0.25, 0.05]
            )[0]
        else:
            marital = random.choices(
                [MaritalStatus.SINGLE, MaritalStatus.MARRIED, MaritalStatus.DIVORCED, MaritalStatus.WIDOWED],
                weights=[0.10, 0.40, 0.20, 0.30]
            )[0]
        
        # Location
        state = random.choice(list(CITIES_BY_STATE.keys()))
        city = random.choice(CITIES_BY_STATE[state])
        street_num = random.randint(100, 9999)
        street = random.choice(STREET_NAMES)
        address = f"{street_num} {street}"
        zip_code = f"{random.randint(10000, 99999)}"
        
        # Coordinates (approximate US bounds)
        lat = random.uniform(25.0, 48.0)
        lon = random.uniform(-125.0, -70.0)
        
        # Income based on socioeconomic level
        if profile.socioeconomic_level == "low":
            income = random.randint(15000, 40000)
        elif profile.socioeconomic_level == "high":
            income = random.randint(100000, 300000)
        else:
            income = random.randint(40000, 100000)
        
        # Healthcare costs
        if profile.encounter_frequency == "very_high":
            healthcare_expenses = random.uniform(50000, 200000)
        elif profile.encounter_frequency == "high":
            healthcare_expenses = random.uniform(20000, 50000)
        elif profile.encounter_frequency == "moderate":
            healthcare_expenses = random.uniform(5000, 20000)
        else:
            healthcare_expenses = random.uniform(1000, 5000)
        
        healthcare_coverage = healthcare_expenses * random.uniform(0.6, 0.95)
        
        return Demographics(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            birth_date=birth_date,
            race=race,
            marital_status=marital,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            county=f"{city} County",
            lat=lat,
            lon=lon,
            healthcare_expenses=round(healthcare_expenses, 2),
            healthcare_coverage=round(healthcare_coverage, 2),
            income=income
        )
    
    def _generate_social_history(self, profile: PersonaProfile, 
                                  demographics: Demographics) -> SocialHistory:
        """Generate social history"""
        
        # Smoking
        if random.random() < profile.smoking_probability:
            if random.random() < 0.6:  # 60% current, 40% former
                smoking_status = "current"
                packs_per_day = random.choice([0.5, 1.0, 1.5, 2.0])
                years_smoked = random.randint(5, min(40, demographics.age - 15))
            else:
                smoking_status = "former"
                packs_per_day = 0
                years_smoked = random.randint(5, 30)
        else:
            smoking_status = "never"
            packs_per_day = 0
            years_smoked = 0
        
        # Alcohol
        alcohol_weights = {
            "none": 0.30,
            "social": 0.40,
            "moderate": 0.20,
            "heavy": 0.10
        }
        if profile.socioeconomic_level == "low":
            alcohol_weights["heavy"] = 0.20
        
        alcohol_use = random.choices(list(alcohol_weights.keys()),
                                      weights=list(alcohol_weights.values()))[0]
        drinks_per_week = {
            "none": 0,
            "social": random.randint(1, 3),
            "moderate": random.randint(4, 10),
            "heavy": random.randint(15, 30)
        }[alcohol_use]
        
        # Exercise
        if profile.obesity_probability > 0.5:
            exercise_weights = {"none": 0.4, "rarely": 0.35, "weekly": 0.20, "daily": 0.05}
        else:
            exercise_weights = {"none": 0.15, "rarely": 0.25, "weekly": 0.40, "daily": 0.20}
        
        exercise_frequency = random.choices(list(exercise_weights.keys()),
                                             weights=list(exercise_weights.values()))[0]
        exercise_minutes = {
            "none": 0,
            "rarely": random.randint(10, 60),
            "weekly": random.randint(60, 150),
            "daily": random.randint(150, 300)
        }[exercise_frequency]
        
        # Diet
        diet_weights = {"poor": 0.25, "average": 0.45, "good": 0.25, "excellent": 0.05}
        if profile.socioeconomic_level == "low":
            diet_weights = {"poor": 0.40, "average": 0.40, "good": 0.15, "excellent": 0.05}
        
        diet_quality = random.choices(list(diet_weights.keys()),
                                       weights=list(diet_weights.values()))[0]
        
        # Occupation
        if demographics.age >= 65:
            occupation = random.choice(["Retired", "Retired", "Retired", "Part-time work"])
        else:
            occupation = random.choice(OCCUPATIONS)
        
        # Education
        education_levels = ["Less than high school", "High school", "Some college", 
                          "Associate degree", "Bachelor's degree", "Master's degree", 
                          "Doctoral degree"]
        if profile.socioeconomic_level == "low":
            education = random.choice(education_levels[:3])
        elif profile.socioeconomic_level == "high":
            education = random.choice(education_levels[4:])
        else:
            education = random.choice(education_levels[1:5])
        
        # Living situation
        if demographics.age < 30:
            living_situations = ["Alone", "With roommates", "With family", "With partner"]
        elif demographics.age > 75:
            living_situations = ["Alone", "With family", "Assisted living", "Nursing home"]
        else:
            living_situations = ["Alone", "With family", "With partner"]
        
        living_situation = random.choice(living_situations)
        
        # Stress
        stress_weights = {"low": 0.25, "moderate": 0.50, "high": 0.25}
        if profile.encounter_frequency in ["high", "very_high"]:
            stress_weights = {"low": 0.10, "moderate": 0.40, "high": 0.50}
        
        stress_level = random.choices(list(stress_weights.keys()),
                                       weights=list(stress_weights.values()))[0]
        
        return SocialHistory(
            smoking_status=smoking_status,
            packs_per_day=packs_per_day,
            years_smoked=years_smoked,
            alcohol_use=alcohol_use,
            drinks_per_week=drinks_per_week,
            drug_use="none",  # Simplified
            exercise_frequency=exercise_frequency,
            exercise_minutes_per_week=exercise_minutes,
            diet_quality=diet_quality,
            occupation=occupation,
            education_level=education,
            living_situation=living_situation,
            stress_level=stress_level
        )
    
    def _generate_conditions(self, profile: PersonaProfile, 
                             demographics: Demographics) -> List[Condition]:
        """Generate medical conditions based on profile"""
        conditions = []
        today = date.today()
        
        # Add primary conditions
        for cond_key in profile.primary_conditions:
            if cond_key in CONDITION_CATALOG:
                template = CONDITION_CATALOG[cond_key]
                
                # Onset date based on typical age range
                min_onset = max(template.typical_onset_age[0], 10)
                max_onset = min(template.typical_onset_age[1], demographics.age)
                
                # If patient is too young for typical onset, use their current age
                if max_onset < min_onset:
                    onset_age = max(10, demographics.age - random.randint(1, 5))
                else:
                    onset_age = random.randint(min_onset, max_onset)
                years_ago = demographics.age - onset_age
                onset_date = today - timedelta(days=years_ago * 365 + random.randint(0, 364))
                
                # Stop date if not chronic
                stop_date = None
                is_active = True
                if not template.chronic and template.typical_duration_years:
                    duration = random.randint(1, template.typical_duration_years)
                    potential_stop = onset_date + timedelta(days=duration * 365)
                    if potential_stop < today:
                        stop_date = potential_stop
                        is_active = False
                
                conditions.append(Condition(
                    code=template.code,
                    description=template.description,
                    start_date=onset_date,
                    stop_date=stop_date,
                    is_active=is_active
                ))
        
        # Add secondary conditions
        n_secondary = random.randint(profile.comorbidity_count[0], 
                                      profile.comorbidity_count[1])
        available_secondary = [c for c in profile.secondary_conditions 
                               if c in CONDITION_CATALOG and c not in profile.excluded_conditions]
        
        if available_secondary:
            selected_secondary = random.sample(
                available_secondary, 
                min(n_secondary, len(available_secondary))
            )
            
            for cond_key in selected_secondary:
                template = CONDITION_CATALOG[cond_key]
                
                min_onset = max(template.typical_onset_age[0], 10)
                max_onset = min(template.typical_onset_age[1], demographics.age)
                
                # If patient is too young for typical onset, use their current age
                if max_onset < min_onset:
                    onset_age = max(10, demographics.age - random.randint(1, 5))
                else:
                    onset_age = random.randint(min_onset, max_onset)
                    
                years_ago = demographics.age - onset_age
                onset_date = today - timedelta(days=years_ago * 365 + random.randint(0, 364))
                
                conditions.append(Condition(
                    code=template.code,
                    description=template.description,
                    start_date=onset_date,
                    stop_date=None,
                    is_active=True
                ))
        
        return conditions
    
    def _generate_medications(self, conditions: List[Condition], 
                               profile: PersonaProfile) -> List[Medication]:
        """Generate medications based on conditions"""
        medications = []
        added_meds = set()
        
        for condition in conditions:
            if not condition.is_active:
                continue
            
            # Find condition key from code
            cond_key = None
            for key, template in CONDITION_CATALOG.items():
                if template.code == condition.code:
                    cond_key = key
                    break
            
            if not cond_key or cond_key not in CONDITION_CATALOG:
                continue
            
            cond_template = CONDITION_CATALOG[cond_key]
            
            # Get typical medications for this condition
            typical_meds = cond_template.typical_medications
            if not typical_meds:
                continue
            
            # Select some medications based on adherence
            n_meds = max(1, int(len(typical_meds) * profile.medication_adherence))
            selected_meds = random.sample(typical_meds, min(n_meds, len(typical_meds)))
            
            for med_key in selected_meds:
                if med_key in added_meds:
                    continue
                if med_key not in MEDICATION_CATALOG:
                    continue
                
                med_template = MEDICATION_CATALOG[med_key]
                added_meds.add(med_key)
                
                # Start date around condition onset
                start_offset = random.randint(0, 90)
                start_datetime = datetime.combine(
                    condition.start_date + timedelta(days=start_offset),
                    datetime.min.time()
                )
                
                dose = random.choice(med_template.typical_doses)
                freq = random.choice(med_template.typical_frequencies)
                
                medications.append(Medication(
                    code=med_template.code,
                    description=f"{med_template.generic_name} {dose}",
                    start_datetime=start_datetime,
                    stop_datetime=None,
                    is_active=True,
                    reason_code=condition.code,
                    reason_description=condition.description,
                    dosage=dose,
                    frequency=freq
                ))
        
        return medications
    
    def _generate_allergies(self) -> List[Allergy]:
        """Generate random allergies"""
        allergies = []
        
        # 30% chance of having any allergies
        if random.random() > 0.30:
            return allergies
        
        # 1-3 allergies
        n_allergies = random.randint(1, 3)
        selected = random.sample(list(ALLERGIES_CATALOG.keys()), 
                                  min(n_allergies, len(ALLERGIES_CATALOG)))
        
        for allergy_key in selected:
            code, description, reaction, severity = ALLERGIES_CATALOG[allergy_key]
            
            allergies.append(Allergy(
                code=code,
                description=description,
                start_date=date.today() - timedelta(days=random.randint(365, 10000)),
                stop_date=None,
                is_active=True,
                reaction=reaction,
                severity=severity
            ))
        
        return allergies
    
    def _generate_family_history(self, conditions: List[Condition]) -> List[FamilyHistory]:
        """Generate family history based on patient conditions"""
        family_history = []
        relations = ["mother", "father", "sibling", "maternal grandmother", 
                     "paternal grandfather", "aunt", "uncle"]
        
        # Add family history related to conditions
        for condition in conditions[:3]:  # Limit to first 3 conditions
            if random.random() < 0.5:  # 50% chance of family history
                relation = random.choice(relations)
                
                # Map condition to family history description
                desc_lower = condition.description.lower()
                if "diabetes" in desc_lower:
                    fh_condition = "Type 2 diabetes"
                elif "hypertension" in desc_lower:
                    fh_condition = "Hypertension"
                elif "heart" in desc_lower or "coronary" in desc_lower:
                    fh_condition = "Heart disease"
                elif "cancer" in desc_lower:
                    fh_condition = "Cancer"
                else:
                    fh_condition = random.choice(FAMILY_CONDITIONS)
                
                family_history.append(FamilyHistory(
                    relation=relation,
                    condition=fh_condition,
                    age_at_onset=random.randint(40, 70),
                    deceased=random.random() < 0.3,
                    age_at_death=random.randint(60, 90) if random.random() < 0.3 else None
                ))
        
        # Add some random family history
        n_additional = random.randint(0, 2)
        for _ in range(n_additional):
            family_history.append(FamilyHistory(
                relation=random.choice(relations),
                condition=random.choice(FAMILY_CONDITIONS),
                age_at_onset=random.randint(35, 75),
                deceased=random.random() < 0.3
            ))
        
        return family_history
    
    def _generate_vitals_history(self, profile: PersonaProfile,
                                  conditions: List[Condition],
                                  social_history: SocialHistory) -> List[VitalSigns]:
        """Generate vital signs time series"""
        vitals_history = []
        today = datetime.now()
        
        # Determine number of vitals readings based on encounter frequency
        n_readings = {
            "low": random.randint(3, 6),
            "moderate": random.randint(6, 12),
            "high": random.randint(12, 24),
            "very_high": random.randint(24, 48)
        }.get(profile.encounter_frequency, 6)
        
        # Get base vital patterns from conditions
        base_pattern = VitalPattern()  # Normal
        for condition in conditions:
            for key, template in CONDITION_CATALOG.items():
                if template.code == condition.code and condition.is_active:
                    # Merge patterns (use most abnormal values)
                    bp = template.vital_pattern
                    if bp.systolic_bp[0] > base_pattern.systolic_bp[0]:
                        base_pattern = VitalPattern(
                            systolic_bp=bp.systolic_bp,
                            diastolic_bp=bp.diastolic_bp,
                            heart_rate=bp.heart_rate,
                            respiratory_rate=bp.respiratory_rate,
                            temperature=bp.temperature,
                            oxygen_saturation=bp.oxygen_saturation
                        )
                    break
        
        # Base height and weight
        if profile.obesity_probability > 0.5 and random.random() < profile.obesity_probability:
            base_bmi = random.uniform(30, 45)
        else:
            base_bmi = random.uniform(22, 29)
        
        base_height = random.uniform(155, 190)  # cm
        base_weight = base_bmi * ((base_height / 100) ** 2)
        
        # Generate time series
        years_span = min(5, n_readings // 4 + 1)
        
        for i in range(n_readings):
            # Spread readings over time
            days_ago = int((n_readings - i - 1) * (years_span * 365 / n_readings))
            measurement_date = today - timedelta(days=days_ago + random.randint(-30, 30))
            
            # Add some variation to vitals
            vitals = VitalSigns(
                measurement_date=measurement_date,
                systolic_bp=random.randint(base_pattern.systolic_bp[0], 
                                           base_pattern.systolic_bp[1]),
                diastolic_bp=random.randint(base_pattern.diastolic_bp[0], 
                                            base_pattern.diastolic_bp[1]),
                heart_rate=random.randint(base_pattern.heart_rate[0], 
                                          base_pattern.heart_rate[1]),
                respiratory_rate=random.randint(base_pattern.respiratory_rate[0], 
                                                base_pattern.respiratory_rate[1]),
                temperature=round(random.uniform(base_pattern.temperature[0], 
                                                  base_pattern.temperature[1]), 1),
                oxygen_saturation=round(random.uniform(base_pattern.oxygen_saturation[0], 
                                                        base_pattern.oxygen_saturation[1]), 1),
                height_cm=base_height,
                weight_kg=round(base_weight + random.uniform(-5, 5), 1)
            )
            vitals_history.append(vitals)
        
        return sorted(vitals_history, key=lambda v: v.measurement_date)
    
    def _generate_labs_history(self, conditions: List[Condition]) -> List[LabResult]:
        """Generate lab results time series"""
        labs_history = []
        today = datetime.now()
        
        # Get base lab patterns from conditions
        base_pattern = LabPattern()  # Normal
        for condition in conditions:
            for key, template in CONDITION_CATALOG.items():
                if template.code == condition.code and condition.is_active:
                    base_pattern = template.lab_pattern
                    break
        
        # Number of lab panels
        n_panels = random.randint(3, 8)
        
        # Lab tests to generate
        lab_tests = [
            ("GLUCOSE_FASTING", "Glucose fasting", "mg/dL", base_pattern.glucose_fasting),
            ("HBA1C", "Hemoglobin A1c", "%", base_pattern.hba1c),
            ("CREATININE", "Creatinine", "mg/dL", base_pattern.creatinine),
            ("EGFR", "eGFR", "mL/min/1.73m2", base_pattern.egfr),
            ("BUN", "Blood urea nitrogen", "mg/dL", base_pattern.bun),
            ("SODIUM", "Sodium", "mEq/L", base_pattern.sodium),
            ("POTASSIUM", "Potassium", "mEq/L", base_pattern.potassium),
            ("TOTAL_CHOLESTEROL", "Total Cholesterol", "mg/dL", base_pattern.total_cholesterol),
            ("LDL", "LDL Cholesterol", "mg/dL", base_pattern.ldl),
            ("HDL", "HDL Cholesterol", "mg/dL", base_pattern.hdl),
            ("TRIGLYCERIDES", "Triglycerides", "mg/dL", base_pattern.triglycerides),
            ("WBC", "White blood cells", "K/uL", base_pattern.wbc),
            ("HEMOGLOBIN", "Hemoglobin", "g/dL", base_pattern.hemoglobin),
            ("HEMATOCRIT", "Hematocrit", "%", base_pattern.hematocrit),
            ("PLATELETS", "Platelets", "K/uL", base_pattern.platelets),
            ("ALT", "Alanine aminotransferase", "U/L", base_pattern.alt),
            ("AST", "Aspartate aminotransferase", "U/L", base_pattern.ast),
        ]
        
        for i in range(n_panels):
            days_ago = int((n_panels - i - 1) * (365 * 3 / n_panels))
            test_date = today - timedelta(days=days_ago + random.randint(-30, 30))
            
            for code, name, unit, range_tuple in lab_tests:
                value = round(random.uniform(range_tuple[0], range_tuple[1]), 2)
                
                labs_history.append(LabResult(
                    test_date=test_date,
                    test_code=code,
                    test_name=name,
                    value=value,
                    unit=unit,
                    reference_low=range_tuple[2],
                    reference_high=range_tuple[3]
                ))
        
        return sorted(labs_history, key=lambda l: l.test_date)
    
    def _generate_encounters(self, profile: PersonaProfile,
                              conditions: List[Condition]) -> List[Encounter]:
        """Generate encounter history"""
        encounters = []
        today = datetime.now()
        
        # Number of encounters based on frequency
        n_encounters = {
            "low": random.randint(2, 6),
            "moderate": random.randint(6, 15),
            "high": random.randint(15, 30),
            "very_high": random.randint(30, 60)
        }.get(profile.encounter_frequency, 10)
        
        encounter_types = [
            ("ambulatory", "General examination", 150),
            ("ambulatory", "Follow-up visit", 100),
            ("ambulatory", "Specialist consultation", 250),
            ("wellness", "Annual physical", 200),
            ("urgentcare", "Urgent care visit", 300),
            ("emergency", "Emergency department visit", 1500),
            ("inpatient", "Hospital admission", 15000),
        ]
        
        # Weight encounter types based on profile
        if profile.encounter_frequency == "very_high":
            weights = [0.20, 0.25, 0.15, 0.05, 0.10, 0.15, 0.10]
        elif profile.encounter_frequency == "high":
            weights = [0.25, 0.30, 0.15, 0.05, 0.10, 0.10, 0.05]
        else:
            weights = [0.30, 0.30, 0.10, 0.15, 0.10, 0.04, 0.01]
        
        for i in range(n_encounters):
            days_ago = int((n_encounters - i - 1) * (365 * 4 / n_encounters))
            start_datetime = today - timedelta(days=days_ago + random.randint(-30, 30))
            
            # Select encounter type
            enc_type = random.choices(encounter_types, weights=weights)[0]
            
            # Duration based on type
            if enc_type[0] == "inpatient":
                duration_hours = random.randint(24, 168)
            elif enc_type[0] == "emergency":
                duration_hours = random.randint(2, 12)
            else:
                duration_hours = random.randint(1, 3)
            
            stop_datetime = start_datetime + timedelta(hours=duration_hours)
            
            # Get reason from conditions
            reason_code = None
            reason_desc = None
            if conditions and random.random() < 0.7:
                condition = random.choice(conditions)
                reason_code = condition.code
                reason_desc = condition.description
            
            encounters.append(Encounter(
                encounter_id=str(uuid.uuid4()),
                encounter_class=enc_type[0],
                encounter_type=enc_type[1],
                start_datetime=start_datetime,
                stop_datetime=stop_datetime,
                reason_code=reason_code,
                reason_description=reason_desc,
                provider=f"Dr. {random.choice(LAST_NAMES)}",
                organization=f"{random.choice(['City', 'County', 'Regional', 'University'])} Medical Center",
                payer=random.choice(["Medicare", "Medicaid", "Blue Cross", "Aetna", "United"]),
                base_cost=enc_type[2],
                total_claim_cost=enc_type[2] * random.uniform(1.0, 2.5),
                payer_coverage=enc_type[2] * random.uniform(0.5, 0.95)
            ))
        
        return sorted(encounters, key=lambda e: e.start_datetime)
    
    def get_available_profiles(self) -> List[str]:
        """Get list of available profile names"""
        return list(PERSONA_PROFILES.keys())
    
    def get_profile_description(self, profile_name: str) -> Optional[str]:
        """Get description of a profile"""
        if profile_name in PERSONA_PROFILES:
            return PERSONA_PROFILES[profile_name].description
        return None
