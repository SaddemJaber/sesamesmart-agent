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
```

## Statut du projet

| Task | Description | Status |
|---|---|---|
| 1 | Environnement & repo | ✅ |
| 2 | Mock data (20 étudiants, 8 profs, 5 docs) | ✅ |
| 3 | Supabase + pgvector + seed | ✅ |
| 4 | Pré-traitement & ingestion RAG (9 chunks) | ✅ |
| 5 | Cerveau chatbot (routeur + SQL + RAG) | ✅ |
| 6 | API Flask — 24/24 tests | ✅ |
| 7 | Scénarios jury — 18/18 tests | ✅ |
| 8 | Démo & rapport | ⏳ |

## ⚠️ Réseau

Les appels vers `generativelanguage.googleapis.com` nécessitent un **hotspot mobile** — le WiFi école bloque ces connexions.
