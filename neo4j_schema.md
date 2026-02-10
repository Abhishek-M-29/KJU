# Neo4j Knowledge Graph Schema

## 1. Graph Structure

### Node Labels
| Label | Count |
| :--- | :--- |
| Observation | 40168 |
| LabResult | 25366 |
| VitalSign | 14802 |
| Procedure | 12052 |
| MedicalProcedure | 12052 |
| Encounter | 6197 |
| Visit | 6197 |
| Medication | 3884 |
| Prescription | 3778 |
| Condition | 3573 |
| Diagnosis | 3439 |
| Immunization | 1837 |
| Vaccine | 1837 |
| CarePlan | 361 |
| TreatmentPlan | 360 |
| Organization | 269 |
| HealthcareFacility | 269 |
| Provider | 269 |
| Clinician | 269 |
| ImagingStudy | 216 |
| Radiology | 216 |
| Patient | 181 |
| Person | 144 |
| AIFeatureSet | 133 |
| Device | 130 |
| MedicalDevice | 130 |
| FamilyHistory | 120 |
| Allergy | 60 |
| SocialHistory | 48 |
| RiskProfile | 37 |
| Lifestyle | 19 |
| RiskFactor | 3 |
| LabTrend | 1 |
| Doctor | 30 |

### Relationship Types
| Type | Count |
| :--- | :--- |
| SAME_DIAGNOSIS | 347296 |
| TREATS | 63343 |
| HAS_OBSERVATION | 40168 |
| RECORDED_OBSERVATION | 40168 |
| HAD_PROCEDURE | 12052 |
| PERFORMED_PROCEDURE | 12052 |
| HAS_ENCOUNTER | 6197 |
| AT_ORGANIZATION | 6197 |
| WITH_PROVIDER | 6197 |
| TAKES_MEDICATION | 4291 |
| HAS_CONDITION | 3910 |
| PRESCRIBED_MEDICATION | 3778 |
| DIAGNOSED_CONDITION | 3439 |
| RECEIVED_IMMUNIZATION | 1837 |
| ADMINISTERED_IMMUNIZATION | 1837 |
| TREATMENT_FOR | 1699 |
| HAS_CARE_PLAN | 361 |
| CREATED_CARE_PLAN | 360 |
| WORKS_AT | 269 |
| HAS_IMAGING_STUDY | 216 |
| ORDERED_IMAGING | 216 |
| TREATED_BY | 181 |
| HAS_FAMILY_HISTORY | 159 |
| HAS_AI_FEATURES | 133 |
| HAS_DEVICE | 130 |
| IMPLANTED_DEVICE | 130 |
| HAS_RISK_FACTOR | 76 |
| HAS_ALLERGY | 70 |
| HAS_SOCIAL_HISTORY | 48 |
| HAS_RISK_PROFILE | 37 |
| HAS_LIFESTYLE | 19 |
| HAS_LAB_TREND | 1 |

## 2. Node Schemas

### :`AIFeatureSet`
| Property | Type |
| :--- | :--- |
| age | Long |
| age_years | String |
| alcohol_use | Long |
| blood_glucose_fasting | Double |
| bmi | Double |
| bp_diastolic | Long, Double |
| bp_systolic | Long, Double |
| cholesterol_level | Long |
| cvd_risk_score | Long |
| data_source | String |
| diabetes_risk_score | Long |
| fasting_glucose | Long |
| gender | String |
| gender_numeric | Long |
| glucose_level | Long |
| has_heart_disease | Long |
| has_hypertension | Long |
| hba1c | Double |
| hba1c_level | Double |
| hdl | Long |
| heart_rate | Long |
| height_cm | Long, Double |
| is_smoker | Long |
| last_updated | DateTime |
| ldl | Long |
| node_type | String |
| patient_id | String |
| physical_activity | Long |
| smoking_history | String |
| smoking_status | String |
| total_cholesterol | Long |
| triglycerides | Long |
| weight_kg | Long, Double |

