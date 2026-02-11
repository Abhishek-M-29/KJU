"""
Add comprehensive medical knowledge for cardiovascular disease, diabetes, and sepsis.
This adds detailed symptoms, risk factors, diagnostics, and treatment information.
"""

import json
from pathlib import Path

JSONL_FILE = Path(__file__).parent / "disease-ontology" / "data" / "disease_ontology_compiled.jsonl"

# Comprehensive medical knowledge entries with citations
MEDICAL_KNOWLEDGE = [
    # ============================================
    # CARDIOVASCULAR DISEASES - DETAILED
    # ============================================
    {
        "id": "CUSTOM:CVD:001",
        "name": "Cardiovascular Disease Overview",
        "description": "Cardiovascular disease (CVD) refers to a class of diseases that involve the heart or blood vessels. It includes coronary artery disease, heart failure, arrhythmias, heart valve disease, and peripheral artery disease. CVD is the leading cause of death globally.",
        "synonyms": ["heart disease", "cardiac disease", "CVD"],
        "related_synonyms": ["circulatory system disease"],
        "category": "cardiovascular",
        "pathophysiology": "vascular",
        "child_diseases": [],
        "symptoms": ["chest pain", "shortness of breath", "fatigue", "irregular heartbeat", "dizziness", "swelling in legs", "pain in neck/jaw/throat", "numbness in extremities"],
        "risk_factors": ["high blood pressure", "high cholesterol", "smoking", "diabetes", "obesity", "physical inactivity", "unhealthy diet", "excessive alcohol", "stress", "family history", "age over 65"],
        "diagnostics": ["ECG/EKG", "echocardiogram", "stress test", "cardiac catheterization", "CT scan", "MRI", "blood tests for troponin", "BNP test", "lipid panel", "Holter monitor"],
        "treatments": ["lifestyle changes", "medications (statins, beta-blockers, ACE inhibitors)", "angioplasty", "bypass surgery", "pacemaker", "defibrillator implant"],
        "source": "American Heart Association Clinical Guidelines 2024",
        "text": ""
    },
    {
        "id": "CUSTOM:CVD:002",
        "name": "Heart Attack Symptoms",
        "description": "A heart attack (myocardial infarction) occurs when blood flow to the heart muscle is severely reduced or blocked. Warning signs can appear hours, days, or weeks before. Immediate recognition saves lives.",
        "synonyms": ["myocardial infarction symptoms", "MI symptoms", "cardiac arrest warning signs"],
        "related_synonyms": ["acute coronary syndrome"],
        "category": "cardiovascular",
        "pathophysiology": "ischemic",
        "child_diseases": [],
        "symptoms": [
            "chest pain or discomfort (pressure, squeezing, fullness)",
            "pain radiating to left arm, shoulder, back, neck, or jaw",
            "shortness of breath",
            "cold sweat",
            "nausea or vomiting",
            "lightheadedness or dizziness",
            "unusual fatigue",
            "heartburn-like sensation",
            "women may have atypical symptoms: back pain, jaw pain, nausea without chest pain"
        ],
        "risk_factors": ["previous heart attack", "coronary artery disease", "high blood pressure", "high LDL cholesterol", "low HDL cholesterol", "diabetes", "smoking", "obesity", "sedentary lifestyle", "stress", "cocaine use", "family history of heart disease"],
        "diagnostics": ["troponin blood test", "ECG changes (ST elevation, Q waves)", "cardiac enzymes (CK-MB)", "coronary angiography", "echocardiogram"],
        "treatments": ["aspirin (chew immediately)", "nitroglycerin", "thrombolytics", "PCI/angioplasty with stent", "CABG surgery", "oxygen therapy", "morphine for pain"],
        "emergency_action": "Call 911 immediately. Chew aspirin if not allergic. Do not drive yourself to hospital.",
        "source": "American College of Cardiology/American Heart Association STEMI Guidelines 2023",
        "text": ""
    },
    {
        "id": "CUSTOM:CVD:003",
        "name": "Heart Failure",
        "description": "Heart failure is a chronic condition where the heart cannot pump blood efficiently to meet the body's needs. Can be systolic (reduced ejection fraction) or diastolic (preserved ejection fraction). Progressive disease requiring ongoing management.",
        "synonyms": ["congestive heart failure", "CHF", "cardiac failure", "HFrEF", "HFpEF"],
        "related_synonyms": ["cardiac insufficiency"],
        "category": "cardiovascular",
        "pathophysiology": "cardiac dysfunction",
        "child_diseases": [],
        "symptoms": [
            "shortness of breath (dyspnea) especially when lying down",
            "fatigue and weakness",
            "swelling in legs, ankles, feet (edema)",
            "rapid or irregular heartbeat",
            "reduced ability to exercise",
            "persistent cough with white or pink phlegm",
            "increased need to urinate at night",
            "swelling of abdomen (ascites)",
            "sudden weight gain from fluid retention",
            "lack of appetite and nausea",
            "difficulty concentrating"
        ],
        "risk_factors": ["coronary artery disease", "heart attack history", "high blood pressure", "diabetes", "obesity", "valvular heart disease", "cardiomyopathy", "myocarditis", "congenital heart defects", "sleep apnea", "alcohol abuse", "chemotherapy drugs"],
        "nyha_classification": ["Class I: No symptoms", "Class II: Mild symptoms with ordinary activity", "Class III: Marked limitation, symptoms with less than ordinary activity", "Class IV: Symptoms at rest"],
        "diagnostics": ["BNP/NT-proBNP blood test", "echocardiogram (ejection fraction)", "chest X-ray", "ECG", "stress test", "cardiac MRI", "coronary angiography", "right heart catheterization"],
        "treatments": ["ACE inhibitors", "ARBs", "beta-blockers", "diuretics", "aldosterone antagonists", "SGLT2 inhibitors", "digoxin", "hydralazine/nitrates", "cardiac resynchronization therapy (CRT)", "LVAD", "heart transplant"],
        "source": "American College of Cardiology/American Heart Association Heart Failure Guidelines 2023",
        "text": ""
    },
    {
        "id": "CUSTOM:CVD:004",
        "name": "Hypertension",
        "description": "Hypertension (high blood pressure) is a chronic condition where blood pressure in arteries is persistently elevated. Often called the 'silent killer' because it typically has no symptoms until significant damage occurs. Major risk factor for heart attack, stroke, and kidney disease.",
        "synonyms": ["high blood pressure", "HTN", "arterial hypertension", "elevated blood pressure"],
        "related_synonyms": ["essential hypertension", "secondary hypertension"],
        "category": "cardiovascular",
        "pathophysiology": "vascular",
        "child_diseases": [],
        "symptoms": [
            "usually asymptomatic (silent killer)",
            "severe hypertension may cause: headaches",
            "shortness of breath",
            "nosebleeds",
            "dizziness",
            "chest pain",
            "visual changes",
            "blood in urine"
        ],
        "blood_pressure_categories": [
            "Normal: less than 120/80 mmHg",
            "Elevated: 120-129/less than 80 mmHg",
            "Stage 1 Hypertension: 130-139/80-89 mmHg",
            "Stage 2 Hypertension: 140+/90+ mmHg",
            "Hypertensive Crisis: higher than 180/120 mmHg"
        ],
        "risk_factors": ["age", "family history", "obesity", "sedentary lifestyle", "tobacco use", "high sodium diet", "low potassium", "excessive alcohol", "stress", "chronic kidney disease", "diabetes", "sleep apnea"],
        "complications": ["heart attack", "stroke", "heart failure", "kidney damage", "vision loss", "sexual dysfunction", "peripheral artery disease", "dementia"],
        "diagnostics": ["blood pressure measurement (multiple readings)", "ambulatory BP monitoring", "blood tests (kidney function, potassium, glucose)", "urinalysis", "ECG", "echocardiogram"],
        "treatments": ["lifestyle modifications (DASH diet, exercise, weight loss, reduce sodium)", "thiazide diuretics", "ACE inhibitors", "ARBs", "calcium channel blockers", "beta-blockers"],
        "source": "American College of Cardiology/American Heart Association Hypertension Guidelines 2023",
        "text": ""
    },
    {
        "id": "CUSTOM:CVD:005",
        "name": "Atrial Fibrillation",
        "description": "Atrial fibrillation (AFib) is an irregular and often rapid heart rhythm originating in the atria. The most common cardiac arrhythmia. Increases risk of stroke 5-fold due to blood clot formation in the heart.",
        "synonyms": ["AFib", "AF", "auricular fibrillation", "irregular heartbeat"],
        "related_synonyms": ["cardiac arrhythmia", "supraventricular tachycardia"],
        "category": "cardiovascular",
        "pathophysiology": "arrhythmia",
        "child_diseases": [],
        "symptoms": [
            "palpitations (racing, fluttering heartbeat)",
            "irregular pulse",
            "fatigue",
            "shortness of breath",
            "dizziness or lightheadedness",
            "chest pain or discomfort",
            "reduced exercise tolerance",
            "some patients are asymptomatic"
        ],
        "types": ["Paroxysmal (comes and goes)", "Persistent (lasts more than 7 days)", "Long-standing persistent (more than 12 months)", "Permanent (cannot be restored to normal rhythm)"],
        "risk_factors": ["age over 60", "high blood pressure", "heart disease", "obesity", "diabetes", "hyperthyroidism", "sleep apnea", "excessive alcohol (holiday heart)", "caffeine", "heart surgery", "lung disease"],
        "complications": ["stroke (5x increased risk)", "heart failure", "cognitive decline", "reduced quality of life"],
        "diagnostics": ["ECG showing irregularly irregular rhythm", "Holter monitor", "event recorder", "echocardiogram", "thyroid function tests", "CHA2DS2-VASc score for stroke risk"],
        "treatments": ["rate control (beta-blockers, calcium channel blockers, digoxin)", "rhythm control (antiarrhythmics, cardioversion)", "anticoagulation (warfarin, DOACs)", "catheter ablation", "left atrial appendage closure", "AV node ablation with pacemaker"],
        "source": "American Heart Association/American College of Cardiology AFib Guidelines 2023",
        "text": ""
    },
    {
        "id": "CUSTOM:CVD:006",
        "name": "Stroke Symptoms",
        "description": "A stroke occurs when blood supply to part of the brain is interrupted (ischemic) or when a blood vessel in the brain bursts (hemorrhagic). Brain cells begin dying within minutes. Time-critical emergency - 'time is brain'.",
        "synonyms": ["cerebrovascular accident", "CVA", "brain attack"],
        "related_synonyms": ["TIA", "mini-stroke", "ischemic stroke", "hemorrhagic stroke"],
        "category": "cardiovascular",
        "pathophysiology": "cerebrovascular",
        "child_diseases": [],
        "symptoms": [
            "FAST signs: Face drooping, Arm weakness, Speech difficulty, Time to call 911",
            "sudden numbness or weakness (especially one side)",
            "sudden confusion",
            "sudden trouble speaking or understanding",
            "sudden vision problems in one or both eyes",
            "sudden severe headache with no known cause",
            "sudden trouble walking, dizziness, loss of balance",
            "sudden trouble with coordination"
        ],
        "risk_factors": ["high blood pressure", "atrial fibrillation", "diabetes", "high cholesterol", "smoking", "obesity", "physical inactivity", "excessive alcohol", "drug use (cocaine)", "family history", "previous stroke or TIA", "carotid artery disease"],
        "types": ["Ischemic stroke (87% - blood clot blocks artery)", "Hemorrhagic stroke (bleeding in brain)", "TIA (transient ischemic attack - temporary blockage)"],
        "diagnostics": ["CT scan (rule out hemorrhage)", "MRI", "CT angiography", "carotid ultrasound", "echocardiogram", "blood tests"],
        "treatments": ["tPA (tissue plasminogen activator) within 4.5 hours", "mechanical thrombectomy within 24 hours", "blood pressure management", "antiplatelet therapy", "anticoagulation for AFib", "carotid endarterectomy", "rehabilitation"],
        "emergency_action": "Call 911 immediately. Note time symptoms started. Do not give aspirin until stroke type confirmed.",
        "source": "American Stroke Association Guidelines for Early Management of Acute Ischemic Stroke 2024",
        "text": ""
    },
    {
        "id": "CUSTOM:CVD:007",
        "name": "Peripheral Artery Disease",
        "description": "Peripheral artery disease (PAD) is a circulatory condition where narrowed arteries reduce blood flow to the limbs, usually the legs. Often a sign of widespread atherosclerosis. Increases risk of heart attack and stroke.",
        "synonyms": ["PAD", "peripheral vascular disease", "PVD", "claudication"],
        "related_synonyms": ["atherosclerosis", "hardening of arteries"],
        "category": "cardiovascular",
        "pathophysiology": "vascular occlusive",
        "child_diseases": [],
        "symptoms": [
            "leg pain when walking (claudication) that improves with rest",
            "leg numbness or weakness",
            "coldness in lower leg or foot",
            "sores on toes, feet, or legs that won't heal",
            "color changes in legs",
            "hair loss on legs",
            "slower toenail growth",
            "shiny skin on legs",
            "weak or absent pulse in legs",
            "erectile dysfunction in men"
        ],
        "risk_factors": ["smoking (strongest risk factor)", "diabetes", "high blood pressure", "high cholesterol", "age over 50", "family history", "obesity", "kidney disease"],
        "diagnostics": ["ankle-brachial index (ABI)", "Doppler ultrasound", "CT angiography", "MR angiography", "angiography"],
        "treatments": ["smoking cessation", "supervised exercise program", "cilostazol", "antiplatelet therapy", "statins", "blood pressure control", "diabetes management", "angioplasty with stent", "bypass surgery", "amputation in severe cases"],
        "source": "American Heart Association PAD Guidelines 2024",
        "text": ""
    },
    
    # ============================================
    # DIABETES - COMPREHENSIVE
    # ============================================
    {
        "id": "CUSTOM:DM:001",
        "name": "Diabetes Mellitus Overview",
        "description": "Diabetes mellitus is a group of metabolic diseases characterized by chronic hyperglycemia resulting from defects in insulin secretion, insulin action, or both. Long-term complications affect eyes, kidneys, nerves, heart, and blood vessels.",
        "synonyms": ["diabetes", "sugar disease", "DM"],
        "related_synonyms": ["hyperglycemia", "glucose intolerance"],
        "category": "metabolic",
        "pathophysiology": "metabolic/endocrine",
        "child_diseases": [],
        "symptoms": [
            "increased thirst (polydipsia)",
            "frequent urination (polyuria)",
            "extreme hunger (polyphagia)",
            "unexplained weight loss",
            "fatigue",
            "blurred vision",
            "slow-healing sores",
            "frequent infections",
            "areas of darkened skin (acanthosis nigricans)",
            "numbness or tingling in hands/feet"
        ],
        "types": [
            "Type 1: Autoimmune destruction of beta cells, requires insulin",
            "Type 2: Insulin resistance with relative insulin deficiency, most common (90-95%)",
            "Gestational: Develops during pregnancy",
            "Other: MODY, drug-induced, pancreatitis-related"
        ],
        "risk_factors_type2": ["obesity", "physical inactivity", "family history", "age over 45", "race/ethnicity", "gestational diabetes history", "PCOS", "prediabetes", "high blood pressure", "abnormal cholesterol"],
        "diagnostics": [
            "Fasting plasma glucose >= 126 mg/dL",
            "2-hour OGTT >= 200 mg/dL",
            "HbA1c >= 6.5%",
            "Random glucose >= 200 mg/dL with symptoms",
            "C-peptide (distinguish Type 1 vs 2)",
            "Antibodies (GAD65, IA-2, ZnT8 for Type 1)"
        ],
        "treatments": ["lifestyle modification", "metformin", "SGLT2 inhibitors", "GLP-1 receptor agonists", "DPP-4 inhibitors", "sulfonylureas", "thiazolidinediones", "insulin therapy", "bariatric surgery"],
        "source": "American Diabetes Association Standards of Medical Care in Diabetes 2024",
        "text": ""
    },
    {
        "id": "CUSTOM:DM:002",
        "name": "Type 1 Diabetes",
        "description": "Type 1 diabetes is an autoimmune condition where the immune system attacks and destroys insulin-producing beta cells in the pancreas. Requires lifelong insulin therapy. Can occur at any age but often diagnosed in children and young adults.",
        "synonyms": ["T1D", "juvenile diabetes", "insulin-dependent diabetes", "IDDM"],
        "related_synonyms": ["autoimmune diabetes", "brittle diabetes"],
        "category": "metabolic",
        "pathophysiology": "autoimmune",
        "child_diseases": [],
        "symptoms": [
            "rapid onset of symptoms",
            "extreme thirst",
            "frequent urination",
            "bed-wetting in children",
            "extreme hunger",
            "unintended weight loss",
            "irritability and mood changes",
            "fatigue and weakness",
            "blurred vision",
            "diabetic ketoacidosis (DKA) may be presenting feature"
        ],
        "risk_factors": ["family history of Type 1", "genetics (HLA-DR3, HLA-DR4)", "presence of autoantibodies", "viral infections as trigger", "northern latitude", "early introduction of cow's milk"],
        "diagnostics": ["autoantibodies (GAD65, IA-2, IAA, ZnT8)", "low C-peptide", "HbA1c", "fasting glucose", "genetic testing"],
        "treatments": [
            "multiple daily insulin injections (MDI)",
            "insulin pump therapy",
            "continuous glucose monitoring (CGM)",
            "carbohydrate counting",
            "hybrid closed-loop systems (artificial pancreas)",
            "islet cell transplantation (research)"
        ],
        "complications": ["diabetic ketoacidosis (DKA)", "hypoglycemia", "retinopathy", "nephropathy", "neuropathy", "cardiovascular disease"],
        "source": "American Diabetes Association Type 1 Diabetes Guidelines 2024",
        "text": ""
    },
    {
        "id": "CUSTOM:DM:003",
        "name": "Type 2 Diabetes",
        "description": "Type 2 diabetes is characterized by insulin resistance and progressive beta cell dysfunction. The most common form of diabetes (90-95% of cases). Often associated with obesity and sedentary lifestyle. Can often be prevented or delayed with lifestyle changes.",
        "synonyms": ["T2D", "adult-onset diabetes", "non-insulin-dependent diabetes", "NIDDM"],
        "related_synonyms": ["insulin resistance syndrome", "metabolic syndrome"],
        "category": "metabolic",
        "pathophysiology": "insulin resistance",
        "child_diseases": [],
        "symptoms": [
            "symptoms develop gradually over years",
            "increased thirst and urination",
            "increased hunger",
            "fatigue",
            "blurred vision",
            "slow-healing cuts and bruises",
            "tingling or numbness in hands/feet",
            "frequent yeast infections",
            "darkened skin patches (acanthosis nigricans)",
            "many patients asymptomatic at diagnosis"
        ],
        "risk_factors": [
            "overweight or obesity (BMI >= 25)",
            "waist circumference (men >40 inches, women >35 inches)",
            "physical inactivity",
            "family history (first-degree relative)",
            "age >= 45 years",
            "race/ethnicity (African American, Hispanic, Native American, Asian)",
            "history of gestational diabetes",
            "prediabetes (HbA1c 5.7-6.4%)",
            "polycystic ovary syndrome",
            "high blood pressure (>=140/90)",
            "HDL <35 mg/dL or triglycerides >250 mg/dL"
        ],
        "diagnostics": ["HbA1c", "fasting plasma glucose", "oral glucose tolerance test", "random plasma glucose"],
        "treatments": [
            "lifestyle modification (weight loss 5-10%, exercise 150 min/week)",
            "metformin (first-line)",
            "SGLT2 inhibitors (especially with CVD or CKD)",
            "GLP-1 receptor agonists (especially with CVD or obesity)",
            "DPP-4 inhibitors",
            "sulfonylureas",
            "thiazolidinediones",
            "insulin (when other agents insufficient)",
            "bariatric surgery (BMI >= 35 with diabetes)"
        ],
        "target_goals": ["HbA1c <7% (individualized)", "fasting glucose 80-130 mg/dL", "BP <130/80 mmHg", "LDL <100 mg/dL"],
        "source": "American Diabetes Association Standards of Care 2024",
        "text": ""
    },
    {
        "id": "CUSTOM:DM:004",
        "name": "Diabetic Ketoacidosis",
        "description": "Diabetic ketoacidosis (DKA) is a serious, life-threatening complication of diabetes characterized by hyperglycemia, ketosis, and metabolic acidosis. Medical emergency requiring immediate treatment. Most common in Type 1 but can occur in Type 2.",
        "synonyms": ["DKA", "ketoacidosis", "diabetic acidosis"],
        "related_synonyms": ["hyperglycemic crisis"],
        "category": "metabolic emergency",
        "pathophysiology": "metabolic acidosis",
        "child_diseases": [],
        "symptoms": [
            "excessive thirst",
            "frequent urination",
            "nausea and vomiting",
            "abdominal pain",
            "weakness or fatigue",
            "shortness of breath",
            "fruity-scented breath (ketones)",
            "confusion or difficulty concentrating",
            "Kussmaul breathing (deep, rapid breathing)",
            "dehydration",
            "altered consciousness or coma"
        ],
        "triggers": ["missed insulin doses", "infection", "heart attack", "stroke", "pancreatitis", "certain medications (steroids)", "new diagnosis of Type 1 diabetes", "insulin pump failure"],
        "diagnostics": [
            "blood glucose >250 mg/dL",
            "arterial pH <7.3",
            "serum bicarbonate <18 mEq/L",
            "anion gap >10",
            "positive serum/urine ketones",
            "basic metabolic panel",
            "serum osmolality"
        ],
        "treatments": [
            "IV fluid resuscitation (normal saline)",
            "IV insulin infusion",
            "potassium replacement",
            "bicarbonate (if pH <6.9)",
            "treat underlying cause",
            "ICU monitoring",
            "transition to subcutaneous insulin when resolved"
        ],
        "emergency_action": "Call 911 or go to ER immediately. This is a medical emergency.",
        "source": "American Diabetes Association DKA Management Guidelines 2024",
        "text": ""
    },
    {
        "id": "CUSTOM:DM:005",
        "name": "Hypoglycemia",
        "description": "Hypoglycemia (low blood sugar) occurs when blood glucose falls below 70 mg/dL. Can be life-threatening if severe. Common in people taking insulin or certain diabetes medications. Requires immediate treatment.",
        "synonyms": ["low blood sugar", "insulin reaction", "insulin shock"],
        "related_synonyms": ["glucose deficiency"],
        "category": "metabolic",
        "pathophysiology": "glucose deficit",
        "child_diseases": [],
        "symptoms": [
            "Level 1 (glucose <70 mg/dL): shakiness, sweating, hunger, rapid heartbeat, anxiety, irritability, pale skin",
            "Level 2 (glucose <54 mg/dL): confusion, blurred vision, difficulty speaking, drowsiness, weakness, poor coordination",
            "Level 3 (severe): seizures, loss of consciousness, coma, requires assistance",
            "hypoglycemia unawareness (no warning symptoms)"
        ],
        "causes": ["too much insulin", "missed meals", "excessive exercise", "alcohol consumption", "certain medications", "kidney disease", "liver disease"],
        "diagnostics": ["blood glucose measurement", "CGM readings"],
        "treatments": [
            "Rule of 15: 15g fast-acting carbs, wait 15 minutes, recheck",
            "fast-acting carbs: glucose tablets, juice, regular soda, candy",
            "glucagon injection/nasal spray for severe hypoglycemia",
            "IV dextrose in hospital setting",
            "eat a snack or meal after recovery"
        ],
        "prevention": ["regular glucose monitoring", "CGM use", "consistent meal timing", "adjust insulin for exercise", "limit alcohol", "carry fast-acting glucose"],
        "source": "American Diabetes Association Hypoglycemia Guidelines 2024",
        "text": ""
    },
    {
        "id": "CUSTOM:DM:006",
        "name": "Diabetic Neuropathy",
        "description": "Diabetic neuropathy is nerve damage caused by chronic high blood sugar. Affects up to 50% of people with diabetes. Most commonly affects legs and feet (peripheral neuropathy). Can also affect autonomic nerves controlling organs.",
        "synonyms": ["diabetic nerve damage", "peripheral neuropathy", "autonomic neuropathy"],
        "related_synonyms": ["polyneuropathy", "nerve pain"],
        "category": "diabetes complication",
        "pathophysiology": "neurological",
        "child_diseases": [],
        "symptoms": [
            "Peripheral neuropathy: numbness, tingling, burning pain in feet/hands, sensitivity to touch, muscle weakness, loss of reflexes, balance problems",
            "Autonomic neuropathy: gastroparesis, bladder problems, erectile dysfunction, orthostatic hypotension, excessive or reduced sweating, heart rate abnormalities",
            "Proximal neuropathy: severe pain in hip/thigh/buttock, weakness in legs",
            "Focal neuropathy: sudden weakness, double vision, Bell's palsy"
        ],
        "risk_factors": ["poor blood sugar control", "long duration of diabetes", "obesity", "smoking", "high blood pressure", "kidney disease"],
        "diagnostics": ["monofilament test", "tuning fork vibration test", "nerve conduction studies", "EMG", "autonomic function tests", "skin biopsy"],
        "treatments": [
            "blood sugar control (primary)",
            "pain medications: pregabalin, gabapentin, duloxetine, amitriptyline",
            "topical treatments: capsaicin, lidocaine patches",
            "physical therapy",
            "transcutaneous electrical nerve stimulation (TENS)",
            "foot care to prevent ulcers"
        ],
        "source": "American Diabetes Association Neuropathy Guidelines 2024",
        "text": ""
    },
    {
        "id": "CUSTOM:DM:007",
        "name": "Diabetic Retinopathy",
        "description": "Diabetic retinopathy is damage to blood vessels in the retina caused by diabetes. Leading cause of blindness in working-age adults. Often asymptomatic in early stages. Annual eye exams essential for early detection.",
        "synonyms": ["diabetic eye disease", "retinal damage from diabetes"],
        "related_synonyms": ["macular edema", "proliferative retinopathy"],
        "category": "diabetes complication",
        "pathophysiology": "microvascular",
        "child_diseases": [],
        "symptoms": [
            "early stages: often no symptoms",
            "blurred vision",
            "floaters (dark spots or strings)",
            "fluctuating vision",
            "dark or empty areas in vision",
            "vision loss",
            "difficulty perceiving colors"
        ],
        "stages": [
            "Mild nonproliferative: microaneurysms",
            "Moderate nonproliferative: blocked blood vessels",
            "Severe nonproliferative: many blocked vessels, retina signals for new vessels",
            "Proliferative: new abnormal blood vessels grow (neovascularization)"
        ],
        "risk_factors": ["poor blood sugar control", "long duration of diabetes", "high blood pressure", "high cholesterol", "pregnancy", "smoking"],
        "diagnostics": ["dilated eye exam", "fluorescein angiography", "optical coherence tomography (OCT)", "fundus photography"],
        "treatments": [
            "blood sugar, BP, and cholesterol control",
            "anti-VEGF injections (ranibizumab, aflibercept, bevacizumab)",
            "laser photocoagulation",
            "vitrectomy surgery",
            "steroid injections"
        ],
        "screening": "Annual dilated eye exam for all people with diabetes",
        "source": "American Academy of Ophthalmology Diabetic Retinopathy Guidelines 2024",
        "text": ""
    },
    {
        "id": "CUSTOM:DM:008",
        "name": "Diabetic Nephropathy",
        "description": "Diabetic nephropathy (diabetic kidney disease) is progressive kidney damage caused by diabetes. Leading cause of end-stage renal disease. Early detection through regular screening can slow progression.",
        "synonyms": ["diabetic kidney disease", "DKD", "diabetic nephropathy"],
        "related_synonyms": ["chronic kidney disease from diabetes", "Kimmelstiel-Wilson syndrome"],
        "category": "diabetes complication",
        "pathophysiology": "microvascular/renal",
        "child_diseases": [],
        "symptoms": [
            "early stages: no symptoms",
            "swelling in hands, feet, face",
            "weight gain from fluid retention",
            "poor appetite",
            "nausea and vomiting",
            "fatigue",
            "itching",
            "confusion",
            "foamy urine (proteinuria)",
            "need to urinate more often at night"
        ],
        "stages": [
            "Stage 1: Kidney damage with normal GFR (>=90)",
            "Stage 2: Mild reduction in GFR (60-89)",
            "Stage 3: Moderate reduction (30-59)",
            "Stage 4: Severe reduction (15-29)",
            "Stage 5: Kidney failure (<15) - requires dialysis or transplant"
        ],
        "risk_factors": ["poor blood sugar control", "uncontrolled hypertension", "long diabetes duration", "smoking", "obesity", "family history of kidney disease", "African American, Hispanic, Native American ethnicity"],
        "diagnostics": ["urine albumin-to-creatinine ratio (UACR)", "serum creatinine", "eGFR calculation", "kidney ultrasound", "kidney biopsy (rare)"],
        "treatments": [
            "blood sugar control (HbA1c <7%)",
            "blood pressure control (<130/80)",
            "ACE inhibitors or ARBs (first-line)",
            "SGLT2 inhibitors (reduce progression)",
            "finerenone (nonsteroidal MRA)",
            "dietary protein restriction",
            "dialysis (hemodialysis or peritoneal)",
            "kidney transplant"
        ],
        "screening": "Annual UACR and eGFR for all people with diabetes",
        "source": "KDIGO Diabetic Kidney Disease Guidelines 2024",
        "text": ""
    },
    
    # ============================================
    # SEPSIS - COMPREHENSIVE
    # ============================================
    {
        "id": "CUSTOM:SEPSIS:001",
        "name": "Sepsis Overview",
        "description": "Sepsis is a life-threatening organ dysfunction caused by a dysregulated host response to infection. It can rapidly progress to septic shock and death. Time-critical emergency - every hour of delayed treatment increases mortality by 8%. Third Sepsis definition (Sepsis-3).",
        "synonyms": ["blood poisoning", "septicemia", "systemic infection"],
        "related_synonyms": ["SIRS", "bacteremia", "severe sepsis"],
        "category": "infectious/critical care",
        "pathophysiology": "inflammatory/immune dysregulation",
        "child_diseases": [],
        "symptoms": [
            "fever (>100.4°F/38°C) or hypothermia (<96.8°F/36°C)",
            "heart rate >90 beats per minute",
            "rapid breathing (>20 breaths/min)",
            "confusion or altered mental status",
            "extreme pain or discomfort",
            "clammy or sweaty skin",
            "shortness of breath",
            "low blood pressure",
            "'I feel like I might die' feeling"
        ],
        "warning_signs_mnemonic": "TIME: T-temperature abnormal, I-infection signs, M-mental decline, E-extremely ill",
        "common_infection_sources": ["pneumonia (most common)", "urinary tract infection", "abdominal infection", "skin/soft tissue infection", "central line infection", "surgical site infection"],
        "risk_factors": ["age >65 or <1 year", "weakened immune system", "chronic diseases (diabetes, cancer, kidney disease)", "recent hospitalization", "invasive devices (catheters, ventilators)", "recent surgery", "antibiotic-resistant infections"],
        "diagnostics": [
            "SOFA score (Sequential Organ Failure Assessment)",
            "qSOFA (quick SOFA): altered mental status, SBP <=100, RR >=22",
            "blood cultures (before antibiotics)",
            "lactate level",
            "complete blood count",
            "comprehensive metabolic panel",
            "procalcitonin",
            "imaging to find source"
        ],
        "treatments": [
            "1-hour bundle: measure lactate, obtain cultures, administer broad-spectrum antibiotics, IV fluids (30 mL/kg), vasopressors if needed",
            "source control (drain abscess, remove infected device)",
            "ICU admission",
            "organ support (ventilation, dialysis)",
            "corticosteroids in refractory shock"
        ],
        "emergency_action": "Call 911 immediately if sepsis suspected. Say 'I think this might be sepsis'. Time is critical.",
        "source": "Surviving Sepsis Campaign Guidelines 2024",
        "text": ""
    },
    {
        "id": "CUSTOM:SEPSIS:002",
        "name": "Septic Shock",
        "description": "Septic shock is a subset of sepsis with circulatory, cellular, and metabolic abnormalities. Defined as sepsis with persistent hypotension requiring vasopressors AND lactate >2 mmol/L despite adequate fluid resuscitation. Mortality rate 40-60%.",
        "synonyms": ["severe sepsis with shock", "distributive shock from sepsis"],
        "related_synonyms": ["refractory hypotension", "warm shock", "cold shock"],
        "category": "critical care emergency",
        "pathophysiology": "circulatory failure",
        "child_diseases": [],
        "symptoms": [
            "all sepsis symptoms plus:",
            "blood pressure dangerously low (MAP <65 mmHg)",
            "cool, mottled extremities",
            "weak or thready pulse",
            "decreased urine output (<0.5 mL/kg/hr)",
            "severe confusion or unconsciousness",
            "rapid heart rate that doesn't respond to fluids",
            "difficulty breathing",
            "lactic acidosis"
        ],
        "criteria": [
            "Sepsis present",
            "Vasopressors required to maintain MAP >=65 mmHg",
            "Lactate >2 mmol/L despite adequate fluid resuscitation"
        ],
        "diagnostics": ["arterial blood gas", "central venous pressure", "ScvO2 (central venous oxygen saturation)", "echocardiogram", "invasive hemodynamic monitoring"],
        "treatments": [
            "immediate ICU admission",
            "aggressive IV fluids (30 mL/kg crystalloid)",
            "vasopressors: norepinephrine (first-line), vasopressin, epinephrine",
            "inotropes if cardiac dysfunction",
            "mechanical ventilation if needed",
            "renal replacement therapy if AKI",
            "corticosteroids (hydrocortisone 200mg/day)",
            "blood transfusion if Hgb <7",
            "stress ulcer prophylaxis",
            "DVT prophylaxis"
        ],
        "source": "Surviving Sepsis Campaign Guidelines 2024",
        "text": ""
    },
    {
        "id": "CUSTOM:SEPSIS:003",
        "name": "Sepsis Early Warning Signs",
        "description": "Early recognition of sepsis saves lives. Sepsis can develop from any infection. Know the early warning signs and act fast. Every hour of delayed antibiotic treatment increases mortality by approximately 8%.",
        "synonyms": ["sepsis red flags", "sepsis screening criteria"],
        "related_synonyms": ["infection warning signs"],
        "category": "clinical screening",
        "pathophysiology": "early inflammatory response",
        "child_diseases": [],
        "symptoms": [
            "EARLY SIGNS:",
            "high heart rate (>90 bpm) at rest",
            "fast breathing (>20/min)",
            "fever >101°F (38.3°C) or low temperature <96.8°F (36°C)",
            "shaking chills (rigors)",
            "confusion or disorientation",
            "feeling worse than expected for the infection",
            "",
            "SIGNS OF PROGRESSION:",
            "slurred speech or confusion",
            "extreme shivering or muscle pain",
            "passing no urine in 12 hours",
            "severe breathlessness",
            "skin mottled, bluish, or pale",
            "loss of consciousness",
            "'I feel like I might die'"
        ],
        "screening_tools": [
            "qSOFA (>=2 points concerning): Altered mental status, SBP <=100, RR >=22",
            "NEWS2 score",
            "SIRS criteria (older): Temp >38 or <36, HR >90, RR >20, WBC >12k or <4k"
        ],
        "when_to_seek_emergency_care": [
            "any infection with confusion",
            "fever with rapid breathing and heart rate",
            "skin that is mottled, cold, or discolored",
            "not urinating for 12+ hours",
            "severe weakness",
            "feeling like you might die"
        ],
        "source": "Sepsis Alliance Education Materials 2024 and Surviving Sepsis Campaign",
        "text": ""
    },
    {
        "id": "CUSTOM:SEPSIS:004",
        "name": "Sepsis in Elderly Patients",
        "description": "Sepsis in older adults (>65 years) often presents atypically. Classic signs like fever may be absent. Altered mental status may be the only sign. Higher mortality risk. Requires high index of suspicion.",
        "synonyms": ["geriatric sepsis", "sepsis in older adults"],
        "related_synonyms": ["atypical sepsis presentation"],
        "category": "geriatric emergency",
        "pathophysiology": "age-related immune dysfunction",
        "child_diseases": [],
        "symptoms": [
            "ATYPICAL PRESENTATIONS (no fever in 20-30%):",
            "new confusion or delirium (often first sign)",
            "falls",
            "generalized weakness",
            "decreased mobility",
            "loss of appetite",
            "incontinence (new onset)",
            "lethargy or fatigue",
            "hypothermia more common than fever",
            "may not have elevated heart rate (beta-blocker use)"
        ],
        "risk_factors": ["nursing home residence", "multiple comorbidities", "immunosuppression", "malnutrition", "urinary catheter", "diabetes", "COPD", "dementia", "recent antibiotic use", "polypharmacy"],
        "common_sources": ["urinary tract infection (most common)", "pneumonia", "skin/soft tissue infections", "intra-abdominal infections"],
        "diagnostics": ["lower threshold for sepsis workup", "mental status assessment", "comprehensive metabolic panel", "urinalysis and culture", "chest X-ray", "blood cultures"],
        "treatments": ["same as standard sepsis treatment", "early antibiotics crucial", "careful fluid management (risk of overload)", "consider baseline functional status", "goals of care discussion important"],
        "source": "Society of Critical Care Medicine Geriatric Sepsis Guidelines 2024",
        "text": ""
    },
    {
        "id": "CUSTOM:SEPSIS:005",
        "name": "Neonatal Sepsis",
        "description": "Neonatal sepsis is a serious bacterial infection in newborns (<28 days). Early-onset (within 72 hours) usually from maternal transmission. Late-onset (>72 hours) often from environmental sources. High mortality without prompt treatment.",
        "synonyms": ["newborn sepsis", "neonatal infection", "sepsis neonatorum"],
        "related_synonyms": ["early-onset sepsis", "late-onset sepsis"],
        "category": "neonatal emergency",
        "pathophysiology": "neonatal immune immaturity",
        "child_diseases": [],
        "symptoms": [
            "temperature instability (fever or hypothermia)",
            "poor feeding or feeding intolerance",
            "lethargy or decreased activity",
            "irritability",
            "respiratory distress (grunting, flaring, retracting)",
            "apnea (pauses in breathing)",
            "tachycardia or bradycardia",
            "poor perfusion (mottled, pale, or gray skin)",
            "abdominal distension",
            "jaundice",
            "seizures",
            "bulging fontanelle (meningitis)"
        ],
        "risk_factors_early_onset": ["maternal GBS colonization", "prolonged rupture of membranes >18 hours", "maternal fever", "prematurity", "chorioamnionitis"],
        "risk_factors_late_onset": ["prematurity", "low birth weight", "central lines", "mechanical ventilation", "prolonged hospitalization", "prior antibiotic exposure"],
        "common_pathogens": ["Group B Streptococcus", "E. coli", "Listeria monocytogenes", "Coagulase-negative staphylococci", "Staphylococcus aureus", "Klebsiella"],
        "diagnostics": ["blood culture", "complete blood count with differential", "C-reactive protein", "procalcitonin", "lumbar puncture", "chest X-ray", "urinalysis"],
        "treatments": ["empiric antibiotics (ampicillin + gentamicin for early-onset)", "supportive care", "respiratory support", "IV fluids", "thermoregulation", "vasopressors if needed"],
        "source": "American Academy of Pediatrics Neonatal Sepsis Guidelines 2024",
        "text": ""
    },
    {
        "id": "CUSTOM:SEPSIS:006",
        "name": "Post-Sepsis Syndrome",
        "description": "Post-sepsis syndrome (PSS) refers to long-term physical, psychological, and cognitive effects that sepsis survivors may experience. Up to 50% of sepsis survivors experience PSS. Can last months to years.",
        "synonyms": ["sepsis survivorship", "sepsis sequelae", "long-term effects of sepsis"],
        "related_synonyms": ["post-ICU syndrome", "PICS"],
        "category": "survivorship",
        "pathophysiology": "post-inflammatory/recovery",
        "child_diseases": [],
        "symptoms": [
            "PHYSICAL:",
            "extreme fatigue and muscle weakness",
            "shortness of breath",
            "joint and muscle pain",
            "swollen limbs",
            "frequent infections",
            "poor wound healing",
            "hair loss",
            "dry, flaking skin",
            "",
            "COGNITIVE:",
            "poor concentration (brain fog)",
            "memory problems",
            "difficulty with complex tasks",
            "processing speed issues",
            "",
            "PSYCHOLOGICAL:",
            "anxiety",
            "depression",
            "PTSD",
            "nightmares and flashbacks",
            "insomnia"
        ],
        "risk_factors": ["severe sepsis/septic shock", "prolonged ICU stay", "mechanical ventilation", "delirium during illness", "pre-existing conditions"],
        "management": [
            "gradual physical rehabilitation",
            "occupational therapy",
            "cognitive rehabilitation",
            "psychological support/counseling",
            "treatment of specific symptoms",
            "sleep hygiene",
            "peer support groups",
            "regular medical follow-up"
        ],
        "source": "Sepsis Alliance Post-Sepsis Syndrome Resources 2024",
        "text": ""
    },
    {
        "id": "CUSTOM:SEPSIS:007",
        "name": "Urosepsis",
        "description": "Urosepsis is sepsis originating from a urinary tract infection. One of the most common sources of sepsis. Often occurs with urinary obstruction, catheters, or instrumentation. Requires prompt recognition and treatment.",
        "synonyms": ["urinary sepsis", "UTI sepsis"],
        "related_synonyms": ["complicated UTI", "pyelonephritis with sepsis"],
        "category": "infectious/urological",
        "pathophysiology": "ascending urinary infection",
        "child_diseases": [],
        "symptoms": [
            "urinary symptoms: dysuria, frequency, urgency, hematuria",
            "flank pain or costovertebral angle tenderness",
            "fever and chills (rigors)",
            "confusion (especially in elderly)",
            "nausea and vomiting",
            "hypotension",
            "tachycardia",
            "rapid breathing",
            "elderly may only have confusion or weakness"
        ],
        "risk_factors": ["urinary catheter", "urinary obstruction (stones, BPH)", "recent urological procedure", "diabetes", "immunosuppression", "female gender for UTI", "elderly", "neurogenic bladder", "pregnancy"],
        "common_pathogens": ["E. coli (most common)", "Klebsiella", "Proteus", "Pseudomonas", "Enterococcus"],
        "diagnostics": ["urinalysis", "urine culture", "blood cultures", "renal ultrasound or CT (for obstruction)", "lactate", "renal function tests"],
        "treatments": [
            "broad-spectrum antibiotics (fluoroquinolone, cephalosporin, or carbapenem)",
            "IV fluids",
            "relieve obstruction if present (catheter, nephrostomy, stent)",
            "remove or change infected urinary catheter",
            "vasopressors if septic shock"
        ],
        "source": "European Association of Urology Urosepsis Guidelines 2024",
        "text": ""
    },
    {
        "id": "CUSTOM:SEPSIS:008",
        "name": "Pneumonia-related Sepsis",
        "description": "Pneumonia is the most common source of sepsis. Can be community-acquired (CAP) or hospital-acquired (HAP). Bacterial pneumonia carries highest sepsis risk. Early antibiotics and supportive care are essential.",
        "synonyms": ["pulmonary sepsis", "sepsis from pneumonia"],
        "related_synonyms": ["severe pneumonia", "pneumonia with organ dysfunction"],
        "category": "infectious/pulmonary",
        "pathophysiology": "pulmonary infection with systemic spread",
        "child_diseases": [],
        "symptoms": [
            "pneumonia symptoms: cough, fever, sputum production, chest pain",
            "shortness of breath or rapid breathing",
            "hypoxia (low oxygen)",
            "sepsis signs: confusion, hypotension, tachycardia",
            "multi-organ dysfunction signs",
            "elderly may present with confusion only"
        ],
        "risk_factors": ["age >65", "chronic lung disease (COPD, asthma)", "smoking", "immunosuppression", "aspiration risk", "recent viral illness (influenza, COVID-19)", "nursing home residence", "mechanical ventilation"],
        "common_pathogens": ["Streptococcus pneumoniae (most common CAP)", "Staphylococcus aureus (including MRSA)", "Haemophilus influenzae", "Klebsiella pneumoniae", "Pseudomonas aeruginosa (HAP)", "Legionella", "atypical organisms"],
        "diagnostics": ["chest X-ray or CT", "blood cultures", "sputum culture", "respiratory viral panel", "urinary pneumococcal and Legionella antigens", "procalcitonin", "lactate"],
        "treatments": [
            "empiric antibiotics based on setting (CAP vs HAP)",
            "oxygen therapy",
            "IV fluids (careful in ARDS)",
            "vasopressors if needed",
            "mechanical ventilation if respiratory failure",
            "corticosteroids in selected cases"
        ],
        "source": "IDSA/ATS Community-Acquired Pneumonia Guidelines 2024",
        "text": ""
    }
]


