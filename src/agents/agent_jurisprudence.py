"""
Agent Jurisprudence — Recherche les articles de loi pertinents via RAG.

Rôle : Pour chaque clause extraite du contrat, interroger la base vectorielle
       ChromaDB (Code du Travail marocain) via LlamaIndex et retourner
       les articles de loi les plus pertinents.
"""
from src.utils.helpers import get_retriever


def run_jurisprudence(state: dict) -> dict:
    """
    Nœud LangGraph : Effectue le RAG sur le Code du Travail pour chaque clause.
    
    Lit   : state["clauses"]
    Écrit : state["clause_analyses"] (partiellement — seulement clause + articles)
    """
    print("\n📚 [Agent Jurisprudence] Recherche des articles de loi pertinents...")
    
    clauses = state["clauses"]
    retriever = get_retriever(top_k=5)

    partial_analyses = []

    for i, clause in enumerate(clauses):
        title = clause["title"]
        text = clause["text"]

        # Construction de la requête RAG contextuelle
        query = (
            f"Articles régissant la clause : {title}\n"
            f"Contenu : {text}"
        )

        print(f"  🔎 [{i+1}/{len(clauses)}] RAG pour la clause : « {title} »")

        # Interrogation de la base vectorielle via le retriever
        nodes = retriever.retrieve(query)

        # Extraction des passages sources retrouvés
        source_texts = []
        for node in nodes:
            source_texts.append(node.get_content())

        relevant_articles = "\n---\n".join(source_texts) if source_texts else "Aucun article trouvé."

        partial_analyses.append({
            "clause_title": title,
            "clause_text": text,
            "relevant_articles": relevant_articles,
            "risk_level": "",          # Sera rempli par l'Agent Risques
            "risk_justification": "",  # Sera rempli par l'Agent Risques
            "recommendation": "",     # Sera rempli par l'Agent Risques
        })

    print(f"✅ [Agent Jurisprudence] Articles trouvés pour {len(partial_analyses)} clauses.")
    return {"clause_analyses": partial_analyses}
