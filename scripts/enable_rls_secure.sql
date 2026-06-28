-- ✅ RÉACTIVER RLS AVEC POLICIES SÉCURISÉES
-- À exécuter dans Supabase SQL Editor une fois le seed terminé

-- ============================================================
-- 1️⃣ RÉACTIVER RLS
-- ============================================================

ALTER TABLE etudiants ENABLE ROW LEVEL SECURITY;
ALTER TABLE professeurs ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE requetes_frequentes ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- 2️⃣ CRÉER LES POLICIES (PERMISSIF POUR LE POC)
-- ============================================================

-- Pour etudiants
CREATE POLICY "Lecture publique etudiants"
    ON etudiants FOR SELECT
    USING (true);

CREATE POLICY "Insertion libre etudiants"
    ON etudiants FOR INSERT
    WITH CHECK (true);

-- Pour professeurs
CREATE POLICY "Lecture publique professeurs"
    ON professeurs FOR SELECT
    USING (true);

CREATE POLICY "Insertion libre professeurs"
    ON professeurs FOR INSERT
    WITH CHECK (true);

-- Pour documents
CREATE POLICY "Lecture publique documents"
    ON documents FOR SELECT
    USING (true);

CREATE POLICY "Insertion libre documents"
    ON documents FOR INSERT
    WITH CHECK (true);

-- Pour document_chunks
CREATE POLICY "Lecture publique chunks"
    ON document_chunks FOR SELECT
    USING (true);

CREATE POLICY "Insertion libre chunks"
    ON document_chunks FOR INSERT
    WITH CHECK (true);

-- Pour requetes_frequentes (cache)
CREATE POLICY "Lecture cache"
    ON requetes_frequentes FOR SELECT
    USING (true);

CREATE POLICY "Insertion cache"
    ON requetes_frequentes FOR INSERT
    WITH CHECK (true);

-- ============================================================
-- VÉRIFICATION
-- ============================================================

SELECT schemaname, tablename, policyname, permissive, qual, with_check
FROM pg_policies
WHERE tablename IN ('etudiants', 'professeurs', 'documents', 'document_chunks', 'requetes_frequentes')
ORDER BY tablename;
