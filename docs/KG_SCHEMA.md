# Healthcare Knowledge Graph Schema

**Generated**: February 10, 2026  
**Database**: Neo4j  
**Project**: KJU Healthcare Analytics Platform

---

## 📊 Schema Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         HEALTHCARE KNOWLEDGE GRAPH                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Total Nodes: ~130,000+                                                          │
│  Total Relationships: ~550,000+                                                  │
│  Node Types: 33                                                                  │
│  Relationship Types: 36                                                          │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Node Labels (Entities)

### Core Patient Entities

| Label | Alias | Count | Description |
|-------|-------|-------|-------------|
| `Person` | `Patient` | 144/181 | Core patient entity with demographics |
| `AIFeatureSet` | - | 133 | ML-ready features for predictions |
| `RiskProfile` | - | 37 | Patient risk assessment data |
| `RiskFactor` | - | 3 | Categorical risk factors (Smoking, Obesity, Hypertension) |

### Clinical Observations

| Label | Alias | Count | Description |
|-------|-------|-------|-------------|
| `Observation` | - | 40,168 | Clinical observations and measurements |
| `LabResult` | - | 25,366 | Laboratory test results |
| `VitalSign` | - | 14,802 | Vital signs (BP, HR, Temp, etc.) |

### Medical Events

| Label | Alias | Count | Description |
|-------|-------|-------|-------------|
| `Encounter` | `Visit` | 6,197 | Patient encounters/visits |
| `Procedure` | `MedicalProcedure` | 12,052 | Medical procedures performed |
| `ImagingStudy` | `Radiology` | 216 | Imaging/radiology studies |

### Conditions & Treatments

| Label | Alias | Count | Description |
|-------|-------|-------|-------------|
| `Condition` | `Diagnosis` | 3,573/3,439 | Medical conditions/diagnoses |
| `Medication` | `Prescription` | 3,884/3,778 | Prescribed medications |
| `Immunization` | `Vaccine` | 1,837 | Vaccination records |
| `CarePlan` | `TreatmentPlan` | 361/360 | Care and treatment plans |

### Patient History

| Label | Alias | Count | Description |
|-------|-------|-------|-------------|
| `Allergy` | - | 60 | Allergy information |
| `FamilyHistory` | - | 120 | Family medical history |
| `SocialHistory` | - | 48 | Social determinants of health |
| `Lifestyle` | - | 19 | Lifestyle factors |
| `Device` | `MedicalDevice` | 130 | Implanted/used medical devices |

### Healthcare Providers

| Label | Alias | Count | Description |
|-------|-------|-------|-------------|
| `Organization` | `HealthcareFacility` | 269 | Healthcare organizations |
| `Provider` | `Clinician` | 269 | Healthcare providers/clinicians |

---

## 🔗 Relationship Types

### Patient-Centric Relationships

```cypher
(:Person)-[:HAS_OBSERVATION]->(:Observation)      # 40,168
(:Person)-[:HAS_ENCOUNTER]->(:Encounter)          # 6,197
(:Person)-[:HAD_PROCEDURE]->(:Procedure)          # 12,052
(:Person)-[:HAS_CONDITION]->(:Condition)          # 3,559
(:Person)-[:TAKES_MEDICATION]->(:Medication)      # 3,823
(:Person)-[:RECEIVED_IMMUNIZATION]->(:Immunization) # 1,837
(:Person)-[:HAS_CARE_PLAN]->(:CarePlan)           # 361
(:Person)-[:HAS_IMAGING_STUDY]->(:ImagingStudy)   # 216
(:Person)-[:HAS_DEVICE]->(:Device)                # 130
(:Person)-[:HAS_ALLERGY]->(:Allergy)              # 52
(:Person)-[:HAS_FAMILY_HISTORY]->(:FamilyHistory) # 77
(:Person)-[:HAS_SOCIAL_HISTORY]->(:SocialHistory) # 11
(:Person)-[:HAS_LIFESTYLE]->(:Lifestyle)          # 19
(:Person)-[:HAS_AI_FEATURES]->(:AIFeatureSet)     # 133
(:Person)-[:HAS_RISK_FACTOR]->(:RiskFactor)       # 76
(:Person)-[:HAS_LAB_TREND]->(:LabTrend)           # 1
```

### Encounter-Based Relationships

