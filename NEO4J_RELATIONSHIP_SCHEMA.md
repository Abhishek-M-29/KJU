# MediMax Neo4j Relationship Schema

Generated: 2025-09-15T00:00:00Z
Source: Live Neo4j database query (mapping summary)

This document describes the relationships present in the MediMax healthcare knowledge graph. It lists each relationship type, the typical start and end node labels, the property keys observed on those relationships, their counts in the graph, and a short description/purpose. Use this doc as an operational reference and for schema-driven development.

---

## Summary (top-level counts)
- Total relationships observed: 724 (visual) / 724 (live mapping total rows aggregated)
- Key node labels: Patient, Symptom, MedicalHistory, Medication, LabFinding, LabResult/TestResult, LabReport, Treatment, Condition, Encounter, LabStudy/DiagnosticStudy, Appointment, Person, Observation

---

## Relationship details

Below each entry shows:
- RelationshipType — StartLabels → EndLabels (count)
- Property keys observed
- Purpose / notes

### HAS_SYMPTOM — Patient → Symptom (65)
- Property keys: `date`, `relationship_type`, `severity`
- Purpose: Patient-level symptom entries (often simple symptom records with a date and severity).

### REPORTED_SYMPTOM — Appointment → Symptom (65)
- Property keys: `relationship_type`, `severity`
- Purpose: Symptoms reported at appointment intake (patient-reported).

### HAS_MEDICAL_HISTORY — Patient → MedicalHistory (64)
- Property keys: `type`, `date`, `relationship_type`, `severity`
- Purpose: Links patients to discrete medical history items (allergies, surgeries, family history, lifestyle).

### CONTAINS_RESULT — LabStudy/DiagnosticStudy → LabResult/TestResult (42)
- Property keys: `relationship_type`, `is_abnormal`, `created_at`, `result_sequence`
- Purpose: A diagnostic/lab study contains individual test results.

### HAS_LAB_RESULT — Person/Patient → LabResult/TestResult (42)
- Property keys: `relationship_type`, `is_abnormal`, `created_at`, `clinical_significance`, `result_date`
- Purpose: Patient or person linked to individual result records.

### TAKES_MEDICATION — Patient → Medication (42)
- Property keys: `date`, `status`, `relationship_type`, `prescriber`, `indication`
- Purpose: Medication prescriptions and active medications for patients.

### DOCUMENTED_SYMPTOM — Encounter/Appointment → Symptom/Observation (39)
- Property keys: `relationship_type`, `severity`, `created_at`, `documented_by`
- Purpose: Clinician-documented symptoms during encounters.

### HAS_SYMPTOM — Person/Patient → Symptom/Observation (39)
- Property keys: `relationship_type`, `severity`, `reported_date`, `created_at`, `duration`, `onset_type`
- Purpose: Clinical symptom records including onset/duration metadata.

### HAS_APPOINTMENT — Patient → Appointment (37)
- Property keys: `date`, `status`, `relationship_type`
- Purpose: Patient appointment records.

### CONTAINS_FINDING — LabReport → LabFinding (34)
- Property keys: `relationship_type`, `abnormal`
- Purpose: Lab report documents containing specific findings.

### HAS_LAB_FINDING — Patient → LabFinding (34)
- Property keys: `date`, `relationship_type`, `abnormal`
- Purpose: Patient-specific lab finding links.

### CONTAINS_FINDING — LabReport → LabFinding (31)
- Property keys: `relationship_type`, `flag`, `abnormal`
- Purpose: Alternate form of `CONTAINS_FINDING` with flag metadata.

### HAS_LAB_FINDING — Patient → LabFinding (31)
- Property keys: `date`, `relationship_type`, `flag`, `abnormal`
- Purpose: Patient lab finding with flag metadata.

### HAS_LAB_REPORT — Patient → LabReport (28)
- Property keys: `type`, `date`, `relationship_type`
- Purpose: Patient linked to lab report documents.

### TAKES_MEDICATION — Person/Patient → Medication/Treatment (28)
- Property keys: `status`, `relationship_type`, `dosage`, `prescribed_date`, `prescriber`, `created_at`, `frequency`
- Purpose: Medication entries including dosage and frequency.

### TREATS_CONDITION — Medication → MedicalHistory (28)
- Property keys: `relationship_type`
- Purpose: Medications mapped to the condition(s) they treat.

### HAS_CONDITION — Person/Patient → MedicalHistory/Condition (22)
- Property keys: `status`, `relationship_type`, `severity`, `created_at`, `condition_category`, `onset_date`
- Purpose: Patient conditions and medical history entries.

### HAS_ENCOUNTER — Person/Patient → Encounter/Appointment (20)
- Property keys: `status`, `relationship_type`, `created_at`, `encounter_date`, `encounter_type`, `provider`
- Purpose: Encounters (consultation, follow_up, routine_checkup, emergency).

