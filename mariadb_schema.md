# MariaDB Database Schema

## 1. List of Tables

- AI_Risk_Assessment
- Appointment
- Appointment_Symptom
- Chat_History
- Lab_Finding
- Lab_Report
- Medical_History
- Medication
- Medication_Purpose
- Patient
- Patient_AI_Features
- Patient_Data
- Patient_Vitals_Summary
- Report
- Report_Finding
- Synthea_Allergy
- Synthea_CarePlan
- Synthea_Condition
- Synthea_Device
- Synthea_Encounter
- Synthea_ImagingStudy
- Synthea_Immunization
- Synthea_Medication
- Synthea_Observation
- Synthea_Organization
- Synthea_Patient
- Synthea_Procedure
- Synthea_Provider

## 2. Table Descriptions

### AI_Risk_Assessment
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| assessment_id | int | NO | null |
| synthea_patient_id | varchar | YES | NULL |
| assessment_type | enum | NO | null |
| risk_score | decimal | YES | NULL |
| risk_category | varchar | YES | NULL |
| confidence_score | decimal | YES | NULL |
| input_features | longtext | YES | NULL |
| top_risk_factors | longtext | YES | NULL |
| recommendations | longtext | YES | NULL |
| model_version | varchar | YES | NULL |
| assessed_at | timestamp | YES | current_timestamp() |
| assessed_by | varchar | YES | 'AI_Model' |

### Appointment
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| appointment_id | int | NO | null |
| patient_id | int | YES | NULL |
| appointment_date | date | NO | null |
| appointment_time | time | YES | NULL |
| status | enum | YES | NULL |
| appointment_type | enum | YES | NULL |
| doctor_name | varchar | YES | NULL |
| notes | text | YES | NULL |

### Appointment_Symptom
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| symptom_id | int | NO | null |
| appointment_id | int | YES | NULL |
| symptom_name | varchar | NO | null |
| symptom_description | text | YES | NULL |
| severity | enum | YES | NULL |
| duration | varchar | YES | NULL |
| onset_type | enum | YES | NULL |

### Chat_History
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| chat_id | int | NO | null |
| patient_id | int | YES | NULL |
| message_text | text | NO | null |
| message_type | enum | YES | NULL |
| timestamp | timestamp | YES | current_timestamp() |
| session_id | varchar | YES | NULL |

### Lab_Finding
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| lab_finding_id | int | NO | null |
| lab_report_id | int | YES | NULL |
| test_name | varchar | NO | null |
| test_value | varchar | NO | null |
| test_unit | varchar | YES | NULL |
| reference_range | varchar | YES | NULL |
| is_abnormal | tinyint | YES | 0 |
| abnormal_flag | enum | YES | NULL |

### Lab_Report
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| lab_report_id | int | NO | null |
| patient_id | int | YES | NULL |
| lab_date | date | NO | null |
| lab_type | varchar | YES | NULL |
| ordering_doctor | varchar | YES | NULL |
| lab_facility | varchar | YES | NULL |

### Medical_History
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| history_id | int | NO | null |
| patient_id | int | YES | NULL |
| history_type | enum | YES | NULL |
| history_item | varchar | YES | NULL |
| history_details | text | YES | NULL |
| history_date | date | YES | NULL |
| severity | enum | YES | NULL |
| is_active | tinyint | YES | 1 |
| updated_at | timestamp | YES | current_timestamp() |

### Medication
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| medication_id | int | NO | null |
| patient_id | int | YES | NULL |
| medicine_name | varchar | NO | null |
| is_continued | tinyint | YES | 1 |
| prescribed_date | date | NO | null |
| discontinued_date | date | YES | NULL |
| dosage | varchar | YES | NULL |
| frequency | varchar | YES | NULL |
| prescribed_by | varchar | YES | NULL |

### Medication_Purpose
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| purpose_id | int | NO | null |
| medication_id | int | YES | NULL |
| condition_name | varchar | NO | null |
| purpose_description | text | YES | NULL |

