# SesameSmart — Chatbot académique hybride (SQL + RAG)

POC d'un assistant étudiant pour Sesame.
- Backend : Flask + Supabase (pgvector)
- IA : Google Gemini (gemini-embedding-001, models/gemini-2.5-flash)
- Architecture : routeur déterministe SQL / RAG + abstention stricte

---

## Statut du projet

```
Tasks complètes : 1 ✅ 2 ✅ 3 ✅ 4 ✅ 5 ✅
En cours        : Task 6 — API Flask (app/main.py)
```

---

## Structure du projet

```
sesamesmart-agent/
├── app/
│   ├── __init__.py
│   ├── router.py           # Routeur déterministe (SQL vs RAG)
│   ├── sql_handler.py      # 3 requêtes SQL paramétrées
│   ├── rag_handler.py      # Pipeline RAG embed→retrieve→generate
│   └── response_builder.py # Format JSON unifié + abstention
├── data/
│   ├── corpus/             # 5 documents .txt nettoyés (DOC001–DOC005)
│   ├── etudiants.json
│   ├── professeurs.json
│   └── documents_metadata.json
├── scripts/
│   ├── create_schema.sql
│   ├── seed_supabase.py
│   ├── ingest_corpus.py
│   └── spike_rag.py
├── tests/
│   ├── test_router.py
│   ├── test_sql_handler.py
│   ├── test_rag_handler.py
│   └── test_response_builder.py
├── .env.example
├── requirements.txt
├── PROJECT_LOG.md
└── TROUBLESHOOTING.md
```

---

## Variables d'environnement

Copier `.env.example` → `.env` et remplir :

```env
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_KEY=<anon_key>
GEMINI_API_KEY=...   # Clé AI Studio (format AQ.Ab8R...)
                     # ⚠️ Utiliser hotspot téléphone — WiFi école bloque Gemini
```

---

## Installation

```bash
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## Commandes de test

```bash
# Tous les tests Task 5 (zéro réseau sauf test_rag et test_main)
.\venv\Scripts\python.exe tests/test_router.py
.\venv\Scripts\python.exe tests/test_sql_handler.py
.\venv\Scripts\python.exe tests/test_rag_handler.py   # hotspot requis
.\venv\Scripts\python.exe tests/test_response_builder.py
```

---

## Ingestion RAG

```bash
# Hotspot téléphone obligatoire
.\venv\Scripts\python.exe scripts/ingest_corpus.py
```

9 chunks dans Supabase (DOC001:2, DOC002:3, DOC003:2, DOC004:1, DOC005:1)
