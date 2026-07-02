# SesameSmart — Chatbot académique hybride (SQL + RAG)

POC d'un assistant étudiant pour l'école Sesame.

## Stack technique

| Composant | Technologie |
|---|---|
| Backend | Flask (Python) |
| Base de données | Supabase + pgvector |
| Embeddings | Google Gemini `gemini-embedding-001` (REST, 768d) |
| Génération | Google Gemini `gemini-2.5-flash` (REST) |
| Architecture | Routeur unique : SQL ou RAG + abstention stricte |

## Architecture

```
Question étudiant
       ↓
Routeur déterministe
      /      \
    SQL       RAG
(données    (corpus
personnelles) documentaire)
      \      /
   Réponse JSON
{reponse, sources, suggestions, confidence}
```

## Lancer le projet

```bash
# 1. Activer l'environnement
.\venv\Scripts\activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer les variables d'environnement
copy .env.example .env
# Remplir SUPABASE_URL, SUPABASE_KEY, GEMINI_API_KEY

# 4. Lancer le serveur
.\venv\Scripts\python.exe -m app.main
```

## Tests

```bash
# Tests d'intégration Flask (24/24)
.\venv\Scripts\python.exe tests/test_main.py

# Scénarios jury (18/18)
.\venv\Scripts\python.exe tests/test_demo_jury.py
```

## Interface chat (CLI)

```bash
# Terminal 1 — serveur Flask
.\venv\Scripts\python.exe -m app.main

# Terminal 2 — chat
.\venv\Scripts\python.exe chat.py
```

Fonctionnalités : validation email, vérification contre la base, affichage coloré selon confidence, suggestions cliquables (`1`/`2`), `/help`, `/history`.

## Variables d'environnement

Voir `.env.example` pour la liste complète :

```env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=sb_publishable_...
GEMINI_API_KEY=AQ...

# Rotation clés Gemini (optionnel — 1 clé suffit)
GEMINI_API_KEY_1=
GEMINI_API_KEY_2=
GEMINI_API_KEY_3=
GEMINI_API_KEY_4=
```

La rotation de clés Gemini est supportée via `GEMINI_API_KEY_1`, `_2`, `_3`, `_4`. Sur erreur 429, le système bascule automatiquement vers la clé suivante — élimine les interruptions de service en cas de rate limit.

## Intents SQL supportés

| Intent | Exemple de question | Réponse |
|---|---|---|
| `moyenne` | "Quelle est ma moyenne ?" | Retourne la moyenne générale de l'étudiant |
| `statut_financier` | "Quel est mon statut financier ?" | Retourne A_JOUR ou BLOQUE |
| `professeur_matiere` | "Qui enseigne Algorithmique ?" | Retourne le(s) professeur(s) de la matière |
| `filiere` | "Quelle est ma filière ?" | Retourne la filière de l'étudiant |
| `annee` | "En quelle année suis-je ?" | Retourne l'année d'études |
| `classement` | "Quel est mon classement ?" | Retourne le rang dans la filière |
| `note_matiere` | "Quelle est ma note en Maths ?" | Retourne la note de l'étudiant dans une matière |
| `meilleure_matiere` | "Quelle est ma meilleure matière ?" | Retourne la matière avec la note la plus haute |
| `moyenne_promo` | "Quelle est la moyenne de ma filière ?" | Retourne la moyenne agrégée de la promotion |
| `professeur_sans_matiere` | "Qui sont mes profs ?" | Réponse guidée — demande de préciser la matière |

## Schéma de données

Table `notes` : 180 lignes (30 étudiants × 6 matières). Colonnes : `id`, `etudiant_id`, `matiere`, `note`. `moyenne_generale` dans `etudiants` est dérivée de cette table via `AVG`.

## Ingestion / RAG

- **Corpus :** 8 documents `.txt` dans `data/corpus/`
- **Embeddings :** `gemini-embedding-001`, REST v1beta, `outputDimensionality=768`, `taskType=RETRIEVAL_DOCUMENT`
- **Chunking :** fenêtre glissante, max 550 tokens, overlap 100 tokens
- **Chunks actuels :** 13 (DOC001:1, DOC002:2, DOC003:1, DOC004:1, DOC005:1, DOC006:5, DOC007:1, DOC008:1)
- **Recherche :** RPC Supabase `match_chunks`, similarité cosine via pgvector
- **Seuils :** `SEUIL_BAS=0.58` (génération), `SEUIL_HAUT=0.65` (confidence high)

### Corpus RAG

| ID | Titre | Type | Scope | Description |
|---|---|---|---|---|
| DOC001 | Note absences KONOSYS | note | FTA | Gestion et validation des absences |
| DOC002 | Règlement Intérieur FTA | reglement | FTA | Règlement départemental |
| DOC003 | Charte de l'étudiant | charte | Transversal | Droits et devoirs étudiants |
| DOC004 | Email réinscription | email | Transversal | Processus de réinscription |
| DOC005 | Email attestation | email | Transversal | Validation attestation et diplôme |
| DOC006 | FAQ Scolarité | faq | Transversal | Questions fréquentes scolarité |
| DOC007 | Règlement des examens | reglement | Transversal | Admissibilité, rattrapage, fraude |
| DOC008 | Guide des stages | guide | Transversal | Conventions, évaluation, stages |

> ⚠️ Avant toute ré-ingestion, INSERT les nouveaux docs dans la table `documents` (foreign key `document_chunks` → `documents`). Puis DELETE manuel dans SQL Editor Supabase.

```bash
# Hotspot mobile obligatoire
.\venv\Scripts\python.exe scripts/ingest_corpus.py
```

## Statut du projet

| Task | Description | Status |
|---|---|---|
| 1 | Environnement & repo | ✅ |
| 2 | Mock data (30 étudiants, 8 profs, 8 docs) | ✅ |
| 3 | Supabase + pgvector + seed | ✅ |
| 4 | Pré-traitement & ingestion RAG (13 chunks, 8 docs) | ✅ |
| 5 | Cerveau chatbot (routeur + SQL + RAG) | ✅ |
| 6 | API Flask — 24/24 tests | ✅ |
| 7 | Scénarios jury — 18/18 tests | ✅ |
| 8 | Démo & rapport | ⏳ |

## ⚠️ Réseau

Les appels vers `generativelanguage.googleapis.com` nécessitent un **hotspot mobile** — le WiFi école bloque ces connexions.
