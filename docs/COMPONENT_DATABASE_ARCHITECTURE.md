# MediMax Database Architecture - Comprehensive Medical Data Management

## 🗄️ Overview

The MediMax Database Architecture provides the foundational data layer for comprehensive healthcare management, implementing a sophisticated dual-database approach with MariaDB for transactional data and Neo4j for complex medical relationships. This architecture enables atomic fact storage, temporal tracking, and advanced medical analytics through patient-centric design principles.

## 🎯 Core Design Principles

- **Atomic Facts Storage**: Granular medical information for precise tracking
- **Patient-Centric Design**: All data organized around patient entities
- **Temporal Tracking**: Complete audit trails with timestamps
- **Normalized Structure**: Eliminates redundancy while maintaining performance
- **Graph Relationships**: Complex medical relationships in Neo4j
- **Scalable Architecture**: Designed for healthcare enterprise requirements

## 🏗️ Dual Database Architecture

### Architecture Overview
```
┌─────────────────────────────────────┐
│         Application Layer           │
│    (FastAPI, Chat API, Agents)      │
└─────────────┬───────────────────────┘
              │ SQL/Cypher Queries
┌─────────────▼───────────────────────┐
│        Database Abstraction         │
│                                     │
│ ├── SQL Query Builder              │
│ ├── Cypher Query Generator          │
│ ├── Connection Pool Management      │
│ └── Transaction Coordination        │
└─────┬───────────────────────┬───────┘
      │                       │
┌─────▼───────┐      ┌────────▼──────┐
│   MariaDB   │      │     Neo4j     │
│ (Port 3305) │      │  (AuraDB)     │
│             │      │               │
│ Transactional│      │ Relationships │
│ ACID Data   │      │ Graph Queries │
│ 11 Tables   │      │ 18 Node Types │
│ Atomic Facts│      │ 17 Relations  │
└─────────────┘      └───────────────┘
```

### Technology Stack
- **Relational DB**: MariaDB/MySQL for ACID transactions
- **Graph DB**: Neo4j AuraDB for relationship modeling
- **Connectivity**: PyMySQL for SQL, Neo4j Python driver for Cypher
- **Connection Pooling**: Efficient connection management
- **Query Optimization**: Indexed searches and optimized queries

## 📊 MariaDB - Atomic Facts Schema

### Database Configuration
```python
# Production Database Configuration
DB_CONFIG = {
    "host": "9f12fn.h.filess.io",
    "port": 3305,
    "database": "Hospital_controlmet",
    "user": "Hospital_controlmet",
    "password": "secure_password",
    "charset": "utf8mb4",
    "autocommit": True
}
```

### Core Tables Architecture

#### 1. Patient Table (Central Entity)
```sql
CREATE TABLE Patient (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    dob DATE,
    sex ENUM('Male', 'Female', 'Other'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_patient_name (name),
    INDEX idx_patient_dob (dob),
    INDEX idx_patient_sex (sex)
);
```

**Purpose**: Central entity storing basic demographic information
**Relationships**: Parent table for all medical records
**Atomic Facts**: Name, DOB, gender stored as individual facts

#### 2. Medical_History Table
```sql
CREATE TABLE Medical_History (
    history_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    history_type ENUM('allergy', 'surgery', 'chronic_condition', 'family_history', 'lifestyle'),
    history_item VARCHAR(255) NOT NULL,
    history_details TEXT,
    history_date DATE,
    severity ENUM('Mild', 'Moderate', 'Severe', 'Critical'),
    is_active TINYINT DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE,
    INDEX idx_history_patient (patient_id),
    INDEX idx_history_type (history_type),
    INDEX idx_history_date (history_date)
);
```

**Atomic Facts Design**: 
- Each medical history item stored as separate record
- Granular categorization (allergy, surgery, chronic condition)
- Temporal tracking with severity classification

#### 3. Appointment Table
```sql
CREATE TABLE Appointment (
    appointment_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME,
    status ENUM('Scheduled', 'Confirmed', 'Pending', 'Completed', 'Cancelled', 'No_Show'),
    appointment_type ENUM('Regular', 'Emergency', 'Follow_up', 'Consultation', 'Surgery'),
    doctor_name VARCHAR(255),
    notes TEXT,
    
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE,
    INDEX idx_appointment_patient (patient_id),
    INDEX idx_appointment_date (appointment_date),
    INDEX idx_appointment_status (status)
);
```

