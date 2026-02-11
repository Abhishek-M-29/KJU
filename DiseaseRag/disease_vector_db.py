"""
Disease Ontology Vector Database
Creates and queries a FAISS vector database from the compiled disease data.
Uses sentence-transformers for local embeddings (no API key needed).
"""

import json
import pickle
import numpy as np
from pathlib import Path
from tqdm import tqdm

# Paths
DATA_FILE = Path(__file__).parent / "disease-ontology" / "data" / "disease_ontology_compiled.jsonl"
DB_DIR = Path(__file__).parent / "disease_vector_db"
INDEX_FILE = DB_DIR / "faiss_index.bin"
METADATA_FILE = DB_DIR / "metadata.pkl"
EMBEDDINGS_FILE = DB_DIR / "embeddings.npy"

# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def load_disease_data():
    """Load the compiled disease data from JSONL."""
    documents = []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            doc = json.loads(line.strip())
            if doc.get("text"):  # Only include docs with text
                documents.append(doc)
    return documents


def create_embeddings(texts, model):
    """Create embeddings for a list of texts."""
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True  # For cosine similarity
    )
    return embeddings


def create_vector_db():
    """Create the FAISS vector database."""
    import faiss
    from sentence_transformers import SentenceTransformer
    
    print("=" * 60)
    print("Disease Ontology Vector Database Creator")
    print("=" * 60)
    
    # Create output directory
    DB_DIR.mkdir(exist_ok=True)
    
    # Load data
    print("\nLoading disease data...")
    documents = load_disease_data()
    print(f"Loaded {len(documents)} disease documents")
    
    # Load embedding model
    print(f"\nLoading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)
    
    # Extract texts and metadata
    texts = [doc["text"] for doc in documents]
    metadata = []
    for doc in documents:
        metadata.append({
            "id": doc["id"],
            "name": doc.get("name", ""),
            "description": doc.get("description", ""),
            "synonyms": doc.get("synonyms", []),
            "related_synonyms": doc.get("related_synonyms", []),
            "category": doc.get("category"),
            "pathophysiology": doc.get("pathophysiology"),
            "child_diseases": doc.get("child_diseases", []),
            "symptoms": doc.get("symptoms", []),
            "risk_factors": doc.get("risk_factors", []),
            "diagnostics": doc.get("diagnostics", []),
            "treatments": doc.get("treatments", []),
            "source": doc.get("source", "Disease Ontology Database"),
            "text": doc["text"]
        })
    
    # Create embeddings
    print(f"\nCreating embeddings for {len(texts)} documents...")
    embeddings = create_embeddings(texts, model)
    print(f"Embedding shape: {embeddings.shape}")
    
    # Create FAISS index
    print("\nCreating FAISS index...")
    dimension = embeddings.shape[1]
    
    # Use IndexFlatIP for cosine similarity (since embeddings are normalized)
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings.astype('float32'))
    
    print(f"Index contains {index.ntotal} vectors")
    
    # Save everything
    print("\nSaving database files...")
    
    # Save FAISS index
    faiss.write_index(index, str(INDEX_FILE))
    print(f"  Saved index to: {INDEX_FILE}")
    
    # Save metadata
    with open(METADATA_FILE, 'wb') as f:
        pickle.dump(metadata, f)
    print(f"  Saved metadata to: {METADATA_FILE}")
    
    # Save embeddings (for potential updates)
    np.save(EMBEDDINGS_FILE, embeddings)
    print(f"  Saved embeddings to: {EMBEDDINGS_FILE}")
    
    print(f"\n✅ Vector database created successfully!")
    print(f"   Location: {DB_DIR}")
    print(f"   Documents: {len(metadata)}")
    print(f"   Embedding dimension: {dimension}")
    
    return index, metadata, model


