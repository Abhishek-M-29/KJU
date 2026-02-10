# Neo4j Graph Database Guidelines - COMPLETE REFERENCE

This document provides a comprehensive guide to understanding and utilizing the MediMax patient-centric knowledge graph. It is intended to be the single source of truth for developers writing Cypher queries.

**Database Statistics:**
- **Total Node Labels:** 18 (including variations)
- **Total Relationship Types:** 17
- **Graph Architecture:** Patient-centric with full medical data hierarchy

## 1. Core Concept: The Patient-Centric Graph

The entire graph is designed around the `Patient` node. Every piece of information, from a lab result to a medication, is directly or indirectly connected to a patient. This ensures that all data is contextualized within a specific individual's health journey. When querying, you will almost always start your traversal from a `Patient` node.

**Key Architectural Principles:**
1. **Patient Centricity:** All nodes are connected to patients (directly or indirectly)
2. **Hierarchical Structure:** Lab data follows Report → Study → Result hierarchy
3. **Clinical Relationships:** Symptoms, conditions, and medications are interlinked
4. **Temporal Tracking:** All entities include timestamps and historical data

---

## 2. Complete Node Labels Reference

### **Central Entity Nodes**

#### `Patient` / `Person` - The Core Entity (16 instances)
- **Description**: The central entity representing individuals receiving healthcare. `Patient` and `Person` are used interchangeably as labels.
- **Key Properties**:
    - `patient_id`: (String) - **PRIMARY KEY** - Unique identifier for the patient
    - `name` / `full_name`: (String) - Patient's complete name
    - `dob`: (Date) - Date of birth (format: YYYY-MM-DD)
    - `gender` / `sex`: (String) - Patient's gender ("Male", "Female")
    - `graph_center`: (String) - Always "True", marking this as a central node
    - `node_type`: (String) - Always "Patient"
    - `entity_type`: (String) - Always "person"
    - `created_at`: (DateTime) - Node creation timestamp
    - `last_updated`: (DateTime) - Last modification timestamp

---

### **Clinical Encounter Nodes**

#### `Appointment` - Healthcare Appointments (57 instances)
- **Description**: Represents scheduled or completed healthcare appointments and visits.
- **Complete Properties**:
    - `appointment_id`: (String) - Unique appointment identifier
    - `patient_id`: (String) - **FOREIGN KEY** - Links to Patient
    - `name`: (String) - Appointment name/title
    - `appointment_date`: (Date) - Scheduled/actual appointment date
    - `appointment_time`: (Time) - Scheduled appointment time
    - `appointment_type`: (String) - Type of appointment ("follow_up", "consultation", etc.)
    - `status`: (String) - Appointment status ("completed", "scheduled", "cancelled")
    - `doctor_name` / `provider`: (String) - Healthcare provider name
    - `description`: (String) - Appointment description/notes
    - `clinical_notes`: (String) - Clinical observations from the visit
    - `encounter_date`: (Date) - Actual encounter date (may differ from appointment_date)
    - `encounter_status`: (String) - Status of the encounter
    - `encounter_type`: (String) - Type of encounter
    - `node_type`: (String) - Node classification
    - `entity_type`: (String) - Entity classification
    - `last_updated`: (DateTime) - Last modification timestamp

#### `Encounter` - Healthcare Encounters (20 instances)
- **Description**: Represents actual healthcare interactions/visits. Very similar to Appointment but focused on completed interactions.
- **Complete Properties**: *[Same as Appointment - these appear to be synonymous in the current implementation]*
    - All properties identical to `Appointment` nodes
    - Often used interchangeably with `Appointment`

---

### **Medical Condition Nodes**

#### `Condition` - Medical Conditions (27 instances)
- **Description**: Represents diagnosed medical conditions, diseases, or health problems.
- **Complete Properties**:
    - `history_id`: (String) - Unique condition/history identifier
    - `patient_id`: (String) - **FOREIGN KEY** - Links to Patient
    - `name` / `condition_name`: (String) - Name of the condition
    - `description`: (String) - Detailed condition description
    - `category`: (String) - Condition category ("condition", "disease", etc.)
    - `condition_type`: (String) - Type classification of the condition
    - `status`: (String) - Current status ("active", "resolved", "managed")
    - `severity`: (String) - Severity level ("mild", "moderate", "severe")
    - `is_chronic`: (Boolean) - Whether condition is chronic
    - `node_type`: (String) - Node classification
    - `entity_type`: (String) - Entity classification
    - `last_updated`: (DateTime) - Last modification timestamp

