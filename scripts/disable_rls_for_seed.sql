-- ✅ DÉSACTIVER RLS TEMPORAIREMENT POUR LE SEED
-- Exécute ce script dans Supabase SQL Editor, puis reviens pour le seed

-- ⚠️ Désactive RLS temporairement
ALTER TABLE etudiants DISABLE ROW LEVEL SECURITY;
ALTER TABLE professeurs DISABLE ROW LEVEL SECURITY;
ALTER TABLE documents DISABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks DISABLE ROW LEVEL SECURITY;

-- ✅ Après avoir exécuté le seed dans VS Code, tu relanceras ce script
-- (décommente les 4 lignes suivantes une fois le seed terminé) :

-- ALTER TABLE etudiants ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE professeurs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
