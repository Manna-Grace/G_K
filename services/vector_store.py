import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

def build_or_load_vector_store(data_dir: str, force_rebuild: bool = False):
    """Builds a fresh vector database or loads the existing one smoothly! 📚"""
    from core.config import DB_DIR
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    if os.path.exists(DB_DIR) and not force_rebuild and len(os.listdir(DB_DIR)) > 0:
        print("✨ Loading existing educational vector store database...")
        return Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    
    print("🚀 Building a brand new knowledge base from your PDFs...")
    all_docs = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=120)
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    for file in os.listdir(data_dir):
        if file.endswith(".pdf"):
            file_path = os.path.join(data_dir, file)
            subject_name = file.replace(".pdf", "") # Matches filename to subject filter
            
            try:
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                chunks = text_splitter.split_documents(docs)
                
                for chunk in chunks:
                    chunk.metadata["variant"] = subject_name  # Used for subject filtering
                    chunk.metadata["source"] = file
                    all_docs.append(chunk)
            except Exception as e:
                print(f"🙈 Oops! Could not load {file}: {e}")
                
    if all_docs:
        vector_store = Chroma.from_documents(
            documents=all_docs,
            embedding=embeddings,
            persist_directory=DB_DIR
        )
        print(f"🌸 Successfully indexed {len(all_docs)} sweet chunks of knowledge!")
        return vector_store
    else:
        print("⚠️ No PDFs found in your data/ directory yet! Drop some in soon!")
        return None

def search_rules(vector_store, query: str, variant_filter: str, k: int = 5):
    """Retrieves context filtered precisely by the active study subject."""
    if not vector_store:
        return []
    return vector_store.similarity_search(
        query, 
        k=k, 
        filter={"variant": variant_filter}
    )