```cypher
(:Encounter)-[:RECORDED_OBSERVATION]->(:Observation)     # 40,168
(:Encounter)-[:PERFORMED_PROCEDURE]->(:Procedure)        # 12,052
(:Encounter)-[:AT_ORGANIZATION]->(:Organization)         # 6,197
(:Encounter)-[:WITH_PROVIDER]->(:Provider)               # 6,197
(:Encounter)-[:PRESCRIBED_MEDICATION]->(:Medication)     # 3,778
(:Encounter)-[:DIAGNOSED_CONDITION]->(:Condition)        # 3,439
(:Encounter)-[:ADMINISTERED_IMMUNIZATION]->(:Immunization) # 1,837
(:Encounter)-[:CREATED_CARE_PLAN]->(:CarePlan)           # 360
(:Encounter)-[:ORDERED_IMAGING]->(:ImagingStudy)         # 216
(:Encounter)-[:IMPLANTED_DEVICE]->(:Device)              # 130
```

### Clinical Inference Relationships

```cypher
(:Condition)-[:SAME_DIAGNOSIS]->(:Condition)     # 347,296 (semantic linking)
(:Medication)-[:TREATS]->(:Condition)            # 63,343
(:Procedure)-[:TREATMENT_FOR]->(:Condition)      # 1,699
(:Provider)-[:WORKS_AT]->(:Organization)         # 269
```

---

## 📐 Entity Schemas

### Person/Patient Node

```json
{
  "synthea_id": "uuid-string",
  "name": "Full Name",
  "first_name": "First",
  "last_name": "Last",
  "gender": "M/F",
  "birthdate": "YYYY-MM-DD",
  "age": 45,
  "race": "White/Black/Asian/...",
  "ethnicity": "Hispanic/Non-Hispanic",
  "address": "Street Address",
  "city": "City",
  "state": "State",
  "zip": "12345",
  "marital_status": "S/M/D/W",
  "created_at": "datetime",
  "data_source": "Synthea/MCP_Created"
}
```

### AIFeatureSet Node (ML Features)

```json
{
  "patient_id": "synthea_id reference",
  "age_years": 45,
  "gender_numeric": 1,
  "height_cm": 175.0,
  "weight_kg": 80.0,
  "bmi": 26.1,
  "bp_systolic": 130,
  "bp_diastolic": 85,
  "cholesterol_level": 2,
  "glucose_level": 1,
  "is_smoker": 0,
  "smoking_history": 0,
  "alcohol_use": 0,
  "physical_activity": 1,
  "has_hypertension": 1,
  "has_heart_disease": 0,
  "hba1c_level": 5.7,
  "blood_glucose_fasting": 100,
  "created_at": "datetime"
}
```

### Condition Node

```json
{
  "synthea_id": "uuid-string",
  "code": "SNOMED-CT code",
  "description": "Condition description",
  "category": "chronic/acute",
  "onset_date": "YYYY-MM-DD",
  "abatement_date": "YYYY-MM-DD or null",
  "clinical_status": "active/resolved",
  "verification_status": "confirmed",
  "severity": "mild/moderate/severe"
}
```

### Medication Node

```json
{
  "synthea_id": "uuid-string",
  "code": "RxNorm code",
  "description": "Medication name",
  "base_cost": 50.00,
  "dispenses": 1,
  "total_cost": 50.00,
  "start_date": "YYYY-MM-DD",
  "stop_date": "YYYY-MM-DD or null",
  "reason_code": "SNOMED code",
  "reason_description": "Indication"
}
```

### Encounter Node

```json
{
  "synthea_id": "uuid-string",
  "encounter_class": "ambulatory/emergency/inpatient/...",
  "code": "SNOMED code",
  "description": "Encounter type",
  "start_time": "datetime",
  "stop_time": "datetime",
  "base_cost": 100.00,
  "total_claim_cost": 150.00,
  "payer_coverage": 120.00,
  "reason_code": "SNOMED code",
  "reason_description": "Visit reason"
}
```

### RiskFactor Node

```json
{
  "name": "Smoking/Obesity/Hypertension",
  "category": "cardiovascular/diabetes/lifestyle",
  "description": "Risk factor description",
  "severity_weight": 1.5
}
```

---

## 🔍 Common Query Patterns

### Get Patient with All Related Data

```cypher
MATCH (p:Person {synthea_id: $patient_id})
OPTIONAL MATCH (p)-[:HAS_CONDITION]->(c:Condition)
OPTIONAL MATCH (p)-[:TAKES_MEDICATION]->(m:Medication)
OPTIONAL MATCH (p)-[:HAS_AI_FEATURES]->(ai:AIFeatureSet)
OPTIONAL MATCH (p)-[:HAS_RISK_FACTOR]->(rf:RiskFactor)
RETURN p, collect(DISTINCT c) as conditions, 
       collect(DISTINCT m) as medications,
       ai, collect(DISTINCT rf) as risk_factors
```

