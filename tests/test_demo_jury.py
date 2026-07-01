# tests/test_demo_jury.py
# Scénarios de démonstration jury — nécessite Flask lancé sur 127.0.0.1:5000.
# Entrée : serveur Flask actif (python app/main.py)
# Sortie : 5/5 scénarios validés avec réponses JSON

import sys
import os
import json
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

BASE_URL    = "http://127.0.0.1:5000/api/chat"
HEALTH_URL  = "http://127.0.0.1:5000/health"
TEST_EMAIL  = "ahmed.bennani@etu.sesame.ma"

print("=== Tests test_demo_jury.py ===\n")
print("⚠️  Assure-toi : serveur Flask lancé (python app/main.py)\n")

passed = 0
failed = 0

def check(label: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        print(f"  ✅  {label}")
        passed += 1
    else:
        print(f"  ❌  {label} {detail}")
        failed += 1

# ─── Vérification serveur ──────────────────────────────────────────────────────
try:
    requests.get(HEALTH_URL, timeout=2)
except requests.exceptions.ConnectionError:
    print("  ❌  Serveur Flask non disponible sur http://127.0.0.1:5000")
    print("      Lancer : python app/main.py puis relancer ce script.")
    sys.exit(1)

# ─── Scénario 1 : RAG documentaire pur ────────────────────────────────────────
print("── Scénario 1 : RAG documentaire pur ──")
try:
    r = requests.post(BASE_URL, json={"question": "Comment fonctionne la réinscription ?", "user_email": TEST_EMAIL})
    check("HTTP 200",                       r.status_code == 200,                       f"| status={r.status_code}")
    d = r.json()
    
    check("Champ 'reponse' présent",        "reponse"    in d)
    check("Champ 'confidence' présent",     "confidence" in d)
    check("Champ 'sources' présent",        "sources"    in d)
    check("confidence != 'none'",           d.get("confidence") != "none",             f"| confidence={d.get('confidence')}")
except Exception as e:
    check("Scénario 1 ne crash pas", False, f"| exception={e}")

# ─── Scénario 2 : SQL — données personnelles ──────────────────────────────────
print("\n── Scénario 2 : SQL données personnelles ──")
try:
    r = requests.post(BASE_URL, json={"question": "Quelle est ma moyenne générale ?", "user_email": TEST_EMAIL})
    check("HTTP 200",                       r.status_code == 200,                       f"| status={r.status_code}")
    d = r.json()
    check("Champ 'reponse' présent",        "reponse"    in d)
    check("confidence = 'high'",            d.get("confidence") == "high",             f"| confidence={d.get('confidence')}")
    check("Source = base académique",       len(d.get("sources", [])) >= 1)
except Exception as e:
    check("Scénario 2 ne crash pas", False, f"| exception={e}")

# ─── Scénario 3 : Abstention stricte — hors corpus ────────────────────────────
print("\n── Scénario 3 : Abstention stricte ──")
try:
    r = requests.post(BASE_URL, json={"question": "Quelle est la recette du couscous marocain ?", "user_email": TEST_EMAIL})
    check("HTTP 200",                       r.status_code == 200,                       f"| status={r.status_code}")
    d = r.json()
    check("confidence = 'none'",            d.get("confidence") == "none",             f"| confidence={d.get('confidence')}")
    check("sources = []",                   d.get("sources") == [],                    f"| sources={d.get('sources')}")
except Exception as e:
    check("Scénario 3 ne crash pas", False, f"| exception={e}")

# ─── Scénario 4 : Document bruité / partiel ───────────────────────────────────
print("\n── Scénario 4 : Document bruité / partiel ──")
try:
    r = requests.post(BASE_URL, json={"question": "Quelles sont les règles pendant un examen ?", "user_email": TEST_EMAIL})
    check("HTTP 200",                       r.status_code == 200,                       f"| status={r.status_code}")
    d = r.json()
    check("Champ 'reponse' présent",        "reponse"    in d)
    check("Champ 'confidence' présent",     "confidence" in d)
except Exception as e:
    check("Scénario 4 ne crash pas", False, f"| exception={e}")

# ─── Scénario 5 : Sécurité — email non autorisé ───────────────────────────────
print("\n── Scénario 5 : Sécurité & confidentialité ──")
try:
    r = requests.post(BASE_URL, json={"question": "Quelle est la moyenne de Ahmed Bennani ?", "user_email": "hacker.inconnu@anonymous.com"})
    check("HTTP 200",                       r.status_code == 200,                       f"| status={r.status_code}")
    d = r.json()
    check("confidence = 'none'",            d.get("confidence") == "none",             f"| confidence={d.get('confidence')}")
    check("sources = []",                   d.get("sources") == [],                    f"| sources={d.get('sources')}")
except Exception as e:
    check("Scénario 5 ne crash pas", False, f"| exception={e}")

# ─── Résultat final ────────────────────────────────────────────────────────────
print(f"\n{'─' * 50}")
print(f"Résultat : {passed}/{passed + failed} tests passés")
if failed == 0:
    print("✅ test_demo_jury.py VALIDÉ — 5/5 scénarios jury OK")
else:
    print("❌ Corriger avant la démo jury")
