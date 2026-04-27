# ⚖️ Assistant Juridique Intelligent (Multi-Agents & RAG)

Ce projet est un Assistant Juridique basé sur l'IA (LangChain, LangGraph, LlamaIndex, Gemini) permettant d'analyser la conformité de contrats de travail par rapport au Code du Travail marocain.

---

## 🚀 Guide d'installation (Comment lancer le projet sur une autre machine)

Si vous venez de récupérer ce projet depuis GitHub (ou une clé USB), suivez ces étapes pour le faire fonctionner sur votre ordinateur.

### Prérequis
- Avoir **Python 3.9 ou plus** installé sur votre machine (`python --version` pour vérifier).
- Avoir accès à internet pour télécharger les bibliothèques et utiliser l'API Gemini.

### Étape 1 : Cloner / Récupérer le projet
Ouvrez un terminal (Powershell ou Command Prompt sur Windows, Terminal sur Mac/Linux) et naviguez vers le dossier du projet :
```bash
cd chemin/vers/le/dossier/ctrl-agentic-ai
```

### Étape 2 : Créer un Environnement Virtuel
Il est indispensable de créer un environnement virtuel pour ne pas polluer votre installation Python globale.
```bash
python -m venv venv
```

### Étape 3 : Activer l'Environnement Virtuel
- **Sur Windows (Powershell) :**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
  *(Si vous avez une erreur de droits, exécutez d'abord `Set-ExecutionPolicy Unrestricted -Scope CurrentUser`)*
  
- **Sur Mac / Linux :**
  ```bash
  source venv/bin/activate
  ```

### Étape 4 : Installer les dépendances
Une fois le `(venv)` affiché dans votre terminal, installez toutes les bibliothèques requises :
```bash
pip install -r requirements.txt
```

### Étape 5 : Configurer les Variables d'Environnement (.env)
1. Créez un fichier nommé **`.env`** à la racine du projet.
2. Ouvrez-le avec un éditeur de texte et ajoutez-y votre clé API Gemini comme ceci :
```env
GEMINI_API_KEY=votre_cle_api_ici
LLM_MODEL=gemini-1.5-flash
```

### Étape 6 : (Optionnel) Indexer le Code du Travail
*Si le dossier `data/chromadb` n'a pas été copié sur la nouvelle machine, vous devez recréer la base de données vectorielle.*
Placez votre `Code du travail.pdf` dans `data/raw/` puis lancez :
```bash
python src/ingestion/pipeline.py
```
*(Cela va télécharger le modèle HuggingFace localement et créer l'index).*

### Étape 7 : Lancer l'Interface Graphique (UI)
Tout est prêt ! Vous pouvez maintenant lancer l'application web Streamlit :
```bash
streamlit run app.py
```
Votre navigateur s'ouvrira automatiquement sur **http://localhost:8501**. Glissez-y un contrat de test (`.pdf`, `.docx`, ou `.txt`) et laissez les agents travailler !
