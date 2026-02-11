# Correct Cypher Query Patterns for Hospital Database

This document provides correct Cypher query patterns to avoid syntax errors when querying the Neo4j hospital database.

## Common Error: Multiple RETURN Statements

❌ **INCORRECT - This causes syntax error:**
```cypher
MATCH (p:Patient {synthea_id: '03'}) RETURN p.first_name, p.last_name
MATCH (p:Patient {synthea_id: '03'}) OPTIONAL MATCH (p)-[:HAS_CONDITION]->(c) RETURN c
```

**Error:** "RETURN can only be used at the end of the query"

✅ **CORRECT - Single query with RETURN at end:**
```cypher
MATCH (p:Patient {synthea_id: '03'})
OPTIONAL MATCH (p)-[:HAS_CONDITION]->(c)
OPTIONAL MATCH (p)-[:TAKES_MEDICATION]->(m)
RETURN p.first_name, p.last_name, 
       collect(DISTINCT c.description) as conditions,
       collect(DISTINCT m.description) as medications
```

## Query Patterns by Use Case

### 1. Get Patient Basic Info
```cypher
MATCH (p:Patient {synthea_id: '03'})
RETURN p.first_name, p.last_name, p.age, p.gender
```

### 2. Get Patient with Conditions
```cypher
MATCH (p:Patient {synthea_id: '03'})
OPTIONAL MATCH (p)-[:HAS_CONDITION]->(c:Condition)
RETURN p.first_name, p.last_name,
       collect(c.description) as conditions
```

### 3. Get Patient with Medications
```cypher
MATCH (p:Patient {synthea_id: '03'})
OPTIONAL MATCH (p)-[:TAKES_MEDICATION]->(m:Medication)
RETURN p.first_name, p.last_name,
       collect(m.description) as medications
```

### 4. Get Complete Patient Profile
```cypher
MATCH (p:Patient {synthea_id: '03'})
OPTIONAL MATCH (p)-[:HAS_CONDITION]->(c:Condition)
OPTIONAL MATCH (p)-[:TAKES_MEDICATION]->(m:Medication)
OPTIONAL MATCH (p)-[:HAS_RISK_FACTOR]->(rf:RiskFactor)
OPTIONAL MATCH (p)-[:HAS_AI_FEATURES]->(ai:AIFeatureSet)
RETURN p.first_name, p.last_name, p.age, p.gender,
       collect(DISTINCT c.description) as conditions,
       collect(DISTINCT m.description) as medications,
       collect(DISTINCT rf.name) as risk_factors,
       ai.bmi as bmi,
       ai.bp_systolic as blood_pressure_systolic,
       ai.bp_diastolic as blood_pressure_diastolic
```

### 5. Get Patients with Specific Condition
```cypher
MATCH (p:Patient)-[:HAS_CONDITION]->(c:Condition)
WHERE c.description CONTAINS 'Diabetes'
RETURN p.synthea_id, p.first_name, p.last_name, c.description
LIMIT 10
```

### 6. Get High-Risk Patients
```cypher
MATCH (p:Patient)-[:HAS_RISK_FACTOR]->(rf:RiskFactor)
WITH p, collect(rf.name) as risk_factors, count(rf) as risk_count
WHERE risk_count >= 3
RETURN p.synthea_id, p.first_name, p.last_name, 
       risk_count, risk_factors
ORDER BY risk_count DESC
```

### 7. Get Doctor Appointments (MariaDB Query)
```sql
SELECT 
    a.appointment_id,
    a.appointment_date,
    a.appointment_time,
    a.status,
    p.name as patient_name,
    d.first_name as doctor_first_name,
    d.last_name as doctor_last_name,
    d.specialization
FROM Appointment a
JOIN Patient p ON a.patient_id = p.patient_id
JOIN Doctor d ON a.doctor_id = d.doctor_id
WHERE a.appointment_date >= CURDATE()
ORDER BY a.appointment_date, a.appointment_time
LIMIT 20;
```

### 8. Get Patient Appointments (MariaDB Query)
```sql
SELECT 
    a.appointment_id,
    a.appointment_date,
    a.appointment_time,
    a.status,
    a.appointment_type,
    a.notes,
    CONCAT(d.first_name, ' ', d.last_name) as doctor_name,
    d.specialization
FROM Appointment a
JOIN Doctor d ON a.doctor_id = d.doctor_id
WHERE a.patient_id = 1
ORDER BY a.appointment_date DESC
LIMIT 10;
```

## Key Rules

1. **RETURN must be at the end** - You can only have ONE RETURN statement per query
2. **Use OPTIONAL MATCH** for relationships that may not exist
3. **Use collect()** to aggregate multiple results
4. **Use DISTINCT** to avoid duplicates in collections
5. **Chain MATCH and OPTIONAL MATCH** before the final RETURN
6. **Use WITH** for intermediate processing if needed

## Multiple Queries

If you need to run multiple separate queries, execute them individually:

```python
# Python example using MCP tool
query1 = "MATCH (p:Patient {synthea_id: '03'}) RETURN p.first_name, p.last_name"
result1 = execute_query_neo4j(query1)

query2 = "MATCH (p:Patient {synthea_id: '03'})-[:HAS_CONDITION]->(c) RETURN collect(c.description) as conditions"
result2 = execute_query_neo4j(query2)
```

❌ **DO NOT concatenate queries:**
```python
# WRONG - This will cause syntax error
bad_query = query1 + " " + query2
```

## Using WITH for Complex Queries

For multi-step queries, use WITH to pass results between steps:

```cypher
MATCH (p:Patient)
WHERE p.age > 50
WITH p
MATCH (p)-[:HAS_CONDITION]->(c:Condition)
WHERE c.description CONTAINS 'Heart'
WITH p, collect(c.description) as conditions
OPTIONAL MATCH (p)-[:TAKES_MEDICATION]->(m:Medication)
RETURN p.synthea_id, p.first_name, p.last_name, 
       conditions, collect(m.description) as medications
LIMIT 10
```

## Testing Your Queries

Always test your Cypher queries before using them in production:

1. Use Neo4j Browser at http://127.0.0.1:7474
2. Test with LIMIT clause first
3. Check the execution plan with EXPLAIN or PROFILE
4. Verify the results are what you expect

## Common Mistakes to Avoid

1. ❌ Multiple RETURN statements in one query
2. ❌ Using MATCH after RETURN
3. ❌ Forgetting collect() when returning multiple relationships
4. ❌ Not using OPTIONAL MATCH for relationships that may not exist
5. ❌ Concatenating separate queries as strings
6. ❌ Missing quotes around string values in WHERE clauses
7. ❌ Using LIMIT without ORDER BY for consistent results