### Patient
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| patient_id | int | NO | null |
| name | varchar | NO | null |
| dob | date | YES | NULL |
| sex | enum | YES | NULL |
| created_at | timestamp | YES | current_timestamp() |
| updated_at | timestamp | YES | current_timestamp() |

### Patient_AI_Features
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| feature_id | int | NO | null |
| synthea_patient_id | varchar | YES | NULL |
| age_years | decimal | YES | NULL |
| gender_numeric | int | YES | NULL |
| height_cm | decimal | YES | NULL |
| weight_kg | decimal | YES | NULL |
| bmi | decimal | YES | NULL |
| bp_systolic | int | YES | NULL |
| bp_diastolic | int | YES | NULL |
| cholesterol_level | int | YES | NULL |
| glucose_level | int | YES | NULL |
| is_smoker | int | YES | 0 |
| smoking_history | varchar | YES | NULL |
| alcohol_use | int | YES | 0 |
| physical_activity | int | YES | 1 |
| has_hypertension | int | YES | 0 |
| has_heart_disease | int | YES | 0 |
| hba1c_level | decimal | YES | NULL |
| blood_glucose_fasting | int | YES | NULL |
| cardio_risk_score | decimal | YES | NULL |
| cardio_risk_category | varchar | YES | NULL |
| diabetes_risk_score | decimal | YES | NULL |
| diabetes_risk_category | varchar | YES | NULL |
| last_observation_date | date | YES | NULL |
| data_completeness_score | decimal | YES | NULL |
| created_at | timestamp | YES | current_timestamp() |
| updated_at | timestamp | YES | current_timestamp() |