### :`Allergy`
| Property | Type |
| :--- | :--- |
| allergen | String |
| allergy_id | Long |
| allergy_type | String |
| category | String |
| code | String |
| code_system | String |
| data_source | String |
| description | String |
| entity_type | String |
| is_active | Boolean |
| last_updated | DateTime |
| name | String |
| node_type | String |
| patient_id | String |
| reaction | String |
| reaction1 | String |
| reaction1_severity | String |
| reaction2 | String |
| reaction2_severity | String |
| severity | String |
| start_date | String |
| type | String |

### :`CarePlan`:`TreatmentPlan`
| Property | Type |
| :--- | :--- |
| careplan_id | Long |
| code | String |
| condition | String |
| data_source | String |
| description | String |
| encounter_id | String |
| entity_type | String |
| goals | StringArray |
| interventions | StringArray |
| is_active | Boolean |
| last_updated | DateTime |
| name | String |
| node_type | String |
| patient_id | String |
| reason_code | String |
| reason_description | String |
| start_date | String |
| stop_date | String |
| synthea_id | String |

### :`Clinician`:`Provider`
| Property | Type |
| :--- | :--- |
| address | String |
| city | String |
| data_source | String |
| entity_type | String |
| gender | String |
| last_updated | DateTime |
| latitude | Double |
| longitude | Double |
| name | String |
| node_type | String |
| organization_id | String |
| speciality | String |
| state | String |
| synthea_id | String |
| utilization | Long |
| zip | String |

### :`Condition`:`Diagnosis`
| Property | Type |
| :--- | :--- |
| abatement_date | String |
| category | String |
| code | String |
| code_system | String |
| condition_id | Long |
| data_source | String |
| description | String |
| encounter_id | String |
| entity_type | String |
| is_active | Boolean |
| last_updated | DateTime |
| name | String |
| node_type | String |
| note | String |
| onset_date | String |
| patient_id | String |
| severity | String |
| start_date | String |
| stop_date | String |

### :`Device`:`MedicalDevice`
| Property | Type |
| :--- | :--- |
| code | String |
| data_source | String |
| description | String |
| device_id | Long |
| encounter_id | String |
| entity_type | String |
| last_updated | DateTime |
| name | String |
| node_type | String |
| start_datetime | String |
| stop_datetime | String |
| udi | String |

### :`Encounter`:`Visit`
| Property | Type |
| :--- | :--- |
| base_cost | Double |
| code | String |
| data_source | String |
| description | String |
| encounter_class | String |
| entity_type | String |
| last_updated | DateTime |
| node_type | String |
| organization_id | String |
| payer_coverage | Double |
| provider_id | String |
| reason_code | String |
| reason_description | String |
| start_datetime | String |
| stop_datetime | String |
| synthea_id | String |
| total_claim_cost | Double |

### :`FamilyHistory`
| Property | Type |
| :--- | :--- |
| age | String |
| age_at_onset | Long |
| condition | String |
| conditions | String |
| deceased | Boolean |
| patient_id | String |
| relation | String |
| relative | String |
| status | String |

### :`HealthcareFacility`:`Organization`
| Property | Type |
| :--- | :--- |
| address | String |
| city | String |
| data_source | String |
| entity_type | String |
| last_updated | DateTime |
| latitude | Double |
| longitude | Double |
| name | String |
| node_type | String |
| phone | String |
| revenue | Double |
| state | String |
| synthea_id | String |
| utilization | Long |
| zip | String |

### :`ImagingStudy`:`Radiology`
| Property | Type |
| :--- | :--- |
| bodysite_code | String |
| bodysite_description | String |
| data_source | String |
| encounter_id | String |
| entity_type | String |
| imaging_id | Long |
| last_updated | DateTime |
| modality_code | String |
| modality_description | String |
| node_type | String |
| procedure_code | String |
| series_uid | String |
| study_date | String |
| synthea_id | String |

### :`Immunization`:`Vaccine`
| Property | Type |
| :--- | :--- |
| base_cost | Double |
| code | String |
| data_source | String |
| description | String |
| encounter_id | String |
| entity_type | String |
| immunization_date | String |
| immunization_id | Long |
| last_updated | DateTime |
| name | String |
| node_type | String |

### :`LabResult`:`Observation`
| Property | Type |
| :--- | :--- |
| category | String |
| code | String |
| data_source | String |
| description | String |
| encounter_id | String |
| entity_type | String |
| last_updated | DateTime |
| name | String |
| node_type | String |
| observation_date | String |
| observation_id | Long |
| units | String |
| value | String |
| value_type | String |

