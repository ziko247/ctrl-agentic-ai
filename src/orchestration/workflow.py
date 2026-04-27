"""
Workflow d'Orchestration — LangGraph StateGraph.

Définit le graphe d'exécution séquentiel qui connecte les 4 agents :
  Parseur → Jurisprudence → Risques → Synthèse
"""
from langgraph.graph import StateGraph, START, END
from src.orchestration.state import AgentState
from src.agents.agent_parseur import run_parseur
from src.agents.agent_jurisprudence import run_jurisprudence
from src.agents.agent_risques import run_risques
from src.agents.agent_synthese import run_synthese


def build_workflow():
    """
    Construit et compile le graphe LangGraph.
    
    Flux :
        START → parseur → jurisprudence → risques → synthese → END
    
    Returns:
        Un CompiledGraph prêt à être invoqué avec un état initial.
    """
    # Création du graphe avec notre State typé
    workflow = StateGraph(AgentState)

    # ─── Ajout des nœuds (chaque agent est un nœud) ───
    workflow.add_node("parseur", run_parseur)
    workflow.add_node("jurisprudence", run_jurisprudence)
    workflow.add_node("risques", run_risques)
    workflow.add_node("synthese", run_synthese)

    # ─── Définition du flux séquentiel ───
    workflow.add_edge(START, "parseur")
    workflow.add_edge("parseur", "jurisprudence")
    workflow.add_edge("jurisprudence", "risques")
    workflow.add_edge("risques", "synthese")
    workflow.add_edge("synthese", END)

    # ─── Compilation ───
    app = workflow.compile()
    print("🔗 Workflow LangGraph compilé : Parseur → Jurisprudence → Risques → Synthèse")
    
    return app
