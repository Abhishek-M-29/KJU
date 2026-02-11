"""
Database Manager for Persona Generator
Handles insertion into MariaDB and Neo4j
"""

import os
import json
from datetime import datetime, date
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseManager:
    """
    Manages database connections and persona insertion
    """
    
    def __init__(self, 
                 mariadb_config: Optional[dict] = None,
                 neo4j_config: Optional[dict] = None):
        """
        Initialize database connections
        
        Args:
            mariadb_config: Dict with host, port, user, password, database
            neo4j_config: Dict with uri, user, password
        """
        self.mariadb_config = mariadb_config or {
            "host": os.getenv("DB_HOST", "lkdncj.h.filess.io"),
            "port": int(os.getenv("DB_PORT", "3305")),
            "user": os.getenv("DB_USER", "hospital_howeverwhy"),
            "password": os.getenv("DB_PASSWORD", "379bcdd8edfc2dac1580190b74428fba1acf5cd3"),
            "database": os.getenv("DB_NAME", "hospital_howeverwhy")
        }
        
        self.neo4j_config = neo4j_config or {
            "uri": os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687"),
            "user": os.getenv("AURA_USER", "neo4j"),
            "password": os.getenv("AURA_PASSWORD", "123456789")
        }
        
        self._mariadb_conn = None
        self._neo4j_driver = None
    
    def _get_mariadb_connection(self):
        """Get or create MariaDB connection"""
        if self._mariadb_conn is None:
            import mariadb
            self._mariadb_conn = mariadb.connect(**self.mariadb_config)
        return self._mariadb_conn
    
    def _get_neo4j_driver(self):
        """Get or create Neo4j driver"""
        if self._neo4j_driver is None:
            from neo4j import GraphDatabase
            self._neo4j_driver = GraphDatabase.driver(
                self.neo4j_config["uri"],
                auth=(self.neo4j_config["user"], self.neo4j_config["password"])
            )
        return self._neo4j_driver
    
    def close(self):
        """Close all database connections"""
        if self._mariadb_conn:
            self._mariadb_conn.close()
            self._mariadb_conn = None
        if self._neo4j_driver:
            self._neo4j_driver.close()
            self._neo4j_driver = None
    
    def get_max_persona_id(self) -> int:
        """Get the maximum persona_id from Patient_Data table"""
        conn = self._get_mariadb_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COALESCE(MAX(persona_id), 0) FROM Patient_Data WHERE is_persona = 1")
            result = cursor.fetchone()
            return result[0] if result else 0
        finally:
            cursor.close()
    
    def get_persona_by_id(self, persona_id: int) -> Optional[dict]:
        """
        Get a persona by its numeric persona_id
        
        Args:
            persona_id: The numeric persona ID (1, 2, 3, ...)
            
        Returns:
            Dictionary with persona data or None if not found
        """
        conn = self._get_mariadb_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT * FROM Patient_Data 
                WHERE is_persona = 1 AND persona_id = ?
            """, (persona_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        finally:
            cursor.close()
    
    def list_personas(self, limit: int = 100) -> List[dict]:
        """
        List all personas from Patient_Data
        
        Args:
            limit: Maximum number of personas to return
            
        Returns:
            List of persona dictionaries with basic info
        """
        conn = self._get_mariadb_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT persona_id, synthea_id, first_name, last_name, age_years, gender,
                       total_conditions_count, total_medications_count,
                       diabetes_risk_score, cardiovascular_risk_score
                FROM Patient_Data 
                WHERE is_persona = 1 
                ORDER BY persona_id
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
    
    def insert_persona(self, persona, verbose: bool = True, show_errors: bool = True) -> bool:
        """
        Insert a single persona into both databases and Patient_Data
        
        Args:
            persona: PersonaBase object
            verbose: Print progress messages
            show_errors: Print error details when insertion fails
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure persona has a persona_id
            if persona.persona_id is None:
                persona.assign_persona_id()
            
            # Insert into MariaDB (Synthea tables)
            self._insert_mariadb(persona, verbose)
            
            # Insert/update Patient_Data table
            self._insert_patient_data(persona, verbose)
            
            # Insert into Neo4j
            self._insert_neo4j(persona, verbose)
            
            return True
        except Exception as e:
            if show_errors:
                print(f"\n   ⚠️  Error inserting {persona.demographics.full_name}:")
                print(f"       {type(e).__name__}: {e}")
            return False
    
    def insert_personas(self, personas: List, verbose: bool = True, show_errors: bool = True) -> int:
        """
        Insert multiple personas
        
        Args:
            personas: List of PersonaBase objects
            verbose: Print progress messages
            show_errors: Print detailed error messages for failed insertions
            
        Returns:
            Number of successfully inserted personas
        """
        # Initialize persona_id counter from database
        from .base import PersonaBase
        max_id = self.get_max_persona_id()
        PersonaBase.set_starting_persona_id(max_id + 1)
        success_count = 0
        failed_personas = []
        
        for i, persona in enumerate(personas, 1):
            if verbose:
                print(f"📋 [{i}/{len(personas)}] Inserting {persona.demographics.full_name}...", end=" ", flush=True)
            
            if self.insert_persona(persona, verbose=False, show_errors=show_errors):
                success_count += 1
                if verbose:
                    print("✅")
            else:
                failed_personas.append(persona.demographics.full_name)
                if verbose:
                    print("❌")
        
        if verbose:
            print(f"\n✅ Successfully inserted {success_count}/{len(personas)} personas")
            if failed_personas and show_errors:
                print(f"❌ Failed: {', '.join(failed_personas)}")
        
        return success_count
    
    def _insert_mariadb(self, persona, verbose: bool):
        """Insert persona into MariaDB"""
        conn = self._get_mariadb_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Insert patient (using correct column names)
            cursor.execute("""
                INSERT INTO Synthea_Patient 
                (synthea_id, first_name, last_name, birthdate, gender, race, marital_status,
                 address, city, state, zip, county, latitude, longitude, 
                 healthcare_expenses, healthcare_coverage, income)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                persona.id,
                persona.demographics.first_name,
                persona.demographics.last_name,
                persona.demographics.birth_date.isoformat(),
                persona.demographics.gender.value,
                persona.demographics.race.value,
                persona.demographics.marital_status.value,
                persona.demographics.address,
                persona.demographics.city,
                persona.demographics.state,
                persona.demographics.zip_code,
                persona.demographics.county,
                persona.demographics.lat,
                persona.demographics.lon,
                persona.demographics.healthcare_expenses,
                persona.demographics.healthcare_coverage,
                persona.demographics.income
            ))
            
            # 2. Insert conditions (using synthea_patient_id)
            for condition in persona.conditions:
                stop_date = condition.stop_date.isoformat() if condition.stop_date else None
                cursor.execute("""
                    INSERT INTO Synthea_Condition 
                    (synthea_patient_id, code, description, start_date, stop_date, is_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    persona.id,
                    condition.code,
                    condition.description,
                    condition.start_date.isoformat(),
                    stop_date,
                    1 if condition.is_active else 0
                ))
            
            # 3. Insert medications (using synthea_patient_id)
            for medication in persona.medications:
                stop_datetime = medication.stop_datetime.isoformat() if medication.stop_datetime else None
                cursor.execute("""
                    INSERT INTO Synthea_Medication 
                    (synthea_patient_id, code, description, start_datetime, stop_datetime, 
                     is_active, reason_code, reason_description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    persona.id,
                    medication.code,
                    medication.description,
                    medication.start_datetime.isoformat(),
                    stop_datetime,
                    1 if medication.is_active else 0,
                    medication.reason_code,
                    medication.reason_description
                ))
            
            # 4. Insert allergies (using synthea_patient_id)
            for allergy in persona.allergies:
                stop_date = allergy.stop_date.isoformat() if allergy.stop_date else None
                cursor.execute("""
                    INSERT INTO Synthea_Allergy 
                    (synthea_patient_id, code, description, start_date, stop_date, is_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    persona.id,
                    allergy.code,
                    allergy.description,
                    allergy.start_date.isoformat(),
                    stop_date,
                    1 if allergy.is_active else 0
                ))
            
            # 5. Insert observations (vitals and labs combined)
            for vitals in persona.vital_signs_history:
                obs_date = vitals.measurement_date.strftime("%Y-%m-%d")
                observations = [
                    ("8480-6", "Systolic blood pressure", vitals.systolic_bp, "mmHg"),
                    ("8462-4", "Diastolic blood pressure", vitals.diastolic_bp, "mmHg"),
                    ("8867-4", "Heart rate", vitals.heart_rate, "bpm"),
                    ("9279-1", "Respiratory rate", vitals.respiratory_rate, "/min"),
                    ("8310-5", "Body temperature", vitals.temperature, "Cel"),
                    ("2708-6", "Oxygen saturation", vitals.oxygen_saturation, "%"),
                    ("8302-2", "Body height", vitals.height_cm, "cm"),
                    ("29463-7", "Body weight", vitals.weight_kg, "kg"),
                    ("39156-5", "Body Mass Index", vitals.bmi, "kg/m2"),
                ]
                for code, desc, value, unit in observations:
                    cursor.execute("""
                        INSERT INTO Synthea_Observation 
                        (synthea_patient_id, code, description, value, units, observation_date)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (persona.id, code, desc, str(value), unit, obs_date))
            
            for lab in persona.lab_results:
                obs_date = lab.test_date.strftime("%Y-%m-%d")
                cursor.execute("""
                    INSERT INTO Synthea_Observation 
                    (synthea_patient_id, code, description, value, units, observation_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (persona.id, lab.test_code, lab.test_name, str(lab.value), lab.unit, obs_date))
            
            # 6. Insert encounters (using synthea_patient_id and synthea_id)
            for encounter in persona.encounters:
                cursor.execute("""
                    INSERT INTO Synthea_Encounter 
                    (synthea_id, synthea_patient_id, encounter_class, code, description, 
                     start_datetime, stop_datetime, reason_code, reason_description,
                     base_cost, total_claim_cost, payer_coverage)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    encounter.encounter_id,
                    persona.id,
                    encounter.encounter_class,
                    "185349003",  # Generic encounter code
                    encounter.encounter_type,
                    encounter.start_datetime.isoformat(),
                    encounter.stop_datetime.isoformat(),
                    encounter.reason_code,
                    encounter.reason_description,
                    encounter.base_cost,
                    encounter.total_claim_cost,
                    encounter.payer_coverage
                ))
            
            # 7. Insert AI features
            if persona.ai_features:
                af = persona.ai_features
                # Get latest vitals for the record
                latest_vitals = persona.vital_signs_history[-1] if persona.vital_signs_history else None
                # Get latest labs for glucose/hba1c/cholesterol
                glucose_level = None
                hba1c_level = None
                cholesterol_level = None
                for lab in persona.lab_results:
                    if "glucose" in lab.test_name.lower():
                        glucose_level = int(lab.value) if lab.value else None
                    if "hba1c" in lab.test_name.lower() or "hemoglobin" in lab.test_name.lower():
                        hba1c_level = lab.value
                    if "cholesterol" in lab.test_name.lower():
                        cholesterol_level = int(lab.value) if lab.value else None
                
                # Map string values to integers
                alcohol_map = {'none': 0, 'social': 1, 'moderate': 2, 'heavy': 3}
                activity_map = {'sedentary': 0, 'rarely': 1, 'weekly': 2, 'daily': 3}
                
                alcohol_val = alcohol_map.get(persona.social_history.alcohol_use if persona.social_history else 'none', 0)
                activity_val = activity_map.get(persona.social_history.exercise_frequency if persona.social_history else 'rarely', 1)
                
                cursor.execute("""
                    INSERT INTO Patient_AI_Features 
                    (synthea_patient_id, age_years, gender_numeric, height_cm, weight_kg, bmi,
                     bp_systolic, bp_diastolic, cholesterol_level, glucose_level,
                     is_smoker, smoking_history, alcohol_use, physical_activity,
                     has_hypertension, has_heart_disease, hba1c_level, blood_glucose_fasting,
                     cardio_risk_score, cardio_risk_category, diabetes_risk_score, diabetes_risk_category)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    persona.id,
                    persona.demographics.age,
                    1 if persona.demographics.gender.value == 'M' else 0,
                    latest_vitals.height_cm if latest_vitals else None,
                    latest_vitals.weight_kg if latest_vitals else None,
                    latest_vitals.bmi if latest_vitals else None,
                    int(latest_vitals.systolic_bp) if latest_vitals else None,
                    int(latest_vitals.diastolic_bp) if latest_vitals else None,
                    cholesterol_level,
                    glucose_level,
                    1 if af.is_smoker else 0,
                    persona.social_history.smoking_status if persona.social_history else 'never',
                    alcohol_val,
                    activity_val,
                    1 if af.has_hypertension else 0,
                    1 if af.has_heart_disease else 0,
                    hba1c_level,
                    glucose_level,
                    # Scale risk scores to fit decimal(5,4) column (0-1 range)
                    round(af.cardiovascular_risk_score / 10.0, 4),
                    'high' if af.cardiovascular_risk_score >= 7 else ('moderate' if af.cardiovascular_risk_score >= 4 else 'low'),
                    round(af.diabetes_risk_score / 10.0, 4),
                    'high' if af.diabetes_risk_score >= 7 else ('moderate' if af.diabetes_risk_score >= 4 else 'low')
                ))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def _insert_patient_data(self, persona, verbose: bool):
        """Insert persona into Patient_Data table as single source of truth"""
        conn = self._get_mariadb_connection()
        cursor = conn.cursor()
        
        try:
            # Get latest vitals
            latest_vitals = persona.vital_signs_history[-1] if persona.vital_signs_history else None
            
            # Extract lab values
            lab_values = {}
            for lab in persona.lab_results:
                test_name_lower = lab.test_name.lower()
                if "glucose" in test_name_lower and "fasting" not in test_name_lower:
                    lab_values['glucose'] = lab.value
                elif "fasting" in test_name_lower and "glucose" in test_name_lower:
                    lab_values['glucose_fasting'] = lab.value
                elif "hba1c" in test_name_lower or "hemoglobin a1c" in test_name_lower:
                    lab_values['hba1c'] = lab.value
                elif "creatinine" in test_name_lower:
                    lab_values['creatinine'] = lab.value
                elif "cholesterol" in test_name_lower and "total" in test_name_lower:
                    lab_values['cholesterol_total'] = lab.value
                elif "ldl" in test_name_lower:
                    lab_values['ldl'] = lab.value
                elif "hdl" in test_name_lower:
                    lab_values['hdl'] = lab.value
                elif "triglyceride" in test_name_lower:
                    lab_values['triglycerides'] = lab.value
            
            # Aggregate conditions, medications, allergies
            conditions_json = json.dumps([{
                'code': c.code, 
                'description': c.description, 
                'is_active': c.is_active
            } for c in persona.conditions])
            
            medications_json = json.dumps([{
                'code': m.code, 
                'description': m.description, 
                'is_active': m.is_active,
                'dosage': m.dosage
            } for m in persona.medications])
            
            allergies_json = json.dumps([{
                'code': a.code, 
                'description': a.description
            } for a in persona.allergies])
            
            # AI features JSON
            ai_features = {}
            if persona.ai_features:
                af = persona.ai_features
                ai_features = {
                    'patient_id': persona.id,
                    'persona_id': persona.persona_id,
                    'age': persona.demographics.age,
                    'gender': persona.demographics.gender.value,
                    'bmi': latest_vitals.bmi if latest_vitals else None,
                    'bp_systolic': latest_vitals.systolic_bp if latest_vitals else None,
                    'bp_diastolic': latest_vitals.diastolic_bp if latest_vitals else None,
                    'heart_rate': latest_vitals.heart_rate if latest_vitals else None,
                    'glucose': lab_values.get('glucose'),
                    'hba1c': lab_values.get('hba1c'),
                    'cholesterol_total': lab_values.get('cholesterol_total'),
                    'ldl': lab_values.get('ldl'),
                    'hdl': lab_values.get('hdl'),
                    'has_diabetes': af.has_diabetes,
                    'has_hypertension': af.has_hypertension,
                    'has_heart_disease': af.has_heart_disease,
                    'has_ckd': af.has_ckd,
                    'has_obesity': af.is_obese,
                    'is_smoker': af.is_smoker,
                    'diabetes_risk_score': af.diabetes_risk_score / 10.0,
                    'cardiovascular_risk_score': af.cardiovascular_risk_score / 10.0,
                    'total_conditions': len(persona.conditions),
                    'total_medications': len(persona.medications),
                    'total_encounters': len(persona.encounters)
                }
            ai_features_json = json.dumps(ai_features)
            
            # Count statistics
            total_conditions = len(persona.conditions)
            active_conditions = len([c for c in persona.conditions if c.is_active])
            total_medications = len(persona.medications)
            active_medications = len([m for m in persona.medications if m.is_active])
            total_allergies = len(persona.allergies)
            total_encounters = len(persona.encounters)
            emergency_encounters = len([e for e in persona.encounters if e.encounter_class == 'emergency'])
            inpatient_encounters = len([e for e in persona.encounters if e.encounter_class == 'inpatient'])
            
            # Check for clinical flags
            condition_descs = [c.description.lower() for c in persona.conditions]
            has_diabetes = any('diabetes' in d for d in condition_descs) if persona.ai_features else persona.ai_features.has_diabetes
            has_hypertension = any('hypertension' in d for d in condition_descs) if persona.ai_features else persona.ai_features.has_hypertension
            has_heart_disease = any(x in ' '.join(condition_descs) for x in ['heart failure', 'coronary', 'myocardial', 'atrial fib'])
            has_ckd = any('kidney' in d for d in condition_descs)
            has_copd = any('copd' in d for d in condition_descs)
            
            # Insert into Patient_Data
            cursor.execute("""
                INSERT INTO Patient_Data 
                (is_persona, persona_id, synthea_id, first_name, last_name, full_name, 
                 birthdate, age_years, gender, race, marital_status,
                 address, city, state, zip, latitude, longitude, income,
                 healthcare_expenses, healthcare_coverage,
                 bp_systolic, bp_diastolic, heart_rate, respiratory_rate, temperature,
                 oxygen_saturation, height_cm, weight_kg, bmi,
                 glucose, hba1c, cholesterol_total, ldl, hdl, triglycerides, creatinine,
                 total_conditions_count, active_conditions_count,
                 total_medications_count, active_medications_count, total_allergies_count,
                 total_encounters_count, emergency_encounters, inpatient_encounters,
                 has_diabetes, has_hypertension, has_heart_disease, has_ckd, has_copd,
                 is_smoker, all_conditions_json, all_medications_json, all_allergies_json,
                 ai_features_json)
                VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON DUPLICATE KEY UPDATE
                    is_persona = 1,
                    persona_id = VALUES(persona_id),
                    first_name = VALUES(first_name),
                    last_name = VALUES(last_name),
                    full_name = VALUES(full_name),
                    age_years = VALUES(age_years),
                    bp_systolic = VALUES(bp_systolic),
                    bp_diastolic = VALUES(bp_diastolic),
                    total_conditions_count = VALUES(total_conditions_count),
                    active_conditions_count = VALUES(active_conditions_count),
                    total_medications_count = VALUES(total_medications_count),
                    ai_features_json = VALUES(ai_features_json)
            """, (
                persona.persona_id,
                persona.id,
                persona.demographics.first_name,
                persona.demographics.last_name,
                persona.demographics.full_name,
                persona.demographics.birth_date.isoformat(),
                persona.demographics.age,
                persona.demographics.gender.value,
                persona.demographics.race.value,
                persona.demographics.marital_status.value,
                persona.demographics.address,
                persona.demographics.city,
                persona.demographics.state,
                persona.demographics.zip_code,
                persona.demographics.lat,
                persona.demographics.lon,
                persona.demographics.income,
                persona.demographics.healthcare_expenses,
                persona.demographics.healthcare_coverage,
                latest_vitals.systolic_bp if latest_vitals else None,
                latest_vitals.diastolic_bp if latest_vitals else None,
                latest_vitals.heart_rate if latest_vitals else None,
                latest_vitals.respiratory_rate if latest_vitals else None,
                latest_vitals.temperature if latest_vitals else None,
                latest_vitals.oxygen_saturation if latest_vitals else None,
                latest_vitals.height_cm if latest_vitals else None,
                latest_vitals.weight_kg if latest_vitals else None,
                latest_vitals.bmi if latest_vitals else None,
                lab_values.get('glucose'),
                lab_values.get('hba1c'),
                lab_values.get('cholesterol_total'),
                lab_values.get('ldl'),
                lab_values.get('hdl'),
                lab_values.get('triglycerides'),
                lab_values.get('creatinine'),
                total_conditions,
                active_conditions,
                total_medications,
                active_medications,
                total_allergies,
                total_encounters,
                emergency_encounters,
                inpatient_encounters,
                1 if has_diabetes else 0,
                1 if has_hypertension else 0,
                1 if has_heart_disease else 0,
                1 if has_ckd else 0,
                1 if has_copd else 0,
                1 if (persona.ai_features and persona.ai_features.is_smoker) else 0,
                conditions_json,
                medications_json,
                allergies_json,
                ai_features_json
            ))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

    def _insert_neo4j(self, persona, verbose: bool):
        """Insert persona into Neo4j knowledge graph"""
        driver = self._get_neo4j_driver()
        
        with driver.session() as session:
            # Create Patient node with patient_no (matches persona_id in MariaDB)
            session.run("""
                MERGE (p:Patient {id: $id})
                SET p.first_name = $first_name,
                    p.last_name = $last_name,
                    p.birth_date = $birth_date,
                    p.gender = $gender,
                    p.race = $race,
                    p.age = $age,
                    p.narrative = $narrative,
                    p.is_persona = $is_persona,
                    p.patient_no = $patient_no
            """, {
                "id": persona.id,
                "first_name": persona.demographics.first_name,
                "last_name": persona.demographics.last_name,
                "birth_date": persona.demographics.birth_date.isoformat(),
                "gender": persona.demographics.gender.value,
                "race": persona.demographics.race.value,
                "age": persona.demographics.age,
                "narrative": persona.narrative,
                "is_persona": True,
                "patient_no": persona.persona_id
            })
            
            # Create Condition nodes and relationships
            for condition in persona.conditions:
                session.run("""
                    MERGE (c:Condition {code: $code})
                    SET c.description = $description
                    WITH c
                    MATCH (p:Patient {id: $patient_id})
                    MERGE (p)-[r:HAS_CONDITION]->(c)
                    SET r.start_date = $start_date,
                        r.is_active = $is_active
                """, {
                    "code": condition.code,
                    "description": condition.description,
                    "patient_id": persona.id,
                    "start_date": condition.start_date.isoformat(),
                    "is_active": condition.is_active
                })
            
            # Create Medication nodes and relationships
            for medication in persona.medications:
                session.run("""
                    MERGE (m:Medication {code: $code})
                    SET m.description = $description
                    WITH m
                    MATCH (p:Patient {id: $patient_id})
                    MERGE (p)-[r:TAKES_MEDICATION]->(m)
                    SET r.start_datetime = $start_datetime,
                        r.is_active = $is_active,
                        r.dosage = $dosage,
                        r.frequency = $frequency
                """, {
                    "code": medication.code,
                    "description": medication.description,
                    "patient_id": persona.id,
                    "start_datetime": medication.start_datetime.isoformat(),
                    "is_active": medication.is_active,
                    "dosage": medication.dosage,
                    "frequency": medication.frequency
                })
            
            # Create Allergy nodes and relationships
            for allergy in persona.allergies:
                session.run("""
                    MERGE (a:Allergy {code: $code})
                    SET a.description = $description
                    WITH a
                    MATCH (p:Patient {id: $patient_id})
                    MERGE (p)-[r:HAS_ALLERGY]->(a)
                    SET r.severity = $severity,
                        r.reaction = $reaction
                """, {
                    "code": allergy.code,
                    "description": allergy.description,
                    "patient_id": persona.id,
                    "severity": allergy.severity,
                    "reaction": allergy.reaction
                })
            
            # Create RiskProfile node
            if persona.ai_features:
                af = persona.ai_features
                session.run("""
                    MATCH (p:Patient {id: $patient_id})
                    MERGE (p)-[:HAS_RISK_PROFILE]->(rp:RiskProfile)
                    SET rp.diabetes_risk = $diabetes_risk,
                        rp.cardiovascular_risk = $cv_risk,
                        rp.sepsis_risk = $sepsis_risk,
                        rp.readmission_risk = $readmission_risk,
                        rp.mortality_risk = $mortality_risk
                """, {
                    "patient_id": persona.id,
                    "diabetes_risk": af.diabetes_risk_score,
                    "cv_risk": af.cardiovascular_risk_score,
                    "sepsis_risk": af.sepsis_risk_score,
                    "readmission_risk": af.readmission_risk_score,
                    "mortality_risk": af.mortality_risk_score
                })
            
            # Create Social History node
            if persona.social_history:
                sh = persona.social_history
                session.run("""
                    MATCH (p:Patient {id: $patient_id})
                    MERGE (p)-[:HAS_SOCIAL_HISTORY]->(s:SocialHistory)
                    SET s.smoking_status = $smoking_status,
                        s.alcohol_use = $alcohol_use,
                        s.exercise_frequency = $exercise_frequency,
                        s.diet_quality = $diet_quality,
                        s.occupation = $occupation,
                        s.stress_level = $stress_level
                """, {
                    "patient_id": persona.id,
                    "smoking_status": sh.smoking_status,
                    "alcohol_use": sh.alcohol_use,
                    "exercise_frequency": sh.exercise_frequency,
                    "diet_quality": sh.diet_quality,
                    "occupation": sh.occupation,
                    "stress_level": sh.stress_level
                })
            
            # Create Family History relationships
            for fh in persona.family_history:
                session.run("""
                    MATCH (p:Patient {id: $patient_id})
                    MERGE (fh:FamilyHistory {condition: $condition, relation: $relation})
                    MERGE (p)-[:HAS_FAMILY_HISTORY]->(fh)
                    SET fh.age_at_onset = $age_at_onset,
                        fh.deceased = $deceased
                """, {
                    "patient_id": persona.id,
                    "condition": fh.condition,
                    "relation": fh.relation,
                    "age_at_onset": fh.age_at_onset,
                    "deceased": fh.deceased
                })
    
    def clear_generated_personas(self, persona_ids: List[str], verbose: bool = True):
        """
        Remove personas from databases by ID
        
        Args:
            persona_ids: List of persona IDs to remove
            verbose: Print progress messages
        """
        conn = self._get_mariadb_connection()
        cursor = conn.cursor()
        driver = self._get_neo4j_driver()
        
        try:
            for pid in persona_ids:
                if verbose:
                    print(f"🗑️ Removing persona {pid}...", end=" ")
                
                # Remove from MariaDB (using correct column names)
                cursor.execute("DELETE FROM Patient_AI_Features WHERE synthea_patient_id = ?", (pid,))
                cursor.execute("DELETE FROM Synthea_Observation WHERE synthea_patient_id = ?", (pid,))
                cursor.execute("DELETE FROM Synthea_Encounter WHERE synthea_patient_id = ?", (pid,))
                cursor.execute("DELETE FROM Synthea_Medication WHERE synthea_patient_id = ?", (pid,))
                cursor.execute("DELETE FROM Synthea_Allergy WHERE synthea_patient_id = ?", (pid,))
                cursor.execute("DELETE FROM Synthea_Condition WHERE synthea_patient_id = ?", (pid,))
                cursor.execute("DELETE FROM Synthea_Patient WHERE synthea_id = ?", (pid,))
                
                conn.commit()
                
                # Remove from Neo4j
                with driver.session() as session:
                    session.run("""
                        MATCH (p:Patient {id: $id})
                        OPTIONAL MATCH (p)-[r]->(n)
                        DELETE r
                        WITH p
                        DETACH DELETE p
                    """, {"id": pid})
                
                if verbose:
                    print("✅")
                    
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def get_persona_count(self) -> dict:
        """Get count of personas in databases"""
        conn = self._get_mariadb_connection()
        cursor = conn.cursor()
        driver = self._get_neo4j_driver()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM Synthea_Patient")
            mariadb_count = cursor.fetchone()[0]
            
            with driver.session() as session:
                result = session.run("MATCH (p:Patient) RETURN COUNT(p) as count")
                neo4j_count = result.single()["count"]
            
            return {
                "mariadb": mariadb_count,
                "neo4j": neo4j_count
            }
        finally:
            cursor.close()