### :`LabTrend`
| Property | Type |
| :--- | :--- |
| glucose_first | Long |
| glucose_latest | Long |
| glucose_peak | Long |
| hba1c_first | Double |
| hba1c_latest | Double |
| hba1c_peak | Double |
| patient_id | String |
| trend_direction | String |

### :`Lifestyle`
| Property | Type |
| :--- | :--- |
| alcohol_use | String |
| diet_quality | String |
| exercise_frequency | String |
| patient_id | String |
| sleep_hours | Long |
| smoking_pack_years | Long |
| smoking_status | String |
| stress_level | String |

### :`MedicalProcedure`:`Procedure`
| Property | Type |
| :--- | :--- |
| base_cost | Double |
| code | String |
| code_system | String |
| data_source | String |
| description | String |
| encounter_id | String |
| entity_type | String |
| last_updated | DateTime |
| name | String |
| node_type | String |
| procedure_id | Long |
| reason_code | String |
| reason_description | String |
| start_datetime | String |
| stop_datetime | String |

### :`Medication`:`Prescription`
| Property | Type |
| :--- | :--- |
| base_cost | Double |
| code | String |
| data_source | String |
| description | String |
| dispenses | Long |
| dosage | String |
| encounter_id | String |
| entity_type | String |
| is_active | Boolean |
| last_updated | DateTime |
| medication_id | Long |
| name | String |
| node_type | String |
| patient_id | String |
| reason_code | String |
| reason_description | String |
| start_datetime | String |
| status | String |
| stop_datetime | String |
| total_cost | Double |
| stop_reason | String |

### :`Observation`:`VitalSign`
| Property | Type |
| :--- | :--- |
| category | String |
| code | String |
| data_source | String |
| description | String |
| encounter_id | String |
| entity_type | String |
| last_updated | DateTime |
| name | String |
| node_type | String |
| observation_date | String |
| observation_id | Long |
| units | String |
| value | String |
| value_type | String |

### :`Doctor`
| Property | Type |
| :--- | :--- |
| name | String |
| first_name | String |
| last_name | String |
| doctor_id | Long |
| specialization | String |

### :`Patient`:`Person`
| Property | Type |
| :--- | :--- |
| address | String |
| age | Long |
| birth_date | String |
| birthdate | String |
| city | String |
| county | String |
| cvd_risk | Long |
| data_source | String |
| deathdate | String |
| diabetes_risk | Long |
| entity_type | String |
| ethnicity | String |
| first_name | String |
| full_name | String |
| gender | String |
| healthcare_coverage | Double |
| healthcare_expenses | Double |
| id | String |
| income | Long |
| is_deceased | Boolean |
| is_detailed | Boolean |
| is_persona | Boolean |
| last_name | String |
| last_updated | DateTime |
| latitude | Double |
| longitude | Double |
| marital_status | String |
| middle_name | String |
| name | String |
| narrative | String |
| node_type | String |
| occupation | String |
| patient_id | Long |
| patient_no | Long |
| race | String |
| state | String |
| synthea_id | String |
| zip | String |
| doctor_id | Long |

### :`RiskFactor`
| Property | Type |
| :--- | :--- |
| category | String |
| description | String |
| name | String |
| threshold_bmi | Long |
| threshold_diastolic | Long |
| threshold_glucose | Long |
| threshold_hba1c | Double |
| threshold_systolic | Long |

### :`RiskProfile`
| Property | Type |
| :--- | :--- |
| cardiovascular_risk | Long |
| diabetes_risk | Long |
| mortality_risk | Long |
| readmission_risk | Long |
| sepsis_risk | Long |

### :`SocialHistory`
| Property | Type |
| :--- | :--- |
| alcohol | String |
| alcohol_use | String |
| diet | String |
| diet_quality | String |
| education | String |
| employment | String |
| exercise | String |
| exercise_frequency | String |
| food_security | String |
| health_literacy | String |
| living_situation | String |
| occupation | String |
| patient_id | String |
| relationships | String |
| smoking_status | String |
| social_support | String |
| stress | String |
| stress_level | String |
| tobacco | String |
| transportation | String |
