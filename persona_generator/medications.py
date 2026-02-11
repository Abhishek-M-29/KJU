"""
Medication Templates and Catalog
Defines realistic medication data with dosages and frequencies
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from enum import Enum


class MedicationClass(Enum):
    ANTIHYPERTENSIVE = "antihypertensive"
    ANTIDIABETIC = "antidiabetic"
    STATIN = "statin"
    ANTICOAGULANT = "anticoagulant"
    ANTIPLATELET = "antiplatelet"
    DIURETIC = "diuretic"
    BETA_BLOCKER = "beta_blocker"
    ACE_INHIBITOR = "ace_inhibitor"
    ARB = "arb"
    CALCIUM_CHANNEL_BLOCKER = "calcium_channel_blocker"
    BRONCHODILATOR = "bronchodilator"
    INHALED_STEROID = "inhaled_steroid"
    ANTIDEPRESSANT = "antidepressant"
    ANXIOLYTIC = "anxiolytic"
    ANTIPSYCHOTIC = "antipsychotic"
    MOOD_STABILIZER = "mood_stabilizer"
    PAIN_RELIEVER = "pain_reliever"
    OPIOID = "opioid"
    ANTIBIOTIC = "antibiotic"
    ANTIVIRAL = "antiviral"
    PPI = "ppi"
    H2_BLOCKER = "h2_blocker"
    THYROID = "thyroid"
    IMMUNOSUPPRESSANT = "immunosuppressant"
    BIOLOGIC = "biologic"
    ANTICONVULSANT = "anticonvulsant"
    INSULIN = "insulin"
    SUPPLEMENT = "supplement"
    OTHER = "other"


@dataclass
class MedicationTemplate:
    """Template for a medication"""
    code: str  # RxNorm code
    generic_name: str
    brand_names: List[str]
    medication_class: MedicationClass
    typical_doses: List[str]  # e.g., ["5 mg", "10 mg", "20 mg"]
    typical_frequencies: List[str]  # e.g., ["once daily", "twice daily"]
    route: str = "oral"  # oral, injection, inhalation, topical, etc.
    common_indications: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    monitoring_required: List[str] = field(default_factory=list)
    base_cost_monthly: float = 10.0


# ============================================================
# COMPREHENSIVE MEDICATION CATALOG
# ============================================================

MEDICATION_CATALOG = {
    # -------------------- CARDIOVASCULAR - ANTIHYPERTENSIVES --------------------
    "lisinopril": MedicationTemplate(
        code="314077",
        generic_name="Lisinopril",
        brand_names=["Prinivil", "Zestril"],
        medication_class=MedicationClass.ACE_INHIBITOR,
        typical_doses=["5 mg", "10 mg", "20 mg", "40 mg"],
        typical_frequencies=["once daily"],
        common_indications=["essential_hypertension", "heart_failure_systolic", "diabetic_nephropathy"],
        contraindications=["pregnancy", "angioedema_history", "bilateral_renal_artery_stenosis"],
        monitoring_required=["potassium", "creatinine"],
        base_cost_monthly=5.0
    ),
    
    "losartan": MedicationTemplate(
        code="203160",
        generic_name="Losartan",
        brand_names=["Cozaar"],
        medication_class=MedicationClass.ARB,
        typical_doses=["25 mg", "50 mg", "100 mg"],
        typical_frequencies=["once daily"],
        common_indications=["essential_hypertension", "diabetic_nephropathy", "heart_failure_preserved"],
        contraindications=["pregnancy"],
        monitoring_required=["potassium", "creatinine"],
        base_cost_monthly=8.0
    ),
    
    "valsartan": MedicationTemplate(
        code="69749",
        generic_name="Valsartan",
        brand_names=["Diovan"],
        medication_class=MedicationClass.ARB,
        typical_doses=["80 mg", "160 mg", "320 mg"],
        typical_frequencies=["once daily"],
        common_indications=["essential_hypertension", "heart_failure_systolic"],
        base_cost_monthly=15.0
    ),
    
    "amlodipine": MedicationTemplate(
        code="329528",
        generic_name="Amlodipine",
        brand_names=["Norvasc"],
        medication_class=MedicationClass.CALCIUM_CHANNEL_BLOCKER,
        typical_doses=["2.5 mg", "5 mg", "10 mg"],
        typical_frequencies=["once daily"],
        common_indications=["essential_hypertension", "coronary_artery_disease"],
        base_cost_monthly=5.0
    ),
    
    "diltiazem": MedicationTemplate(
        code="3443",
        generic_name="Diltiazem",
        brand_names=["Cardizem", "Tiazac"],
        medication_class=MedicationClass.CALCIUM_CHANNEL_BLOCKER,
        typical_doses=["120 mg", "180 mg", "240 mg", "360 mg"],
        typical_frequencies=["once daily", "twice daily"],
        common_indications=["essential_hypertension", "atrial_fibrillation", "coronary_artery_disease"],
        base_cost_monthly=20.0
    ),
    
    "metoprolol": MedicationTemplate(
        code="6918",
        generic_name="Metoprolol Succinate",
        brand_names=["Toprol-XL", "Lopressor"],
        medication_class=MedicationClass.BETA_BLOCKER,
        typical_doses=["25 mg", "50 mg", "100 mg", "200 mg"],
        typical_frequencies=["once daily", "twice daily"],
        common_indications=["essential_hypertension", "heart_failure_systolic", "atrial_fibrillation", "prior_mi"],
        contraindications=["severe_bradycardia", "heart_block", "decompensated_heart_failure"],
        base_cost_monthly=8.0
    ),
    
    "carvedilol": MedicationTemplate(
        code="20352",
        generic_name="Carvedilol",
        brand_names=["Coreg"],
        medication_class=MedicationClass.BETA_BLOCKER,
        typical_doses=["3.125 mg", "6.25 mg", "12.5 mg", "25 mg"],
        typical_frequencies=["twice daily"],
        common_indications=["heart_failure_systolic", "essential_hypertension", "prior_mi"],
        base_cost_monthly=10.0
    ),
    
    "atenolol": MedicationTemplate(
        code="1202",
        generic_name="Atenolol",
        brand_names=["Tenormin"],
        medication_class=MedicationClass.BETA_BLOCKER,
        typical_doses=["25 mg", "50 mg", "100 mg"],
        typical_frequencies=["once daily"],
        common_indications=["essential_hypertension", "coronary_artery_disease"],
        base_cost_monthly=5.0
    ),
    
    "propranolol": MedicationTemplate(
        code="8787",
        generic_name="Propranolol",
        brand_names=["Inderal"],
        medication_class=MedicationClass.BETA_BLOCKER,
        typical_doses=["10 mg", "20 mg", "40 mg", "80 mg"],
        typical_frequencies=["twice daily", "three times daily"],
        common_indications=["essential_hypertension", "migraine", "tremor", "anxiety"],
        base_cost_monthly=8.0
    ),
    
    "hydrochlorothiazide": MedicationTemplate(
        code="5487",
        generic_name="Hydrochlorothiazide",
        brand_names=["Microzide"],
        medication_class=MedicationClass.DIURETIC,
        typical_doses=["12.5 mg", "25 mg", "50 mg"],
        typical_frequencies=["once daily"],
        common_indications=["essential_hypertension", "edema"],
        monitoring_required=["potassium", "sodium", "creatinine"],
        base_cost_monthly=4.0
    ),
    
    "furosemide": MedicationTemplate(
        code="4603",
        generic_name="Furosemide",
        brand_names=["Lasix"],
        medication_class=MedicationClass.DIURETIC,
        typical_doses=["20 mg", "40 mg", "80 mg"],
        typical_frequencies=["once daily", "twice daily"],
        common_indications=["heart_failure_systolic", "edema", "ckd_stage4"],
        monitoring_required=["potassium", "creatinine", "weight"],
        base_cost_monthly=5.0
    ),
    
    "spironolactone": MedicationTemplate(
        code="9997",
        generic_name="Spironolactone",
        brand_names=["Aldactone"],
        medication_class=MedicationClass.DIURETIC,
        typical_doses=["12.5 mg", "25 mg", "50 mg", "100 mg"],
        typical_frequencies=["once daily"],
        common_indications=["heart_failure_systolic", "cirrhosis", "essential_hypertension"],
        monitoring_required=["potassium"],
        base_cost_monthly=10.0
    ),
    
    "sacubitril_valsartan": MedicationTemplate(
        code="1656340",
        generic_name="Sacubitril/Valsartan",
        brand_names=["Entresto"],
        medication_class=MedicationClass.ARB,
        typical_doses=["24/26 mg", "49/51 mg", "97/103 mg"],
        typical_frequencies=["twice daily"],
        common_indications=["heart_failure_systolic"],
        contraindications=["ace_inhibitor_within_36h", "pregnancy"],
        base_cost_monthly=500.0
    ),
    
    # -------------------- ANTICOAGULANTS / ANTIPLATELETS --------------------
    "aspirin": MedicationTemplate(
        code="1191",
        generic_name="Aspirin",
        brand_names=["Bayer", "Ecotrin"],
        medication_class=MedicationClass.ANTIPLATELET,
        typical_doses=["81 mg", "325 mg"],
        typical_frequencies=["once daily"],
        common_indications=["coronary_artery_disease", "prior_mi", "stroke_ischemic"],
        contraindications=["active_bleeding", "aspirin_allergy"],
        base_cost_monthly=3.0
    ),
    
    "clopidogrel": MedicationTemplate(
        code="32968",
        generic_name="Clopidogrel",
        brand_names=["Plavix"],
        medication_class=MedicationClass.ANTIPLATELET,
        typical_doses=["75 mg"],
        typical_frequencies=["once daily"],
        common_indications=["coronary_artery_disease", "prior_mi", "stroke_ischemic", "peripheral_vascular_disease"],
        base_cost_monthly=15.0
    ),
    
    "warfarin": MedicationTemplate(
        code="11289",
        generic_name="Warfarin",
        brand_names=["Coumadin", "Jantoven"],
        medication_class=MedicationClass.ANTICOAGULANT,
        typical_doses=["2 mg", "2.5 mg", "5 mg", "7.5 mg", "10 mg"],
        typical_frequencies=["once daily"],
        common_indications=["atrial_fibrillation", "dvt_history", "pulmonary_embolism_history"],
        monitoring_required=["INR"],
        contraindications=["active_bleeding", "pregnancy"],
        base_cost_monthly=8.0
    ),
    
    "apixaban": MedicationTemplate(
        code="1364430",
        generic_name="Apixaban",
        brand_names=["Eliquis"],
        medication_class=MedicationClass.ANTICOAGULANT,
        typical_doses=["2.5 mg", "5 mg"],
        typical_frequencies=["twice daily"],
        common_indications=["atrial_fibrillation", "dvt_history", "pulmonary_embolism_history"],
        contraindications=["active_bleeding"],
        base_cost_monthly=450.0
    ),
    
    "rivaroxaban": MedicationTemplate(
        code="1114195",
        generic_name="Rivaroxaban",
        brand_names=["Xarelto"],
        medication_class=MedicationClass.ANTICOAGULANT,
        typical_doses=["10 mg", "15 mg", "20 mg"],
        typical_frequencies=["once daily"],
        common_indications=["atrial_fibrillation", "dvt_history", "pulmonary_embolism_history"],
        base_cost_monthly=450.0
    ),
    
    "digoxin": MedicationTemplate(
        code="3407",
        generic_name="Digoxin",
        brand_names=["Lanoxin"],
        medication_class=MedicationClass.OTHER,
        typical_doses=["0.125 mg", "0.25 mg"],
        typical_frequencies=["once daily"],
        common_indications=["atrial_fibrillation", "heart_failure_systolic"],
        monitoring_required=["digoxin_level", "potassium", "creatinine"],
        base_cost_monthly=10.0
    ),
    
    "amiodarone": MedicationTemplate(
        code="703",
        generic_name="Amiodarone",
        brand_names=["Pacerone", "Cordarone"],
        medication_class=MedicationClass.OTHER,
        typical_doses=["100 mg", "200 mg", "400 mg"],
        typical_frequencies=["once daily"],
        common_indications=["atrial_fibrillation", "ventricular_arrhythmias"],
        monitoring_required=["thyroid", "liver_function", "pulmonary_function"],
        base_cost_monthly=30.0
    ),
    
    # -------------------- LIPID LOWERING --------------------
    "atorvastatin": MedicationTemplate(
        code="83367",
        generic_name="Atorvastatin",
        brand_names=["Lipitor"],
        medication_class=MedicationClass.STATIN,
        typical_doses=["10 mg", "20 mg", "40 mg", "80 mg"],
        typical_frequencies=["once daily"],
        common_indications=["hyperlipidemia", "coronary_artery_disease", "prior_mi", "type2_diabetes"],
        monitoring_required=["lipid_panel", "liver_function"],
        base_cost_monthly=8.0
    ),
    
    "rosuvastatin": MedicationTemplate(
        code="301542",
        generic_name="Rosuvastatin",
        brand_names=["Crestor"],
        medication_class=MedicationClass.STATIN,
        typical_doses=["5 mg", "10 mg", "20 mg", "40 mg"],
        typical_frequencies=["once daily"],
        common_indications=["hyperlipidemia", "coronary_artery_disease"],
        base_cost_monthly=12.0
    ),
    
    "simvastatin": MedicationTemplate(
        code="36567",
        generic_name="Simvastatin",
        brand_names=["Zocor"],
        medication_class=MedicationClass.STATIN,
        typical_doses=["10 mg", "20 mg", "40 mg"],
        typical_frequencies=["once daily at bedtime"],
        common_indications=["hyperlipidemia"],
        base_cost_monthly=5.0
    ),
    
    "ezetimibe": MedicationTemplate(
        code="341248",
        generic_name="Ezetimibe",
        brand_names=["Zetia"],
        medication_class=MedicationClass.OTHER,
        typical_doses=["10 mg"],
        typical_frequencies=["once daily"],
        common_indications=["hyperlipidemia"],
        base_cost_monthly=180.0
    ),
    
    "fenofibrate": MedicationTemplate(
        code="8703",
        generic_name="Fenofibrate",
        brand_names=["Tricor", "Fenoglide"],
        medication_class=MedicationClass.OTHER,
        typical_doses=["48 mg", "145 mg"],
        typical_frequencies=["once daily"],
        common_indications=["hyperlipidemia", "hypertriglyceridemia"],
        base_cost_monthly=25.0
    ),
    
    # -------------------- DIABETES --------------------
    "metformin": MedicationTemplate(
        code="6809",
        generic_name="Metformin",
        brand_names=["Glucophage"],
        medication_class=MedicationClass.ANTIDIABETIC,
        typical_doses=["500 mg", "850 mg", "1000 mg"],
        typical_frequencies=["twice daily", "three times daily"],
        common_indications=["type2_diabetes", "prediabetes"],
        contraindications=["ckd_stage4", "ckd_stage5", "lactic_acidosis_risk"],
        monitoring_required=["creatinine", "b12"],
        base_cost_monthly=5.0
    ),
    
    "glipizide": MedicationTemplate(
        code="4821",
        generic_name="Glipizide",
        brand_names=["Glucotrol"],
        medication_class=MedicationClass.ANTIDIABETIC,
        typical_doses=["2.5 mg", "5 mg", "10 mg"],
        typical_frequencies=["once daily", "twice daily"],
        common_indications=["type2_diabetes"],
        contraindications=["type1_diabetes", "dka"],
        base_cost_monthly=5.0
    ),
    
    "glyburide": MedicationTemplate(
        code="4815",
        generic_name="Glyburide",
        brand_names=["Diabeta", "Micronase"],
        medication_class=MedicationClass.ANTIDIABETIC,
        typical_doses=["1.25 mg", "2.5 mg", "5 mg"],
        typical_frequencies=["once daily", "twice daily"],
        common_indications=["type2_diabetes"],
        base_cost_monthly=5.0
    ),
    
    "sitagliptin": MedicationTemplate(
        code="593411",
        generic_name="Sitagliptin",
        brand_names=["Januvia"],
        medication_class=MedicationClass.ANTIDIABETIC,
        typical_doses=["25 mg", "50 mg", "100 mg"],
        typical_frequencies=["once daily"],
        common_indications=["type2_diabetes"],
        base_cost_monthly=450.0
    ),
    
    "empagliflozin": MedicationTemplate(
        code="1545653",
        generic_name="Empagliflozin",
        brand_names=["Jardiance"],
        medication_class=MedicationClass.ANTIDIABETIC,
        typical_doses=["10 mg", "25 mg"],
        typical_frequencies=["once daily"],
        common_indications=["type2_diabetes", "heart_failure_systolic", "ckd_stage3"],
        base_cost_monthly=500.0
    ),
    
    "dapagliflozin": MedicationTemplate(
        code="1488564",
        generic_name="Dapagliflozin",
        brand_names=["Farxiga"],
        medication_class=MedicationClass.ANTIDIABETIC,
        typical_doses=["5 mg", "10 mg"],
        typical_frequencies=["once daily"],
        common_indications=["type2_diabetes", "heart_failure_systolic", "ckd_stage3"],
        base_cost_monthly=500.0
    ),
    
    "liraglutide": MedicationTemplate(
        code="897122",
        generic_name="Liraglutide",
        brand_names=["Victoza"],
        medication_class=MedicationClass.ANTIDIABETIC,
        typical_doses=["0.6 mg", "1.2 mg", "1.8 mg"],
        typical_frequencies=["once daily"],
        route="subcutaneous injection",
        common_indications=["type2_diabetes", "obesity"],
        base_cost_monthly=900.0
    ),
    
    "semaglutide": MedicationTemplate(
        code="1991302",
        generic_name="Semaglutide",
        brand_names=["Ozempic", "Wegovy", "Rybelsus"],
        medication_class=MedicationClass.ANTIDIABETIC,
        typical_doses=["0.25 mg", "0.5 mg", "1 mg", "2 mg"],
        typical_frequencies=["once weekly"],
        route="subcutaneous injection",
        common_indications=["type2_diabetes", "obesity"],
        base_cost_monthly=900.0
    ),
    
    "insulin_glargine": MedicationTemplate(
        code="274783",
        generic_name="Insulin Glargine",
        brand_names=["Lantus", "Basaglar", "Toujeo"],
        medication_class=MedicationClass.INSULIN,
        typical_doses=["10 units", "20 units", "30 units", "40 units", "50 units"],
        typical_frequencies=["once daily at bedtime"],
        route="subcutaneous injection",
        common_indications=["type1_diabetes", "type2_diabetes_with_complications"],
        monitoring_required=["blood_glucose"],
        base_cost_monthly=350.0
    ),
    
    "insulin_lispro": MedicationTemplate(
        code="86009",
        generic_name="Insulin Lispro",
        brand_names=["Humalog", "Admelog"],
        medication_class=MedicationClass.INSULIN,
        typical_doses=["sliding scale", "fixed dose with meals"],
        typical_frequencies=["with meals"],
        route="subcutaneous injection",
        common_indications=["type1_diabetes", "type2_diabetes_with_complications"],
        base_cost_monthly=350.0
    ),
    
    "insulin_aspart": MedicationTemplate(
        code="86012",
        generic_name="Insulin Aspart",
        brand_names=["NovoLog", "Fiasp"],
        medication_class=MedicationClass.INSULIN,
        typical_doses=["sliding scale", "fixed dose with meals"],
        typical_frequencies=["with meals"],
        route="subcutaneous injection",
        common_indications=["type1_diabetes", "type2_diabetes_with_complications"],
        base_cost_monthly=350.0
    ),
    
    "pioglitazone": MedicationTemplate(
        code="33738",
        generic_name="Pioglitazone",
        brand_names=["Actos"],
        medication_class=MedicationClass.ANTIDIABETIC,
        typical_doses=["15 mg", "30 mg", "45 mg"],
        typical_frequencies=["once daily"],
        common_indications=["type2_diabetes", "nash"],
        contraindications=["heart_failure"],
        base_cost_monthly=15.0
    ),
    
    # -------------------- RESPIRATORY --------------------
    "albuterol": MedicationTemplate(
        code="435",
        generic_name="Albuterol",
        brand_names=["ProAir", "Ventolin", "Proventil"],
        medication_class=MedicationClass.BRONCHODILATOR,
        typical_doses=["90 mcg/actuation", "2 puffs"],
        typical_frequencies=["every 4-6 hours as needed"],
        route="inhalation",
        common_indications=["asthma", "copd"],
        base_cost_monthly=50.0
    ),
    
    "tiotropium": MedicationTemplate(
        code="274535",
        generic_name="Tiotropium",
        brand_names=["Spiriva"],
        medication_class=MedicationClass.BRONCHODILATOR,
        typical_doses=["18 mcg", "2.5 mcg"],
        typical_frequencies=["once daily"],
        route="inhalation",
        common_indications=["copd", "asthma_moderate"],
        base_cost_monthly=450.0
    ),
    
    "fluticasone": MedicationTemplate(
        code="41126",
        generic_name="Fluticasone",
        brand_names=["Flovent", "Arnuity"],
        medication_class=MedicationClass.INHALED_STEROID,
        typical_doses=["44 mcg", "110 mcg", "220 mcg"],
        typical_frequencies=["twice daily"],
        route="inhalation",
        common_indications=["asthma"],
        base_cost_monthly=200.0
    ),
    
    "fluticasone_salmeterol": MedicationTemplate(
        code="896188",
        generic_name="Fluticasone/Salmeterol",
        brand_names=["Advair", "AirDuo"],
        medication_class=MedicationClass.INHALED_STEROID,
        typical_doses=["100/50", "250/50", "500/50"],
        typical_frequencies=["twice daily"],
        route="inhalation",
        common_indications=["asthma_moderate", "copd"],
        base_cost_monthly=350.0
    ),
    
    "budesonide_formoterol": MedicationTemplate(
        code="896197",
        generic_name="Budesonide/Formoterol",
        brand_names=["Symbicort"],
        medication_class=MedicationClass.INHALED_STEROID,
        typical_doses=["80/4.5", "160/4.5"],
        typical_frequencies=["twice daily"],
        route="inhalation",
        common_indications=["asthma_moderate", "copd"],
        base_cost_monthly=350.0
    ),
    
    "montelukast": MedicationTemplate(
        code="88249",
        generic_name="Montelukast",
        brand_names=["Singulair"],
        medication_class=MedicationClass.OTHER,
        typical_doses=["10 mg"],
        typical_frequencies=["once daily at bedtime"],
        common_indications=["asthma", "allergic_rhinitis"],
        base_cost_monthly=15.0
    ),
    
    "prednisone": MedicationTemplate(
        code="8640",
        generic_name="Prednisone",
        brand_names=["Deltasone", "Rayos"],
        medication_class=MedicationClass.OTHER,
        typical_doses=["5 mg", "10 mg", "20 mg", "40 mg", "60 mg"],
        typical_frequencies=["once daily", "taper schedule"],
        common_indications=["copd_severe", "asthma", "rheumatoid_arthritis", "ibd_crohns"],
        monitoring_required=["blood_glucose", "bone_density"],
        base_cost_monthly=10.0
    ),
    
    # -------------------- PSYCHIATRIC --------------------
    "sertraline": MedicationTemplate(
        code="36437",
        generic_name="Sertraline",
        brand_names=["Zoloft"],
        medication_class=MedicationClass.ANTIDEPRESSANT,
        typical_doses=["25 mg", "50 mg", "100 mg", "150 mg", "200 mg"],
        typical_frequencies=["once daily"],
        common_indications=["major_depression", "generalized_anxiety", "ptsd"],
        base_cost_monthly=8.0
    ),
    
    "escitalopram": MedicationTemplate(
        code="321988",
        generic_name="Escitalopram",
        brand_names=["Lexapro"],
        medication_class=MedicationClass.ANTIDEPRESSANT,
        typical_doses=["5 mg", "10 mg", "20 mg"],
        typical_frequencies=["once daily"],
        common_indications=["major_depression", "generalized_anxiety"],
        base_cost_monthly=10.0
    ),
    
    "fluoxetine": MedicationTemplate(
        code="4493",
        generic_name="Fluoxetine",
        brand_names=["Prozac"],
        medication_class=MedicationClass.ANTIDEPRESSANT,
        typical_doses=["10 mg", "20 mg", "40 mg", "60 mg"],
        typical_frequencies=["once daily"],
        common_indications=["major_depression"],
        base_cost_monthly=5.0
    ),
    
    "bupropion": MedicationTemplate(
        code="42347",
        generic_name="Bupropion",
        brand_names=["Wellbutrin"],
        medication_class=MedicationClass.ANTIDEPRESSANT,
        typical_doses=["150 mg", "300 mg"],
        typical_frequencies=["once daily", "twice daily"],
        common_indications=["major_depression", "smoking_cessation"],
        contraindications=["seizure_disorder", "eating_disorder"],
        base_cost_monthly=20.0
    ),
    
    "venlafaxine": MedicationTemplate(
        code="39786",
        generic_name="Venlafaxine",
        brand_names=["Effexor"],
        medication_class=MedicationClass.ANTIDEPRESSANT,
        typical_doses=["37.5 mg", "75 mg", "150 mg", "225 mg"],
        typical_frequencies=["once daily"],
        common_indications=["major_depression_recurrent", "generalized_anxiety", "ptsd"],
        base_cost_monthly=15.0
    ),
    
    "duloxetine": MedicationTemplate(
        code="72625",
        generic_name="Duloxetine",
        brand_names=["Cymbalta"],
        medication_class=MedicationClass.ANTIDEPRESSANT,
        typical_doses=["20 mg", "30 mg", "60 mg"],
        typical_frequencies=["once daily"],
        common_indications=["major_depression", "diabetic_neuropathy", "fibromyalgia"],
        base_cost_monthly=25.0
    ),
    
    "mirtazapine": MedicationTemplate(
        code="15996",
        generic_name="Mirtazapine",
        brand_names=["Remeron"],
        medication_class=MedicationClass.ANTIDEPRESSANT,
        typical_doses=["7.5 mg", "15 mg", "30 mg", "45 mg"],
        typical_frequencies=["once daily at bedtime"],
        common_indications=["major_depression_recurrent", "insomnia"],
        base_cost_monthly=10.0
    ),
    
    "trazodone": MedicationTemplate(
        code="10737",
        generic_name="Trazodone",
        brand_names=["Desyrel", "Oleptro"],
        medication_class=MedicationClass.ANTIDEPRESSANT,
        typical_doses=["25 mg", "50 mg", "100 mg", "150 mg"],
        typical_frequencies=["once daily at bedtime"],
        common_indications=["insomnia", "major_depression"],
        base_cost_monthly=5.0
    ),
    
    "buspirone": MedicationTemplate(
        code="1827",
        generic_name="Buspirone",
        brand_names=["Buspar"],
        medication_class=MedicationClass.ANXIOLYTIC,
        typical_doses=["5 mg", "7.5 mg", "10 mg", "15 mg"],
        typical_frequencies=["twice daily", "three times daily"],
        common_indications=["generalized_anxiety"],
        base_cost_monthly=12.0
    ),
    
    "hydroxyzine": MedicationTemplate(
        code="5553",
        generic_name="Hydroxyzine",
        brand_names=["Vistaril", "Atarax"],
        medication_class=MedicationClass.ANXIOLYTIC,
        typical_doses=["10 mg", "25 mg", "50 mg"],
        typical_frequencies=["three times daily", "as needed"],
        common_indications=["generalized_anxiety", "insomnia"],
        base_cost_monthly=8.0
    ),
    
    "lithium": MedicationTemplate(
        code="6448",
        generic_name="Lithium",
        brand_names=["Lithobid", "Eskalith"],
        medication_class=MedicationClass.MOOD_STABILIZER,
        typical_doses=["300 mg", "450 mg", "600 mg"],
        typical_frequencies=["twice daily", "three times daily"],
        common_indications=["bipolar_disorder"],
        monitoring_required=["lithium_level", "thyroid", "creatinine"],
        base_cost_monthly=15.0
    ),
    
    "valproic_acid": MedicationTemplate(
        code="11118",
        generic_name="Valproic Acid",
        brand_names=["Depakote", "Depakene"],
        medication_class=MedicationClass.MOOD_STABILIZER,
        typical_doses=["250 mg", "500 mg", "750 mg"],
        typical_frequencies=["twice daily"],
        common_indications=["bipolar_disorder", "epilepsy"],
        monitoring_required=["valproic_acid_level", "liver_function", "cbc"],
        base_cost_monthly=20.0
    ),
    
    "lamotrigine": MedicationTemplate(
        code="28439",
        generic_name="Lamotrigine",
        brand_names=["Lamictal"],
        medication_class=MedicationClass.MOOD_STABILIZER,
        typical_doses=["25 mg", "50 mg", "100 mg", "200 mg"],
        typical_frequencies=["once daily", "twice daily"],
        common_indications=["bipolar_disorder", "epilepsy"],
        base_cost_monthly=15.0
    ),
    
    "quetiapine": MedicationTemplate(
        code="51272",
        generic_name="Quetiapine",
        brand_names=["Seroquel"],
        medication_class=MedicationClass.ANTIPSYCHOTIC,
        typical_doses=["25 mg", "50 mg", "100 mg", "200 mg", "300 mg", "400 mg"],
        typical_frequencies=["once daily at bedtime", "twice daily"],
        common_indications=["bipolar_disorder", "schizophrenia", "major_depression"],
        monitoring_required=["metabolic_panel", "lipids", "weight"],
        base_cost_monthly=20.0
    ),
    
    "risperidone": MedicationTemplate(
        code="35636",
        generic_name="Risperidone",
        brand_names=["Risperdal"],
        medication_class=MedicationClass.ANTIPSYCHOTIC,
        typical_doses=["0.5 mg", "1 mg", "2 mg", "3 mg", "4 mg"],
        typical_frequencies=["once daily", "twice daily"],
        common_indications=["schizophrenia", "bipolar_disorder"],
        monitoring_required=["metabolic_panel", "prolactin"],
        base_cost_monthly=15.0
    ),
    
    "olanzapine": MedicationTemplate(
        code="61381",
        generic_name="Olanzapine",
        brand_names=["Zyprexa"],
        medication_class=MedicationClass.ANTIPSYCHOTIC,
        typical_doses=["2.5 mg", "5 mg", "10 mg", "15 mg", "20 mg"],
        typical_frequencies=["once daily"],
        common_indications=["schizophrenia", "bipolar_disorder"],
        monitoring_required=["metabolic_panel", "lipids", "weight"],
        base_cost_monthly=25.0
    ),
    
    "aripiprazole": MedicationTemplate(
        code="89013",
        generic_name="Aripiprazole",
        brand_names=["Abilify"],
        medication_class=MedicationClass.ANTIPSYCHOTIC,
        typical_doses=["2 mg", "5 mg", "10 mg", "15 mg", "20 mg", "30 mg"],
        typical_frequencies=["once daily"],
        common_indications=["schizophrenia", "bipolar_disorder", "major_depression"],
        base_cost_monthly=400.0
    ),
    
    "prazosin": MedicationTemplate(
        code="8629",
        generic_name="Prazosin",
        brand_names=["Minipress"],
        medication_class=MedicationClass.ANTIHYPERTENSIVE,
        typical_doses=["1 mg", "2 mg", "5 mg"],
        typical_frequencies=["at bedtime", "twice daily"],
        common_indications=["ptsd", "nightmares", "essential_hypertension"],
        base_cost_monthly=15.0
    ),
    
    # -------------------- PAIN --------------------
    "acetaminophen": MedicationTemplate(
        code="161",
        generic_name="Acetaminophen",
        brand_names=["Tylenol"],
        medication_class=MedicationClass.PAIN_RELIEVER,
        typical_doses=["325 mg", "500 mg", "650 mg", "1000 mg"],
        typical_frequencies=["every 4-6 hours as needed"],
        common_indications=["osteoarthritis", "pain", "fever"],
        base_cost_monthly=5.0
    ),
    
    "ibuprofen": MedicationTemplate(
        code="5640",
        generic_name="Ibuprofen",
        brand_names=["Advil", "Motrin"],
        medication_class=MedicationClass.PAIN_RELIEVER,
        typical_doses=["200 mg", "400 mg", "600 mg", "800 mg"],
        typical_frequencies=["every 6-8 hours as needed"],
        common_indications=["osteoarthritis", "pain", "inflammation"],
        contraindications=["ckd_stage4", "gi_bleeding", "heart_failure"],
        base_cost_monthly=5.0
    ),
    
    "naproxen": MedicationTemplate(
        code="7258",
        generic_name="Naproxen",
        brand_names=["Aleve", "Naprosyn"],
        medication_class=MedicationClass.PAIN_RELIEVER,
        typical_doses=["220 mg", "250 mg", "375 mg", "500 mg"],
        typical_frequencies=["twice daily"],
        common_indications=["osteoarthritis", "rheumatoid_arthritis"],
        base_cost_monthly=8.0
    ),
    
    "meloxicam": MedicationTemplate(
        code="41493",
        generic_name="Meloxicam",
        brand_names=["Mobic"],
        medication_class=MedicationClass.PAIN_RELIEVER,
        typical_doses=["7.5 mg", "15 mg"],
        typical_frequencies=["once daily"],
        common_indications=["osteoarthritis", "rheumatoid_arthritis"],
        base_cost_monthly=8.0
    ),
    
    "gabapentin": MedicationTemplate(
        code="25480",
        generic_name="Gabapentin",
        brand_names=["Neurontin"],
        medication_class=MedicationClass.ANTICONVULSANT,
        typical_doses=["100 mg", "300 mg", "400 mg", "600 mg", "800 mg"],
        typical_frequencies=["three times daily"],
        common_indications=["diabetic_neuropathy", "epilepsy", "chronic_pain"],
        base_cost_monthly=12.0
    ),
    
    "pregabalin": MedicationTemplate(
        code="187832",
        generic_name="Pregabalin",
        brand_names=["Lyrica"],
        medication_class=MedicationClass.ANTICONVULSANT,
        typical_doses=["25 mg", "50 mg", "75 mg", "150 mg", "300 mg"],
        typical_frequencies=["twice daily"],
        common_indications=["diabetic_neuropathy", "fibromyalgia"],
        base_cost_monthly=200.0
    ),
    
    # -------------------- GI --------------------
    "omeprazole": MedicationTemplate(
        code="7646",
        generic_name="Omeprazole",
        brand_names=["Prilosec"],
        medication_class=MedicationClass.PPI,
        typical_doses=["20 mg", "40 mg"],
        typical_frequencies=["once daily before breakfast"],
        common_indications=["gerd", "peptic_ulcer"],
        base_cost_monthly=8.0
    ),
    
    "pantoprazole": MedicationTemplate(
        code="40790",
        generic_name="Pantoprazole",
        brand_names=["Protonix"],
        medication_class=MedicationClass.PPI,
        typical_doses=["20 mg", "40 mg"],
        typical_frequencies=["once daily before breakfast"],
        common_indications=["gerd"],
        base_cost_monthly=10.0
    ),
    
    "famotidine": MedicationTemplate(
        code="4278",
        generic_name="Famotidine",
        brand_names=["Pepcid"],
        medication_class=MedicationClass.H2_BLOCKER,
        typical_doses=["10 mg", "20 mg", "40 mg"],
        typical_frequencies=["once daily", "twice daily"],
        common_indications=["gerd"],
        base_cost_monthly=8.0
    ),
    
    "lactulose": MedicationTemplate(
        code="6143",
        generic_name="Lactulose",
        brand_names=["Enulose", "Kristalose"],
        medication_class=MedicationClass.OTHER,
        typical_doses=["15 mL", "30 mL"],
        typical_frequencies=["twice daily", "three times daily"],
        common_indications=["cirrhosis", "hepatic_encephalopathy"],
        base_cost_monthly=30.0
    ),
    
    "rifaximin": MedicationTemplate(
        code="190376",
        generic_name="Rifaximin",
        brand_names=["Xifaxan"],
        medication_class=MedicationClass.ANTIBIOTIC,
        typical_doses=["550 mg"],
        typical_frequencies=["twice daily"],
        common_indications=["cirrhosis", "hepatic_encephalopathy"],
        base_cost_monthly=1500.0
    ),
    
    # -------------------- THYROID --------------------
    "levothyroxine": MedicationTemplate(
        code="10582",
        generic_name="Levothyroxine",
        brand_names=["Synthroid", "Levoxyl"],
        medication_class=MedicationClass.THYROID,
        typical_doses=["25 mcg", "50 mcg", "75 mcg", "100 mcg", "125 mcg", "150 mcg"],
        typical_frequencies=["once daily on empty stomach"],
        common_indications=["hypothyroidism"],
        monitoring_required=["tsh"],
        base_cost_monthly=10.0
    ),
    
    "methimazole": MedicationTemplate(
        code="6835",
        generic_name="Methimazole",
        brand_names=["Tapazole"],
        medication_class=MedicationClass.THYROID,
        typical_doses=["5 mg", "10 mg", "15 mg", "20 mg"],
        typical_frequencies=["once daily", "three times daily"],
        common_indications=["hyperthyroidism"],
        monitoring_required=["tsh", "free_t4", "cbc"],
        base_cost_monthly=15.0
    ),
    
    # -------------------- RHEUMATOLOGY / IMMUNOLOGY --------------------
    "methotrexate": MedicationTemplate(
        code="6851",
        generic_name="Methotrexate",
        brand_names=["Trexall", "Rheumatrex"],
        medication_class=MedicationClass.IMMUNOSUPPRESSANT,
        typical_doses=["7.5 mg", "10 mg", "15 mg", "20 mg", "25 mg"],
        typical_frequencies=["once weekly"],
        common_indications=["rheumatoid_arthritis", "psoriasis"],
        monitoring_required=["cbc", "liver_function", "creatinine"],
        base_cost_monthly=20.0
    ),
    
    "hydroxychloroquine": MedicationTemplate(
        code="5521",
        generic_name="Hydroxychloroquine",
        brand_names=["Plaquenil"],
        medication_class=MedicationClass.IMMUNOSUPPRESSANT,
        typical_doses=["200 mg", "400 mg"],
        typical_frequencies=["once daily", "twice daily"],
        common_indications=["rheumatoid_arthritis", "lupus"],
        monitoring_required=["eye_exam"],
        base_cost_monthly=20.0
    ),
    
    "adalimumab": MedicationTemplate(
        code="327361",
        generic_name="Adalimumab",
        brand_names=["Humira"],
        medication_class=MedicationClass.BIOLOGIC,
        typical_doses=["40 mg"],
        typical_frequencies=["every 2 weeks"],
        route="subcutaneous injection",
        common_indications=["rheumatoid_arthritis", "ibd_crohns", "psoriasis"],
        base_cost_monthly=5000.0
    ),
    
    "etanercept": MedicationTemplate(
        code="214555",
        generic_name="Etanercept",
        brand_names=["Enbrel"],
        medication_class=MedicationClass.BIOLOGIC,
        typical_doses=["25 mg", "50 mg"],
        typical_frequencies=["once weekly", "twice weekly"],
        route="subcutaneous injection",
        common_indications=["rheumatoid_arthritis", "psoriasis"],
        base_cost_monthly=5000.0
    ),
    
    "infliximab": MedicationTemplate(
        code="191831",
        generic_name="Infliximab",
        brand_names=["Remicade"],
        medication_class=MedicationClass.BIOLOGIC,
        typical_doses=["3 mg/kg", "5 mg/kg"],
        typical_frequencies=["every 8 weeks"],
        route="intravenous infusion",
        common_indications=["rheumatoid_arthritis", "ibd_crohns", "ibd_uc"],
        base_cost_monthly=4000.0
    ),
    
    "colchicine": MedicationTemplate(
        code="2683",
        generic_name="Colchicine",
        brand_names=["Colcrys"],
        medication_class=MedicationClass.OTHER,
        typical_doses=["0.6 mg"],
        typical_frequencies=["once daily", "twice daily"],
        common_indications=["gout"],
        base_cost_monthly=200.0
    ),
    
    "allopurinol": MedicationTemplate(
        code="519",
        generic_name="Allopurinol",
        brand_names=["Zyloprim"],
        medication_class=MedicationClass.OTHER,
        typical_doses=["100 mg", "200 mg", "300 mg"],
        typical_frequencies=["once daily"],
        common_indications=["gout"],
        monitoring_required=["uric_acid"],
        base_cost_monthly=8.0
    ),
    
    # -------------------- BONE --------------------
    "alendronate": MedicationTemplate(
        code="1115",
        generic_name="Alendronate",
        brand_names=["Fosamax"],
        medication_class=MedicationClass.OTHER,
        typical_doses=["35 mg", "70 mg"],
        typical_frequencies=["once weekly"],
        common_indications=["osteoporosis"],
        base_cost_monthly=15.0
    ),
    
    "calcium_vitamin_d": MedicationTemplate(
        code="216373",
        generic_name="Calcium/Vitamin D",
        brand_names=["Caltrate", "Os-Cal"],
        medication_class=MedicationClass.SUPPLEMENT,
        typical_doses=["600 mg/400 IU", "500 mg/200 IU"],
        typical_frequencies=["once daily", "twice daily"],
        common_indications=["osteoporosis", "vitamin_d_deficiency"],
        base_cost_monthly=10.0
    ),
    
    # -------------------- ANTICONVULSANTS --------------------
    "levetiracetam": MedicationTemplate(
        code="187874",
        generic_name="Levetiracetam",
        brand_names=["Keppra"],
        medication_class=MedicationClass.ANTICONVULSANT,
        typical_doses=["250 mg", "500 mg", "750 mg", "1000 mg"],
        typical_frequencies=["twice daily"],
        common_indications=["epilepsy"],
        base_cost_monthly=20.0
    ),
    
    "phenytoin": MedicationTemplate(
        code="8183",
        generic_name="Phenytoin",
        brand_names=["Dilantin"],
        medication_class=MedicationClass.ANTICONVULSANT,
        typical_doses=["100 mg", "200 mg", "300 mg"],
        typical_frequencies=["once daily", "twice daily"],
        common_indications=["epilepsy"],
        monitoring_required=["phenytoin_level"],
        base_cost_monthly=15.0
    ),
    
    "carbamazepine": MedicationTemplate(
        code="2002",
        generic_name="Carbamazepine",
        brand_names=["Tegretol"],
        medication_class=MedicationClass.ANTICONVULSANT,
        typical_doses=["200 mg", "400 mg"],
        typical_frequencies=["twice daily", "three times daily"],
        common_indications=["epilepsy", "trigeminal_neuralgia"],
        monitoring_required=["cbc", "liver_function", "drug_level"],
        base_cost_monthly=15.0
    ),
    
    # -------------------- NEUROLOGICAL --------------------
    "carbidopa_levodopa": MedicationTemplate(
        code="103890",
        generic_name="Carbidopa/Levodopa",
        brand_names=["Sinemet"],
        medication_class=MedicationClass.OTHER,
        typical_doses=["25/100 mg", "25/250 mg", "50/200 mg"],
        typical_frequencies=["three times daily", "four times daily"],
        common_indications=["parkinsons"],
        base_cost_monthly=30.0
    ),
    
    "donepezil": MedicationTemplate(
        code="135447",
        generic_name="Donepezil",
        brand_names=["Aricept"],
        medication_class=MedicationClass.OTHER,
        typical_doses=["5 mg", "10 mg", "23 mg"],
        typical_frequencies=["once daily at bedtime"],
        common_indications=["alzheimers"],
        base_cost_monthly=15.0
    ),
    
    "memantine": MedicationTemplate(
        code="358802",
        generic_name="Memantine",
        brand_names=["Namenda"],
        medication_class=MedicationClass.OTHER,
        typical_doses=["5 mg", "10 mg"],
        typical_frequencies=["twice daily"],
        common_indications=["alzheimers"],
        base_cost_monthly=200.0
    ),
    
    "sumatriptan": MedicationTemplate(
        code="37418",
        generic_name="Sumatriptan",
        brand_names=["Imitrex"],
        medication_class=MedicationClass.OTHER,
        typical_doses=["25 mg", "50 mg", "100 mg"],
        typical_frequencies=["as needed for migraine"],
        common_indications=["migraine"],
        base_cost_monthly=50.0
    ),
    
    "topiramate": MedicationTemplate(
        code="38404",
        generic_name="Topiramate",
        brand_names=["Topamax"],
        medication_class=MedicationClass.ANTICONVULSANT,
        typical_doses=["25 mg", "50 mg", "100 mg", "200 mg"],
        typical_frequencies=["twice daily"],
        common_indications=["migraine", "epilepsy"],
        base_cost_monthly=15.0
    ),
    
    # -------------------- HIV --------------------
    "bictegravir_emtricitabine_tenofovir": MedicationTemplate(
        code="2047236",
        generic_name="Bictegravir/Emtricitabine/Tenofovir alafenamide",
        brand_names=["Biktarvy"],
        medication_class=MedicationClass.ANTIVIRAL,
        typical_doses=["50/200/25 mg"],
        typical_frequencies=["once daily"],
        common_indications=["hiv_controlled"],
        monitoring_required=["hiv_viral_load", "cd4_count", "creatinine"],
        base_cost_monthly=3000.0
    ),
    
    "dolutegravir": MedicationTemplate(
        code="1433868",
        generic_name="Dolutegravir",
        brand_names=["Tivicay"],
        medication_class=MedicationClass.ANTIVIRAL,
        typical_doses=["50 mg"],
        typical_frequencies=["once daily"],
        common_indications=["hiv_controlled"],
        base_cost_monthly=1500.0
    ),
    
    # -------------------- HEPATITIS --------------------
    "sofosbuvir_velpatasvir": MedicationTemplate(
        code="1721522",
        generic_name="Sofosbuvir/Velpatasvir",
        brand_names=["Epclusa"],
        medication_class=MedicationClass.ANTIVIRAL,
        typical_doses=["400/100 mg"],
        typical_frequencies=["once daily"],
        common_indications=["hepatitis_c_treated"],
        base_cost_monthly=25000.0  # 12 week course
    ),
    
    "entecavir": MedicationTemplate(
        code="321060",
        generic_name="Entecavir",
        brand_names=["Baraclude"],
        medication_class=MedicationClass.ANTIVIRAL,
        typical_doses=["0.5 mg", "1 mg"],
        typical_frequencies=["once daily"],
        common_indications=["hepatitis_b"],
        monitoring_required=["hbv_dna", "liver_function"],
        base_cost_monthly=800.0
    ),
    
    # -------------------- RENAL --------------------
    "sevelamer": MedicationTemplate(
        code="203154",
        generic_name="Sevelamer",
        brand_names=["Renvela", "Renagel"],
        medication_class=MedicationClass.OTHER,
        typical_doses=["800 mg"],
        typical_frequencies=["with meals"],
        common_indications=["ckd_stage4", "ckd_stage5"],
        base_cost_monthly=200.0
    ),
    
    "epoetin_alfa": MedicationTemplate(
        code="3950",
        generic_name="Epoetin Alfa",
        brand_names=["Epogen", "Procrit"],
        medication_class=MedicationClass.OTHER,
        typical_doses=["2000 units", "4000 units", "10000 units"],
        typical_frequencies=["three times weekly", "once weekly"],
        route="subcutaneous injection",
        common_indications=["anemia_ckd"],
        monitoring_required=["hemoglobin", "iron_studies"],
        base_cost_monthly=500.0
    ),
    
    "calcitriol": MedicationTemplate(
        code="1998",
        generic_name="Calcitriol",
        brand_names=["Rocaltrol"],
        medication_class=MedicationClass.SUPPLEMENT,
        typical_doses=["0.25 mcg", "0.5 mcg"],
        typical_frequencies=["once daily"],
        common_indications=["ckd_stage4", "ckd_stage5", "secondary_hyperparathyroidism"],
        monitoring_required=["calcium", "phosphorus", "pth"],
        base_cost_monthly=30.0
    ),
    
    "sodium_bicarbonate": MedicationTemplate(
        code="9548",
        generic_name="Sodium Bicarbonate",
        brand_names=["generic"],
        medication_class=MedicationClass.OTHER,
        typical_doses=["650 mg"],
        typical_frequencies=["three times daily"],
        common_indications=["ckd_stage3", "metabolic_acidosis"],
        base_cost_monthly=10.0
    ),
}


class MedicationTemplates:
    """Helper class for working with medication templates"""
    
    @staticmethod
    def get_by_class(med_class: MedicationClass) -> dict:
        """Get all medications in a class"""
        return {k: v for k, v in MEDICATION_CATALOG.items()
                if v.medication_class == med_class}
    
    @staticmethod
    def get_for_condition(condition_key: str) -> list:
        """Get medications that treat a condition"""
        meds = []
        for key, med in MEDICATION_CATALOG.items():
            if condition_key in med.common_indications:
                meds.append(key)
        return meds
    
    @staticmethod
    def get_random_dose(medication_key: str) -> str:
        """Get a random typical dose for a medication"""
        import random
        if medication_key in MEDICATION_CATALOG:
            return random.choice(MEDICATION_CATALOG[medication_key].typical_doses)
        return "standard dose"
    
    @staticmethod
    def get_random_frequency(medication_key: str) -> str:
        """Get a random typical frequency for a medication"""
        import random
        if medication_key in MEDICATION_CATALOG:
            return random.choice(MEDICATION_CATALOG[medication_key].typical_frequencies)
        return "once daily"
    
    @staticmethod
    def format_medication_description(medication_key: str) -> str:
        """Format a medication description for display"""
        if medication_key in MEDICATION_CATALOG:
            med = MEDICATION_CATALOG[medication_key]
            dose = MedicationTemplates.get_random_dose(medication_key)
            return f"{med.generic_name} {dose}"
        return medication_key