def build_text_field(entry):
    """Build the comprehensive text field for embedding."""
    parts = []
    
    # Basic info
    parts.append(f"Disease: {entry['name']}")
    
    if entry.get('description'):
        parts.append(f"Description: {entry['description']}")
    
    if entry.get('synonyms'):
        parts.append(f"Also known as: {', '.join(entry['synonyms'])}")
    
    # Symptoms (critical for search)
    if entry.get('symptoms'):
        symptoms = entry['symptoms']
        # Filter out empty strings and headers
        clean_symptoms = [s for s in symptoms if s and not s.endswith(':')]
        parts.append(f"Symptoms: {', '.join(clean_symptoms)}")
    
    # Risk factors
    if entry.get('risk_factors'):
        parts.append(f"Risk factors: {', '.join(entry['risk_factors'])}")
    
    if entry.get('risk_factors_type2'):
        parts.append(f"Risk factors: {', '.join(entry['risk_factors_type2'])}")
    
    # Diagnostics
    if entry.get('diagnostics'):
        parts.append(f"Diagnostics: {', '.join(entry['diagnostics'])}")
    
    # Treatments
    if entry.get('treatments'):
        parts.append(f"Treatments: {', '.join(entry['treatments'])}")
    
    # Category
    if entry.get('category'):
        parts.append(f"Category: {entry['category']}")
    
    # Special fields
    if entry.get('emergency_action'):
        parts.append(f"Emergency action: {entry['emergency_action']}")
    
    if entry.get('types'):
        parts.append(f"Types: {', '.join(entry['types'])}")
    
    return " | ".join(parts)