#### `MedicalHistory` - Historical Medical Events (91 instances)
- **Description**: Broader category encompassing medical history events, including conditions.
- **Complete Properties**: *[Identical to Condition]*
    - Contains the same property structure as `Condition`
    - Represents historical medical events and ongoing conditions
    - Larger dataset suggesting it's the primary label for medical conditions

---

### **Medication & Treatment Nodes**

#### `Medication` - Prescribed Medications (70 instances)
- **Description**: Represents prescribed medications and pharmaceutical treatments.
- **Complete Properties**:
    - `medication_id`: (String) - Unique medication record identifier
    - `patient_id`: (String) - **FOREIGN KEY** - Links to Patient
    - `name` / `medicine_name` / `drug_name`: (String) - Medication name
    - `dosage` / `dose`: (String) - Prescribed dosage (e.g., "10mg", "5ml")
    - `frequency`: (String) - Administration frequency ("Once daily", "Twice daily", "As needed")
    - `route`: (String) - Administration route ("oral", "injection", "topical")
    - `status`: (String) - Medication status ("active", "discontinued", "completed")
    - `is_active`: (Boolean) - Whether medication is currently active
    - `prescribed_by` / `prescriber`: (String) - Prescribing physician name
    - `prescribed_date` / `start_date`: (Date) - Date medication was prescribed/started
    - `node_type`: (String) - Node classification
    - `entity_type`: (String) - Entity classification
    - `last_updated`: (DateTime) - Last modification timestamp

#### `Treatment` - Medical Treatments (28 instances)
- **Description**: Represents broader medical treatments, including medications and therapies.
- **Complete Properties**: *[Identical to Medication]*
    - Same property structure as `Medication`
    - May include non-pharmaceutical treatments
    - Broader category that encompasses medications

---

### **Symptom & Observation Nodes**

#### `Symptom` - Patient Symptoms (104 instances)
- **Description**: Represents symptoms reported by or observed in patients.
- **Complete Properties**:
    - `symptom_id`: (String) - Unique symptom identifier
    - `patient_id`: (String) - **FOREIGN KEY** - Links to Patient
    - `appointment_id`: (String) - **FOREIGN KEY** - Links to related appointment
    - `name` / `symptom_name` / `observation_name`: (String) - Symptom name
    - `description`: (String) - Detailed symptom description
    - `severity`: (String) - Symptom severity ("mild", "moderate", "severe")
    - `reported_date` / `observation_date`: (Date) - Date symptom was reported/observed
    - `duration`: (String) - How long symptom has been present
    - `onset_type`: (String) - Type of symptom onset
    - `onset_pattern`: (String) - Pattern of symptom occurrence
    - `observation_type`: (String) - Type of observation
    - `clinical_significance`: (String) - Clinical importance of the symptom
    - `node_type`: (String) - Node classification
    - `entity_type`: (String) - Entity classification
    - `last_updated`: (DateTime) - Last modification timestamp

#### `Observation` - Clinical Observations (39 instances)
- **Description**: Represents clinical observations made during healthcare encounters.
- **Complete Properties**: *[Identical to Symptom]*
    - Same property structure as `Symptom`
    - Used for more formal clinical observations
    - Often interchangeable with `Symptom` in current implementation

---

### **Laboratory & Diagnostic Nodes**

#### `LabReport` - Laboratory Reports (28 instances)
- **Description**: Container node representing complete laboratory reports from a single order.
- **Complete Properties**:
    - `lab_report_id`: (String) - **PRIMARY KEY** - Unique report identifier
    - `patient_id`: (String) - **FOREIGN KEY** - Links to Patient
    - `type`: (String) - Report type ("Depression Screening", "Blood Panel", etc.)
    - `date`: (Date) - Date of the report
    - `facility`: (String) - Laboratory facility name
    - `doctor`: (String) - Ordering physician
    - `node_type`: (String) - Node classification

