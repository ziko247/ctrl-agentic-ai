"""
Agent Synthèse — Rédige le rapport final en Markdown.

Rôle : Compiler toutes les analyses de clauses en un rapport structuré,
       lisible et actionnable pour un juriste ou un RH.
"""
from datetime import datetime
from src.utils.helpers import get_llm


SYSTEM_PROMPT = """Tu es un rédacteur juridique expert. 

On te fournit l'analyse complète de toutes les clauses d'un contrat de travail, 
avec pour chacune : le texte de la clause, les articles de loi pertinents, 
le niveau de risque et les recommandations.

Ta mission est de rédiger un **rapport d'analyse juridique complet en Markdown** 
qui sera remis à un cabinet juridique ou un département RH.

Le rapport doit contenir :
1. Un **résumé exécutif** (vue d'ensemble des risques identifiés)
2. Un **tableau récapitulatif** de toutes les clauses avec leur niveau de risque
3. L'**analyse détaillée** de chaque clause (texte, articles de loi, justification, recommandation)
4. Une **conclusion** avec les actions prioritaires

Utilise des emojis pour les niveaux de risque :
- ✅ Conforme
- ⚠️ Risque Modéré  
- 🚫 Illégal

Le rapport doit être professionnel, bien structuré et directement utilisable."""


def run_synthese(state: dict) -> dict:
    """
    Nœud LangGraph : Génère le rapport Markdown final.
    
    Lit   : state["clause_analyses"]
    Écrit : state["final_report"]
    """
    print("\n📝 [Agent Synthèse] Rédaction du rapport final...")
    
    clause_analyses = state["clause_analyses"]
    llm = get_llm()

    # Préparer les données pour le LLM
    analyses_text = ""
    for i, analysis in enumerate(clause_analyses):
        analyses_text += (
            f"\n### Clause {i+1} : {analysis['clause_title']}\n"
            f"**Texte de la clause :**\n{analysis['clause_text']}\n\n"
            f"**Articles de loi pertinents :**\n{analysis['relevant_articles']}\n\n"
            f"**Niveau de risque :** {analysis['risk_level']}\n"
            f"**Justification :** {analysis['risk_justification']}\n"
            f"**Recommandation :** {analysis['recommendation']}\n"
            f"{'─' * 60}\n"
        )

    user_message = (
        f"Date de l'analyse : {datetime.now().strftime('%d/%m/%Y à %H:%M')}\n\n"
        f"Voici l'analyse complète de toutes les clauses du contrat :\n"
        f"{analyses_text}\n\n"
        f"Rédige maintenant le rapport complet en Markdown."
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]

    response = llm.invoke(messages)
    final_report = response.content.strip()

    print("✅ [Agent Synthèse] Rapport Markdown généré avec succès.")
    return {"final_report": final_report}