class DiseaseVectorDB:
    """Disease Ontology Vector Database for semantic search."""
    
    def __init__(self):
        """Load the vector database."""
        import faiss
        from sentence_transformers import SentenceTransformer
        
        if not INDEX_FILE.exists():
            raise FileNotFoundError(
                f"Vector database not found at {DB_DIR}. "
                "Run 'python disease_vector_db.py' to create it."
            )
        
        # Load FAISS index
        self.index = faiss.read_index(str(INDEX_FILE))
        
        # Load metadata
        with open(METADATA_FILE, 'rb') as f:
            self.metadata = pickle.load(f)
        
        # Load embedding model
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        
        print(f"Loaded vector database with {len(self.metadata)} diseases")
    
    def search(self, query: str, n_results: int = 5) -> list:
        """
        Search for diseases matching a query.
        
        Args:
            query: Search query (symptoms, disease name, description, etc.)
            n_results: Number of results to return
            
        Returns:
            List of matching diseases with similarity scores
        """
        # Create query embedding
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype('float32')
        
        # Search
        scores, indices = self.index.search(query_embedding, n_results)
        
        # Format results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result["similarity"] = float(score)
                results.append(result)
        
        return results
    
    def search_by_symptoms(self, symptoms: list, n_results: int = 5) -> list:
        """Search for diseases by a list of symptoms."""
        query = "symptoms: " + ", ".join(symptoms)
        return self.search(query, n_results)
    
    def get_disease_by_id(self, disease_id: str) -> dict:
        """Get a disease by its DOID."""
        for meta in self.metadata:
            if meta["id"] == disease_id:
                return meta
        return None
    
    def get_similar_diseases(self, disease_id: str, n_results: int = 5) -> list:
        """Find diseases similar to a given disease."""
        disease = self.get_disease_by_id(disease_id)
        if disease:
            return self.search(disease["text"], n_results + 1)[1:]  # Exclude self
        return []


def interactive_search():
    """Interactive search mode."""
    db = DiseaseVectorDB()
    
    print("\n" + "=" * 60)
    print("Disease Ontology Search")
    print("=" * 60)
    print("Enter your query to search for diseases.")
    print("Type 'quit' to exit.\n")
    
    while True:
        query = input("🔍 Search: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not query:
            continue
        
        results = db.search(query, n_results=5)
        
        print(f"\n📋 Found {len(results)} results:\n")
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['name']} ({result['id']})")
            print(f"   Similarity: {result['similarity']:.2%}")
            print(f"   📚 Source: {result.get('source', 'Disease Ontology Database')}")
            if result['description']:
                desc = result['description'][:200] + "..." if len(result['description']) > 200 else result['description']
                print(f"   {desc}")
            if result.get('symptoms'):
                symptoms = result['symptoms'][:5] if isinstance(result['symptoms'], list) else []
                if symptoms:
                    print(f"   Symptoms: {', '.join(symptoms)}")
            if result.get('synonyms'):
                synonyms = ", ".join(result['synonyms'][:3]) if isinstance(result['synonyms'], list) else result['synonyms']
                print(f"   Also known as: {synonyms}")
            print()


def test_search():
    """Run test searches."""
    db = DiseaseVectorDB()
    
    print("\n" + "=" * 60)
    print("Testing search...")
    print("=" * 60)
    
    test_queries = [
        "diabetes high blood sugar insulin",
        "cancer in the lungs difficulty breathing",
        "skin rash fever mosquito bite",
        "heart attack chest pain",
        "memory loss dementia alzheimer",
        "joint pain arthritis inflammation"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        results = db.search(query, n_results=3)
        
        for result in results:
            print(f"   • {result['name']} (similarity: {result['similarity']:.2%})")
            print(f"     📚 Citation: {result.get('source', 'Disease Ontology Database')}")
            if result['description']:
                desc = result['description'][:100] + "..." if len(result['description']) > 100 else result['description']
                print(f"     {desc}")
            if result.get('symptoms') and isinstance(result['symptoms'], list) and result['symptoms']:
                print(f"     Key symptoms: {', '.join(result['symptoms'][:3])}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "search":
            interactive_search()
        elif sys.argv[1] == "test":
            test_search()
    else:
        # Create database
        create_vector_db()
        
        # Run tests
        test_search()