#### `LabStudy` / `DiagnosticStudy` - Laboratory Studies (18 instances each)
- **Description**: Represents specific laboratory studies or test panels within a report.
- **Complete Properties**:
    - `patient_id`: (String) - **FOREIGN KEY** - Links to Patient
    - `lab_report_id`: (String) - **FOREIGN KEY** - Links to LabReport
    - `name` / `study_name`: (String) - Name of the study/panel
    - `description`: (String) - Study description
    - `study_date` / `lab_date`: (Date) - Date study was performed
    - `study_type` / `lab_type`: (String) - Type of study
    - `study_category`: (String) - Category classification
    - `facility` / `lab_facility`: (String) - Facility where study was performed
    - `ordering_provider` / `ordering_doctor`: (String) - Physician who ordered the study
    - `node_type`: (String) - Node classification
    - `entity_type`: (String) - Entity classification
    - `last_updated`: (DateTime) - Last modification timestamp

#### `LabResult` / `TestResult` - Individual Test Results (42 instances each)
- **Description**: Represents individual test results within a laboratory study.
- **Complete Properties**:
    - `lab_finding_id`: (String) - Unique finding identifier
    - `patient_id`: (String) - **FOREIGN KEY** - Links to Patient
    - `lab_report_id`: (String) - **FOREIGN KEY** - Links to LabReport
    - `name` / `test_name` / `result_name`: (String) - Test name
    - `value` / `result_value` / `test_value`: (String/Number) - Test result value
    - `unit` / `test_unit`: (String) - Unit of measurement ("mg/dL", "mmol/L", etc.)
    - `reference_range` / `normal_range`: (String) - Normal reference range
    - `abnormal_flag`: (String) - Abnormality indicator ("high", "low", "normal")
    - `is_abnormal`: (Boolean) - Whether result is outside normal range
    - `result_type`: (String) - Type of result
    - `result_status`: (String) - Status of the result
    - `result_date` / `test_date`: (Date) - Date of the test
    - `clinical_significance`: (String) - Clinical importance of the result
    - `node_type`: (String) - Node classification
    - `entity_type`: (String) - Entity classification
    - `last_updated`: (DateTime) - Last modification timestamp

#### `LabFinding` - Laboratory Findings (65 instances)
- **Description**: Represents significant laboratory findings, often abnormal results.
- **Complete Properties**:
    - `patient_id`: (String) - **FOREIGN KEY** - Links to Patient
    - `lab_report_id`: (String) - **FOREIGN KEY** - Links to LabReport
    - `test_name`: (String) - Name of the test
    - `value`: (String/Number) - Test value
    - `unit`: (String) - Unit of measurement
    - `abnormal_flag`: (String) - Abnormality indicator
    - `is_abnormal`: (Boolean) - Whether finding is abnormal
    - `date`: (Date) - Date of the finding
    - `node_type`: (String) - Node classification

---

## 3. Complete Relationship Types Reference

### **Patient-Centric Relationships (Direct Patient Connections)**

#### `HAS_CONDITION` (27 instances)
- **Pattern**: `(Patient)-[:HAS_CONDITION]->(Condition|MedicalHistory)`
- **Description**: Connects patients to their diagnosed medical conditions
- **Usage**: Primary relationship for linking patients to their health conditions
- **Properties**: None (relationship carries no additional data)

#### `TAKES_MEDICATION` (70 instances)
- **Pattern**: `(Patient)-[:TAKES_MEDICATION]->(Medication|Treatment)`
- **Description**: Links patients to medications they are prescribed or taking
- **Usage**: Core relationship for medication management queries
- **Properties**: None

#### `HAS_APPOINTMENT` (37 instances)
- **Pattern**: `(Patient)-[:HAS_APPOINTMENT]->(Appointment)`
- **Description**: Connects patients to their scheduled or completed appointments
- **Usage**: For appointment history and scheduling queries
- **Properties**: None

#### `HAS_ENCOUNTER` (20 instances)
- **Pattern**: `(Patient)-[:HAS_ENCOUNTER]->(Encounter)`
- **Description**: Links patients to their healthcare encounters/visits
- **Usage**: For encounter history and clinical visit tracking
- **Properties**: None

