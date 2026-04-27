import streamlit as st
import tempfile
import os
from pathlib import Path
from src.orchestration.workflow import build_workflow
from main import extract_text

# Configuration esthétique de la page
st.set_page_config(
    page_title="Assistant Juridique", 
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS pour donner un aspect premium
st.markdown("""
<style>
    .report-box {
        background-color: #1E1E1E;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #333;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 50px;
        font-size: 18px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ Assistant Juridique Intelligent")
st.markdown("Analysez la conformité légale de vos contrats de travail instantanément grâce à une architecture Multi-Agents (LangGraph) et RAG (LlamaIndex).")

with st.sidebar:
    st.header("⚙️ Paramètres")
    st.info("Ce système utilise une base vectorielle locale ChromaDB contenant le Code du Travail marocain et le LLM OpenRouter pour le raisonnement.")
    st.markdown("---")
    st.markdown("**Agents Actifs :**")
    st.markdown("1. 🔍 **Parseur** (Extraction)")
    st.markdown("2. 📚 **Jurisprudence** (RAG)")
    st.markdown("3. ⚖️ **Risques** (Analyse LLM)")
    st.markdown("4. 📝 **Synthèse** (Rapport)")

# Zone d'upload (support du docx, pdf et txt)
uploaded_file = st.file_uploader(
    "Glissez un contrat de travail (PDF, DOCX ou TXT)", 
    type=["pdf", "txt", "docx"]
)

if uploaded_file is not None:
    # Sauvegarde temporaire du fichier pour pouvoir le lire avec LlamaIndex / PyPDF / docx
    suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    if st.button("🚀 Lancer l'analyse Multi-Agents", type="primary"):
        
        # Disposition en 2 colonnes : À gauche le log des agents, à droite le résultat final
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("🤖 Activité des Agents")
            status_container = st.container()
            
        with col2:
            st.subheader("📋 Rapport Final")
            report_placeholder = st.empty()
            report_placeholder.info("Le rapport s'affichera ici une fois l'analyse terminée...")

        try:
            workflow = build_workflow()
            
            with status_container:
                with st.status("Démarrage du processus...", expanded=True) as status:
                    
                    st.write("📖 **Système** : Extraction du texte...")
                    contract_text = extract_text(tmp_path)
                    st.write(f"✅ {len(contract_text)} caractères extraits avec succès.")
                    
                    initial_state = {
                        "contract_path": tmp_path,
                        "contract_text": contract_text,
                        "clauses": [],
                        "clause_analyses": [],
                        "final_report": "",
                    }

                    # Exécution en direct (streaming) de LangGraph
                    final_report = ""
                    for output in workflow.stream(initial_state):
                        if "parseur" in output:
                            clauses = output["parseur"].get("clauses", [])
                            st.write(f"🔍 **Agent Parseur** : {len(clauses)} clauses identifiées.")
                        
                        elif "jurisprudence" in output:
                            st.write("📚 **Agent Jurisprudence** : RAG effectué. Articles de loi récupérés pour chaque clause.")
                        
                        elif "risques" in output:
                            st.write("⚖️ **Agent Risques** : Analyse de conformité et calcul des risques terminés.")
                        
                        elif "synthese" in output:
                            st.write("📝 **Agent Synthèse** : Rédaction du rapport en cours...")
                            final_report = output["synthese"].get("final_report", "")

                    status.update(label="Analyse terminée avec succès !", state="complete", expanded=False)
            
            # Affichage du rapport final dans la colonne de droite
            with col2:
                if final_report:
                    st.markdown(f"<div class='report-box'>{final_report}</div>", unsafe_allow_html=True)
                else:
                    st.error("Erreur : Aucun rapport n'a été généré.")

        except Exception as e:
            st.error(f"Une erreur critique s'est produite lors de l'analyse : {e}")
            
        finally:
            # Nettoyage du fichier temporaire
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
