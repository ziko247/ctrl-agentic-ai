"""
Définition du State partagé entre les 4 agents via LangGraph.
Ce TypedDict est le "contrat de données" que chaque agent lit et enrichit.
"""
from typing import TypedDict, List, Optional


class ClauseAnalysis(TypedDict):
    """Analyse d'une clause individuelle."""
    clause_title: str           # Titre de la clause (ex: "Période d'essai")
    clause_text: str            # Texte brut de la clause extraite du contrat
    relevant_articles: str      # Articles du Code du Travail trouvés par le RAG
    risk_level: str             # "Conforme" | "Risque Modéré" | "Illégal"
    risk_justification: str     # Explication détaillée du risque
    recommendation: str         # Recommandation pour corriger la clause


class AgentState(TypedDict):
    """
    État partagé entre tous les agents du workflow LangGraph.
    Chaque agent lit les champs dont il a besoin et écrit dans les siens.
    """
    # ─── Entrée ───
    contract_path: str                          # Chemin vers le contrat PDF
    contract_text: str                          # Texte brut extrait du contrat

    # ─── Agent Parseur ───
    clauses: List[dict]                         # Liste des clauses extraites
                                                # Chaque dict: {"title": str, "text": str}

    # ─── Agents Jurisprudence + Risques ───
    clause_analyses: List[ClauseAnalysis]       # Analyse complète de chaque clause

    # ─── Agent Synthèse ───
    final_report: str                           # Rapport Markdown final
