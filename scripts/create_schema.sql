-- ✅ SCRIPT SQL COMPLET POUR SUPABASE
-- Copie tout ce contenu dans l'éditeur SQL de Supabase et exécute-le

-- ============================================================
-- 1️⃣ CREATE TABLES
-- ============================================================

-- Table étudiants (données structurées — PAS d'embedding ici)
CREATE TABLE IF NOT EXISTS etudiants (
    id          TEXT PRIMARY KEY,
    nom         TEXT NOT NULL,
    prenom      TEXT NOT NULL,
    filiere     TEXT NOT NULL,
    annee       INTEGER NOT NULL,
    email       TEXT UNIQUE NOT NULL,
    moyenne_generale  NUMERIC(4,2),
    statut_financier  TEXT CHECK (statut_financier IN ('A_JOUR', 'BLOQUE'))
);

-- Table professeurs (données structurées — PAS d'embedding ici)
CREATE TABLE IF NOT EXISTS professeurs (
    id                  TEXT PRIMARY KEY,
    nom_complet         TEXT NOT NULL,
    departement         TEXT NOT NULL,
    matieres_enseignees TEXT[],
    disponibilite       TEXT,
    bio_prof            TEXT,
    email               TEXT UNIQUE NOT NULL
);

-- Table documents (métadonnées des fichiers sources)
CREATE TABLE IF NOT EXISTS documents (
    id                  TEXT PRIMARY KEY,
    titre               TEXT NOT NULL,
    type                TEXT NOT NULL,
    source              TEXT,
    filiere             TEXT,
    access_level        TEXT DEFAULT 'etudiant',
    rag_readiness       TEXT,
    rag_suitable        BOOLEAN DEFAULT TRUE,
    preprocessing_needed BOOLEAN DEFAULT FALSE,
    preprocessing_notes  TEXT,
    test_case           JSONB
);

-- Table document_chunks (vecteurs RAG — embedding ici UNIQUEMENT)
-- ⚠️ ATTENTION : pgvector doit être activée dans Supabase Extensions d'abord !
-- Si vector ne fonctionne pas, exécute d'abord : CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS document_chunks (
    id          BIGSERIAL PRIMARY KEY,
    document_id TEXT REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content     TEXT NOT NULL,
    token_count INTEGER,
    embedding   vector(768)
);

-- Index pour la recherche vectorielle
CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx
    ON document_chunks
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 10);

-- Table cache (schéma uniquement — logique implémentée en extension)
CREATE TABLE IF NOT EXISTS requetes_frequentes (
    id          BIGSERIAL PRIMARY KEY,
    question_hash TEXT UNIQUE NOT NULL,
    question    TEXT NOT NULL,
    reponse     JSONB NOT NULL,
    hit_count   INTEGER DEFAULT 1,
    created_at  TIMESTAMPTZ DEFAULT now(),
    updated_at  TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- 2️⃣ ENABLE ROW LEVEL SECURITY (RLS)
-- ============================================================

ALTER TABLE etudiants ENABLE ROW LEVEL SECURITY;
ALTER TABLE professeurs ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Policy de base : lecture publique sur documents et chunks (pas de données perso)
CREATE POLICY "Lecture publique documents"
    ON documents FOR SELECT
    USING (true);

CREATE POLICY "Lecture publique chunks"
    ON document_chunks FOR SELECT
    USING (true);

-- Policy étudiants : chaque étudiant ne voit que son propre profil
-- (simulé ici par email — en prod ce serait auth.uid())
CREATE POLICY "Etudiant voit son propre profil"
    ON etudiants FOR SELECT
    USING (true);  -- relaxé pour le POC, à restreindre en production

-- ============================================================
-- DONE ✅
-- ============================================================
-- Après exécution réussie :
-- 1. Retourne dans VS Code
-- 2. Lance : .\venv\Scripts\python.exe scripts/seed_supabase.py
-- 3. Les données seront chargées dans Supabase
