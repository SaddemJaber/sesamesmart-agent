# tests/test_sql_handler.py
# Nécessite : hotspot téléphone + .env correct + Supabase avec données seedées

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.sql_handler import handle_sql

TEST_EMAIL = "ahmed.bennani@etu.sesame.ma"   # ETU001 — doit exister dans Supabase

print("=== Tests sql_handler.py ===\n")

passed = 0
failed = 0

def check(label, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  ✅  {label}")
        passed += 1
    else:
        print(f"  ❌  {label} {detail}")
        failed += 1

# ── Test 1 : Moyenne ──────────────────────────────────────────────────────────
r = handle_sql('moyenne', {}, TEST_EMAIL)
check("Intent 'moyenne' → pas d'erreur",       r['error'] is None,            f"| error={r['error']}")
check("Intent 'moyenne' → clé moyenne_generale", 'moyenne_generale' in (r['data'] or {}))
if r['data']:
    m = r['data']['moyenne_generale']
    check("Moyenne entre 0 et 20",              0 <= float(m) <= 20,           f"| valeur={m}")

# ── Test 2 : Statut financier ─────────────────────────────────────────────────
r = handle_sql('statut_financier', {}, TEST_EMAIL)
check("Intent 'statut_financier' → pas d'erreur", r['error'] is None,         f"| error={r['error']}")
check("Statut ∈ {A_JOUR, BLOQUE}",
      (r['data'] or {}).get('statut_financier') in ('A_JOUR', 'BLOQUE'),       f"| data={r['data']}")

# ── Test 3 : Professeur matière (matière qui DOIT exister dans tes données) ───
# Remplace "Mathématiques" par une matière présente dans professeurs.json si besoin
r = handle_sql('professeur_matiere', {'matiere': 'Algorithmique'}, TEST_EMAIL)
check("Résultat contient 'professeurs'",           'professeurs' in (r['data'] or {}))
if r['data']:
    check("Au moins 1 professeur retourné",        len(r['data']['professeurs']) >= 1, f"| data={r['data']}")
# ── Test 4 : Sécurité — email inexistant → not_found, pas de crash ────────────
r = handle_sql('moyenne', {}, 'inconnu@etu.sesame.ma')
check("Email inexistant → error='not_found' (pas de crash)",
      r['error'] == 'not_found',                                               f"| error={r['error']}")

# ── Test 5 : Intent inconnu → error='intent_inconnu' ─────────────────────────
r = handle_sql('inconnu', {}, TEST_EMAIL)
check("Intent inconnu → error='intent_inconnu'",
      r['error'] == 'intent_inconnu',                                          f"| error={r['error']}")

print(f"\n{'─'*50}")
print(f"Résultat : {passed}/{passed+failed} tests passés")
if failed == 0:
    print("✅ sql_handler.py VALIDÉ — tu peux passer à rag_handler.py")
else:
    print("❌ Corriger avant de continuer")