### Patient_Data
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| patient_data_id | int | NO | null |
| synthea_id | varchar | NO | null |
| first_name | varchar | YES | NULL |
| middle_name | varchar | YES | NULL |
| last_name | varchar | YES | NULL |
| full_name | varchar | YES | NULL |
| prefix | varchar | YES | NULL |
| suffix | varchar | YES | NULL |
| maiden_name | varchar | YES | NULL |
| ssn | varchar | YES | NULL |
| drivers_license | varchar | YES | NULL |
| passport | varchar | YES | NULL |
| birthdate | date | YES | NULL |
| deathdate | date | YES | NULL |
| age_years | int | YES | NULL |
| is_deceased | tinyint | YES | 0 |
| gender | varchar | YES | NULL |
| race | varchar | YES | NULL |
| ethnicity | varchar | YES | NULL |
| marital_status | varchar | YES | NULL |
| address | text | YES | NULL |
| city | varchar | YES | NULL |
| state | varchar | YES | NULL |
| county | varchar | YES | NULL |
| zip | varchar | YES | NULL |
| latitude | decimal | YES | NULL |
| longitude | decimal | YES | NULL |
| income | int | YES | NULL |
| healthcare_expenses | decimal | YES | NULL |
| healthcare_coverage | decimal | YES | NULL |
| total_medication_costs | decimal | YES | NULL |
| total_procedure_costs | decimal | YES | NULL |
| total_encounter_costs | decimal | YES | NULL |
| total_conditions_count | int | YES | 0 |
| active_conditions_count | int | YES | 0 |
| resolved_conditions_count | int | YES | 0 |
| active_conditions_list | longtext | YES | NULL |
| active_conditions_codes | text | YES | NULL |
| resolved_conditions_list | longtext | YES | NULL |
| all_conditions_list | longtext | YES | NULL |
| first_condition_date | date | YES | NULL |
| latest_condition_date | date | YES | NULL |
| total_medications_count | int | YES | 0 |
| active_medications_count | int | YES | 0 |
| active_medications_list | longtext | YES | NULL |
| active_medications_codes | text | YES | NULL |
| all_medications_list | longtext | YES | NULL |
| first_medication_date | date | YES | NULL |
| latest_medication_date | date | YES | NULL |
| total_allergies_count | int | YES | 0 |
| active_allergies_count | int | YES | 0 |
| active_allergies_list | longtext | YES | NULL |
| allergy_categories | text | YES | NULL |
| severe_allergies_list | text | YES | NULL |
| total_procedures_count | int | YES | 0 |
| procedures_list | longtext | YES | NULL |
| procedure_codes | text | YES | NULL |
| first_procedure_date | date | YES | NULL |
| latest_procedure_date | date | YES | NULL |
| total_immunizations_count | int | YES | 0 |
| immunizations_list | longtext | YES | NULL |
| latest_immunization_date | date | YES | NULL |
| total_careplans_count | int | YES | 0 |
| active_careplans_count | int | YES | 0 |
| active_careplans_list | longtext | YES | NULL |
| total_devices_count | int | YES | 0 |
| active_devices_list | text | YES | NULL |
| total_imaging_count | int | YES | 0 |
| imaging_studies_list | longtext | YES | NULL |
| latest_imaging_date | date | YES | NULL |
| total_encounters_count | int | YES | 0 |
| ambulatory_encounters | int | YES | 0 |
| emergency_encounters | int | YES | 0 |
| inpatient_encounters | int | YES | 0 |
| wellness_encounters | int | YES | 0 |
| outpatient_encounters | int | YES | 0 |
| urgentcare_encounters | int | YES | 0 |
| first_encounter_date | date | YES | NULL |
| latest_encounter_date | date | YES | NULL |
| latest_encounter_type | varchar | YES | NULL |
| latest_encounter_reason | text | YES | NULL |
| encounters_last_year | int | YES | 0 |
| latest_vitals_date | date | YES | NULL |
| bp_systolic | int | YES | NULL |
| bp_diastolic | int | YES | NULL |
| heart_rate | int | YES | NULL |
| respiratory_rate | int | YES | NULL |
| temperature | decimal | YES | NULL |
| oxygen_saturation | decimal | YES | NULL |
| height_cm | decimal | YES | NULL |
| weight_kg | decimal | YES | NULL |
| bmi | decimal | YES | NULL |
| latest_labs_date | date | YES | NULL |
| glucose | int | YES | NULL |
| glucose_fasting | int | YES | NULL |
| hba1c | decimal | YES | NULL |
| creatinine | decimal | YES | NULL |
| bun | decimal | YES | NULL |
| egfr | decimal | YES | NULL |
| sodium | int | YES | NULL |
| potassium | decimal | YES | NULL |
| chloride | int | YES | NULL |
| co2_total | decimal | YES | NULL |
| calcium | decimal | YES | NULL |
| cholesterol_total | int | YES | NULL |
| ldl | int | YES | NULL |
| hdl | int | YES | NULL |
| triglycerides | int | YES | NULL |
| alt | int | YES | NULL |
| ast | int | YES | NULL |
| albumin | decimal | YES | NULL |
| bilirubin_total | decimal | YES | NULL |
| wbc | decimal | YES | NULL |
| rbc | decimal | YES | NULL |
| hemoglobin | decimal | YES | NULL |
| hematocrit | decimal | YES | NULL |
| platelets | int | YES | NULL |
| troponin | decimal | YES | NULL |
| bnp | int | YES | NULL |
| tsh | decimal | YES | NULL |
| urine_protein | varchar | YES | NULL |
| microalbumin_creatinine_ratio | decimal | YES | NULL |
| all_observations_json | longtext | YES | NULL |
| all_observations_list | longtext | YES | NULL |
| ai_features_json | longtext | YES | NULL |
| total_observations_count | int | YES | 0 |
| diabetes_risk_score | decimal | YES | NULL |
| diabetes_risk_category | varchar | YES | NULL |
| cardiovascular_risk_score | decimal | YES | NULL |
| cardiovascular_risk_category | varchar | YES | NULL |
| has_diabetes | tinyint | YES | 0 |
| has_prediabetes | tinyint | YES | 0 |
| has_hypertension | tinyint | YES | 0 |
| has_heart_disease | tinyint | YES | 0 |
| has_heart_failure | tinyint | YES | 0 |
| has_afib | tinyint | YES | 0 |
| has_ckd | tinyint | YES | 0 |
| has_copd | tinyint | YES | 0 |
| has_asthma | tinyint | YES | 0 |
| has_cancer | tinyint | YES | 0 |
| has_depression | tinyint | YES | 0 |
| has_anxiety | tinyint | YES | 0 |
| has_obesity | tinyint | YES | 0 |
| has_stroke_history | tinyint | YES | 0 |
| has_mi_history | tinyint | YES | 0 |
| is_smoker | tinyint | YES | 0 |
| smoking_history | varchar | YES | NULL |
| alcohol_use | int | YES | NULL |
| physical_activity | int | YES | NULL |
| data_completeness_score | decimal | YES | NULL |
| has_vitals | tinyint | YES | 0 |
| has_labs | tinyint | YES | 0 |
| has_conditions | tinyint | YES | 0 |
| has_medications | tinyint | YES | 0 |
| has_encounters | tinyint | YES | 0 |
| created_at | timestamp | YES | current_timestamp() |
| updated_at | timestamp | YES | current_timestamp() |

