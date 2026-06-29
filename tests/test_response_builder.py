# tests/test_response_builder.py
# Tests unitaires purs — pas de réseau, pas de Supabase.

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.response_builder import (
    build_rag_response, build_sql_response,
    ABSTENTION_STRICTE, REFUS_SECURITE, REPONSE_BLOQUE, SOURCE_SQL
)

print("=== Tests response_builder.py ===\n")

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


# ── RAG : abstention stricte (score < SEUIL_BAS) ─────────────────────────────
print("── RAG : abstention stricte ──")
r = build_rag_response({"should_generate": False, "top_score": 0.40, "answer": "", "sources": []})
check("reponse = phrase verbatim",   r["reponse"] == ABSTENTION_STRICTE, f"| {r['reponse']!r}")
check("confidence = 'none'",         r["confidence"] == "none")
check("sources = []",                r["sources"] == [])
check("suggestions = []",            r["suggestions"] == [])

# ── RAG : réponse partielle (0.55 ≤ score < 0.65) ────────────────────────────
print("\n── RAG : réponse partielle ──")
r = build_rag_response({
    "should_generate": True, "top_score": 0.58,
    "answer": "Texte partiel.", "sources": ["Charte de l'étudiant"]
})
check("confidence = 'partial'",      r["confidence"] == "partial",       f"| {r['confidence']}")
check("sources non vides",           len(r["sources"]) >= 1)
check("suggestions = []",            r["suggestions"] == [])

# ── RAG : réponse normale (score ≥ 0.65) ─────────────────────────────────────
print("\n── RAG : réponse normale ──")
r = build_rag_response({
    "should_generate": True, "top_score": 0.78,
    "answer": "Pour contester une absence, connectez-vous à KONOSYS.",
    "sources": ["Note de service absences KONOSYS"]
})
check("confidence = 'high'",         r["confidence"] == "high",          f"| {r['confidence']}")
check("answer transmis",             "KONOSYS" in r["reponse"])
check("sources présentes",           len(r["sources"]) >= 1)
check("suggestions générées",        len(r["suggestions"]) == 2,         f"| {r['suggestions']}")

# ── SQL : moyenne ─────────────────────────────────────────────────────────────
print("\n── SQL : moyenne ──")
r = build_sql_response({"intent": "moyenne", "data": {"moyenne_generale": 14.5}, "error": None})
check("confidence = 'high'",         r["confidence"] == "high")
check("moyenne dans reponse",        "14.5" in r["reponse"],             f"| {r['reponse']}")
check("source = label neutre",       r["sources"] == [SOURCE_SQL])

# ── SQL : statut BLOQUE → phrase actionnable ──────────────────────────────────
print("\n── SQL : statut BLOQUE ──")
r = build_sql_response({"intent": "statut_financier", "data": {"statut_financier": "BLOQUE"}, "error": None})
check("BLOQUE dans reponse",         "BLOQUÉ" in r["reponse"],           f"| {r['reponse']}")
check("phrase actionnable présente", REPONSE_BLOQUE in r["reponse"],     f"| {r['reponse']}")
check("confidence = 'high'",         r["confidence"] == "high")

# ── SQL : statut A_JOUR ───────────────────────────────────────────────────────
print("\n── SQL : statut A_JOUR ──")
r = build_sql_response({"intent": "statut_financier", "data": {"statut_financier": "A_JOUR"}, "error": None})
check("à jour dans reponse",         "jour" in r["reponse"].lower(),     f"| {r['reponse']}")
check("confidence = 'high'",         r["confidence"] == "high")

# ── SQL : professeur trouvé ───────────────────────────────────────────────────
print("\n── SQL : professeur ──")
r = build_sql_response({
    "intent": "professeur_matiere",
    "data": {"professeurs": [{"nom_complet": "Layla Bensouda", "departement": "ING"}]},
    "error": None
})
check("nom prof dans reponse",       "Layla Bensouda" in r["reponse"],   f"| {r['reponse']}")
check("confidence = 'high'",         r["confidence"] == "high")

# ── SQL : sécurité — not_found → refus ───────────────────────────────────────
print("\n── SQL : refus sécurité ──")
r = build_sql_response({"intent": "moyenne", "data": None, "error": "not_found"})
check("reponse = refus sécurité",    r["reponse"] == REFUS_SECURITE,     f"| {r['reponse']!r}")
check("confidence = 'none'",         r["confidence"] == "none")
check("sources = []",                r["sources"] == [])


print(f"\n{'─' * 50}")
print(f"Résultat : {passed}/{passed + failed} tests passés")
if failed == 0:
    print("✅ response_builder.py VALIDÉ — Task 5 complète, passe à app/main.py (Task 6)")
else:
    print("❌ Corriger avant de continuer")