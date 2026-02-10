from service.rag_pipeline import GraphRAGService
from core.config import get_settings
import logging

# Setup basic logging to see the flow
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    print("Initializing Graph RAG Service...")
    try:
        service = GraphRAGService()
        settings = get_settings()
        
        print(f"\nConfiguration Loaded. Model: {settings.MODEL_NAME}")
        print("Note: Ensure your .env file has valid GROQ_API_KEY and NEO4J credentials.")
        
        while True:
            print("\n" + "="*50)
            patient_id = input("Enter Patient ID (or leave blank for Global Search, 'q' to quit): ").strip()
            if patient_id.lower() == 'q':
                break
                
            query = input("Enter your question: ").strip()
            if not query:
                continue

            print("\nThinking...")
            try:
                # Pass None if string is empty
                pid = patient_id if patient_id else None
                response = service.process_request(query, pid)
                print(f"\n[Answer]: {response}")
            except Exception as e:
                print(f"\n[Error]: An unexpected error occurred: {e}")

    except Exception as e:
        print(f"Critical Startup Error: {e}")

if __name__ == "__main__":
    main()