### HAS_LAB_STUDY — Person/Patient → LabStudy/DiagnosticStudy (18)
- Property keys: `relationship_type`, `created_at`, `facility`, `ordering_provider`, `study_date`
- Purpose: Ordered diagnostic studies for patients.

### INDICATES_CONDITION — Symptom → MedicalHistory (6)
- Property keys: `relationship_type`
- Purpose: Explicit symptom -> condition associations.

### HAS_CONDITION — Person/Patient → MedicalHistory/Condition (5)
- Property keys: `status`, `relationship_type`, `severity`, `created_at`, `condition_category`
- Purpose: Another occurrence of `HAS_CONDITION` with slightly different observed keys.

### MAY_INDICATE — Symptom/Observation → MedicalHistory/Condition (4)
- Property keys: `relationship_type`, `created_at`, `confidence`
- Purpose: Probabilistic clinical indications.

---

## Graph diagram

Below is a concise diagram of the primary node labels and relationship types observed in the MediMax graph. It uses Mermaid syntax — render it in a Mermaid-enabled viewer (GitHub, VS Code Markdown preview with Mermaid support, etc.). The arrow labels show the relationship type and an approximate count observed in the dataset.

```mermaid
graph LR
    %% explicit node declarations help Mermaid parsers and avoid ambiguous tokens
    Patient[Patient]
    Appointment[Appointment]
    Encounter[Encounter]
    Symptom[Symptom]
    MedicalHistory[MedicalHistory]
    Medication[Medication]
    LabStudy[LabStudy]
    LabResult[LabResult]
    LabReport[LabReport]
    LabFinding[LabFinding]
    Condition[Condition]
    Person[Person]
    Observation[Observation]

    Patient -->|"HAS_APPOINTMENT (37)"| Appointment
    Patient -->|"HAS_ENCOUNTER (20)"| Encounter
    Patient -->|"HAS_SYMPTOM (104)"| Symptom
    Patient -->|"HAS_MEDICAL_HISTORY (64)"| MedicalHistory
    Patient -->|"TAKES_MEDICATION (70)"| Medication
    Patient -->|"HAS_LAB_STUDY (18)"| LabStudy
    Patient -->|"HAS_LAB_RESULT (42)"| LabResult
    Patient -->|"HAS_LAB_REPORT (28)"| LabReport
    LabStudy -->|"CONTAINS_RESULT (42)"| LabResult
    LabReport -->|"CONTAINS_FINDING (65)"| LabFinding
    Medication -->|"TREATS_CONDITION (28)"| MedicalHistory
    Appointment -->|"REPORTED_SYMPTOM (65)"| Symptom
    Encounter -->|"DOCUMENTED_SYMPTOM (39)"| Symptom
    Symptom -->|"MAY_INDICATE (4)"| MedicalHistory
    Symptom -->|"INDICATES_CONDITION (6)"| MedicalHistory
    MedicalHistory -->|"HAS_CONDITION (27)"| Condition
    Person -->|"REPRESENTS"| Patient
    Observation -->|"RELATES_TO"| Symptom
```

Notes:
- Counts are taken from the live mapping summary and the visual schema and are approximate indicators of cardinality.
- Mermaid rendering needs to be enabled in your Markdown viewer; if it doesn't render, the block will show as plain code.


## Recommended queries
- Schema summary:
```
MATCH (n)-[r]->(m)
RETURN type(r) AS relationship_type,
       labels(n) AS start_node_labels,
       labels(m) AS end_node_labels,
       keys(r) AS relationship_property_keys,
       count(*) AS occurrence_count
ORDER BY occurrence_count DESC, relationship_type;
```

- Export mapping to CSV (APOC required):
```
CALL apoc.export.csv.query("MATCH (n)-[r]->(m) RETURN type(r) AS relationship_type, labels(n) AS start_node_labels, labels(m) AS end_node_labels, keys(r) AS relationship_property_keys, count(*) AS occurrence_count ORDER BY occurrence_count DESC, relationship_type;", "relationship_mapping.csv", {});
```

---

## Suggested indexes & constraints
- Index: `:Patient(name)` or `:Patient(patient_id)`
- Index: `:Medication(name)`
- Constraint: `:Patient(patient_id) IS UNIQUE` if `patient_id` exists

---

## Notes & next steps
- There are duplicate/variant relationships (e.g., `HAS_SYMPTOM` appears twice with slightly different start labels and property keys). Consider normalizing label/relationship usage.
- I have created `neo4j_relationship_mappings_live.json` and `neo4j_relationship_mappings_live.csv` in the repository root.
- If you want, I can create a regenerating script `scripts/generate_relationship_mapping.py` that runs the mapping query and writes these files on demand.

---

If you'd like any adjustments (include example rows, expand to node property keys, enforce constraints), tell me and I'll add them.