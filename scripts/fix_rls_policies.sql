-- ✅ CORRECTIONS RLS - À EXÉCUTER DANS SUPABASE SQL EDITOR
-- Le seed est bloqué par les policies RLS insuffisantes
-- Exécute ce script pour ajouter les permissions INSERT

-- Ajouter les policies INSERT pour permettre le seeding
CREATE POLICY "Insertion libre dans etudiants"
    ON etudiants FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Insertion libre dans professeurs"
    ON professeurs FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Insertion libre dans documents"
    ON documents FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Insertion libre dans document_chunks"
    ON document_chunks FOR INSERT
    WITH CHECK (true);

-- Optionnel : UPDATE et DELETE (pour l'admin)
CREATE POLICY "Update libre dans etudiants"
    ON etudiants FOR UPDATE
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Delete libre dans etudiants"
    ON etudiants FOR DELETE
    USING (true);

-- Vérification : affiche les policies
SELECT * FROM pg_policies WHERE tablename IN ('etudiants', 'professeurs', 'documents', 'document_chunks');