#### 4. Appointment_Symptom Table
```sql
CREATE TABLE Appointment_Symptom (
    symptom_id INT PRIMARY KEY AUTO_INCREMENT,
    appointment_id INT NOT NULL,
    symptom_name VARCHAR(255) NOT NULL,
    symptom_description TEXT,
    severity ENUM('Mild', 'Moderate', 'Severe', 'Critical'),
    duration VARCHAR(100),
    onset_type ENUM('Sudden', 'Gradual', 'Chronic', 'Intermittent'),
    
    FOREIGN KEY (appointment_id) REFERENCES Appointment(appointment_id) ON DELETE CASCADE,
    INDEX idx_symptom_appointment (appointment_id),
    INDEX idx_symptom_name (symptom_name),
    INDEX idx_symptom_severity (severity)
);
```

**Granular Symptom Tracking**:
- Each symptom recorded as atomic fact
- Linked to specific appointments
- Detailed characterization (severity, duration, onset)

#### 5. Medication Table
```sql
CREATE TABLE Medication (
    medication_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    medicine_name VARCHAR(255) NOT NULL,
    is_continued TINYINT DEFAULT 1,
    prescribed_date DATE NOT NULL,
    discontinued_date DATE,
    dosage VARCHAR(100),
    frequency VARCHAR(100),
    prescribed_by VARCHAR(255),
    
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE,
    INDEX idx_medication_patient (patient_id),
    INDEX idx_medication_name (medicine_name),
    INDEX idx_medication_status (is_continued)
);
```

#### 6. Medication_Purpose Table
```sql
CREATE TABLE Medication_Purpose (
    purpose_id INT PRIMARY KEY AUTO_INCREMENT,
    medication_id INT NOT NULL,
    condition_name VARCHAR(255) NOT NULL,
    purpose_description TEXT,
    
    FOREIGN KEY (medication_id) REFERENCES Medication(medication_id) ON DELETE CASCADE,
    INDEX idx_purpose_medication (medication_id),
    INDEX idx_purpose_condition (condition_name)
);
```

**Multi-Purpose Medication Tracking**:
- Single medication can treat multiple conditions
- Atomic relationship between medication and condition
- Detailed purpose descriptions

#### 7. Lab_Report Table
```sql
CREATE TABLE Lab_Report (
    lab_report_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    lab_date DATE NOT NULL,
    lab_type VARCHAR(255),
    ordering_doctor VARCHAR(255),
    lab_facility VARCHAR(255),
    
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE,
    INDEX idx_lab_patient (patient_id),
    INDEX idx_lab_date (lab_date),
    INDEX idx_lab_type (lab_type)
);
```

#### 8. Lab_Finding Table
```sql
CREATE TABLE Lab_Finding (
    lab_finding_id INT PRIMARY KEY AUTO_INCREMENT,
    lab_report_id INT NOT NULL,
    test_name VARCHAR(255) NOT NULL,
    test_value VARCHAR(255) NOT NULL,
    test_unit VARCHAR(50),
    reference_range VARCHAR(100),
    is_abnormal TINYINT DEFAULT 0,
    abnormal_flag ENUM('High', 'Low', 'Critical_High', 'Critical_Low'),
    
    FOREIGN KEY (lab_report_id) REFERENCES Lab_Report(lab_report_id) ON DELETE CASCADE,
    INDEX idx_finding_report (lab_report_id),
    INDEX idx_finding_test (test_name),
    INDEX idx_finding_abnormal (is_abnormal)
);
```

**Granular Lab Data**:
- Each test result as atomic fact
- Structured abnormal flag system
- Reference range tracking for clinical context

#### 9. Report Table
```sql
CREATE TABLE Report (
    report_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    report_type ENUM('Radiology', 'Pathology', 'Clinical', 'Discharge', 'Consultation'),
    report_date DATE NOT NULL,
    complete_report LONGTEXT,
    report_summary TEXT,
    doctor_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE,
    INDEX idx_report_patient (patient_id),
    INDEX idx_report_type (report_type),
    INDEX idx_report_date (report_date)
);
```

