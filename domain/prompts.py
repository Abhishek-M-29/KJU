from domain.schema import CLINICAL_SCHEMA
from datetime import datetime

class PromptBuilder:
    
    SYSTEM_TEMPLATE = """
    You are an expert Neo4j Developer translating natural language questions into precise Cypher queries.

    Task: Generate a Cypher query to answer the user's question based strictly on the provided schema.

    Schema:
    {schema}

    Critical Instructions:
    1. Read-Only: NEVER generate queries that CREATE, UPDATE, DELETE, or MERGE data. Use only MATCH and RETURN.
    2. Schema Compliance: Use ONLY the node labels, relationship types, and properties defined in the Schema.
       - Do not assume relationships like (Encouter)-[:HAS_PATIENT]->(Patient) if not listed.
       - Verify property names (e.g., use 'onset_date', not 'date', for Conditions if that's what the schema says).
    3. Syntax rules:
       - Use `toInteger()` instead of `TO_INT()`.
       - Use `EXISTS()` or `IS NOT NULL` to check for property existence.
       - Use `substring()` instead of `substr()`. 
       - For string matching, use case-insensitive comparison: `WHERE toLower(n.prop) CONTAINS toLower('term')` or `(?i)` regex.
    4. Output Format:
       - Return ONLY the raw Cypher query string.
       - Do NOT wrap in markdown blocks (```cypher ... ```).
       - Do NOT provide explanations.
    5. Logic:
       - If asking for "latest" or "most recent", order by date DESC and use LIMIT 1.
       - When querying dates, assume string format YYYY-MM-DD.
    
    Context:
    - Current Date: {current_date}
    {context_instruction}
    """
    
    @staticmethod
    def get_cypher_gen_messages(query: str, patient_id: str = None, doctor_id: str = None) -> list:
        context_instruction = ""
        val_repr = None

        if doctor_id:
            try:
                # Format doctor ID correctly for Cypher (int vs string)
                clean_doc_id = int(str(doctor_id))
                val_repr = str(clean_doc_id)
            except ValueError:
                val_repr = f"'{doctor_id}'"

        # 1. Handle Patient Context
        if patient_id:
            # Determine if UUID or Integer ID
            if "-" in str(patient_id) and any(c.isalpha() for c in str(patient_id)):
                # UUID case
                base_match = f"MATCH (p:Patient {{synthea_id: '{patient_id}'}})"
            else:
                # Integer case
                try:
                    clean_id = int(str(patient_id))
                except ValueError:
                    clean_id = patient_id 
                base_match = f"MATCH (p:Patient {{patient_no: {clean_id}}})"

            # Add Doctor Security Check if verified
            if doctor_id:
                # Allow access if relationship exists OR if patient record has matching doctor_id property
                # This handles cases where the graph edge might be missing but the foreign key exists
                context_instruction = (
                    f"IMPORTANT: You MUST start your query exactly like this to enforce security:\n"
                    f"{base_match}\n"
                    # Note: We compare doctor_id as string because standard CSV imports often make IDs strings
                    f"WHERE (toString(p.doctor_id) = '{doctor_id}' OR EXISTS {{ (p)<-[:TREATED_BY]-(:Doctor {{doctor_id: {val_repr} }}) }})"
                )
            else:
                context_instruction = f"IMPORTANT: Start your query with: {base_match}"

        elif doctor_id:
            # 2. Handle Doctor-only Context (Cohort analysis)
             context_instruction = f"IMPORTANT: Scope search to patients treated by Doctor {val_repr}. Start query with: MATCH (p:Patient) WHERE p.doctor_id = '{doctor_id}' OR EXISTS {{ (p)<-[:TREATED_BY]-(:Doctor {{doctor_id: {val_repr} }}) }}"

        # Generate System Prompt
        system_prompt = PromptBuilder.SYSTEM_TEMPLATE.format(
            schema=CLINICAL_SCHEMA,
            current_date=datetime.now().strftime("%Y-%m-%d"),
            context_instruction=context_instruction
        )
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]

    @staticmethod
    def get_summarization_messages(query: str, data: list) -> list:
        return [
            {"role": "system", "content": "You are a helpful medical assistant. Summarize the following database results to answer the user's question. Be concise."},
            {"role": "user", "content": f"Question: {query}\nData: {data}"}
        ]
