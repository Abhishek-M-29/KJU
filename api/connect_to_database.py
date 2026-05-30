from fastmcp import FastMCP
import mariadb
import os
import logging
from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.time import Date, DateTime, Time, Duration
from datetime import datetime, date, time
import json
import subprocess
import sys

# Load environment variables
load_dotenv()

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Create logger
logger = logging.getLogger("HospitalDB-MCP")
logger.setLevel(logging.DEBUG)

# Create console handler with formatting
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create file handler for detailed logs
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mcp_server.log')
file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# Create formatters
console_format = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s', datefmt='%H:%M:%S')
file_format = logging.Formatter('%(asctime)s | %(levelname)-8s | %(funcName)-25s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

console_handler.setFormatter(console_format)
file_handler.setFormatter(file_format)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.info("="*60)
logger.info("HospitalDB MCP Server - Initializing")
logger.info("="*60)

# Get DB details
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = int(os.getenv('DB_PORT', 3305))

AURA_USER = os.getenv('AURA_USER')
AURA_PASSWORD = os.getenv('AURA_PASSWORD')

# Custom JSON encoder for Neo4j types
class Neo4jJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if obj is None:
            return None
        elif isinstance(obj, (Date, DateTime)):
            return obj.isoformat()
        elif isinstance(obj, Time):
            return obj.isoformat()
        elif isinstance(obj, Duration):
            return str(obj)
        elif isinstance(obj, (date, datetime, time)):
            return obj.isoformat()
        elif hasattr(obj, 'isoformat'):
            return obj.isoformat()
        elif hasattr(obj, '__str__'):
            return str(obj)
        return super().default(obj)

def serialize_neo4j_result(result):
    """Convert Neo4j result to JSON-serializable format"""
    def convert_value(value):
        if value is None:
            return None
        elif isinstance(value, (Date, DateTime, Time, Duration, date, datetime, time)):
            return str(value)
        elif hasattr(value, 'isoformat'):
            return value.isoformat()
        elif isinstance(value, dict):
            return {k: convert_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [convert_value(v) for v in value]
        elif hasattr(value, '__str__'):
            return str(value)
        return value
    
    if isinstance(result, dict):
        return {k: convert_value(v) for k, v in result.items()}
    elif isinstance(result, list):
        return [convert_value(item) for item in result]
    return convert_value(result)

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
URI = os.getenv('NEO4J_URI', 'neo4j://127.0.0.1:7687')
AUTH = (AURA_USER, AURA_PASSWORD)

# Neo4j connection status - will be verified on first use
NEO4J_AVAILABLE = False

def check_neo4j_connection():
    """Check if Neo4j is available"""
    global NEO4J_AVAILABLE
    logger.debug(f"Checking Neo4j connection to {URI}")
    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            driver.verify_connectivity()
        NEO4J_AVAILABLE = True
        logger.info(f"Neo4j connection verified successfully")
        return True
    except Exception as e:
        NEO4J_AVAILABLE = False
        logger.warning(f"Neo4j connection failed: {str(e)}")
        return False

# Don't fail at startup if Neo4j isn't available
print(f"📊 Neo4j URI: {URI}")
print(f"📊 Neo4j User: {AURA_USER}")
if check_neo4j_connection():
    print("✅ Neo4j connection verified")
else:
    print("⚠️ Neo4j not available - MCP server will start anyway (Neo4j tools will fail until connection is fixed)")


mcp = FastMCP("Database")


# =============================================================================
# INTERNAL HELPER FUNCTIONS (not exposed as MCP tools)
# =============================================================================

def _execute_query_neo4j_internal(cypher_query: str) -> dict:
    """Internal function to execute Neo4j queries - used by other tools."""
    logger.debug(f"Neo4j Query: {cypher_query[:200]}..." if len(cypher_query) > 200 else f"Neo4j Query: {cypher_query}")
    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            with driver.session() as session:
                result = session.run(cypher_query)
                records = [record.data() for record in result]
                serialized_records = serialize_neo4j_result(records)
                logger.debug(f"Neo4j Query returned {len(serialized_records)} records")
                return {"results": serialized_records, "count": len(serialized_records)}
    except Exception as e:
        logger.error(f"Neo4j Query failed: {str(e)}")
        return {"error": f"Database error: {str(e)}"}


def _execute_query_mariadb_internal(query: str) -> dict:
    """Internal function to execute MariaDB queries - used by other tools."""
    logger.debug(f"MariaDB Query: {query[:200]}..." if len(query) > 200 else f"MariaDB Query: {query}")
    
    if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
        logger.error("Database configuration incomplete - missing environment variables")
        return {"error": "Database configuration incomplete. Check .env file."}
    
    conn = None
    try:
        conn = mariadb.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            results = [dict(zip(columns, row)) for row in rows]
            logger.debug(f"MariaDB SELECT returned {len(results)} rows")
            return {"results": results, "count": len(results)}
        else:
            conn.commit()
            logger.debug(f"MariaDB Query executed, {cursor.rowcount} rows affected")
            return {"message": "Query executed successfully", "affected_rows": cursor.rowcount}
            
    except mariadb.Error as e:
        logger.error(f"MariaDB Error: {str(e)}")
        return {"error": f"Database error: {str(e)}"}
    except Exception as e:
        logger.error(f"MariaDB Unexpected Error: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}
    finally:
        if conn:
            conn.close()


# =============================================================================
# MCP TOOL DEFINITIONS
# =============================================================================

@mcp.tool("ExcecuteQuery_Neo4j")
def execute_query_neo4j(cypher_query: str) -> dict:
    """
    Execute a Cypher query on the Neo4j database.
    
    Args:
        cypher_query (str): The Cypher query to execute.
        
    Returns:
        dict: The result of the query or an error message.
    """
    logger.info(f"[TOOL] ExcecuteQuery_Neo4j called")
    result = _execute_query_neo4j_internal(cypher_query)
    if "error" in result:
        logger.warning(f"[TOOL] ExcecuteQuery_Neo4j failed: {result['error']}")
    else:
        logger.info(f"[TOOL] ExcecuteQuery_Neo4j success: {result.get('count', 0)} records")
    return result


@mcp.tool("ExecuteQuery_MariaDB")
def execute_query_mariadb(query: str) -> dict:
    """
    Execute a SQL query on the MariaDB database.
    
    Args:
        query (str): The SQL query to execute.
        
    Returns:
        dict: The result of the query or an error message.
    """
    logger.info(f"[TOOL] ExecuteQuery_MariaDB called")
    result = _execute_query_mariadb_internal(query)
    if "error" in result:
        logger.warning(f"[TOOL] ExecuteQuery_MariaDB failed: {result['error']}")
    else:
        logger.info(f"[TOOL] ExecuteQuery_MariaDB success: {result.get('count', result.get('affected_rows', 0))} rows")
    return result


@mcp.tool("GetPatients_MariaDB")
def get_patients_mariadb(limit: int = 100) -> dict:
    """
    Get all patients from MariaDB database.
    
    Args:
        limit (int): Maximum number of patients to return (default: 100)
        
    Returns:
        dict: List of patients with their basic info.
    """
    logger.info(f"[TOOL] GetPatients_MariaDB called (limit={limit})")
    query = f"SELECT patient_id, name, dob, sex, created_at FROM Patient LIMIT {limit}"
    result = _execute_query_mariadb_internal(query)
    logger.info(f"[TOOL] GetPatients_MariaDB returned {result.get('count', 0)} patients")
    return result


@mcp.tool("GetPatientDetails_MariaDB")
def get_patient_details_mariadb(patient_id: int) -> dict:
    """
    Get comprehensive details for a specific patient from MariaDB.
    
    Args:
        patient_id (int): The patient's ID.
        
    Returns:
        dict: Complete patient information including medical history, appointments, medications, etc.
    """
    logger.info(f"[TOOL] GetPatientDetails_MariaDB called (patient_id={patient_id})")
    result = {
        "patient_id": patient_id,
        "basic_info": None,
        "medical_history": [],
        "appointments": [],
        "medications": [],
        "lab_reports": [],
        "reports": []
    }
    
    # Get basic patient info
    patient_query = f"SELECT * FROM Patient WHERE patient_id = {patient_id}"
    patient_result = _execute_query_mariadb_internal(patient_query)
    if patient_result.get("results"):
        result["basic_info"] = patient_result["results"][0]
    
    # Get medical history
    history_query = f"SELECT * FROM Medical_History WHERE patient_id = {patient_id}"
    history_result = _execute_query_mariadb_internal(history_query)
    if history_result.get("results"):
        result["medical_history"] = history_result["results"]
    
    # Get appointments with symptoms
    appt_query = f"""
        SELECT a.*, GROUP_CONCAT(CONCAT(s.symptom_name, ':', s.severity) SEPARATOR '; ') as symptoms
        FROM Appointment a
        LEFT JOIN Appointment_Symptom s ON a.appointment_id = s.appointment_id
        WHERE a.patient_id = {patient_id}
        GROUP BY a.appointment_id
    """
    appt_result = _execute_query_mariadb_internal(appt_query)
    if appt_result.get("results"):
        result["appointments"] = appt_result["results"]
    
    # Get medications with purposes
    med_query = f"""
        SELECT m.*, GROUP_CONCAT(mp.condition_name SEPARATOR ', ') as conditions_treated
        FROM Medication m
        LEFT JOIN Medication_Purpose mp ON m.medication_id = mp.medication_id
        WHERE m.patient_id = {patient_id}
        GROUP BY m.medication_id
    """
    med_result = _execute_query_mariadb_internal(med_query)
    if med_result.get("results"):
        result["medications"] = med_result["results"]
    
    # Get lab reports with findings
    lab_query = f"""
        SELECT lr.*, GROUP_CONCAT(CONCAT(lf.test_name, ':', lf.test_value, ' ', lf.test_unit) SEPARATOR '; ') as findings
        FROM Lab_Report lr
        LEFT JOIN Lab_Finding lf ON lr.lab_report_id = lf.lab_report_id
        WHERE lr.patient_id = {patient_id}
        GROUP BY lr.lab_report_id
    """
    lab_result = _execute_query_mariadb_internal(lab_query)
    if lab_result.get("results"):
        result["lab_reports"] = lab_result["results"]
    
    # Get clinical reports
    report_query = f"SELECT report_id, report_type, report_date, report_summary, doctor_name FROM Report WHERE patient_id = {patient_id}"
    report_result = _execute_query_mariadb_internal(report_query)
    if report_result.get("results"):
        result["reports"] = report_result["results"]
    
    logger.info(f"[TOOL] GetPatientDetails_MariaDB completed - history:{len(result['medical_history'])}, appts:{len(result['appointments'])}, meds:{len(result['medications'])}")
    return result


@mcp.tool("GetPatients_Neo4j")
def get_patients_neo4j(limit: int = 100) -> dict:
    """
    Get all patients from Neo4j graph database.
    
    Args:
        limit (int): Maximum number of patients to return (default: 100)
        
    Returns:
        dict: List of patients from the knowledge graph.
    """
    logger.info(f"[TOOL] GetPatients_Neo4j called (limit={limit})")
    query = f"""
        MATCH (p:Patient)
        RETURN p.patient_id as patient_id, 
               p.name as name, 
               p.dob as dob, 
               p.gender as gender,
               p.created_at as created_at
        LIMIT {limit}
    """
    result = _execute_query_neo4j_internal(query)
    logger.info(f"[TOOL] GetPatients_Neo4j returned {result.get('count', 0)} patients")
    return result


@mcp.tool("GetPatientGraph_Neo4j")
def get_patient_graph_neo4j(patient_id: int) -> dict:
    """
    Get a patient's complete medical knowledge graph from Neo4j.
    
    Args:
        patient_id (int): The patient's ID.
        
    Returns:
        dict: Patient node with all connected medical entities and relationships.
    """
    logger.info(f"[TOOL] GetPatientGraph_Neo4j called (patient_id={patient_id})")
    query = f"""
        MATCH (p:Patient {{patient_id: '{patient_id}'}})
        OPTIONAL MATCH (p)-[r]->(n)
        WITH p, collect({{
            relationship: type(r),
            node_type: labels(n)[0],
            node_properties: properties(n)
        }}) as connections
        RETURN p as patient, connections
    """
    result = _execute_query_neo4j_internal(query)
    logger.info(f"[TOOL] GetPatientGraph_Neo4j completed for patient {patient_id}")
    return result


@mcp.tool("SyncMariaDBToNeo4j")
def sync_mariadb_to_neo4j(clear_existing: bool = True) -> dict:
    """
    Synchronize all patient data from MariaDB to Neo4j knowledge graph.
    This creates nodes and relationships in Neo4j based on the relational data.
    
    Args:
        clear_existing (bool): Whether to clear existing Neo4j data before sync (default: True)
        
    Returns:
        dict: Sync status and summary.
    """
    logger.info(f"[TOOL] SyncMariaDBToNeo4j called (clear_existing={clear_existing})")
    try:
        # Import the sync module
        from sync_mariadb_to_neo4j import sync_all
        
        success = sync_all(clear_existing=clear_existing)
        
        if success:
            logger.info("[TOOL] SyncMariaDBToNeo4j completed successfully")
            return {
                "status": "success",
                "message": "Successfully synchronized MariaDB data to Neo4j knowledge graph",
                "clear_existing": clear_existing
            }
        else:
            logger.error("[TOOL] SyncMariaDBToNeo4j failed")
            return {
                "status": "error",
                "message": "Synchronization failed. Check logs for details."
            }
    except ImportError as e:
        logger.error(f"[TOOL] SyncMariaDBToNeo4j import error: {str(e)}")
        return {"error": f"Could not import sync module: {str(e)}"}
    except Exception as e:
        logger.error(f"[TOOL] SyncMariaDBToNeo4j exception: {str(e)}")
        return {"error": f"Sync failed: {str(e)}"}


@mcp.tool("PopulateMariaDB")
def populate_mariadb(num_patients: int = 10, clear_existing: bool = True) -> dict:
    """
    Populate MariaDB with comprehensive patient data for testing.
    
    Args:
        num_patients (int): Number of patients to create (default: 10)
        clear_existing (bool): Whether to clear existing data before populating (default: True)
        
    Returns:
        dict: Population status and created patient IDs.
    """
    logger.info(f"[TOOL] PopulateMariaDB called (num_patients={num_patients}, clear_existing={clear_existing})")
    try:
        # Import the population module
        from populate_mariadb import populate_database
        
        patient_ids = populate_database(num_patients=num_patients, clear_existing=clear_existing)
        
        if patient_ids:
            logger.info(f"[TOOL] PopulateMariaDB created {len(patient_ids)} patients")
            return {
                "status": "success",
                "message": f"Successfully created {len(patient_ids)} patients",
                "patient_ids": patient_ids,
                "num_patients": len(patient_ids)
            }
        else:
            logger.error("[TOOL] PopulateMariaDB failed - no patients created")
            return {
                "status": "error",
                "message": "Population failed. Check logs for details."
            }
    except ImportError as e:
        logger.error(f"[TOOL] PopulateMariaDB import error: {str(e)}")
        return {"error": f"Could not import population module: {str(e)}"}
    except Exception as e:
        logger.error(f"[TOOL] PopulateMariaDB exception: {str(e)}")
        return {"error": f"Population failed: {str(e)}"}


@mcp.tool("GetDatabaseStats")
def get_database_stats() -> dict:
    """
    Get statistics from both MariaDB and Neo4j databases.
    
    Returns:
        dict: Counts and statistics from both databases.
    """
    logger.info("[TOOL] GetDatabaseStats called")
    stats = {
        "mariadb": {},
        "neo4j": {}
    }
    
    # MariaDB stats
    tables = ["Patient", "Medical_History", "Appointment", "Appointment_Symptom", 
              "Medication", "Medication_Purpose", "Lab_Report", "Lab_Finding", 
              "Report", "Report_Finding", "Chat_History"]
    
    for table in tables:
        result = _execute_query_mariadb_internal(f"SELECT COUNT(*) as count FROM {table}")
        if result.get("results"):
            stats["mariadb"][table] = result["results"][0]["count"]
    
    # Neo4j stats
    node_query = """
        MATCH (n)
        WITH labels(n) AS labels
        UNWIND labels AS label
        RETURN label, count(*) as count
        ORDER BY count DESC
    """
    node_result = _execute_query_neo4j_internal(node_query)
    if node_result.get("results"):
        stats["neo4j"]["nodes"] = {r["label"]: r["count"] for r in node_result["results"]}
    
    rel_query = """
        MATCH ()-[r]->()
        RETURN type(r) as relationship, count(*) as count
        ORDER BY count DESC
    """
    rel_result = _execute_query_neo4j_internal(rel_query)
    
    logger.info(f"[TOOL] GetDatabaseStats completed - MariaDB tables: {len(stats['mariadb'])}, Neo4j nodes: {len(stats.get('neo4j', {}).get('nodes', {}))}")
    return stats


@mcp.tool("GetGraphSchema_Neo4j")
def get_graph_schema_neo4j() -> dict:
    """
    Get the current schema/structure of the Neo4j graph database.
    
    Returns:
        dict: Node labels, relationship types, and their counts.
    """
    logger.info("[TOOL] GetGraphSchema_Neo4j called")
    schema = {
        "node_labels": [],
        "relationship_types": [],
        "relationship_patterns": []
    }
    
    # Get node labels with counts
    label_query = """
        MATCH (n)
        WITH labels(n) AS labels
        UNWIND labels AS label
        RETURN label, count(*) as count
        ORDER BY count DESC
    """
    label_result = _execute_query_neo4j_internal(label_query)
    if label_result.get("results"):
        schema["node_labels"] = label_result["results"]
    
    # Get relationship types with counts
    rel_query = """
        MATCH ()-[r]->()
        RETURN type(r) as relationship_type, count(*) as count
        ORDER BY count DESC
    """
    rel_result = _execute_query_neo4j_internal(rel_query)
    if rel_result.get("results"):
        schema["relationship_types"] = rel_result["results"]
    
    # Get relationship patterns (start -> relationship -> end)
    pattern_query = """
        MATCH (n)-[r]->(m)
        WITH labels(n)[0] as start_label, type(r) as rel_type, labels(m)[0] as end_label
        RETURN start_label, rel_type, end_label, count(*) as count
        ORDER BY count DESC
        LIMIT 50
    """
    pattern_result = _execute_query_neo4j_internal(pattern_query)
    if pattern_result.get("results"):
        schema["relationship_patterns"] = pattern_result["results"]
    
    logger.info(f"[TOOL] GetGraphSchema_Neo4j completed - labels: {len(schema['node_labels'])}, rel_types: {len(schema['relationship_types'])}")
    return schema


# =============================================================================
# KNOWLEDGE GRAPH MANIPULATION TOOLS
# =============================================================================

@mcp.tool("CreateNode_Neo4j")
def create_node_neo4j(label: str, properties: dict) -> dict:
    """
    Create a new node in the Neo4j knowledge graph.
    
    Args:
        label (str): The node label (e.g., 'Patient', 'Condition', 'RiskFactor')
        properties (dict): Dictionary of node properties
        
    Returns:
        dict: The created node or error message.
    """
    logger.info(f"[TOOL] CreateNode_Neo4j called (label={label}, props={list(properties.keys())})")
    try:
        # Build property string
        prop_items = []
        for key, value in properties.items():
            if isinstance(value, str):
                prop_items.append(f'{key}: "{value}"')
            elif isinstance(value, (int, float)):
                prop_items.append(f'{key}: {value}')
            elif isinstance(value, bool):
                prop_items.append(f'{key}: {"true" if value else "false"}')
            elif value is None:
                continue
            else:
                prop_items.append(f'{key}: "{str(value)}"')
        
        props_str = ', '.join(prop_items)
        
        query = f"""
            CREATE (n:{label} {{{props_str}}})
            SET n.created_at = datetime(),
                n.data_source = 'MCP_Created'
            RETURN n, id(n) as node_id
        """
        result = _execute_query_neo4j_internal(query)
        logger.info(f"[TOOL] CreateNode_Neo4j created node with label {label}")
        return result
    except Exception as e:
        logger.error(f"[TOOL] CreateNode_Neo4j failed: {str(e)}")
        return {"error": f"Failed to create node: {str(e)}"}


@mcp.tool("UpdateNode_Neo4j")
def update_node_neo4j(label: str, match_property: str, match_value: str, updates: dict) -> dict:
    """
    Update an existing node's properties in the Neo4j knowledge graph.
    
    Args:
        label (str): The node label (e.g., 'Patient', 'Condition')
        match_property (str): The property to match on (e.g., 'synthea_id', 'name')
        match_value (str): The value to match
        updates (dict): Dictionary of properties to update
        
    Returns:
        dict: The updated node or error message.
    """
    logger.info(f"[TOOL] UpdateNode_Neo4j called (label={label}, {match_property}={match_value})")
    try:
        # Build SET clause
        set_items = []
        for key, value in updates.items():
            if isinstance(value, str):
                set_items.append(f'n.{key} = "{value}"')
            elif isinstance(value, (int, float)):
                set_items.append(f'n.{key} = {value}')
            elif isinstance(value, bool):
                set_items.append(f'n.{key} = {"true" if value else "false"}')
            elif value is None:
                set_items.append(f'n.{key} = null')
            else:
                set_items.append(f'n.{key} = "{str(value)}"')
        
        set_str = ', '.join(set_items)
        
        query = f"""
            MATCH (n:{label} {{{match_property}: "{match_value}"}})
            SET {set_str},
                n.last_updated = datetime()
            RETURN n
        """
        result = _execute_query_neo4j_internal(query)
        logger.info(f"[TOOL] UpdateNode_Neo4j updated node {label}:{match_value}")
        return result
    except Exception as e:
        logger.error(f"[TOOL] UpdateNode_Neo4j failed: {str(e)}")
        return {"error": f"Failed to update node: {str(e)}"}


@mcp.tool("DeleteNode_Neo4j")
def delete_node_neo4j(label: str, match_property: str, match_value: str, detach: bool = True) -> dict:
    """
    Delete a node from the Neo4j knowledge graph.
    
    Args:
        label (str): The node label (e.g., 'Patient', 'Condition')
        match_property (str): The property to match on
        match_value (str): The value to match
        detach (bool): If True, also delete all relationships (default: True)
        
    Returns:
        dict: Confirmation message or error.
    """
    logger.info(f"[TOOL] DeleteNode_Neo4j called (label={label}, {match_property}={match_value}, detach={detach})")
    try:
        delete_cmd = "DETACH DELETE n" if detach else "DELETE n"
        
        query = f"""
            MATCH (n:{label} {{{match_property}: "{match_value}"}})
            {delete_cmd}
            RETURN count(*) as deleted_count
        """
        result = _execute_query_neo4j_internal(query)
        logger.info(f"[TOOL] DeleteNode_Neo4j deleted node {label}:{match_value}")
        return {"status": "success", "message": f"Node deletion executed", "result": result}
    except Exception as e:
        logger.error(f"[TOOL] DeleteNode_Neo4j failed: {str(e)}")
        return {"error": f"Failed to delete node: {str(e)}"}


@mcp.tool("CreateRelationship_Neo4j")
def create_relationship_neo4j(
    from_label: str, from_property: str, from_value: str,
    to_label: str, to_property: str, to_value: str,
    relationship_type: str, properties: dict = None
) -> dict:
    """
    Create a relationship between two nodes in the Neo4j knowledge graph.
    
    Args:
        from_label (str): Source node label (e.g., 'Patient')
        from_property (str): Source node match property (e.g., 'synthea_id')
        from_value (str): Source node match value
        to_label (str): Target node label (e.g., 'Condition')
        to_property (str): Target node match property
        to_value (str): Target node match value
        relationship_type (str): Type of relationship (e.g., 'HAS_CONDITION', 'TAKES_MEDICATION')
        properties (dict): Optional relationship properties
        
    Returns:
        dict: The created relationship or error message.
    """
    logger.info(f"[TOOL] CreateRelationship_Neo4j called ({from_label})-[{relationship_type}]->({to_label})")
    try:
        # Build properties string if provided
        props_str = ""
        if properties:
            prop_items = []
            for key, value in properties.items():
                if isinstance(value, str):
                    prop_items.append(f'{key}: "{value}"')
                elif isinstance(value, (int, float)):
                    prop_items.append(f'{key}: {value}')
                elif isinstance(value, bool):
                    prop_items.append(f'{key}: {"true" if value else "false"}')
            if prop_items:
                props_str = "{" + ', '.join(prop_items) + ", created_at: datetime()}"
            else:
                props_str = "{created_at: datetime()}"
        else:
            props_str = "{created_at: datetime()}"
        
        query = f"""
            MATCH (a:{from_label} {{{from_property}: "{from_value}"}})
            MATCH (b:{to_label} {{{to_property}: "{to_value}"}})
            MERGE (a)-[r:{relationship_type}]->(b)
            SET r += {props_str}
            RETURN a, r, b
        """
        result = _execute_query_neo4j_internal(query)
        logger.info(f"[TOOL] CreateRelationship_Neo4j created {relationship_type} relationship")
        return result
    except Exception as e:
        logger.error(f"[TOOL] CreateRelationship_Neo4j failed: {str(e)}")
        return {"error": f"Failed to create relationship: {str(e)}"}


@mcp.tool("DeleteRelationship_Neo4j")
def delete_relationship_neo4j(
    from_label: str, from_property: str, from_value: str,
    to_label: str, to_property: str, to_value: str,
    relationship_type: str
) -> dict:
    """
    Delete a relationship between two nodes in the Neo4j knowledge graph.
    
    Args:
        from_label (str): Source node label
        from_property (str): Source node match property
        from_value (str): Source node match value
        to_label (str): Target node label
        to_property (str): Target node match property
        to_value (str): Target node match value
        relationship_type (str): Type of relationship to delete
        
    Returns:
        dict: Confirmation message or error.
    """
    logger.info(f"[TOOL] DeleteRelationship_Neo4j called ({from_label})-[{relationship_type}]->({to_label})")
    try:
        query = f"""
            MATCH (a:{from_label} {{{from_property}: "{from_value}"}})-[r:{relationship_type}]->(b:{to_label} {{{to_property}: "{to_value}"}})
            DELETE r
            RETURN count(*) as deleted_count
        """
        result = _execute_query_neo4j_internal(query)
        logger.info(f"[TOOL] DeleteRelationship_Neo4j deleted {relationship_type} relationship")
        return {"status": "success", "message": "Relationship deleted", "result": result}
    except Exception as e:
        logger.error(f"[TOOL] DeleteRelationship_Neo4j failed: {str(e)}")
        return {"error": f"Failed to delete relationship: {str(e)}"}


# =============================================================================
# SYNTHEA DATA PIPELINE TOOLS
# =============================================================================

@mcp.tool("RunSyntheaPipeline")
def run_synthea_pipeline(num_patients: int = 50, state: str = "Massachusetts", city: str = None, 
                         clear_all: bool = True, skip_generate: bool = False) -> dict:
    """
    Run the complete Synthea healthcare data pipeline.
    Generates synthetic patients, loads into MariaDB, and syncs to Neo4j.
    
    Args:
        num_patients (int): Number of patients to generate (default: 50)
        state (str): US state for patient generation (default: Massachusetts)
        city (str): Optional city for patient generation
        clear_all (bool): Clear existing data before loading (default: True)
        skip_generate (bool): Skip Synthea generation, use existing data (default: False)
        
    Returns:
        dict: Pipeline execution status and summary.
    """
    logger.info(f"[TOOL] RunSyntheaPipeline called (patients={num_patients}, state={state}, city={city})")
    try:
        cmd = [sys.executable, 'synthea_pipeline.py', '-p', str(num_patients), '-s', state]
        if city:
            cmd.extend(['-c', city])
        if clear_all:
            cmd.append('--clear-all')
        if skip_generate:
            cmd.append('--skip-generate')
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode == 0:
            logger.info("[TOOL] RunSyntheaPipeline completed successfully")
        else:
            logger.error(f"[TOOL] RunSyntheaPipeline failed with return code {result.returncode}")
        
        return {
            "status": "success" if result.returncode == 0 else "error",
            "message": f"Pipeline {'completed' if result.returncode == 0 else 'failed'}",
            "output": result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout,
            "errors": result.stderr[-1000:] if result.stderr else None
        }
    except Exception as e:
        logger.error(f"[TOOL] RunSyntheaPipeline exception: {str(e)}")
        return {"error": f"Pipeline failed: {str(e)}"}


@mcp.tool("LoadSyntheaToMariaDB")
def load_synthea_to_mariadb(synthea_dir: str = None, clear_existing: bool = True, skip_ai_features: bool = False) -> dict:
    """
    Load Synthea CSV data into MariaDB and extract AI model features.
    
    Args:
        synthea_dir (str): Path to Synthea output directory (default: synthea_output/csv)
        clear_existing (bool): Whether to clear existing data before loading (default: True)
        skip_ai_features (bool): Skip AI feature extraction (default: False)
        
    Returns:
        dict: Load status and summary.
    """
    logger.info(f"[TOOL] LoadSyntheaToMariaDB called (dir={synthea_dir}, clear={clear_existing})")
    try:
        cmd = [sys.executable, 'synthea_to_mariadb.py']
        if synthea_dir:
            cmd.extend(['--synthea-dir', synthea_dir])
        if clear_existing:
            cmd.append('--clear')
        if skip_ai_features:
            cmd.append('--skip-ai-features')
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode == 0:
            logger.info("[TOOL] LoadSyntheaToMariaDB completed successfully")
        else:
            logger.error(f"[TOOL] LoadSyntheaToMariaDB failed with return code {result.returncode}")
        
        return {
            "status": "success" if result.returncode == 0 else "error",
            "message": "Successfully loaded Synthea data into MariaDB" if result.returncode == 0 else "Loading failed",
            "output": result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout,
            "errors": result.stderr[-1000:] if result.stderr else None
        }
    except Exception as e:
        logger.error(f"[TOOL] LoadSyntheaToMariaDB exception: {str(e)}")
        return {"error": f"Load failed: {str(e)}"}


@mcp.tool("SyncSyntheaToNeo4j")
def sync_synthea_to_neo4j(clear_existing: bool = True, skip_observations: bool = False, skip_ai_features: bool = False) -> dict:
    """
    Synchronize Synthea data from MariaDB to Neo4j knowledge graph.
    This includes all patient data, conditions, medications, and AI model features.
    
    Args:
        clear_existing (bool): Whether to clear existing Neo4j data before sync (default: True)
        skip_observations (bool): Skip syncing observations for faster sync (default: False)
        skip_ai_features (bool): Skip syncing AI model features (default: False)
        
    Returns:
        dict: Sync status and summary.
    """
    logger.info(f"[TOOL] SyncSyntheaToNeo4j called (clear={clear_existing}, skip_obs={skip_observations})")
    try:
        cmd = [sys.executable, 'synthea_to_neo4j.py']
        if clear_existing:
            cmd.append('--clear')
        if skip_observations:
            cmd.append('--skip-observations')
        if skip_ai_features:
            cmd.append('--skip-ai-features')
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode == 0:
            logger.info("[TOOL] SyncSyntheaToNeo4j completed successfully")
        else:
            logger.error(f"[TOOL] SyncSyntheaToNeo4j failed with return code {result.returncode}")
        
        return {
            "status": "success" if result.returncode == 0 else "error",
            "message": "Successfully synced to Neo4j" if result.returncode == 0 else "Sync failed",
            "output": result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout,
            "errors": result.stderr[-1000:] if result.stderr else None
        }
    except Exception as e:
        logger.error(f"[TOOL] SyncSyntheaToNeo4j exception: {str(e)}")
        return {"error": f"Sync failed: {str(e)}"}


# =============================================================================
# AI MODEL INTEGRATION TOOLS
# =============================================================================

@mcp.tool("GetPatientAIFeatures")
def get_patient_ai_features(patient_id: str = None, limit: int = 50) -> dict:
    """
    Get AI model features for patients from the knowledge graph.
    Returns data needed for cardiovascular and diabetes prediction models.
    
    Args:
        patient_id (str): Optional specific patient synthea_id to query
        limit (int): Maximum number of patients to return (default: 50)
        
    Returns:
        dict: AI features for cardiovascular and diabetes models.
    """
    logger.info(f"[TOOL] GetPatientAIFeatures called (patient_id={patient_id}, limit={limit})")
    if patient_id:
        query = f"""
            MATCH (p:Patient {{synthea_id: "{patient_id}"}})-[:HAS_AI_FEATURES]->(ai:AIFeatureSet)
            RETURN p.synthea_id as patient_id,
                   p.name as patient_name,
                   ai.age_years as age,
                   ai.gender as gender,
                   ai.height_cm as height,
                   ai.weight_kg as weight,
                   ai.bmi as bmi,
                   ai.bp_systolic as ap_hi,
                   ai.bp_diastolic as ap_lo,
                   ai.cholesterol_level as cholesterol,
                   ai.glucose_level as gluc,
                   ai.is_smoker as smoke,
                   ai.alcohol_use as alco,
                   ai.physical_activity as active,
                   ai.has_hypertension as hypertension,
                   ai.has_heart_disease as heart_disease,
                   ai.hba1c_level as HbA1c_level,
                   ai.blood_glucose_fasting as blood_glucose_level
        """
    else:
        query = f"""
            MATCH (p:Patient)-[:HAS_AI_FEATURES]->(ai:AIFeatureSet)
            RETURN p.synthea_id as patient_id,
                   p.name as patient_name,
                   ai.age_years as age,
                   ai.gender as gender,
                   ai.height_cm as height,
                   ai.weight_kg as weight,
                   ai.bmi as bmi,
                   ai.bp_systolic as ap_hi,
                   ai.bp_diastolic as ap_lo,
                   ai.cholesterol_level as cholesterol,
                   ai.glucose_level as gluc,
                   ai.is_smoker as smoke,
                   ai.alcohol_use as alco,
                   ai.physical_activity as active
            LIMIT {limit}
        """
    
    result = _execute_query_neo4j_internal(query)
    logger.info(f"[TOOL] GetPatientAIFeatures returned {result.get('count', 0)} records")
    return result


@mcp.tool("GetPatientRiskFactors")
def get_patient_risk_factors(patient_id: str = None) -> dict:
    """
    Get risk factors associated with patients from the knowledge graph.
    
    Args:
        patient_id (str): Optional specific patient synthea_id to query
        
    Returns:
        dict: Patients and their associated risk factors.
    """
    logger.info(f"[TOOL] GetPatientRiskFactors called (patient_id={patient_id})")
    if patient_id:
        query = f"""
            MATCH (p:Patient {{synthea_id: "{patient_id}"}})-[:HAS_RISK_FACTOR]->(rf:RiskFactor)
            RETURN p.synthea_id as patient_id,
                   p.name as patient_name,
                   collect({{
                       name: rf.name,
                       category: rf.category,
                       description: rf.description
                   }}) as risk_factors
        """
    else:
        query = """
            MATCH (p:Patient)-[:HAS_RISK_FACTOR]->(rf:RiskFactor)
            WITH p, collect(rf.name) as risks
            RETURN p.synthea_id as patient_id,
                   p.name as patient_name,
                   risks as risk_factors,
                   size(risks) as risk_count
            ORDER BY risk_count DESC
            LIMIT 50
        """
    
    result = _execute_query_neo4j_internal(query)
    logger.info(f"[TOOL] GetPatientRiskFactors returned {result.get('count', 0)} records")
    return result


@mcp.tool("GetHighRiskPatients")
def get_high_risk_patients(risk_type: str = "all", threshold: int = 2) -> dict:
    """
    Get patients with high risk based on number of risk factors.
    
    Args:
        risk_type (str): Type of risk - 'cardiovascular', 'diabetes', 'all' (default: 'all')
        threshold (int): Minimum number of risk factors to be considered high risk (default: 2)
        
    Returns:
        dict: List of high-risk patients with their risk details.
    """
    logger.info(f"[TOOL] GetHighRiskPatients called (risk_type={risk_type}, threshold={threshold})")
    query = f"""
        MATCH (p:Patient)-[:HAS_RISK_FACTOR]->(rf:RiskFactor)
        WITH p, collect(rf.name) as risks, count(rf) as risk_count
        WHERE risk_count >= {threshold}
        OPTIONAL MATCH (p)-[:HAS_AI_FEATURES]->(ai:AIFeatureSet)
        RETURN p.synthea_id as patient_id,
               p.name as patient_name,
               p.age as age,
               risk_count,
               risks as risk_factors,
               ai.bp_systolic as bp_systolic,
               ai.bmi as bmi
        ORDER BY risk_count DESC
    """
    
    result = _execute_query_neo4j_internal(query)
    logger.info(f"[TOOL] GetHighRiskPatients returned {result.get('count', 0)} high-risk patients")
    return result


@mcp.tool("AnalyzePatientHealth")
def analyze_patient_health(patient_id: str) -> dict:
    """
    Perform comprehensive health analysis on a patient from the knowledge graph.
    Returns conditions, medications, risk factors, and vitals.
    
    Args:
        patient_id (str): Patient's synthea_id
        
    Returns:
        dict: Comprehensive patient health analysis.
    """
    logger.info(f"[TOOL] AnalyzePatientHealth called (patient_id={patient_id})")
    query = f"""
        MATCH (p:Patient {{synthea_id: "{patient_id}"}})
        
        OPTIONAL MATCH (p)-[:HAS_AI_FEATURES]->(ai:AIFeatureSet)
        
        OPTIONAL MATCH (p)-[:HAS_CONDITION]->(c:Condition)
        WITH p, ai, collect(DISTINCT c.description) as conditions
        
        OPTIONAL MATCH (p)-[:TAKES_MEDICATION]->(m:Medication)
        WITH p, ai, conditions, collect(DISTINCT m.description) as medications
        
        OPTIONAL MATCH (p)-[:HAS_RISK_FACTOR]->(rf:RiskFactor)
        WITH p, ai, conditions, medications, collect(DISTINCT rf.name) as risk_factors
        
        OPTIONAL MATCH (p)-[:HAS_ALLERGY]->(a:Allergy)
        WITH p, ai, conditions, medications, risk_factors, collect(DISTINCT a.description) as allergies
        
        RETURN p.synthea_id as patient_id,
               p.name as patient_name,
               p.age as age,
               p.gender as gender,
               {{
                   bmi: ai.bmi,
                   bp_systolic: ai.bp_systolic,
                   bp_diastolic: ai.bp_diastolic,
                   cholesterol: ai.total_cholesterol,
                   glucose: ai.blood_glucose_fasting,
                   hba1c: ai.hba1c_level
               }} as vitals,
               conditions,
               medications,
               risk_factors,
               allergies
    """
    
    result = _execute_query_neo4j_internal(query)
    logger.info(f"[TOOL] AnalyzePatientHealth completed for patient {patient_id}")
    return result


# =============================================================================
# CONNECTION TEST TOOLS
# =============================================================================

@mcp.tool("TestAllConnections")
def test_all_connections() -> dict:
    """
    Test all database connections (MariaDB and Neo4j).
    
    Returns:
        dict: Status of all database connections.
    """
    logger.info("[TOOL] TestAllConnections called")
    results = {
        "mariadb": {"status": "unknown", "message": ""},
        "neo4j": {"status": "unknown", "message": ""}
    }
    
    # Test MariaDB
    try:
        conn = mariadb.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        results["mariadb"] = {
            "status": "connected",
            "message": f"Successfully connected to {DB_HOST}:{DB_PORT}/{DB_NAME}",
            "host": DB_HOST,
            "port": DB_PORT,
            "database": DB_NAME
        }
    except Exception as e:
        results["mariadb"] = {
            "status": "error",
            "message": str(e)
        }
    
    # Test Neo4j
    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            driver.verify_connectivity()
        results["neo4j"] = {
            "status": "connected",
            "message": f"Successfully connected to {URI}",
            "uri": URI,
            "user": AURA_USER
        }
    except Exception as e:
        results["neo4j"] = {
            "status": "error", 
            "message": str(e)
        }
    
    logger.info(f"[TOOL] TestAllConnections completed - MariaDB: {results['mariadb']['status']}, Neo4j: {results['neo4j']['status']}")
    return results


if __name__ == "__main__":
    import argparse
    import socket
    
    parser = argparse.ArgumentParser(description="Healthcare Database MCP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0 for all interfaces)")
    parser.add_argument("--port", type=int, default=8069, help="Port to listen on (default: 8069)")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"], help="Log level")
    args = parser.parse_args()
    
    # Get local IP addresses for network access
    def get_local_ips():
        ips = []
        try:
            # Get all network interfaces
            hostname = socket.gethostname()
            ips.append(f"localhost:{args.port}")
            ips.append(f"127.0.0.1:{args.port}")
            
            # Try to get LAN IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(("8.8.8.8", 80))
                lan_ip = s.getsockname()[0]
                ips.append(f"{lan_ip}:{args.port}")
            except Exception:
                pass
            finally:
                s.close()
            
            # Also try hostname resolution
            try:
                host_ip = socket.gethostbyname(hostname)
                if host_ip not in ["127.0.0.1", "localhost"]:
                    ips.append(f"{host_ip}:{args.port}")
            except Exception:
                pass
                
        except Exception as e:
            print(f"Warning: Could not determine network IPs: {e}")
        return ips
    
    print("\n" + "="*60)
    print("🏥 HEALTHCARE DATABASE MCP SERVER")
    print("="*60)
    print(f"\n📊 Database Configuration:")
    print(f"   MariaDB: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    print(f"   Neo4j:   {URI}")
    
    print(f"\n🌐 MCP Server Network Access URLs:")
    for ip in get_local_ips():
        print(f"   http://{ip}/mcp/")
    
    print(f"\n📋 Add to your mcp.json:")
    print(f'''   {{
     "servers": {{
       "HospitalDB": {{
         "url": "http://<IP_ADDRESS>:{args.port}/mcp/",
         "type": "http"
       }}
     }}
   }}''')
    print("\n" + "="*60 + "\n")
    
    mcp.run(
        transport="streamable-http",
        host=args.host,
        port=args.port,
        log_level=args.log_level
    )
