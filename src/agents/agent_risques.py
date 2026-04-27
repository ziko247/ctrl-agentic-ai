"""
Agent Risques — Évalue la conformité de chaque clause avec le Code du Travail.

Rôle : Pour chaque clause, croiser le texte de la clause avec les articles de loi
       retrouvés par l'Agent Jurisprudence et déterminer le niveau de risque.
"""
import json
from src.utils.helpers import get_llm


SYSTEM_PROMPT = """Tu es un expert en droit du travail marocain. 

On te donne :
1. Une **clause** extraite d'un contrat de travail.
2. Les **articles du Code du Travail marocain** pertinents retrouvés par recherche sémantique.

Ta mission est d'analyser si la clause est conforme au Code du Travail marocain.

Pour chaque clause, tu dois fournir :
- **risk_level** : Un des trois niveaux suivants UNIQUEMENT :
  - "Conforme" : La clause respecte la loi.
  - "Risque Modéré" : La clause est ambiguë ou pourrait poser problème.
  - "Illégal" : La clause viole clairement le Code du Travail.
- **risk_justification** : Explication détaillée de ton analyse, en citant les articles de loi concernés.
- **recommendation** : Recommandation concrète pour corriger ou améliorer la clause.

Tu DOIS répondre UNIQUEMENT avec un JSON valide sous cette forme :
{
    "risk_level": "Conforme | Risque Modéré | Illégal",
    "risk_justification": "Explication détaillée...",
    "recommendation": "Recommandation..."
}

Ne mets RIEN d'autre que le JSON dans ta réponse."""


def run_risques(state: dict) -> dict:
    """
    Nœud LangGraph : Évalue le risque de chaque clause.
    
    Lit   : state["clause_analyses"] (avec les articles de loi)
    Écrit : state["clause_analyses"] (enrichi avec risk_level, justification, recommendation)
    """
    print("\n⚖️ [Agent Risques] Évaluation de la conformité des clauses...")
    
    clause_analyses = state["clause_analyses"]
    llm = get_llm()

    enriched_analyses = []

    for i, analysis in enumerate(clause_analyses):
        title = analysis["clause_title"]
        clause_text = analysis["clause_text"]
        articles = analysis["relevant_articles"]

        print(f"  ⚖️ [{i+1}/{len(clause_analyses)}] Analyse de risque : « {title} »")

        user_message = (
            f"## Clause du contrat : {title}\n"
            f"{clause_text}\n\n"
            f"## Articles du Code du Travail marocain pertinents :\n"
            f"{articles}"
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]

        response = llm.invoke(messages)
        raw_response = response.content.strip()

        # Nettoyage des backticks markdown
        if raw_response.startswith("```"):
            raw_response = raw_response.strip("`").strip()
            if raw_response.startswith("json"):
                raw_response = raw_response[4:].strip()

        try:
            risk_data = json.loads(raw_response)
            analysis["risk_level"] = risk_data.get("risk_level", "Inconnu")
            analysis["risk_justification"] = risk_data.get("risk_justification", "")
            analysis["recommendation"] = risk_data.get("recommendation", "")
        except json.JSONDecodeError:
            print(f"  ⚠️ Erreur de parsing pour « {title} ». Réponse brute conservée.")
            analysis["risk_level"] = "Erreur d'analyse"
            analysis["risk_justification"] = raw_response
            analysis["recommendation"] = "Veuillez analyser manuellement cette clause."

        enriched_analyses.append(analysis)

    # Comptage des risques
    risks = {"Conforme": 0, "Risque Modéré": 0, "Illégal": 0}
    for a in enriched_analyses:
        level = a["risk_level"]
        if level in risks:
            risks[level] += 1

    print(f"✅ [Agent Risques] Analyse terminée : "
          f"✅ {risks['Conforme']} conformes | "
          f"⚠️ {risks['Risque Modéré']} risques modérés | "
          f"🚫 {risks['Illégal']} illégales")

    return {"clause_analyses": enriched_analyses}