#### `HAS_SYMPTOM` (104 instances)
- **Pattern**: `(Patient)-[:HAS_SYMPTOM]->(Symptom)`
- **Description**: Connects patients to their reported or observed symptoms
- **Usage**: For symptom tracking and clinical assessment
- **Properties**: None

#### `HAS_MEDICAL_HISTORY` (64 instances)
- **Pattern**: `(Patient)-[:HAS_MEDICAL_HISTORY]->(MedicalHistory)`
- **Description**: Links patients to their broader medical history events
- **Usage**: For comprehensive medical history queries
- **Properties**: None

#### `HAS_LAB_REPORT` (28 instances)
- **Pattern**: `(Patient)-[:HAS_LAB_REPORT]->(LabReport)`
- **Description**: Connects patients to their laboratory reports
- **Usage**: For accessing complete lab reports
- **Properties**: None

#### `HAS_LAB_STUDY` (18 instances)
- **Pattern**: `(Patient)-[:HAS_LAB_STUDY]->(LabStudy|DiagnosticStudy)`
- **Description**: Links patients directly to specific lab studies
- **Usage**: For direct access to specific diagnostic studies
- **Properties**: None

#### `HAS_LAB_RESULT` (42 instances)
- **Pattern**: `(Patient)-[:HAS_LAB_RESULT]->(LabResult|TestResult)`
- **Description**: Connects patients directly to individual lab results
- **Usage**: For direct result queries without traversing hierarchy
- **Properties**: None

#### `HAS_LAB_FINDING` (65 instances)
- **Pattern**: `(Patient)-[:HAS_LAB_FINDING]->(LabFinding)`
- **Description**: Links patients to significant laboratory findings
- **Usage**: For accessing notable or abnormal lab findings
- **Properties**: None

### **Clinical & Diagnostic Relationships**

#### `INDICATES_CONDITION` (6 instances)
- **Pattern**: `(Symptom|LabResult|LabFinding)-[:INDICATES_CONDITION]->(Condition|MedicalHistory)`
- **Description**: Strong clinical link suggesting symptom/result strongly indicates a condition
- **Usage**: For diagnostic reasoning and condition correlation
- **Properties**: None
- **Clinical Significance**: High confidence diagnostic relationship

#### `MAY_INDICATE` (4 instances)
- **Pattern**: `(Symptom|LabResult)-[:MAY_INDICATE]->(Condition|MedicalHistory)`
- **Description**: Weaker clinical link suggesting possible condition correlation
- **Usage**: For differential diagnosis and potential condition exploration
- **Properties**: None
- **Clinical Significance**: Lower confidence diagnostic relationship

#### `TREATS_CONDITION` (28 instances)
- **Pattern**: `(Medication|Treatment)-[:TREATS_CONDITION]->(Condition|MedicalHistory)`
- **Description**: Links medications/treatments to the conditions they treat
- **Usage**: For treatment plan analysis and medication-condition mapping
- **Properties**: None

#### `DOCUMENTED_SYMPTOM` (39 instances)
- **Pattern**: `(Encounter|Appointment)-[:DOCUMENTED_SYMPTOM]->(Symptom|Observation)`
- **Description**: Shows symptoms that were documented during specific encounters
- **Usage**: For encounter-specific symptom tracking
- **Properties**: None

#### `REPORTED_SYMPTOM` (65 instances)
- **Pattern**: `(Patient|Encounter)-[:REPORTED_SYMPTOM]->(Symptom)`
- **Description**: Links to symptoms that were specifically reported (vs. observed)
- **Usage**: For patient-reported symptom analysis
- **Properties**: None

### **Hierarchical/Structural Relationships**

#### `CONTAINS_FINDING` (65 instances)
- **Pattern**: `(LabReport)-[:CONTAINS_FINDING]->(LabFinding)`
- **Description**: Links laboratory reports to their individual findings
- **Usage**: For navigating from reports to specific findings
- **Properties**: None

#### `CONTAINS_RESULT` (42 instances)
- **Pattern**: `(LabStudy|DiagnosticStudy)-[:CONTAINS_RESULT]->(LabResult|TestResult)`
- **Description**: Links laboratory studies to their individual test results
- **Usage**: For navigating from studies to specific results
- **Properties**: None

