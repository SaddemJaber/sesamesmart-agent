-- ✅ NETTOYER ET RÉACTIVER RLS AVEC POLICIES
-- À exécuter dans Supabase SQL Editor pour finaliser RLS

-- ============================================================
-- 1️⃣ RÉACTIVER RLS (si pas déjà activée)
-- ============================================================

ALTER TABLE etudiants ENABLE ROW LEVEL SECURITY;
ALTER TABLE professeurs ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE requetes_frequentes ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- 2️⃣ NETTOYER LES POLICIES EXISTANTES (si en double)
-- ============================================================

DROP POLICY IF EXISTS "Lecture publique documents" ON documents;
DROP POLICY IF EXISTS "Insertion libre documents" ON documents;
DROP POLICY IF EXISTS "Lecture publique professeurs" ON professeurs;
DROP POLICY IF EXISTS "Insertion libre professeurs" ON professeurs;
DROP POLICY IF EXISTS "Lecture publique etudiants" ON etudiants;
DROP POLICY IF EXISTS "Insertion libre etudiants" ON etudiants;
DROP POLICY IF EXISTS "Lecture publique chunks" ON document_chunks;
DROP POLICY IF EXISTS "Insertion libre chunks" ON document_chunks;
DROP POLICY IF EXISTS "Lecture cache" ON requetes_frequentes;
DROP POLICY IF EXISTS "Insertion cache" ON requetes_frequentes;

-- ============================================================
-- 3️⃣ CRÉER LES POLICIES (PROPRES)
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
-- ✅ VÉRIFICATION FINALE
-- ============================================================

SELECT schemaname, tablename, policyname, permissive, qual, with_check
FROM pg_policies
WHERE tablename IN ('etudiants', 'professeurs', 'documents', 'document_chunks', 'requetes_frequentes')
ORDER BY tablename, policyname;

-- ✅ Résultat attendu : 10 policies (2 par table × 5 tables)
