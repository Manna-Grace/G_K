from sentence_transformers import CrossEncoder

# Initialize encoder 
try:
    reranker_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")
except Exception:
    reranker_model = None

def rerank_documents(query: str, documents, top_n: int = 3):
    """Polishes up our search results to make sure they are super relevant! ✨"""
    if not documents or not reranker_model:
        return documents
        
    pairs = [[query, doc.page_content] for doc in documents]
    scores = reranker_model.predict(pairs)
    
    for doc, score in zip(documents, scores):
        doc.metadata["rerank_score"] = float(score)
        
    sorted_docs = sorted(documents, key=lambda x: x.metadata["rerank_score"], reverse=True)
    return sorted_docs[:top_n]