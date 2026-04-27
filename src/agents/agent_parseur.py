"""
Agent Parseur — Extrait les clauses du contrat.

Rôle : Lire le texte brut d'un contrat de travail et le segmenter
       en clauses individuelles structurées (titre + contenu).
"""
import json
from src.utils.helpers import get_llm


SYSTEM_PROMPT = """Tu es un assistant juridique spécialisé dans l'analyse de contrats de travail marocains.

Ta mission est d'extraire TOUTES les clauses distinctes d'un contrat de travail.

Pour chaque clause, tu dois identifier :
1. Le **titre** de la clause (ex: "Période d'essai", "Rémunération", "Non-concurrence", etc.)
2. Le **texte complet** de la clause, mot pour mot tel qu'il apparaît dans le contrat.

IMPORTANT :
- Extrais TOUTES les clauses, même celles qui semblent anodines.
- Ne modifie PAS le texte original des clauses.
- Si une clause n'a pas de titre explicite, donne-lui un titre descriptif.

Tu DOIS répondre UNIQUEMENT avec un JSON valide, sous cette forme exacte :
[
    {"title": "Titre de la clause", "text": "Texte complet de la clause..."},
    {"title": "Titre de la clause 2", "text": "Texte complet..."}
]

Ne mets RIEN d'autre que le JSON dans ta réponse. Pas de commentaires, pas de markdown."""


def run_parseur(state: dict) -> dict:
    """
    Nœud LangGraph : Extrait les clauses du contrat.
    
    Lit   : state["contract_text"]
    Écrit : state["clauses"]
    """
    print("\n🔍 [Agent Parseur] Extraction des clauses du contrat...")
    
    contract_text = state["contract_text"]
    llm = get_llm()

    # Envoi au LLM pour extraction structurée
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Voici le contrat de travail à analyser :\n\n{contract_text}"}
    ]

    response = llm.invoke(messages)
    raw_response = response.content.strip()

    # Nettoyage robuste avec regex pour trouver la structure de liste JSON
    import re
    match = re.search(r'\[.*\]', raw_response, re.DOTALL)
    if match:
        raw_response = match.group(0)

    try:
        clauses = json.loads(raw_response)
        print(f"✅ [Agent Parseur] {len(clauses)} clauses extraites avec succès.")
    except json.JSONDecodeError:
        print("⚠️ [Agent Parseur] Erreur de parsing JSON. Tentative de récupération...")
        # Fallback : on crée une seule clause avec tout le texte
        clauses = [{"title": "Contrat complet (parsing échoué)", "text": contract_text}]

    return {"clauses": clauses}