### Patient_Vitals_Summary
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| vitals_id | int | NO | null |
| synthea_patient_id | varchar | YES | NULL |
| observation_date | date | YES | NULL |
| height_cm | decimal | YES | NULL |
| weight_kg | decimal | YES | NULL |
| bmi | decimal | YES | NULL |
| bp_systolic | int | YES | NULL |
| bp_diastolic | int | YES | NULL |
| heart_rate | int | YES | NULL |
| respiratory_rate | int | YES | NULL |
| body_temperature | decimal | YES | NULL |
| oxygen_saturation | decimal | YES | NULL |
| total_cholesterol | decimal | YES | NULL |
| ldl_cholesterol | decimal | YES | NULL |
| hdl_cholesterol | decimal | YES | NULL |
| triglycerides | decimal | YES | NULL |
| blood_glucose | decimal | YES | NULL |
| hba1c | decimal | YES | NULL |
| creatinine | decimal | YES | NULL |
| egfr | decimal | YES | NULL |
| encounter_id | varchar | YES | NULL |
| created_at | timestamp | YES | current_timestamp() |

### Report
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| report_id | int | NO | null |
| patient_id | int | YES | NULL |
| report_type | enum | YES | NULL |
| report_date | date | NO | null |
| complete_report | longtext | YES | NULL |
| report_summary | text | YES | NULL |
| doctor_name | varchar | YES | NULL |
| created_at | timestamp | YES | current_timestamp() |

### Report_Finding
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| finding_id | int | NO | null |
| report_id | int | YES | NULL |
| finding_key | varchar | NO | null |
| finding_value | varchar | NO | null |
| finding_unit | varchar | YES | NULL |
| normal_range | varchar | YES | NULL |
| is_abnormal | tinyint | YES | 0 |
| abnormal_severity | enum | YES | NULL |

### Synthea_Allergy
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| allergy_id | int | NO | null |
| synthea_patient_id | varchar | YES | NULL |
| synthea_encounter_id | varchar | YES | NULL |
| code | varchar | YES | NULL |
| code_system | varchar | YES | NULL |
| description | text | YES | NULL |
| allergy_type | varchar | YES | NULL |
| category | varchar | YES | NULL |
| reaction1_code | varchar | YES | NULL |
| reaction1_description | text | YES | NULL |
| reaction1_severity | varchar | YES | NULL |
| reaction2_code | varchar | YES | NULL |
| reaction2_description | text | YES | NULL |
| reaction2_severity | varchar | YES | NULL |
| start_date | date | YES | NULL |
| stop_date | date | YES | NULL |
| is_active | tinyint | YES | 1 |
| created_at | timestamp | YES | current_timestamp() |