---

## 4. Tested and Verified Working Query Examples

**Important Note:** All queries below have been tested and verified to return actual data.

### **Query 1: Complete Patient Medical Profile (TESTED ✅)**
Get comprehensive medical information for a specific patient:

```cypher
MATCH (p:Patient) WHERE toInteger(p.patient_id) = 7
OPTIONAL MATCH (p)-[:HAS_CONDITION]->(cond)
OPTIONAL MATCH (p)-[:TAKES_MEDICATION]->(med)
OPTIONAL MATCH (p)-[:HAS_SYMPTOM]->(symp)
OPTIONAL MATCH (p)-[:HAS_LAB_REPORT]->(lab)
RETURN p.name AS patientName,
       p.dob AS dateOfBirth,
       p.gender AS gender,
       collect(DISTINCT cond.name) AS conditions,
       collect(DISTINCT med.name + ' (' + coalesce(med.dosage, 'No dose') + ')') AS medications,
       collect(DISTINCT symp.name) AS symptoms,
       collect(DISTINCT lab.type) AS labReports
```
**Expected Output:** Returns Maria Elena Gonzalez with 10 conditions, 14 medications, 16 symptoms, and lab reports.

### **Query 2: Find Patients with Specific Conditions (TESTED ✅)**
Search for patients with diabetes or cancer:

```cypher
MATCH (p)-[:HAS_CONDITION]->(c:Condition)
WHERE c.name CONTAINS 'Diabetes' OR c.name CONTAINS 'Cancer'
RETURN p.patient_id AS patientId,
       p.name AS patientName,
       collect(c.name) AS conditions
ORDER BY p.name
```
**Expected Output:** Returns 3 patients: James Chen (Prostate Cancer), Maria Elena Gonzalez (Type 2 Diabetes Mellitus), Robert Johnson (Type 2 Diabetes).

### **Query 3: Most Common Medications Analysis (TESTED ✅)**
Analyze which medications are prescribed most frequently:

```cypher
MATCH (p)-[:TAKES_MEDICATION]->(m)
RETURN m.name AS medicationName,
       m.dosage AS commonDosage,
       collect(p.name) AS patients,
       count(p) AS patientCount
ORDER BY patientCount DESC
LIMIT 5
```
**Expected Output:** Returns top 5 medications with Aspirin (81mg) being most common (3 patients), followed by Metformin, Multivitamin, Lisinopril, and Amlodipine (2 patients each).

### **Query 4: Database Overview Statistics (TESTED ✅)**
Get comprehensive database statistics:

```cypher
MATCH (p:Patient)
OPTIONAL MATCH (p)-[:HAS_CONDITION]->(c)
OPTIONAL MATCH (p)-[:TAKES_MEDICATION]->(m)
OPTIONAL MATCH (p)-[:HAS_SYMPTOM]->(s)
OPTIONAL MATCH (p)-[:HAS_LAB_REPORT]->(l)
RETURN count(DISTINCT p) AS totalPatients,
       count(DISTINCT c) AS totalConditions,
       count(DISTINCT m) AS totalMedications,
       count(DISTINCT s) AS totalSymptoms,
       count(DISTINCT l) AS totalLabReports
```
**Expected Output:** Returns 16 patients, 27 conditions, 70 medications, 104 symptoms, 28 lab reports.

### **Query 5: Patient List with Condition Counts (TESTED ✅)**
List all patients and their condition counts:

```cypher
MATCH (p)-[:HAS_CONDITION]->(c) 
RETURN p.patient_id AS patientId,
       p.name AS patientName,
       count(c) AS conditionCount 
ORDER BY conditionCount DESC
```
**Expected Output:** Returns patients ordered by condition count, with Maria Elena Gonzalez having the most conditions (10).

### **Query 6: All Patients Basic Information (TESTED ✅)**
Get basic information for all patients:

```cypher
MATCH (p:Patient) 
RETURN p.patient_id AS patientId,
       p.name AS patientName,
       p.dob AS dateOfBirth,
       p.gender AS gender
ORDER BY p.name
```
**Expected Output:** Returns 16 patients with their basic demographic information.

