# Simplified Schema Definition for LLM Context
# This avoids sending the entire 40k node schema to the LLM.

CLINICAL_SCHEMA = """
Node Labels & Properties:
- Patient: [synthea_id, patient_no, birth_date, age, gender, race, first_name, last_name, cvd_risk, diabetes_risk, doctor_id, deathdate]
- Condition: [code, description, onset_date, abatement_date, severity]
- Medication: [code, description, start_datetime, stop_datetime, status, dispenses]
- Observation: [code, description, value, units, observation_date, category]
- Encounter: [start_datetime, description, encounter_class, total_claim_cost, reason_description]
- Procedure: [code, description, start_datetime]
- Allergy: [description, start_date, severity, allergen]
- Immunization: [code, description, immunization_date]
- ImagingStudy: [bodysite_description, modality_description, study_date]
- AIFeatureSet: [cvd_risk_score, diabetes_risk_score, bmi, hba1c, smoking_status, last_updated]
- RiskProfile: [cardiovascular_risk, diabetes_risk, mortality_risk, readmission_risk]
- RiskFactor: [name, category, description]
- LabTrend: [patient_id, hba1c_latest, glucose_latest, trend_direction]
- CarePlan: [name, description, reason_description, is_active, start_date]
- FamilyHistory: [relative, relation, condition]
- Doctor: [name, specialization, doctor_id]

Relationships:
(:Patient)-[:HAS_CONDITION]->(:Condition)
(:Patient)-[:TAKES_MEDICATION]->(:Medication)
(:Patient)-[:HAS_OBSERVATION]->(:Observation)
(:Patient)-[:HAS_ENCOUNTER]->(:Encounter)
(:Encounter)-[:HAS_OBSERVATION]->(:Observation)
(:Encounter)-[:DIAGNOSED_CONDITION]->(:Condition)
(:Patient)-[:HAS_PROCEDURE]->(:Procedure)
(:Patient)-[:HAS_ALLERGY]->(:Allergy)
(:Patient)-[:RECEIVED_IMMUNIZATION]->(:Immunization)
(:Patient)-[:HAS_IMAGING_STUDY]->(:ImagingStudy)
(:Patient)-[:HAS_AI_FEATURES]->(:AIFeatureSet)
(:Patient)-[:HAS_RISK_PROFILE]->(:RiskProfile)
(:Patient)-[:HAS_RISK_FACTOR]->(:RiskFactor)
(:Patient)-[:HAS_LAB_TREND]->(:LabTrend)
(:Patient)-[:HAS_CARE_PLAN]->(:CarePlan)
(:Patient)-[:HAS_FAMILY_HISTORY]->(:FamilyHistory)
(:Patient)-[:TREATED_BY]->(:Doctor)

Note: 
- Patient 'synthea_id' is the primary identifier for clinical records. Use it for lookups (e.g. {synthea_id: '...'}).
- Patient 'id' corresponds to the UUID from the source system.
- Dates are typically in ISO 8601 format (YYYY-MM-DD).
"""