#### 10. Report_Finding Table
```sql
CREATE TABLE Report_Finding (
    finding_id INT PRIMARY KEY AUTO_INCREMENT,
    report_id INT NOT NULL,
    finding_key VARCHAR(255) NOT NULL,
    finding_value VARCHAR(255) NOT NULL,
    finding_unit VARCHAR(50),
    normal_range VARCHAR(100),
    is_abnormal TINYINT DEFAULT 0,
    abnormal_severity ENUM('Mild', 'Moderate', 'Severe', 'Critical'),
    
    FOREIGN KEY (report_id) REFERENCES Report(report_id) ON DELETE CASCADE,
    INDEX idx_finding_report (report_id),
    INDEX idx_finding_key (finding_key),
    INDEX idx_finding_abnormal (is_abnormal)
);
```

#### 11. Chat_History Table
```sql
CREATE TABLE Chat_History (
    chat_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    message_text TEXT NOT NULL,
    message_type ENUM('Patient', 'Provider', 'System', 'Bot'),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(100),
    
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE,
    INDEX idx_chat_patient (patient_id),
    INDEX idx_chat_session (session_id),
    INDEX idx_chat_timestamp (timestamp)
);
```

## 🕸️ Neo4j - Knowledge Graph Architecture

### Graph Database Configuration
```python
# Neo4j AuraDB Configuration
NEO4J_CONFIG = {
    "uri": "neo4j+s://98d1982d.databases.neo4j.io",
    "user": "98d1982d",
    "password": "secure_aura_password",
    "database": "neo4j"
}
```

### Node Types and Relationships

#### Core Node Types
```cypher
// Patient/Person - Central entity (16 instances)
CREATE (p:Patient:Person {
    patient_id: "unique_id",
    name: "Full Name",
    dob: date("1970-01-01"),
    gender: "Male/Female",
    graph_center: "True",
    node_type: "Patient",
    entity_type: "person"
})

// Medical conditions (91 instances combined)
CREATE (c:Condition:MedicalHistory {
    history_id: "unique_id",
    patient_id: "patient_ref",
    name: "Condition Name",
    description: "Detailed description",
    category: "condition",
    severity: "mild/moderate/severe",
    status: "active/resolved",
    is_chronic: true/false
})

// Medications (70 instances)
CREATE (m:Medication {
    medication_id: "unique_id",
    patient_id: "patient_ref",
    name: "Medication Name",
    dosage: "Dosage Info",
    frequency: "Frequency",
    status: "active/discontinued",
    prescribed_date: date("2024-01-01")
})
```

#### Relationship Types
```cypher
// Core patient relationships
(Patient)-[:HAS_MEDICAL_HISTORY]->(MedicalHistory)
(Patient)-[:TAKES_MEDICATION]->(Medication)
(Patient)-[:HAS_SYMPTOM]->(Symptom)
(Patient)-[:HAS_APPOINTMENT]->(Appointment)
(Patient)-[:HAS_LAB_RESULT]->(LabResult)

// Clinical relationships
(Medication)-[:TREATS_CONDITION]->(MedicalHistory)
(Symptom)-[:INDICATES_CONDITION]->(MedicalHistory)
(Appointment)-[:REPORTED_SYMPTOM]->(Symptom)
(LabStudy)-[:CONTAINS_RESULT]->(LabResult)

// Hierarchical lab data
(LabReport)-[:CONTAINS_FINDING]->(LabFinding)
(LabStudy)-[:CONTAINS_RESULT]->(TestResult)
```

