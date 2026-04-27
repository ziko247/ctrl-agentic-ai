import os
from pathlib import Path

# Important : On charge les variables d'environnement (pour OPENROUTER_API_KEY plus tard)
from dotenv import load_dotenv
load_dotenv()

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

# Définition des chemins relatifs à la racine du projet
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw"
CHROMA_DB_PATH = PROJECT_ROOT / "data" / "chromadb"

def build_rag_pipeline():
    """
    Ingestion du Code du Travail (PDF ou TXT) avec LlamaIndex,
    découpage optimisé pour le texte juridique et stockage dans ChromaDB.
    """
    print(f"📁 Chargement des documents depuis : {RAW_DATA_PATH}")
    
    # 1. Chargement du document
    docs = SimpleDirectoryReader(input_dir=str(RAW_DATA_PATH)).load_data()
    print(f"✅ {len(docs)} pages/documents chargées.")

    # 2. Configuration locale pour les Embeddings (Gratuit et Rapide)
    # On utilise le modèle all-MiniLM-L6-v2 de HuggingFace via LlamaIndex
    # Cela évite de consommer des tokens d'API pour la longue vectorisation de la loi
    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    Settings.embed_model = embed_model
    # Pour la phase d'ingestion pure, pas besoin de configurer le LLM Anthropic

    # 3. Stratégie de Chunking optimisée pour le Juridique
    # On privilégie la séparation en fonction des mots clés légaux "Article" ou "\n\n"
    # LlamaIndex SentenceSplitter permet d'inclure des séparateurs de paragraphes customisés
    text_splitter = SentenceSplitter(
        chunk_size=1024,
        chunk_overlap=200,
        paragraph_separator="\n\n" # Idéalement, séparer par article
    )
    Settings.node_parser = text_splitter

    # 4. Initialisation de ChromaDB
    print(f"🗄️ Initialisation de la base vectorielle ChromaDB dans : {CHROMA_DB_PATH}")
    db = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
    chroma_collection = db.get_or_create_collection("code_du_travail")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    # Context de stockage pointant vers notre ChromaDB local
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # 5. Création de l'Index Vectoriel
    print("⏳ Création des embeddings (Chunking & Indexation)... Veuillez patienter.")
    index = VectorStoreIndex.from_documents(
        docs, 
        storage_context=storage_context,
        show_progress=True
    )
    
    print("🎉 Pipeline d'ingestion terminée avec succès ! La base de données est prête.")
    return index

if __name__ == "__main__":
    build_rag_pipeline()
