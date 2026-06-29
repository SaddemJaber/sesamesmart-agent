# tests/test_router.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.router import route

tests = [
    # (question, route attendue, intent attendu, matiere attendue ou None)
    ("Quelle est ma moyenne ?",              "sql", "moyenne",              None),
    ("Montre-moi mes notes s'il te plaît",   "sql", "moyenne",              None),
    ("Quel est mon statut financier ?",      "sql", "statut_financier",     None),
    ("Est-ce que je suis bloqué ?",          "sql", "statut_financier",     None),
    ("Qui enseigne les Mathématiques ?",     "sql", "professeur_matiere",   "Mathématiques"),
    ("Qui enseigne l'Anglais ?",             "sql", "professeur_matiere",   "Anglais"),
    # Pièges → doivent aller en RAG
    ("Comment contester une absence sur KONOSYS ?",  "rag", None, None),
    ("Quelle est la procédure de réinscription ?",   "rag", None, None),
    ("Quelles sont les règles pendant un examen ?",  "rag", None, None),
    ("Combien coûte la formation ?",                 "rag", None, None),
]

passed = 0
failed = 0

for question, expected_route, expected_intent, expected_matiere in tests:
    result = route(question)
    ok_route  = result['route']   == expected_route
    ok_intent = result['intent']  == expected_intent
    ok_mat    = (expected_matiere is None) or (result['params'].get('matiere') == expected_matiere)

    if ok_route and ok_intent and ok_mat:
        print(f"  ✅  {question}")
        passed += 1
    else:
        print(f"  ❌  {question}")
        print(f"      attendu  : route={expected_route}, intent={expected_intent}, matiere={expected_matiere}")
        print(f"      obtenu   : {result}")
        failed += 1

print(f"\n{'─'*50}")
print(f"Résultat : {passed}/{passed+failed} tests passés")
if failed == 0:
    print("✅ router.py VALIDÉ — tu peux passer à sql_handler.py")
else:
    print("❌ Corriger avant de continuer")