### Knowledge Graph Creation Process
```python
def create_patient_knowledge_graph(patient_data: dict):
    """Create comprehensive patient-centric knowledge graph"""
    
    with neo4j_session() as session:
        # 1. Create central Patient node
        session.run("""
            CREATE (p:Patient:Person {
                patient_id: $patient_id,
                name: $name,
                dob: $dob,
                gender: $gender,
                graph_center: "True",
                node_type: "Patient",
                created_at: datetime(),
                last_updated: datetime()
            })
        """, patient_data['patient'])
        
        # 2. Create medical history nodes and relationships
        for history in patient_data['medical_history']:
            session.run("""
                MATCH (p:Patient {patient_id: $patient_id})
                CREATE (h:MedicalHistory {
                    history_id: $history_id,
                    name: $history_item,
                    category: $history_type,
                    severity: $severity,
                    status: CASE WHEN $is_active = 1 THEN 'active' ELSE 'resolved' END
                })
                CREATE (p)-[:HAS_MEDICAL_HISTORY {
                    date: $history_date,
                    relationship_type: "medical_history",
                    severity: $severity
                }]->(h)
            """, history)
        
        # 3. Create medication nodes and relationships
        for medication in patient_data['medications']:
            session.run("""
                MATCH (p:Patient {patient_id: $patient_id})
                CREATE (m:Medication {
                    medication_id: $medication_id,
                    name: $medicine_name,
                    dosage: $dosage,
                    frequency: $frequency,
                    status: CASE WHEN $is_continued = 1 THEN 'active' ELSE 'discontinued' END
                })
                CREATE (p)-[:TAKES_MEDICATION {
                    prescribed_date: $prescribed_date,
                    prescriber: $prescribed_by,
                    status: CASE WHEN $is_continued = 1 THEN 'active' ELSE 'discontinued' END
                }]->(m)
            """, medication)
        
        # 4. Create complex lab result hierarchy
        for lab_report in patient_data['lab_reports']:
            # Create report node
            session.run("""
                MATCH (p:Patient {patient_id: $patient_id})
                CREATE (lr:LabReport {
                    lab_report_id: $lab_report_id,
                    lab_date: $lab_date,
                    lab_type: $lab_type,
                    ordering_doctor: $ordering_doctor
                })
                CREATE (p)-[:HAS_LAB_REPORT {
                    date: $lab_date,
                    type: $lab_type
                }]->(lr)
            """, lab_report)
            
            # Create individual lab findings
            for finding in lab_report['findings']:
                session.run("""
                    MATCH (lr:LabReport {lab_report_id: $lab_report_id})
                    CREATE (lf:LabFinding {
                        finding_id: $lab_finding_id,
                        test_name: $test_name,
                        test_value: $test_value,
                        test_unit: $test_unit,
                        is_abnormal: $is_abnormal
                    })
                    CREATE (lr)-[:CONTAINS_FINDING {
                        abnormal: $is_abnormal,
                        flag: $abnormal_flag
                    }]->(lf)
                """, finding)
```

## 🔄 Data Synchronization

### MariaDB to Neo4j Sync
```python
class DatabaseSynchronizer:
    """Synchronize data between MariaDB and Neo4j"""
    
    def sync_patient_to_graph(self, patient_id: int):
        """Complete patient data synchronization"""
        
        # 1. Fetch comprehensive patient data from MariaDB
        patient_data = self.fetch_complete_patient_data(patient_id)
        
        # 2. Clear existing graph data for patient
        self.clear_patient_graph_data(patient_id)
        
        # 3. Create new knowledge graph
        self.create_patient_knowledge_graph(patient_data)
        
        # 4. Validate graph integrity
        self.validate_graph_connectivity(patient_id)
    
    def fetch_complete_patient_data(self, patient_id: int) -> dict:
        """Fetch all patient data from atomic facts tables"""
        
        with mysql_connection() as db:
            # Patient basic info
            patient = fetch_patient_details(db, patient_id)
            
            # Medical history
            medical_history = fetch_medical_history(db, patient_id)
            
            # Medications with purposes
            medications = fetch_medications_with_purposes(db, patient_id)
            
            # Appointments with symptoms
            appointments = fetch_appointments_with_symptoms(db, patient_id)
            
            # Lab reports with findings
            lab_reports = fetch_lab_reports_with_findings(db, patient_id)
            
            # Medical reports with findings
            medical_reports = fetch_medical_reports_with_findings(db, patient_id)
            
            return {
                "patient": patient,
                "medical_history": medical_history,
                "medications": medications,
                "appointments": appointments,
                "lab_reports": lab_reports,
                "medical_reports": medical_reports
            }
```

## 📈 Query Optimization

### MariaDB Optimization
```sql
-- Optimized patient profile query
SELECT 
    p.patient_id,
    p.name,
    p.dob,
    p.sex,
    COUNT(DISTINCT mh.history_id) as history_count,
    COUNT(DISTINCT m.medication_id) as medication_count,
    COUNT(DISTINCT a.appointment_id) as appointment_count,
    COUNT(DISTINCT lr.lab_report_id) as lab_report_count
FROM Patient p
    LEFT JOIN Medical_History mh ON p.patient_id = mh.patient_id
    LEFT JOIN Medication m ON p.patient_id = m.patient_id AND m.is_continued = 1
    LEFT JOIN Appointment a ON p.patient_id = a.patient_id
    LEFT JOIN Lab_Report lr ON p.patient_id = lr.patient_id
WHERE p.patient_id = ?
GROUP BY p.patient_id;

-- Index optimization for frequent queries
CREATE INDEX idx_patient_composite ON Patient(patient_id, name, dob);
CREATE INDEX idx_medication_active ON Medication(patient_id, is_continued, prescribed_date);
CREATE INDEX idx_appointment_recent ON Appointment(patient_id, appointment_date DESC);
CREATE INDEX idx_lab_recent ON Lab_Report(patient_id, lab_date DESC);
```

