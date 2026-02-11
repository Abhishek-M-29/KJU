"""
Condition Templates and Catalog
Defines realistic disease progressions, symptoms, and associated data
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


class ConditionCategory(Enum):
    CARDIOVASCULAR = "cardiovascular"
    METABOLIC = "metabolic"
    RESPIRATORY = "respiratory"
    RENAL = "renal"
    NEUROLOGICAL = "neurological"
    MUSCULOSKELETAL = "musculoskeletal"
    PSYCHIATRIC = "psychiatric"
    ONCOLOGY = "oncology"
    INFECTIOUS = "infectious"
    GASTROINTESTINAL = "gastrointestinal"
    ENDOCRINE = "endocrine"
    HEMATOLOGIC = "hematologic"
    DERMATOLOGIC = "dermatologic"
    OTHER = "other"


class Severity(Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


@dataclass
class VitalPattern:
    """Typical vital sign ranges for a condition"""
    systolic_bp: Tuple[int, int] = (110, 130)
    diastolic_bp: Tuple[int, int] = (70, 85)
    heart_rate: Tuple[int, int] = (60, 100)
    respiratory_rate: Tuple[int, int] = (12, 20)
    temperature: Tuple[float, float] = (36.5, 37.2)
    oxygen_saturation: Tuple[float, float] = (95.0, 100.0)


@dataclass
class LabPattern:
    """Typical lab values for a condition"""
    # Each is (min, max, reference_low, reference_high)
    glucose_fasting: Tuple[float, float, float, float] = (70, 100, 70, 100)
    hba1c: Tuple[float, float, float, float] = (4.5, 5.6, 4.0, 5.7)
    creatinine: Tuple[float, float, float, float] = (0.7, 1.2, 0.6, 1.2)
    egfr: Tuple[float, float, float, float] = (90, 120, 90, 120)
    bun: Tuple[float, float, float, float] = (7, 20, 7, 20)
    sodium: Tuple[float, float, float, float] = (136, 145, 136, 145)
    potassium: Tuple[float, float, float, float] = (3.5, 5.0, 3.5, 5.0)
    total_cholesterol: Tuple[float, float, float, float] = (150, 200, 0, 200)
    ldl: Tuple[float, float, float, float] = (70, 100, 0, 100)
    hdl: Tuple[float, float, float, float] = (40, 60, 40, 100)
    triglycerides: Tuple[float, float, float, float] = (50, 150, 0, 150)
    wbc: Tuple[float, float, float, float] = (4.5, 11.0, 4.5, 11.0)
    hemoglobin: Tuple[float, float, float, float] = (12.0, 17.5, 12.0, 17.5)
    hematocrit: Tuple[float, float, float, float] = (36, 50, 36, 50)
    platelets: Tuple[float, float, float, float] = (150, 400, 150, 400)
    alt: Tuple[float, float, float, float] = (7, 56, 7, 56)
    ast: Tuple[float, float, float, float] = (10, 40, 10, 40)
    alkaline_phosphatase: Tuple[float, float, float, float] = (44, 147, 44, 147)
    bilirubin: Tuple[float, float, float, float] = (0.1, 1.2, 0.1, 1.2)
    albumin: Tuple[float, float, float, float] = (3.4, 5.4, 3.4, 5.4)
    tsh: Tuple[float, float, float, float] = (0.4, 4.0, 0.4, 4.0)
    bnp: Tuple[float, float, float, float] = (0, 100, 0, 100)
    troponin: Tuple[float, float, float, float] = (0, 0.04, 0, 0.04)
    crp: Tuple[float, float, float, float] = (0, 3.0, 0, 3.0)
    procalcitonin: Tuple[float, float, float, float] = (0, 0.1, 0, 0.1)
    lactate: Tuple[float, float, float, float] = (0.5, 2.0, 0.5, 2.2)
    inr: Tuple[float, float, float, float] = (0.9, 1.1, 0.9, 1.1)


@dataclass
class ConditionTemplate:
    """Template for a medical condition with typical patterns"""
    code: str
    description: str
    category: ConditionCategory
    typical_onset_age: Tuple[int, int] = (40, 70)
    chronic: bool = True
    typical_duration_years: Optional[int] = None  # None = lifelong
    severity: Severity = Severity.MODERATE
    
    # Associated patterns
    vital_pattern: VitalPattern = field(default_factory=VitalPattern)
    lab_pattern: LabPattern = field(default_factory=LabPattern)
    
    # Associated conditions that commonly co-occur
    common_comorbidities: List[str] = field(default_factory=list)
    
    # Typical medications for this condition
    typical_medications: List[str] = field(default_factory=list)
    
    # Risk factors
    risk_factors: List[str] = field(default_factory=list)
    
    # Complications
    complications: List[str] = field(default_factory=list)
    
    # Weight impact (affects BMI generation)
    weight_impact: str = "neutral"  # "low", "neutral", "high", "very_high"


# ============================================================
# COMPREHENSIVE CONDITION CATALOG
# ============================================================

CONDITION_CATALOG = {
    # -------------------- CARDIOVASCULAR --------------------
    "essential_hypertension": ConditionTemplate(
        code="I10",
        description="Essential (primary) hypertension",
        category=ConditionCategory.CARDIOVASCULAR,
        typical_onset_age=(35, 65),
        chronic=True,
        severity=Severity.MODERATE,
        vital_pattern=VitalPattern(
            systolic_bp=(140, 180),
            diastolic_bp=(90, 110),
            heart_rate=(65, 95)
        ),
        common_comorbidities=["type2_diabetes", "hyperlipidemia", "obesity", "ckd_stage3"],
        typical_medications=["lisinopril", "amlodipine", "losartan", "metoprolol", "hydrochlorothiazide"],
        risk_factors=["obesity", "high_sodium_diet", "sedentary_lifestyle", "family_history", "smoking"],
        complications=["stroke", "heart_failure", "ckd", "retinopathy"]
    ),
    
    "heart_failure_systolic": ConditionTemplate(
        code="I50.2",
        description="Systolic (congestive) heart failure",
        category=ConditionCategory.CARDIOVASCULAR,
        typical_onset_age=(55, 80),
        chronic=True,
        severity=Severity.SEVERE,
        vital_pattern=VitalPattern(
            systolic_bp=(100, 140),
            diastolic_bp=(60, 90),
            heart_rate=(70, 110),
            oxygen_saturation=(88.0, 96.0),
            respiratory_rate=(16, 24)
        ),
        lab_pattern=LabPattern(
            bnp=(300, 2000, 0, 100),
            creatinine=(1.2, 2.5, 0.6, 1.2),
            sodium=(130, 140, 136, 145)
        ),
        common_comorbidities=["essential_hypertension", "coronary_artery_disease", "atrial_fibrillation", "type2_diabetes", "ckd_stage3"],
        typical_medications=["carvedilol", "lisinopril", "furosemide", "spironolactone", "sacubitril_valsartan"],
        risk_factors=["prior_mi", "hypertension", "coronary_artery_disease", "cardiomyopathy"],
        complications=["acute_decompensation", "arrhythmias", "renal_failure", "death"]
    ),
    
    "heart_failure_preserved": ConditionTemplate(
        code="I50.3",
        description="Diastolic (congestive) heart failure (HFpEF)",
        category=ConditionCategory.CARDIOVASCULAR,
        typical_onset_age=(60, 85),
        chronic=True,
        severity=Severity.MODERATE,
        vital_pattern=VitalPattern(
            systolic_bp=(130, 170),
            diastolic_bp=(70, 100),
            heart_rate=(65, 100),
            oxygen_saturation=(90.0, 97.0)
        ),
        lab_pattern=LabPattern(
            bnp=(100, 800, 0, 100)
        ),
        common_comorbidities=["essential_hypertension", "atrial_fibrillation", "obesity", "type2_diabetes"],
        typical_medications=["furosemide", "spironolactone", "empagliflozin"],
        weight_impact="high"
    ),
    
    "coronary_artery_disease": ConditionTemplate(
        code="I25.10",
        description="Atherosclerotic heart disease of native coronary artery",
        category=ConditionCategory.CARDIOVASCULAR,
        typical_onset_age=(45, 75),
        chronic=True,
        severity=Severity.MODERATE,
        vital_pattern=VitalPattern(
            systolic_bp=(120, 150),
            diastolic_bp=(70, 95),
            heart_rate=(55, 90)
        ),
        lab_pattern=LabPattern(
            ldl=(100, 190, 0, 100),
            total_cholesterol=(180, 280, 0, 200),
            triglycerides=(100, 300, 0, 150)
        ),
        common_comorbidities=["essential_hypertension", "hyperlipidemia", "type2_diabetes"],
        typical_medications=["atorvastatin", "aspirin", "metoprolol", "lisinopril", "clopidogrel"],
        risk_factors=["smoking", "diabetes", "hypertension", "hyperlipidemia", "family_history"],
        complications=["myocardial_infarction", "heart_failure", "arrhythmias"]
    ),
    
    "atrial_fibrillation": ConditionTemplate(
        code="I48.91",
        description="Atrial fibrillation, unspecified",
        category=ConditionCategory.CARDIOVASCULAR,
        typical_onset_age=(50, 80),
        chronic=True,
        severity=Severity.MODERATE,
        vital_pattern=VitalPattern(
            systolic_bp=(110, 160),
            diastolic_bp=(65, 95),
            heart_rate=(60, 150)  # Wide range due to rate control
        ),
        common_comorbidities=["essential_hypertension", "heart_failure_systolic", "coronary_artery_disease"],
        typical_medications=["apixaban", "warfarin", "metoprolol", "diltiazem", "digoxin", "amiodarone"],
        risk_factors=["hypertension", "heart_failure", "obesity", "sleep_apnea", "alcohol"],
        complications=["stroke", "heart_failure", "bleeding_on_anticoagulation"]
    ),
    
    "prior_mi": ConditionTemplate(
        code="I25.2",
        description="Old myocardial infarction",
        category=ConditionCategory.CARDIOVASCULAR,
        typical_onset_age=(50, 75),
        chronic=True,
        severity=Severity.MODERATE,
        vital_pattern=VitalPattern(
            systolic_bp=(100, 140),
            diastolic_bp=(60, 85),
            heart_rate=(55, 85)
        ),
        common_comorbidities=["coronary_artery_disease", "heart_failure_systolic", "essential_hypertension"],
        typical_medications=["aspirin", "atorvastatin", "metoprolol", "lisinopril", "clopidogrel"]
    ),
    
    "peripheral_vascular_disease": ConditionTemplate(
        code="I73.9",
        description="Peripheral vascular disease, unspecified",
        category=ConditionCategory.CARDIOVASCULAR,
        typical_onset_age=(55, 80),
        chronic=True,
        severity=Severity.MODERATE,
        common_comorbidities=["coronary_artery_disease", "type2_diabetes", "essential_hypertension"],
        typical_medications=["aspirin", "cilostazol", "atorvastatin"],
        risk_factors=["smoking", "diabetes", "hypertension"]
    ),
    
    "stroke_ischemic": ConditionTemplate(
        code="I63.9",
        description="Cerebral infarction, unspecified",
        category=ConditionCategory.NEUROLOGICAL,
        typical_onset_age=(60, 85),
        chronic=True,
        severity=Severity.SEVERE,
        vital_pattern=VitalPattern(
            systolic_bp=(130, 180),
            diastolic_bp=(75, 100)
        ),
        common_comorbidities=["atrial_fibrillation", "essential_hypertension", "type2_diabetes", "hyperlipidemia"],
        typical_medications=["aspirin", "clopidogrel", "atorvastatin", "apixaban"],
        risk_factors=["atrial_fibrillation", "hypertension", "diabetes", "smoking", "obesity"]
    ),
    
    # -------------------- METABOLIC / ENDOCRINE --------------------
    "type2_diabetes": ConditionTemplate(
        code="E11.9",
        description="Type 2 diabetes mellitus without complications",
        category=ConditionCategory.METABOLIC,
        typical_onset_age=(35, 65),
        chronic=True,
        severity=Severity.MODERATE,
        vital_pattern=VitalPattern(
            systolic_bp=(120, 150),
            diastolic_bp=(75, 95)
        ),
        lab_pattern=LabPattern(
            glucose_fasting=(126, 250, 70, 100),
            hba1c=(7.0, 11.0, 4.0, 5.7)
        ),
        common_comorbidities=["essential_hypertension", "hyperlipidemia", "obesity", "ckd_stage3"],
        typical_medications=["metformin", "glipizide", "sitagliptin", "empagliflozin", "liraglutide", "insulin_glargine"],
        risk_factors=["obesity", "sedentary_lifestyle", "family_history", "gestational_diabetes"],
        complications=["diabetic_nephropathy", "diabetic_retinopathy", "diabetic_neuropathy", "cardiovascular_disease"],
        weight_impact="high"
    ),
    
    "type2_diabetes_with_complications": ConditionTemplate(
        code="E11.65",
        description="Type 2 diabetes mellitus with hyperglycemia",
        category=ConditionCategory.METABOLIC,
        typical_onset_age=(45, 75),
        chronic=True,
        severity=Severity.SEVERE,
        lab_pattern=LabPattern(
            glucose_fasting=(180, 350, 70, 100),
            hba1c=(9.0, 14.0, 4.0, 5.7),
            creatinine=(1.3, 3.0, 0.6, 1.2)
        ),
        common_comorbidities=["ckd_stage3", "diabetic_retinopathy", "diabetic_neuropathy", "coronary_artery_disease"],
        typical_medications=["insulin_glargine", "insulin_lispro", "metformin", "empagliflozin"],
        weight_impact="high"
    ),
    
    "type1_diabetes": ConditionTemplate(
        code="E10.9",
        description="Type 1 diabetes mellitus without complications",
        category=ConditionCategory.METABOLIC,
        typical_onset_age=(5, 30),
        chronic=True,
        severity=Severity.MODERATE,
        lab_pattern=LabPattern(
            glucose_fasting=(80, 200, 70, 100),
            hba1c=(6.5, 9.0, 4.0, 5.7)
        ),
        typical_medications=["insulin_glargine", "insulin_lispro", "insulin_aspart"],
        weight_impact="neutral"
    ),
    
    "prediabetes": ConditionTemplate(
        code="R73.03",
        description="Prediabetes",
        category=ConditionCategory.METABOLIC,
        typical_onset_age=(30, 60),
        chronic=False,
        typical_duration_years=5,
        severity=Severity.MILD,
        lab_pattern=LabPattern(
            glucose_fasting=(100, 125, 70, 100),
            hba1c=(5.7, 6.4, 4.0, 5.7)
        ),
        common_comorbidities=["obesity", "essential_hypertension"],
        typical_medications=["metformin"],  # Sometimes used
        weight_impact="high"
    ),
    
    "hyperlipidemia": ConditionTemplate(
        code="E78.5",
        description="Hyperlipidemia, unspecified",
        category=ConditionCategory.METABOLIC,
        typical_onset_age=(30, 70),
        chronic=True,
        severity=Severity.MILD,
        lab_pattern=LabPattern(
            total_cholesterol=(200, 300, 0, 200),
            ldl=(130, 200, 0, 100),
            triglycerides=(150, 400, 0, 150)
        ),
        common_comorbidities=["essential_hypertension", "type2_diabetes", "coronary_artery_disease"],
        typical_medications=["atorvastatin", "rosuvastatin", "simvastatin", "ezetimibe", "fenofibrate"],
        risk_factors=["diet", "obesity", "sedentary_lifestyle", "genetics"]
    ),
    
    "obesity": ConditionTemplate(
        code="E66.9",
        description="Obesity, unspecified",
        category=ConditionCategory.METABOLIC,
        typical_onset_age=(20, 60),
        chronic=True,
        severity=Severity.MODERATE,
        common_comorbidities=["type2_diabetes", "essential_hypertension", "hyperlipidemia", "sleep_apnea"],
        typical_medications=["semaglutide", "phentermine"],
        risk_factors=["diet", "sedentary_lifestyle", "genetics"],
        weight_impact="very_high"
    ),
    
    "morbid_obesity": ConditionTemplate(
        code="E66.01",
        description="Morbid (severe) obesity due to excess calories",
        category=ConditionCategory.METABOLIC,
        typical_onset_age=(25, 55),
        chronic=True,
        severity=Severity.SEVERE,
        vital_pattern=VitalPattern(
            systolic_bp=(130, 160),
            diastolic_bp=(85, 100),
            heart_rate=(75, 110),
            oxygen_saturation=(90.0, 96.0)
        ),
        common_comorbidities=["type2_diabetes", "sleep_apnea", "essential_hypertension", "heart_failure_preserved"],
        weight_impact="very_high"
    ),
    
    "hypothyroidism": ConditionTemplate(
        code="E03.9",
        description="Hypothyroidism, unspecified",
        category=ConditionCategory.ENDOCRINE,
        typical_onset_age=(30, 70),
        chronic=True,
        severity=Severity.MILD,
        vital_pattern=VitalPattern(
            heart_rate=(50, 70)
        ),
        lab_pattern=LabPattern(
            tsh=(5.0, 15.0, 0.4, 4.0)
        ),
        typical_medications=["levothyroxine"],
        weight_impact="high"
    ),
    
    "hyperthyroidism": ConditionTemplate(
        code="E05.90",
        description="Thyrotoxicosis, unspecified",
        category=ConditionCategory.ENDOCRINE,
        typical_onset_age=(20, 50),
        chronic=True,
        severity=Severity.MODERATE,
        vital_pattern=VitalPattern(
            heart_rate=(90, 130),
            systolic_bp=(130, 160)
        ),
        lab_pattern=LabPattern(
            tsh=(0.01, 0.3, 0.4, 4.0)
        ),
        typical_medications=["methimazole", "propylthiouracil", "propranolol"],
        weight_impact="low"
    ),
    
    # -------------------- RESPIRATORY --------------------
    "copd": ConditionTemplate(
        code="J44.9",
        description="Chronic obstructive pulmonary disease, unspecified",
        category=ConditionCategory.RESPIRATORY,
        typical_onset_age=(50, 80),
        chronic=True,
        severity=Severity.MODERATE,
        vital_pattern=VitalPattern(
            oxygen_saturation=(88.0, 94.0),
            respiratory_rate=(18, 28),
            heart_rate=(80, 110)
        ),
        common_comorbidities=["essential_hypertension", "coronary_artery_disease", "heart_failure_systolic"],
        typical_medications=["tiotropium", "fluticasone_salmeterol", "albuterol", "prednisone"],
        risk_factors=["smoking", "occupational_exposure", "alpha1_antitrypsin_deficiency"]
    ),
    
    "copd_severe": ConditionTemplate(
        code="J44.1",
        description="Chronic obstructive pulmonary disease with acute exacerbation",
        category=ConditionCategory.RESPIRATORY,
        typical_onset_age=(55, 80),
        chronic=True,
        severity=Severity.SEVERE,
        vital_pattern=VitalPattern(
            oxygen_saturation=(82.0, 90.0),
            respiratory_rate=(22, 32),
            heart_rate=(90, 120)
        ),
        typical_medications=["tiotropium", "fluticasone_salmeterol", "albuterol", "prednisone", "home_oxygen"]
    ),
    
    "asthma": ConditionTemplate(
        code="J45.20",
        description="Mild intermittent asthma, uncomplicated",
        category=ConditionCategory.RESPIRATORY,
        typical_onset_age=(5, 40),
        chronic=True,
        severity=Severity.MILD,
        vital_pattern=VitalPattern(
            oxygen_saturation=(94.0, 99.0),
            respiratory_rate=(14, 22)
        ),
        typical_medications=["albuterol", "fluticasone"],
        risk_factors=["allergies", "family_history", "environmental_triggers"]
    ),
    
    "asthma_moderate": ConditionTemplate(
        code="J45.40",
        description="Moderate persistent asthma, uncomplicated",
        category=ConditionCategory.RESPIRATORY,
        typical_onset_age=(10, 50),
        chronic=True,
        severity=Severity.MODERATE,
        vital_pattern=VitalPattern(
            oxygen_saturation=(92.0, 98.0),
            respiratory_rate=(16, 24)
        ),
        typical_medications=["fluticasone_salmeterol", "montelukast", "albuterol"]
    ),
    
    "sleep_apnea": ConditionTemplate(
        code="G47.33",
        description="Obstructive sleep apnea (adult)",
        category=ConditionCategory.RESPIRATORY,
        typical_onset_age=(35, 70),
        chronic=True,
        severity=Severity.MODERATE,
        vital_pattern=VitalPattern(
            oxygen_saturation=(88.0, 95.0)  # Nocturnal desaturation
        ),
        common_comorbidities=["obesity", "essential_hypertension", "atrial_fibrillation", "type2_diabetes"],
        typical_medications=[],  # CPAP is main treatment
        weight_impact="high"
    ),
    
    "pulmonary_fibrosis": ConditionTemplate(
        code="J84.10",
        description="Pulmonary fibrosis, unspecified",
        category=ConditionCategory.RESPIRATORY,
        typical_onset_age=(50, 75),
        chronic=True,
        severity=Severity.SEVERE,
        vital_pattern=VitalPattern(
            oxygen_saturation=(85.0, 94.0),
            respiratory_rate=(18, 28)
        ),
        typical_medications=["pirfenidone", "nintedanib", "prednisone", "home_oxygen"]
    ),
    
    # -------------------- RENAL --------------------
    "ckd_stage3": ConditionTemplate(
        code="N18.3",
        description="Chronic kidney disease, stage 3 (moderate)",
        category=ConditionCategory.RENAL,
        typical_onset_age=(50, 80),
        chronic=True,
        severity=Severity.MODERATE,
        lab_pattern=LabPattern(
            creatinine=(1.5, 2.5, 0.6, 1.2),
            egfr=(30, 59, 90, 120),
            bun=(20, 40, 7, 20),
            potassium=(4.5, 5.5, 3.5, 5.0)
        ),
        common_comorbidities=["essential_hypertension", "type2_diabetes", "heart_failure_systolic"],
        typical_medications=["lisinopril", "furosemide", "sodium_bicarbonate"],
        risk_factors=["diabetes", "hypertension", "family_history"]
    ),
    
    "ckd_stage4": ConditionTemplate(
        code="N18.4",
        description="Chronic kidney disease, stage 4 (severe)",
        category=ConditionCategory.RENAL,
        typical_onset_age=(55, 80),
        chronic=True,
        severity=Severity.SEVERE,
        lab_pattern=LabPattern(
            creatinine=(2.5, 5.0, 0.6, 1.2),
            egfr=(15, 29, 90, 120),
            bun=(40, 80, 7, 20),
            potassium=(5.0, 6.0, 3.5, 5.0),
            hemoglobin=(9.0, 11.0, 12.0, 17.5)
        ),
        common_comorbidities=["essential_hypertension", "type2_diabetes", "anemia_ckd", "secondary_hyperparathyroidism"],
        typical_medications=["furosemide", "sevelamer", "epoetin_alfa", "calcitriol"]
    ),
    
    "ckd_stage5": ConditionTemplate(
        code="N18.5",
        description="Chronic kidney disease, stage 5",
        category=ConditionCategory.RENAL,
        typical_onset_age=(55, 80),
        chronic=True,
        severity=Severity.CRITICAL,
        lab_pattern=LabPattern(
            creatinine=(5.0, 12.0, 0.6, 1.2),
            egfr=(5, 14, 90, 120),
            bun=(60, 150, 7, 20),
            potassium=(5.5, 7.0, 3.5, 5.0),
            hemoglobin=(7.0, 10.0, 12.0, 17.5)
        ),
        typical_medications=["dialysis", "sevelamer", "epoetin_alfa", "calcitriol"]
    ),
    
    "diabetic_nephropathy": ConditionTemplate(
        code="E11.21",
        description="Type 2 diabetes mellitus with diabetic nephropathy",
        category=ConditionCategory.RENAL,
        typical_onset_age=(50, 75),
        chronic=True,
        severity=Severity.MODERATE,
        lab_pattern=LabPattern(
            creatinine=(1.3, 3.0, 0.6, 1.2),
            egfr=(30, 60, 90, 120),
            hba1c=(7.5, 10.0, 4.0, 5.7)
        ),
        common_comorbidities=["type2_diabetes", "essential_hypertension", "diabetic_retinopathy"],
        typical_medications=["lisinopril", "losartan", "empagliflozin"]
    ),
    
    # -------------------- GASTROINTESTINAL --------------------
    "gerd": ConditionTemplate(
        code="K21.0",
        description="Gastro-esophageal reflux disease with esophagitis",
        category=ConditionCategory.GASTROINTESTINAL,
        typical_onset_age=(25, 65),
        chronic=True,
        severity=Severity.MILD,
        typical_medications=["omeprazole", "pantoprazole", "famotidine"],
        common_comorbidities=["obesity", "hiatal_hernia"]
    ),
    
    "peptic_ulcer": ConditionTemplate(
        code="K27.9",
        description="Peptic ulcer, site unspecified",
        category=ConditionCategory.GASTROINTESTINAL,
        typical_onset_age=(30, 70),
        chronic=False,
        typical_duration_years=1,
        severity=Severity.MODERATE,
        typical_medications=["omeprazole", "clarithromycin", "amoxicillin", "sucralfate"]
    ),
    
    "cirrhosis": ConditionTemplate(
        code="K74.60",
        description="Unspecified cirrhosis of liver",
        category=ConditionCategory.GASTROINTESTINAL,
        typical_onset_age=(45, 75),
        chronic=True,
        severity=Severity.SEVERE,
        lab_pattern=LabPattern(
            alt=(50, 200, 7, 56),
            ast=(60, 250, 10, 40),
            bilirubin=(2.0, 10.0, 0.1, 1.2),
            albumin=(2.0, 3.2, 3.4, 5.4),
            inr=(1.3, 2.5, 0.9, 1.1),
            platelets=(50, 120, 150, 400)
        ),
        common_comorbidities=["portal_hypertension", "hepatic_encephalopathy", "ascites"],
        typical_medications=["lactulose", "spironolactone", "furosemide", "propranolol", "rifaximin"]
    ),
    
    "nash": ConditionTemplate(
        code="K75.81",
        description="Nonalcoholic steatohepatitis (NASH)",
        category=ConditionCategory.GASTROINTESTINAL,
        typical_onset_age=(35, 65),
        chronic=True,
        severity=Severity.MODERATE,
        lab_pattern=LabPattern(
            alt=(45, 150, 7, 56),
            ast=(40, 120, 10, 40)
        ),
        common_comorbidities=["obesity", "type2_diabetes", "hyperlipidemia"],
        typical_medications=["vitamin_e", "pioglitazone"],
        weight_impact="high"
    ),
    
    "ibd_crohns": ConditionTemplate(
        code="K50.90",
        description="Crohn's disease, unspecified",
        category=ConditionCategory.GASTROINTESTINAL,
        typical_onset_age=(15, 40),
        chronic=True,
        severity=Severity.MODERATE,
        lab_pattern=LabPattern(
            crp=(5.0, 50.0, 0, 3.0),
            hemoglobin=(10.0, 13.0, 12.0, 17.5)
        ),
        typical_medications=["mesalamine", "prednisone", "azathioprine", "infliximab", "adalimumab"]
    ),
    
    "ibd_uc": ConditionTemplate(
        code="K51.90",
        description="Ulcerative colitis, unspecified",
        category=ConditionCategory.GASTROINTESTINAL,
        typical_onset_age=(15, 45),
        chronic=True,
        severity=Severity.MODERATE,
        lab_pattern=LabPattern(
            crp=(5.0, 40.0, 0, 3.0),
            hemoglobin=(10.0, 13.5, 12.0, 17.5)
        ),
        typical_medications=["mesalamine", "prednisone", "azathioprine", "vedolizumab"]
    ),
    
    # -------------------- MUSCULOSKELETAL --------------------
    "rheumatoid_arthritis": ConditionTemplate(
        code="M06.9",
        description="Rheumatoid arthritis, unspecified",
        category=ConditionCategory.MUSCULOSKELETAL,
        typical_onset_age=(30, 60),
        chronic=True,
        severity=Severity.MODERATE,
        lab_pattern=LabPattern(
            crp=(3.0, 30.0, 0, 3.0)
        ),
        typical_medications=["methotrexate", "hydroxychloroquine", "prednisone", "adalimumab", "etanercept"],
        complications=["joint_destruction", "cardiovascular_disease"]
    ),
    
    "osteoarthritis": ConditionTemplate(
        code="M19.90",
        description="Unspecified osteoarthritis, unspecified site",
        category=ConditionCategory.MUSCULOSKELETAL,
        typical_onset_age=(50, 80),
        chronic=True,
        severity=Severity.MILD,
        typical_medications=["acetaminophen", "ibuprofen", "naproxen", "meloxicam"],
        risk_factors=["age", "obesity", "prior_injury"]
    ),
    
    "osteoporosis": ConditionTemplate(
        code="M81.0",
        description="Age-related osteoporosis without current pathological fracture",
        category=ConditionCategory.MUSCULOSKELETAL,
        typical_onset_age=(55, 85),
        chronic=True,
        severity=Severity.MILD,
        typical_medications=["alendronate", "risedronate", "denosumab", "calcium", "vitamin_d"],
        risk_factors=["menopause", "low_body_weight", "smoking", "family_history"]
    ),
    
    "gout": ConditionTemplate(
        code="M10.9",
        description="Gout, unspecified",
        category=ConditionCategory.MUSCULOSKELETAL,
        typical_onset_age=(40, 70),
        chronic=True,
        severity=Severity.MILD,
        typical_medications=["allopurinol", "febuxostat", "colchicine", "indomethacin"],
        common_comorbidities=["ckd_stage3", "essential_hypertension", "obesity"],
        risk_factors=["diet", "alcohol", "obesity", "diuretics"]
    ),
    
    "lupus": ConditionTemplate(
        code="M32.9",
        description="Systemic lupus erythematosus, unspecified",
        category=ConditionCategory.MUSCULOSKELETAL,
        typical_onset_age=(15, 45),
        chronic=True,
        severity=Severity.MODERATE,
        common_comorbidities=["lupus_nephritis", "antiphospholipid_syndrome"],
        typical_medications=["hydroxychloroquine", "prednisone", "mycophenolate", "azathioprine", "belimumab"]
    ),
    
    # -------------------- PSYCHIATRIC --------------------
    "major_depression": ConditionTemplate(
        code="F32.9",
        description="Major depressive disorder, single episode, unspecified",
        category=ConditionCategory.PSYCHIATRIC,
        typical_onset_age=(18, 60),
        chronic=False,
        typical_duration_years=2,
        severity=Severity.MODERATE,
        typical_medications=["sertraline", "escitalopram", "fluoxetine", "bupropion", "venlafaxine"],
        risk_factors=["stress", "trauma", "family_history", "chronic_illness"]
    ),
    
    "major_depression_recurrent": ConditionTemplate(
        code="F33.9",
        description="Major depressive disorder, recurrent, unspecified",
        category=ConditionCategory.PSYCHIATRIC,
        typical_onset_age=(20, 55),
        chronic=True,
        severity=Severity.MODERATE,
        typical_medications=["sertraline", "escitalopram", "duloxetine", "venlafaxine", "mirtazapine"]
    ),
    
    "generalized_anxiety": ConditionTemplate(
        code="F41.1",
        description="Generalized anxiety disorder",
        category=ConditionCategory.PSYCHIATRIC,
        typical_onset_age=(20, 50),
        chronic=True,
        severity=Severity.MILD,
        vital_pattern=VitalPattern(
            heart_rate=(75, 110)
        ),
        typical_medications=["sertraline", "escitalopram", "buspirone", "hydroxyzine"],
        common_comorbidities=["major_depression", "insomnia"]
    ),
    
    "bipolar_disorder": ConditionTemplate(
        code="F31.9",
        description="Bipolar disorder, unspecified",
        category=ConditionCategory.PSYCHIATRIC,
        typical_onset_age=(18, 35),
        chronic=True,
        severity=Severity.MODERATE,
        typical_medications=["lithium", "valproic_acid", "lamotrigine", "quetiapine", "aripiprazole"],
        lab_pattern=LabPattern(  # Need to monitor lithium, metabolic effects
            glucose_fasting=(90, 140, 70, 100),
            triglycerides=(100, 250, 0, 150)
        ),
        weight_impact="high"  # Due to medications
    ),
    
    "schizophrenia": ConditionTemplate(
        code="F20.9",
        description="Schizophrenia, unspecified",
        category=ConditionCategory.PSYCHIATRIC,
        typical_onset_age=(18, 35),
        chronic=True,
        severity=Severity.SEVERE,
        typical_medications=["risperidone", "olanzapine", "aripiprazole", "clozapine", "haloperidol"],
        common_comorbidities=["type2_diabetes", "hyperlipidemia"],  # Metabolic side effects
        weight_impact="high"
    ),
    
    "ptsd": ConditionTemplate(
        code="F43.10",
        description="Post-traumatic stress disorder, unspecified",
        category=ConditionCategory.PSYCHIATRIC,
        typical_onset_age=(20, 60),
        chronic=True,
        severity=Severity.MODERATE,
        typical_medications=["sertraline", "paroxetine", "prazosin", "venlafaxine"],
        common_comorbidities=["major_depression", "generalized_anxiety", "substance_use"]
    ),
    
    "adhd_adult": ConditionTemplate(
        code="F90.0",
        description="Attention-deficit hyperactivity disorder, predominantly inattentive type",
        category=ConditionCategory.PSYCHIATRIC,
        typical_onset_age=(6, 18),  # Diagnosed in childhood, persists
        chronic=True,
        severity=Severity.MILD,
        typical_medications=["methylphenidate", "amphetamine_salts", "lisdexamfetamine", "atomoxetine"]
    ),
    
    "insomnia": ConditionTemplate(
        code="G47.00",
        description="Insomnia, unspecified",
        category=ConditionCategory.PSYCHIATRIC,
        typical_onset_age=(25, 70),
        chronic=True,
        severity=Severity.MILD,
        typical_medications=["trazodone", "zolpidem", "eszopiclone", "melatonin"],
        common_comorbidities=["generalized_anxiety", "major_depression"]
    ),
    
    # -------------------- ONCOLOGY --------------------
    "breast_cancer_history": ConditionTemplate(
        code="Z85.3",
        description="Personal history of malignant neoplasm of breast",
        category=ConditionCategory.ONCOLOGY,
        typical_onset_age=(40, 70),
        chronic=True,  # Surveillance
        severity=Severity.MODERATE,
        typical_medications=["tamoxifen", "anastrozole", "letrozole"],
        common_comorbidities=["anxiety", "osteoporosis"]  # From treatment
    ),
    
    "prostate_cancer_history": ConditionTemplate(
        code="Z85.46",
        description="Personal history of malignant neoplasm of prostate",
        category=ConditionCategory.ONCOLOGY,
        typical_onset_age=(55, 80),
        chronic=True,
        severity=Severity.MODERATE,
        typical_medications=["leuprolide", "bicalutamide", "abiraterone"]
    ),
    
    "colon_cancer_history": ConditionTemplate(
        code="Z85.038",
        description="Personal history of malignant neoplasm of large intestine",
        category=ConditionCategory.ONCOLOGY,
        typical_onset_age=(50, 75),
        chronic=True,
        severity=Severity.MODERATE
    ),
    
    "lung_cancer": ConditionTemplate(
        code="C34.90",
        description="Malignant neoplasm of unspecified part of bronchus or lung",
        category=ConditionCategory.ONCOLOGY,
        typical_onset_age=(55, 80),
        chronic=True,
        severity=Severity.SEVERE,
        vital_pattern=VitalPattern(
            oxygen_saturation=(88.0, 95.0)
        ),
        common_comorbidities=["copd", "major_depression"],
        risk_factors=["smoking", "occupational_exposure", "family_history"]
    ),
    
    # -------------------- INFECTIOUS --------------------
    "hiv_controlled": ConditionTemplate(
        code="B20",
        description="Human immunodeficiency virus [HIV] disease",
        category=ConditionCategory.INFECTIOUS,
        typical_onset_age=(20, 50),
        chronic=True,
        severity=Severity.MODERATE,
        typical_medications=["bictegravir_emtricitabine_tenofovir", "dolutegravir", "darunavir"],
        common_comorbidities=["hyperlipidemia", "ckd_stage3"]  # ART side effects
    ),
    
    "hepatitis_c_treated": ConditionTemplate(
        code="B18.2",
        description="Chronic viral hepatitis C",
        category=ConditionCategory.INFECTIOUS,
        typical_onset_age=(40, 70),
        chronic=True,
        severity=Severity.MILD,  # After treatment
        lab_pattern=LabPattern(
            alt=(15, 45, 7, 56),
            ast=(15, 40, 10, 40)
        ),
        typical_medications=["sofosbuvir_velpatasvir", "glecaprevir_pibrentasvir"]
    ),
    
    "hepatitis_b": ConditionTemplate(
        code="B18.1",
        description="Chronic viral hepatitis B without delta-agent",
        category=ConditionCategory.INFECTIOUS,
        typical_onset_age=(25, 60),
        chronic=True,
        severity=Severity.MODERATE,
        lab_pattern=LabPattern(
            alt=(30, 100, 7, 56),
            ast=(25, 80, 10, 40)
        ),
        typical_medications=["entecavir", "tenofovir"]
    ),
    
    # -------------------- NEUROLOGICAL --------------------
    "migraine": ConditionTemplate(
        code="G43.909",
        description="Migraine, unspecified, not intractable",
        category=ConditionCategory.NEUROLOGICAL,
        typical_onset_age=(15, 45),
        chronic=True,
        severity=Severity.MILD,
        typical_medications=["sumatriptan", "topiramate", "propranolol", "amitriptyline"]
    ),
    
    "epilepsy": ConditionTemplate(
        code="G40.909",
        description="Epilepsy, unspecified, not intractable",
        category=ConditionCategory.NEUROLOGICAL,
        typical_onset_age=(5, 50),
        chronic=True,
        severity=Severity.MODERATE,
        typical_medications=["levetiracetam", "lamotrigine", "valproic_acid", "phenytoin", "carbamazepine"]
    ),
    
    "parkinsons": ConditionTemplate(
        code="G20",
        description="Parkinson's disease",
        category=ConditionCategory.NEUROLOGICAL,
        typical_onset_age=(55, 80),
        chronic=True,
        severity=Severity.MODERATE,
        typical_medications=["carbidopa_levodopa", "pramipexole", "rasagiline", "amantadine"],
        complications=["dementia", "falls", "aspiration"]
    ),
    
    "alzheimers": ConditionTemplate(
        code="G30.9",
        description="Alzheimer's disease, unspecified",
        category=ConditionCategory.NEUROLOGICAL,
        typical_onset_age=(65, 90),
        chronic=True,
        severity=Severity.SEVERE,
        typical_medications=["donepezil", "memantine", "rivastigmine"],
        common_comorbidities=["major_depression", "insomnia"]
    ),
    
    "multiple_sclerosis": ConditionTemplate(
        code="G35",
        description="Multiple sclerosis",
        category=ConditionCategory.NEUROLOGICAL,
        typical_onset_age=(20, 50),
        chronic=True,
        severity=Severity.MODERATE,
        typical_medications=["interferon_beta", "glatiramer", "dimethyl_fumarate", "ocrelizumab"]
    ),
    
    "diabetic_neuropathy": ConditionTemplate(
        code="E11.42",
        description="Type 2 diabetes mellitus with diabetic polyneuropathy",
        category=ConditionCategory.NEUROLOGICAL,
        typical_onset_age=(50, 75),
        chronic=True,
        severity=Severity.MILD,
        typical_medications=["gabapentin", "pregabalin", "duloxetine"],
        common_comorbidities=["type2_diabetes"]
    ),
    
    # -------------------- HEMATOLOGIC --------------------
    "anemia_iron_deficiency": ConditionTemplate(
        code="D50.9",
        description="Iron deficiency anemia, unspecified",
        category=ConditionCategory.HEMATOLOGIC,
        typical_onset_age=(20, 70),
        chronic=False,
        typical_duration_years=1,
        severity=Severity.MILD,
        lab_pattern=LabPattern(
            hemoglobin=(8.0, 11.5, 12.0, 17.5),
            hematocrit=(25, 35, 36, 50)
        ),
        typical_medications=["ferrous_sulfate", "iron_infusion"]
    ),
    
    "anemia_ckd": ConditionTemplate(
        code="D63.1",
        description="Anemia in chronic kidney disease",
        category=ConditionCategory.HEMATOLOGIC,
        typical_onset_age=(55, 80),
        chronic=True,
        severity=Severity.MODERATE,
        lab_pattern=LabPattern(
            hemoglobin=(8.5, 11.0, 12.0, 17.5),
            hematocrit=(26, 33, 36, 50)
        ),
        typical_medications=["epoetin_alfa", "darbepoetin", "ferrous_sulfate"],
        common_comorbidities=["ckd_stage4", "ckd_stage5"]
    ),
    
    "dvt_history": ConditionTemplate(
        code="Z86.718",
        description="Personal history of other venous thrombosis and embolism",
        category=ConditionCategory.HEMATOLOGIC,
        typical_onset_age=(35, 75),
        chronic=True,
        severity=Severity.MILD,
        typical_medications=["apixaban", "rivaroxaban", "warfarin"],
        risk_factors=["immobility", "surgery", "cancer", "hypercoagulable_state"]
    ),
    
    "pulmonary_embolism_history": ConditionTemplate(
        code="Z86.711",
        description="Personal history of pulmonary embolism",
        category=ConditionCategory.HEMATOLOGIC,
        typical_onset_age=(40, 75),
        chronic=True,
        severity=Severity.MODERATE,
        typical_medications=["apixaban", "rivaroxaban", "warfarin"]
    ),
}


class ConditionTemplates:
    """Helper class for working with condition templates"""
    
    @staticmethod
    def get_by_category(category: ConditionCategory) -> Dict[str, ConditionTemplate]:
        """Get all conditions in a category"""
        return {k: v for k, v in CONDITION_CATALOG.items() 
                if v.category == category}
    
    @staticmethod
    def get_by_severity(severity: Severity) -> Dict[str, ConditionTemplate]:
        """Get all conditions of a severity level"""
        return {k: v for k, v in CONDITION_CATALOG.items() 
                if v.severity == severity}
    
    @staticmethod
    def get_chronic_conditions() -> Dict[str, ConditionTemplate]:
        """Get all chronic conditions"""
        return {k: v for k, v in CONDITION_CATALOG.items() if v.chronic}
    
    @staticmethod
    def get_comorbidities(condition_key: str) -> List[str]:
        """Get common comorbidities for a condition"""
        if condition_key in CONDITION_CATALOG:
            return CONDITION_CATALOG[condition_key].common_comorbidities
        return []
    
    @staticmethod
    def get_medications(condition_key: str) -> List[str]:
        """Get typical medications for a condition"""
        if condition_key in CONDITION_CATALOG:
            return CONDITION_CATALOG[condition_key].typical_medications
        return []
    
    @staticmethod
    def build_condition_cluster(primary_condition: str, 
                                 max_comorbidities: int = 3) -> List[str]:
        """Build a realistic cluster of conditions starting from a primary"""
        import random
        
        cluster = [primary_condition]
        if primary_condition not in CONDITION_CATALOG:
            return cluster
        
        comorbidities = CONDITION_CATALOG[primary_condition].common_comorbidities
        if comorbidities:
            # Add some comorbidities
            n_comorbidities = min(len(comorbidities), 
                                  random.randint(1, max_comorbidities))
            cluster.extend(random.sample(comorbidities, n_comorbidities))
        
        return cluster
