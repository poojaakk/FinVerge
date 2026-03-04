import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from ..config import settings

model = SentenceTransformer(settings.EMBEDDING_MODEL)

def load_documents(folder=None):
    if folder is None:
        folder = settings.KNOWLEDGE_BASE_PATH
        
    docs = []
    try:
        if not os.path.exists(folder):
            print(f"Warning: {folder} directory not found. Creating empty knowledge base.")
            return []
            
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(('.txt', '.md', '.pdf')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding='utf-8') as f:
                            content = f.read()
                            if content.strip():  # Only add non-empty files
                                docs.append({
                                    "text": content,
                                    "source": file
                                })
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
    except Exception as e:
        print(f"Error loading documents: {e}")
    
    return docs

def build_faiss_index(docs):
    """Build a simple similarity index using sklearn instead of FAISS"""
    if not docs:
        print("No documents found. Creating empty index.")
        return {"embeddings": None, "docs": docs}, docs
    
    texts = [d["text"] for d in docs]
    embeddings = model.encode(texts)
    
    # Store embeddings in a simple dictionary structure
    index = {
        "embeddings": embeddings,
        "docs": docs
    }
    
    print(f"Built index with {len(docs)} documents")
    return index, docs

def retrieve_context(query, index, docs, k=None):
    if k is None:
        k = settings.RAG_TOP_K
        
    if not docs or index["embeddings"] is None:
        return []
        
    query_embedding = model.encode([query])
    
    # Calculate cosine similarity
    similarities = cosine_similarity(query_embedding, index["embeddings"])[0]
    
    # Get top k most similar documents
    top_indices = np.argsort(similarities)[::-1][:k]
    
    results = []
    for idx in top_indices:
        if idx < len(docs):  # Safety check
            results.append(docs[idx])

    return results