### Synthea_CarePlan
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| careplan_id | int | NO | null |
| synthea_id | varchar | YES | NULL |
| synthea_patient_id | varchar | YES | NULL |
| synthea_encounter_id | varchar | YES | NULL |
| code | varchar | YES | NULL |
| description | text | YES | NULL |
| start_date | date | YES | NULL |
| stop_date | date | YES | NULL |
| reason_code | varchar | YES | NULL |
| reason_description | text | YES | NULL |
| is_active | tinyint | YES | 1 |
| created_at | timestamp | YES | current_timestamp() |

### Synthea_Condition
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| condition_id | int | NO | null |
| synthea_patient_id | varchar | YES | NULL |
| synthea_encounter_id | varchar | YES | NULL |
| code | varchar | YES | NULL |
| code_system | varchar | YES | NULL |
| description | text | YES | NULL |
| start_date | date | YES | NULL |
| stop_date | date | YES | NULL |
| is_active | tinyint | YES | 1 |
| created_at | timestamp | YES | current_timestamp() |

### Synthea_Device
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| device_id | int | NO | null |
| synthea_patient_id | varchar | YES | NULL |
| synthea_encounter_id | varchar | YES | NULL |
| code | varchar | YES | NULL |
| description | text | YES | NULL |
| start_datetime | datetime | YES | NULL |
| stop_datetime | datetime | YES | NULL |
| udi | varchar | YES | NULL |
| created_at | timestamp | YES | current_timestamp() |

### Synthea_Encounter
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| encounter_id | int | NO | null |
| synthea_id | varchar | NO | null |
| synthea_patient_id | varchar | YES | NULL |
| synthea_organization_id | varchar | YES | NULL |
| synthea_provider_id | varchar | YES | NULL |
| synthea_payer_id | varchar | YES | NULL |
| encounter_class | varchar | YES | NULL |
| code | varchar | YES | NULL |
| description | text | YES | NULL |
| start_datetime | datetime | YES | NULL |
| stop_datetime | datetime | YES | NULL |
| base_cost | decimal | YES | NULL |
| total_claim_cost | decimal | YES | NULL |
| payer_coverage | decimal | YES | NULL |
| reason_code | varchar | YES | NULL |
| reason_description | text | YES | NULL |
| created_at | timestamp | YES | current_timestamp() |

### Synthea_ImagingStudy
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| imaging_id | int | NO | null |
| synthea_id | varchar | YES | NULL |
| synthea_patient_id | varchar | YES | NULL |
| synthea_encounter_id | varchar | YES | NULL |
| series_uid | varchar | YES | NULL |
| study_date | datetime | YES | NULL |
| bodysite_code | varchar | YES | NULL |
| bodysite_description | text | YES | NULL |
| modality_code | varchar | YES | NULL |
| modality_description | text | YES | NULL |
| instance_uid | varchar | YES | NULL |
| sop_code | varchar | YES | NULL |
| sop_description | text | YES | NULL |
| procedure_code | varchar | YES | NULL |
| created_at | timestamp | YES | current_timestamp() |

### Synthea_Immunization
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| immunization_id | int | NO | null |
| synthea_patient_id | varchar | YES | NULL |
| synthea_encounter_id | varchar | YES | NULL |
| immunization_date | date | YES | NULL |
| code | varchar | YES | NULL |
| description | text | YES | NULL |
| base_cost | decimal | YES | NULL |
| created_at | timestamp | YES | current_timestamp() |

### Synthea_Medication
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| medication_id | int | NO | null |
| synthea_patient_id | varchar | YES | NULL |
| synthea_encounter_id | varchar | YES | NULL |
| synthea_payer_id | varchar | YES | NULL |
| code | varchar | YES | NULL |
| description | text | YES | NULL |
| start_datetime | datetime | YES | NULL |
| stop_datetime | datetime | YES | NULL |
| base_cost | decimal | YES | NULL |
| payer_coverage | decimal | YES | NULL |
| dispenses | int | YES | NULL |
| total_cost | decimal | YES | NULL |
| reason_code | varchar | YES | NULL |
| reason_description | text | YES | NULL |
| is_active | tinyint | YES | 1 |
| created_at | timestamp | YES | current_timestamp() |