### Neo4j Optimization
```cypher
// Optimized patient medication query
MATCH (p:Patient {patient_id: $patient_id})-[r:TAKES_MEDICATION]->(m:Medication)
WHERE r.status = 'active'
RETURN m.name AS medication_name, r.prescribed_date, m.dosage, m.frequency
ORDER BY r.prescribed_date DESC;

// Complex relationship traversal
MATCH (p:Patient {patient_id: $patient_id})-[:HAS_SYMPTOM]->(s:Symptom)-[:INDICATES_CONDITION]->(c:Condition)<-[:TREATS_CONDITION]-(m:Medication)<-[:TAKES_MEDICATION]-(p)
RETURN s.name AS symptom, c.name AS condition, m.name AS medication;

// Index creation for performance
CREATE INDEX patient_id_index FOR (p:Patient) ON (p.patient_id);
CREATE INDEX medication_name_index FOR (m:Medication) ON (m.name);
CREATE INDEX condition_name_index FOR (c:Condition) ON (c.name);
```

## 🔧 Connection Management

### MariaDB Connection Pool
```python
class DatabaseConnectionManager:
    """Efficient database connection management"""
    
    def __init__(self):
        self.connection_pool = Queue(maxsize=10)
        self.initialize_pool()
    
    def get_connection(self):
        """Get connection from pool with retry logic"""
        try:
            if not self.connection_pool.empty():
                conn = self.connection_pool.get_nowait()
                if conn.open:
                    return conn
            
            # Create new connection if pool empty
            return self.create_new_connection()
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            raise HTTPException(status_code=500, detail="Database connection failed")
    
    def return_connection(self, connection):
        """Return connection to pool"""
        if connection.open and not self.connection_pool.full():
            self.connection_pool.put_nowait(connection)
        else:
            connection.close()
```

### Neo4j Session Management
```python
class Neo4jManager:
    """Neo4j connection and session management"""
    
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD),
            max_connection_lifetime=3600,
            max_connection_pool_size=50
        )
    
    @contextmanager
    def session(self):
        """Context manager for Neo4j sessions"""
        session = None
        try:
            session = self.driver.session()
            yield session
        except Exception as e:
            logger.error(f"Neo4j session error: {e}")
            raise
        finally:
            if session:
                session.close()
```

## 🧪 Data Validation & Integrity

### Referential Integrity
```python
def validate_database_integrity():
    """Comprehensive database integrity validation"""
    
    integrity_checks = [
        # Orphaned records check
        "SELECT COUNT(*) FROM Medical_History mh LEFT JOIN Patient p ON mh.patient_id = p.patient_id WHERE p.patient_id IS NULL",
        
        # Medication without purposes
        "SELECT COUNT(*) FROM Medication m LEFT JOIN Medication_Purpose mp ON m.medication_id = mp.medication_id WHERE mp.medication_id IS NULL",
        
        # Appointments without patients
        "SELECT COUNT(*) FROM Appointment a LEFT JOIN Patient p ON a.patient_id = p.patient_id WHERE p.patient_id IS NULL",
        
        # Lab findings without reports
        "SELECT COUNT(*) FROM Lab_Finding lf LEFT JOIN Lab_Report lr ON lf.lab_report_id = lr.lab_report_id WHERE lr.lab_report_id IS NULL"
    ]
    
    for check in integrity_checks:
        result = execute_query(check)
        if result[0][0] > 0:
            logger.warning(f"Integrity issue found: {check}")
```

### Graph Connectivity Validation
```cypher
// Validate all nodes are connected to patients
MATCH (n)
WHERE NOT (n)-[:*1..3]-(p:Patient)
AND NOT n:Patient
RETURN labels(n) AS orphaned_node_types, count(n) AS count;

// Validate relationship consistency
MATCH (p:Patient)-[r]->(n)
WHERE NOT exists(n.patient_id) OR n.patient_id <> p.patient_id
RETURN type(r) AS inconsistent_relationship, count(*) AS count;
```

---

**Part of the MediMax Healthcare Platform - Providing robust, scalable, and comprehensive medical data management with atomic facts architecture and intelligent relationship modeling**