### **Query 7: Medication Usage by Patient (TESTED ✅)**
Show medication usage patterns:

```cypher
MATCH (p)-[:TAKES_MEDICATION]->(m)
RETURN p.name AS patient,
       count(m) AS medicationCount,
       collect(m.name) AS medications
ORDER BY medicationCount DESC
LIMIT 5
```
**Expected Output:** Returns top 5 patients by medication count, showing which patients are on the most medications.

### **Query 8: Symptom Frequency Analysis (TESTED ✅)**
Analyze which symptoms are most common:

```cypher
MATCH (p)-[:HAS_SYMPTOM]->(s)
RETURN s.name AS symptom,
       count(p) AS patientCount,
       collect(DISTINCT p.name) AS affectedPatients
ORDER BY patientCount DESC
LIMIT 10
```
**Expected Output:** Returns the most frequently reported symptoms across all patients.

### **Query 9: Specific Patient Conditions (TESTED ✅)**
Get detailed conditions for a specific patient:

```cypher
MATCH (p:Patient) WHERE toInteger(p.patient_id) = 7
OPTIONAL MATCH (p)-[:HAS_CONDITION]->(cond)
RETURN p.name AS patientName,
       collect(DISTINCT cond.name) AS conditions
```
**Expected Output:** Returns Maria Elena Gonzalez with her 10 medical conditions.

### **Query 10: Relationship Count Summary (TESTED ✅)**
Count all relationship types in the database:

```cypher
MATCH ()-[r]->()
RETURN type(r) AS relationshipType,
       count(r) AS count
ORDER BY count DESC
```
**Expected Output:** Returns all relationship types with their counts, showing HAS_SYMPTOM as most common (104), followed by TAKES_MEDICATION (70), etc.

---

## 5. Data Quality and Consistency Notes

### **Node Label Overlaps**
- `Patient` and `Person`: Identical structure, used interchangeably
- `Condition` and `MedicalHistory`: Same properties, different usage contexts
- `Medication` and `Treatment`: Identical structure, `Treatment` is broader category
- `Symptom` and `Observation`: Same properties, `Observation` more clinical
- `LabResult` and `TestResult`: Identical structure and usage
- `LabStudy` and `DiagnosticStudy`: Same properties and purpose

### **Key Identifier Patterns**
- All nodes have `patient_id` for patient linkage
- Lab-related nodes share `lab_report_id` for hierarchy
- Appointments have `appointment_id` for encounter linking
- Most nodes have `node_type` and `entity_type` for classification

### **Date/Time Handling**
- Dates stored as strings in YYYY-MM-DD format
- DateTime stamps include timezone information
- Always use date() function for date comparisons in queries

### **Boolean Properties**
- `is_abnormal`: Boolean for lab results
- `is_chronic`: Boolean for conditions
- `is_active`: Boolean for medications
- `graph_center`: String "True" for Patient nodes (not boolean)

---

## 6. Performance Optimization Guidelines

### **Indexing Recommendations**
```cypher
// Recommended indexes for optimal performance
CREATE INDEX patient_id_index FOR (p:Patient) ON (p.patient_id);
CREATE INDEX condition_patient_index FOR (c:Condition) ON (c.patient_id);
CREATE INDEX medication_patient_index FOR (m:Medication) ON (m.patient_id);
CREATE INDEX lab_report_patient_index FOR (lr:LabReport) ON (lr.patient_id);
CREATE INDEX symptom_patient_index FOR (s:Symptom) ON (s.patient_id);
```

### **Query Best Practices**
1. **Always start with Patient**: Use patient_id as entry point
2. **Use OPTIONAL MATCH**: For relationships that may not exist
3. **Limit result sets**: Use LIMIT for large datasets
4. **Filter early**: Apply WHERE clauses as early as possible
5. **Use relationship direction**: Specify direction for better performance
6. **Aggregate efficiently**: Use collect() for grouping related data

This comprehensive guide covers all 18 node types and 17 relationship types in the MediMax knowledge graph, providing complete property listings, usage patterns, and advanced querying examples for efficient graph traversal and analysis.
