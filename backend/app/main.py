from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.upload import router as upload_router
from .routes.verify import router as verify_router, set_rag_components
from .services.rag_store import load_documents, build_faiss_index

app = FastAPI(title="FinVerge")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize RAG components
docs = load_documents()
faiss_index, docs = build_faiss_index(docs)

# Set RAG components for verify router
set_rag_components(faiss_index, docs)

# Include routers
app.include_router(upload_router, prefix="/upload")
app.include_router(verify_router, prefix="/verify")

@app.get("/")
def root():
    return {
        "service": "FinVerge Procurement Verification API",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "upload_document": "/upload/",
            "verify_documents": "/verify/2way",
            "api_docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    return {
        "service_status": "healthy",
        "knowledge_base": {
            "documents_loaded": len(docs),
            "search_engine": "sklearn_cosine_similarity",
            "ready": faiss_index["embeddings"] is not None if faiss_index else False
        },
        "capabilities": [
            "PDF document processing",
            "Item extraction from invoices and POs", 
            "2-way verification (PO vs Invoice)",
            "AI-powered compliance checking",
            "Policy-based recommendations"
        ]
    }