### Synthea_Observation
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| observation_id | int | NO | null |
| synthea_patient_id | varchar | YES | NULL |
| synthea_encounter_id | varchar | YES | NULL |
| observation_date | datetime | YES | NULL |
| category | varchar | YES | NULL |
| code | varchar | YES | NULL |
| description | text | YES | NULL |
| value | text | YES | NULL |
| units | varchar | YES | NULL |
| value_type | varchar | YES | NULL |
| created_at | timestamp | YES | current_timestamp() |

### Synthea_Organization
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| organization_id | int | NO | null |
| synthea_id | varchar | NO | null |
| name | varchar | YES | NULL |
| address | text | YES | NULL |
| city | varchar | YES | NULL |
| state | varchar | YES | NULL |
| zip | varchar | YES | NULL |
| latitude | decimal | YES | NULL |
| longitude | decimal | YES | NULL |
| phone | varchar | YES | NULL |
| revenue | decimal | YES | NULL |
| utilization | int | YES | NULL |
| created_at | timestamp | YES | current_timestamp() |

### Synthea_Patient
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| patient_id | int | NO | null |
| synthea_id | varchar | NO | null |
| first_name | varchar | YES | NULL |
| middle_name | varchar | YES | NULL |
| last_name | varchar | YES | NULL |
| prefix | varchar | YES | NULL |
| suffix | varchar | YES | NULL |
| maiden_name | varchar | YES | NULL |
| marital_status | varchar | YES | NULL |
| race | varchar | YES | NULL |
| ethnicity | varchar | YES | NULL |
| gender | enum | YES | NULL |
| birthdate | date | YES | NULL |
| deathdate | date | YES | NULL |
| ssn | varchar | YES | NULL |
| drivers_license | varchar | YES | NULL |
| passport | varchar | YES | NULL |
| address | text | YES | NULL |
| city | varchar | YES | NULL |
| state | varchar | YES | NULL |
| county | varchar | YES | NULL |
| zip | varchar | YES | NULL |
| latitude | decimal | YES | NULL |
| longitude | decimal | YES | NULL |
| healthcare_expenses | decimal | YES | NULL |
| healthcare_coverage | decimal | YES | NULL |
| income | int | YES | NULL |
| created_at | timestamp | YES | current_timestamp() |
| updated_at | timestamp | YES | current_timestamp() |

### Synthea_Procedure
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| procedure_id | int | NO | null |
| synthea_patient_id | varchar | YES | NULL |
| synthea_encounter_id | varchar | YES | NULL |
| code | varchar | YES | NULL |
| code_system | varchar | YES | NULL |
| description | text | YES | NULL |
| start_datetime | datetime | YES | NULL |
| stop_datetime | datetime | YES | NULL |
| base_cost | decimal | YES | NULL |
| reason_code | varchar | YES | NULL |
| reason_description | text | YES | NULL |
| created_at | timestamp | YES | current_timestamp() |

### Synthea_Provider
| Column Name | Data Type | Nullable | Default |
| :--- | :--- | :--- | :--- |
| provider_id | int | NO | null |
| synthea_id | varchar | NO | null |
| synthea_organization_id | varchar | YES | NULL |
| name | varchar | YES | NULL |
| gender | enum | YES | NULL |
| speciality | varchar | YES | NULL |
| address | text | YES | NULL |
| city | varchar | YES | NULL |
| state | varchar | YES | NULL |
| zip | varchar | YES | NULL |
| latitude | decimal | YES | NULL |
| longitude | decimal | YES | NULL |
| utilization | int | YES | NULL |
| created_at | timestamp | YES | current_timestamp() |
