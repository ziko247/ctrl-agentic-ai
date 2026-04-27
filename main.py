"""
main.py — Point d'entrée de l'Assistant Juridique Intelligent.

Usage :
    python main.py                              → Analyse le contrat par défaut dans data/raw/
    python main.py chemin/vers/contrat.pdf       → Analyse un contrat spécifique
"""
import sys
import io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from pypdf import PdfReader
from src.orchestration.workflow import build_workflow


def extract_text(file_path: str) -> str:
    """Extrait le texte brut d'un fichier (PDF, TXT ou DOCX)."""
    path = Path(file_path)
    if path.suffix.lower() == '.pdf':
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
        return text
    elif path.suffix.lower() == '.docx':
        from docx import Document
        doc = Document(path)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return path.read_text(encoding="utf-8")


def main():
    print("=" * 70)
    print("  ⚖️  ASSISTANT JURIDIQUE INTELLIGENT — Analyse de Contrat")
    print("=" * 70)

    # ─── Déterminer le contrat à analyser ───
    if len(sys.argv) > 1:
        contract_path = sys.argv[1]
    else:
        # Par défaut : chercher un contrat de test dans data/raw/
        raw_dir = Path("data/raw")
        pdfs = list(raw_dir.glob("*.pdf"))
        if not pdfs:
            print("❌ Aucun fichier PDF trouvé dans data/raw/.")
            print("   Usage : python main.py chemin/vers/contrat.pdf")
            sys.exit(1)
        contract_path = str(pdfs[0])

    print(f"\n📄 Contrat à analyser : {contract_path}")

    # ─── Extraction du texte ───
    print("📖 Extraction du texte du contrat...")
    contract_text = extract_text(contract_path)
    print(f"   → {len(contract_text)} caractères extraits.\n")

    # ─── Construction et exécution du workflow ───
    app = build_workflow()

    # État initial injecté dans le graphe
    initial_state = {
        "contract_path": contract_path,
        "contract_text": contract_text,
        "clauses": [],
        "clause_analyses": [],
        "final_report": "",
    }

    print("\n🚀 Lancement de l'analyse multi-agents...\n")
    print("─" * 70)

    # Exécution du graphe LangGraph
    final_state = app.invoke(initial_state)

    # ─── Sauvegarde du rapport ───
    report = final_state["final_report"]
    output_path = Path("rapport_juridique.md")
    output_path.write_text(report, encoding="utf-8")

    print("\n" + "─" * 70)
    print(f"📊 Rapport sauvegardé dans : {output_path.resolve()}")
    print("=" * 70)

    # Affichage du rapport dans le terminal
    print("\n" + report)


if __name__ == "__main__":
    main()
