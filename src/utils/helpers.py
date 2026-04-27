"""
Utilitaires partagés : configuration du LLM (OpenRouter) et du Query Engine (LlamaIndex).
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ─── Chemins ───────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CHROMA_DB_PATH = PROJECT_ROOT / "data" / "chromadb"


def get_llm():
    """
    Retourne une instance ChatOpenAI configurée pour OpenRouter.
    OpenRouter expose une API compatible OpenAI, donc on utilise ChatOpenAI
    en redirigeant le base_url.
    """
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY manquant dans le fichier .env")

    llm = ChatGoogleGenerativeAI(
        model=os.getenv("LLM_MODEL", "gemini-1.5-flash"),
        google_api_key=api_key,
        temperature=0.2,  # Basse température pour des réponses juridiques précises
    )
    return llm


def get_retriever(top_k: int = 5):
    """
    Charge l'index ChromaDB existant (créé par pipeline.py)
    et retourne un retriever LlamaIndex prêt à chercher dans le Code du Travail.
    
    Args:
        top_k: Nombre de chunks les plus pertinents à retourner.
    """
    from llama_index.core import VectorStoreIndex, Settings
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.vector_stores.chroma import ChromaVectorStore
    import chromadb

    # Même modèle d'embedding que lors de l'ingestion
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Connexion à la base ChromaDB existante
    db = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
    chroma_collection = db.get_or_create_collection("code_du_travail")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    # Reconstruction de l'index depuis le vector store
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    # Retourne un retriever (recherche vectorielle pure, pas de synthèse LLM)
    retriever = index.as_retriever(similarity_top_k=top_k)
    return retriever
