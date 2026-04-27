# 🎓 Fiche de Préparation à la Soutenance : Assistant Juridique Multi-Agents

Ce document contient les réponses détaillées et vulgarisées aux questions probables de votre jury. **Lisez-le attentivement pour maîtriser chaque aspect de votre code.**

---

## 1. La compréhension du pipeline RAG

**Q : Comment fonctionne l’indexation ?**
L'indexation se passe dans le fichier `src/ingestion/pipeline.py`. 
1. Nous lisons le fichier PDF du Code du Travail avec LlamaIndex.
2. Nous découpons ce long texte en petits morceaux (les "chunks").
3. Chaque chunk est transformé en un vecteur mathématique (une suite de nombres) grâce à un modèle d'Intelligence Artificielle d'Embedding (ici, `all-MiniLM-L6-v2` de HuggingFace, qui tourne en local).
4. Ces vecteurs sont sauvegardés sur le disque dur dans une base de données vectorielle appelée **ChromaDB** (`data/chromadb`). 

**Q : Pourquoi ce chunking précis ?**
Nous avons utilisé le `SentenceSplitter` de LlamaIndex avec une taille de chunk de **512 tokens** et un chevauchement (*overlap*) de **50 tokens**.
- **Pourquoi 512 ?** Le Code du Travail est constitué d'articles courts mais denses. Une taille de 512 tokens est idéale pour englober 1 ou 2 articles de loi complets. Si on faisait plus grand, on diluerait l'information. Si on faisait plus petit, on couperait les articles au milieu.
- **Pourquoi un overlap de 50 ?** Pour s'assurer qu'un mot important ou une condition à la fin d'une page/d'un paragraphe ne soit pas séparée du reste de l'article dans le chunk suivant.

---

## 2. La logique des agents

**Q : Expliquez le raisonnement d'un agent, ses outils et son prompt.**
Prenons le cœur de notre système : **l'Agent Risques** (`src/agents/agent_risques.py`).
- **Son but** : Jouer le rôle d'un avocat spécialisé pour évaluer la légalité d'une clause.
- **Son entrée** : Il reçoit la clause du contrat ET les articles de loi pertinents que l'Agent Jurisprudence a récupéré dans ChromaDB.
- **Son raisonnement (Prompt)** : Dans son Prompt Système, on lui donne des instructions strictes : *"Voici une clause et voici la loi marocaine correspondante. Compare les deux. Dis-moi si c'est Conforme, à Risque Modéré, ou Illégal, et justifie-le"*. 
- **Comment il travaille** : Pour éviter qu'il n'invente des lois (hallucination), on le force (via le prompt) à baser sa réponse *uniquement* sur les articles de loi qu'on lui fournit en contexte.
- *(Note additionnelle)* : L'Agent Jurisprudence, lui, n'utilise même pas de LLM ! Son "outil" est simplement une requête de similarité mathématique vers la base ChromaDB pour récupérer les textes pertinents.

---

## 3. L'orchestration

**Q : Comment les agents communiquent-ils ? Comment l’état est-il géré ?**
- **L'Orchestrateur** : Nous utilisons **LangGraph** (`src/orchestration/workflow.py`). Contrairement à un simple script de bout en bout, LangGraph crée un **Graphe d'États** (StateGraph) où chaque agent est un "nœud".
- **L'État (State)** : La communication ne se fait pas par les agents qui se parlent "entre eux". Ils communiquent via un dictionnaire partagé appelé l'`AgentState` (défini dans `src/orchestration/state.py`).
- **Le Flux** :
  1. L'état initial contient juste le texte du contrat.
  2. Le **Parseur** lit ce texte, crée une liste de clauses, et met à jour l'état.
  3. **Jurisprudence** lit les clauses dans l'état, trouve les lois, ajoute ces lois dans l'état.
  4. **Risques** lit les clauses et les lois dans l'état, fait son analyse LLM, et stocke le résultat dans l'état.
  5. **Synthèse** lit l'analyse de l'état, rédige le Markdown final, et le met dans l'état.
  C'est donc une communication asynchrone via une mémoire centrale (le State).

---

## 4. Les choix techniques

**Q : Pourquoi ce modèle LLM (Google Gemini 1.5 Flash) ?**
- **Vitesse et Performance** : Gemini 1.5 Flash est un modèle extrêmement rapide, ce qui est crucial pour une interface UI en temps réel (Streamlit). De plus, son intégration native via `langchain-google-genai` est très stable.
- **Capacité de contexte** : Les contrats juridiques peuvent être longs. Gemini possède l'une des plus grandes fenêtres de contexte du marché.

**Q : Pourquoi le Vector Store ChromaDB ?**
- **Local et Open-Source** : Contrairement à Pinecone qui nécessite de se connecter à un cloud payant, ChromaDB s'exécute localement sur la machine (stocké dans un simple dossier `data/chromadb`). C'est parfait pour la confidentialité des données juridiques et pour un projet universitaire (0 coût de serveur).

**Q : Pourquoi cette stratégie Multi-Agents plutôt qu'un seul gros prompt ?**
- **Réduction des Hallucinations** : Si on donne tout un contrat et tout un Code du Travail à un LLM en lui disant *"Trouve les erreurs"*, il va se perdre, oublier des clauses ou inventer des lois.
- **Séparation des responsabilités (Divide and Conquer)** : En divisant le problème (1. Isoler les clauses, 2. Trouver la loi spécifique à cette clause, 3. Analyser uniquement cette clause avec cette loi), on force l'IA à se concentrer sur une petite tâche très précise à la fois. Le taux de précision explose et les résultats deviennent déterministes.