def main():
    print("=" * 60)
    print("Adding Comprehensive Medical Knowledge")
    print("=" * 60)
    
    # Build text fields for each entry
    for entry in MEDICAL_KNOWLEDGE:
        entry['text'] = build_text_field(entry)
    
    # Read existing data
    print(f"\nReading existing data from {JSONL_FILE}...")
    existing_data = []
    with open(JSONL_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            existing_data.append(json.loads(line.strip()))
    
    print(f"Found {len(existing_data)} existing entries")
    
    # Add new entries
    print(f"Adding {len(MEDICAL_KNOWLEDGE)} new comprehensive medical entries...")
    
    # Write all data back
    with open(JSONL_FILE, 'w', encoding='utf-8') as f:
        for entry in existing_data:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        for entry in MEDICAL_KNOWLEDGE:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    print(f"\n✅ Successfully added {len(MEDICAL_KNOWLEDGE)} entries!")
    print(f"Total entries now: {len(existing_data) + len(MEDICAL_KNOWLEDGE)}")
    
    # Print sample
    print("\n" + "=" * 60)
    print("Sample entry:")
    print("=" * 60)
    sample = MEDICAL_KNOWLEDGE[0]
    print(f"ID: {sample['id']}")
    print(f"Name: {sample['name']}")
    print(f"Source: {sample['source']}")
    print(f"Symptoms: {sample.get('symptoms', [])[:5]}...")


if __name__ == "__main__":
    main()