### Get High-Risk Patients

```cypher
MATCH (p:Person)-[:HAS_RISK_FACTOR]->(rf:RiskFactor)
WITH p, collect(rf.name) as risks, count(rf) as risk_count
WHERE risk_count >= 2
OPTIONAL MATCH (p)-[:HAS_AI_FEATURES]->(ai:AIFeatureSet)
RETURN p.name, p.age, risks, ai.bmi, ai.bp_systolic
ORDER BY risk_count DESC
```

### Get AI Features for ML Model

```cypher
MATCH (p:Person)-[:HAS_AI_FEATURES]->(ai:AIFeatureSet)
RETURN p.synthea_id as patient_id,
       ai.age_years as age,
       ai.gender_numeric as gender,
       ai.bmi as bmi,
       ai.bp_systolic as ap_hi,
       ai.bp_diastolic as ap_lo,
       ai.cholesterol_level as cholesterol,
       ai.glucose_level as gluc,
       ai.is_smoker as smoke,
       ai.alcohol_use as alco,
       ai.physical_activity as active
```

### Find Conditions Treated by Medication

```cypher
MATCH (m:Medication)-[:TREATS]->(c:Condition)
RETURN m.description as medication, 
       collect(DISTINCT c.description) as treats_conditions
```

---

## 🎯 Visual Schema Diagram

```
                              ┌─────────────────┐
                              │   Organization  │
                              │ HealthcareFacil │
                              └────────▲────────┘
                                       │ WORKS_AT
                              ┌────────┴────────┐
                              │    Provider     │
                              │    Clinician    │
                              └────────▲────────┘
                                       │ WITH_PROVIDER
                                       │
┌──────────┐                  ┌────────┴────────┐                  ┌──────────────┐
│RiskFactor│◄─HAS_RISK_FACTOR─┤                 ├─AT_ORGANIZATION─►│ Organization │
└──────────┘                  │                 │                  └──────────────┘
                              │    Encounter    │
┌──────────┐                  │      Visit      │                  ┌──────────────┐
│AIFeature │◄─HAS_AI_FEATURES─┤                 ├PRESCRIBED_MED───►│  Medication  │
│   Set    │                  │                 │                  │ Prescription │
└──────────┘                  └────────▲────────┘                  └──────┬───────┘
                                       │                                  │
                              HAS_ENCOUNTER                            TREATS
                                       │                                  │
                              ┌────────┴────────┐                  ┌──────▼───────┐
┌──────────┐                  │                 │                  │  Condition   │
│  Allergy │◄───HAS_ALLERGY───┤     Person      ├─HAS_CONDITION───►│  Diagnosis   │
└──────────┘                  │     Patient     │                  └──────────────┘
                              │                 │
┌──────────┐                  │                 │                  ┌──────────────┐
│ Family   │◄─HAS_FAMILY_HIST─┤                 ├─TAKES_MEDICATION►│  Medication  │
│ History  │                  │                 │                  └──────────────┘
└──────────┘                  │                 │
                              │                 │                  ┌──────────────┐
┌──────────┐                  │                 ├─HAS_OBSERVATION─►│ Observation  │
│ Lifestyle│◄──HAS_LIFESTYLE──┤                 │                  │  LabResult   │
└──────────┘                  └────────┬────────┘                  │  VitalSign   │
                                       │                           └──────────────┘
                              HAD_PROCEDURE
                                       │                           ┌──────────────┐
                              ┌────────▼────────┐                  │ Immunization │
                              │   Procedure     ├─TREATMENT_FOR───►│   Vaccine    │
                              │MedicalProcedure │                  └──────────────┘
                              └─────────────────┘
```

---

## 📈 Statistics Summary

| Category | Count |
|----------|-------|
| **Patients (Person)** | 144 |
| **Total Observations** | 40,168 |
| **Conditions** | 3,573 |
| **Medications** | 3,884 |
| **Encounters** | 6,197 |
| **Procedures** | 12,052 |
| **AI Feature Sets** | 133 |
| **Risk Factor Links** | 76 |

---

## 🔧 Data Sources

1. **Synthea** - Synthetic patient data generator
2. **MCP Tools** - Real-time data from HospitalDB MCP server
3. **Manual Entry** - Specialized patient cases for ML testing

---

*Last Updated: February 10, 2026*
