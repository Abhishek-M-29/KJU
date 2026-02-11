import mariadb
import os
import requests
import logging
from dotenv import load_dotenv
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = int(os.getenv('DB_PORT', 3306))

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral" # Use mistral or whatever is available, maybe check?

def get_db_connection():
    try:
        conn = mariadb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        return conn
    except mariadb.Error as e:
        logger.error(f"Error connecting to MariaDB: {e}")
        return None

def concise_text_with_ollama(text):
    if not text or len(text) < 100:
        return text # Already short enough or empty

    prompt = f"""
    You are a medical data assistant. Summarize the following medical document text to be concise but retain all key clinical data points, such as test results, diagnosis, patient summary, and critical flags. Remove formatting lines, headers, and verbose disclaimers.
    
    TEXT:
    {text}
    
    CONCISE SUMMARY:
    """
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get('response', '').strip()
    except Exception as e:
        logger.error(f"Error calling Ollama: {e}")
        return None  # Return None to indicate failure

def main():
    conn = get_db_connection()
    if not conn:
        return

    cursor = conn.cursor()

    try:
        # Get documents
        cursor.execute("SELECT document_id, ocr_text FROM Patient_Documents WHERE ocr_text IS NOT NULL")
        documents = cursor.fetchall()
        
        logger.info(f"Found {len(documents)} documents to process.")

        updated_count = 0
        
        for doc_id, ocr_text in documents:
            if not ocr_text or len(ocr_text) < 200: # Skip small ones
                continue

            # Check if it looks like a lab report or verbose text
            if "=====" in ocr_text or "LABORATORY REPORT" in ocr_text or len(ocr_text) > 500:
                logger.info(f"Processing document {doc_id}...")
                concise_text = concise_text_with_ollama(ocr_text)
                
                if concise_text:
                    # Update DB
                    try:
                        cursor.execute(
                            "UPDATE Patient_Documents SET ocr_text = ? WHERE document_id = ?",
                            (concise_text, doc_id)
                        )
                        conn.commit()
                        updated_count += 1
                        logger.info(f"Updated document {doc_id}.")
                    except mariadb.Error as e:
                        logger.error(f"Failed to update document {doc_id}: {e}")
                else:
                    logger.warning(f"Failed to generate summary for document {doc_id}")
            
    except mariadb.Error as e:
        logger.error(f"Database error: {e}")
    finally:
        conn.close()
        logger.info(f"Finished. Updated {updated_count} documents.")

if __name__ == "__main__":
    main()
