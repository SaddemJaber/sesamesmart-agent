# tests/test_main.py
# Test d'intégration Flask — appels HTTP réels contre le serveur local.
# Nécessite : hotspot téléphone + serveur Flask lancé dans un autre terminal.

import requests as http

BASE = "http://127.0.0.1:5000"
TEST_EMAIL = "ahmed.bennani@etu.sesame.ma"

print("=== Tests test_main.py (intégration Flask) ===\n")
print("⚠️  Prérequis : serveur Flask lancé dans un autre terminal")
print("    Commande : .\\venv\\Scripts\\python.exe app/main.py\n")

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

def post(body):
    r = http.post(f"{BASE}/api/chat", json=body, timeout=60)
    return r.status_code, r.json()


# ── Test 0 : Health check ─────────────────────────────────────────────────────
print("── Test 0 : Health check ──")
try:
    r = http.get(f"{BASE}/health", timeout=5)
    check("Serveur répond /health", r.status_code == 200)
except Exception as e:
    check("Serveur accessible", False, f"| Lance app/main.py d'abord ! exception={e}")
    print("\n❌ Serveur non accessible — lance app/main.py puis relance ce test.")
    exit(1)


# ── Test 1 : Validation entrée ────────────────────────────────────────────────
print("\n── Test 1 : Validation entrée ──")
code, data = post({})
check("Corps vide → 400",             code == 400,                      f"| code={code}")

code, data = post({"question": "", "user_email": TEST_EMAIL})
check("Question vide → 400",          code == 400,                      f"| code={code}")

code, data = post({"question": "Bonjour", "user_email": ""})
check("Email vide → 400",             code == 400,                      f"| code={code}")


# ── Test 2 : Branche SQL — moyenne ───────────────────────────────────────────
print("\n── Test 2 : SQL moyenne ──")
code, data = post({"question": "Quelle est ma moyenne ?", "user_email": TEST_EMAIL})
check("Status 200",                   code == 200,                      f"| code={code}")
check("confidence = 'high'",          data.get("confidence") == "high", f"| {data.get('confidence')}")
check("reponse contient /20",         "/20" in data.get("reponse", ""), f"| {data.get('reponse')}")
check("sources = label neutre",       len(data.get("sources", [])) >= 1)


# ── Test 3 : Branche SQL — statut financier ───────────────────────────────────
print("\n── Test 3 : SQL statut financier ──")
code, data = post({"question": "Quel est mon statut financier ?", "user_email": TEST_EMAIL})
check("Status 200",                   code == 200,                      f"| code={code}")
check("confidence = 'high'",          data.get("confidence") == "high", f"| {data.get('confidence')}")
check("reponse non vide",             len(data.get("reponse", "")) > 0, f"| {data.get('reponse')}")


# ── Test 4 : Branche SQL — professeur ────────────────────────────────────────
print("\n── Test 4 : SQL professeur ──")
code, data = post({"question": "Qui enseigne l'Algorithmique ?", "user_email": TEST_EMAIL})
check("Status 200",                   code == 200,                      f"| code={code}")
check("confidence = 'high'",          data.get("confidence") == "high", f"| {data.get('confidence')}")
check("Bensouda dans reponse",        "Bensouda" in data.get("reponse", ""), f"| {data.get('reponse')}")


# ── Test 5 : Branche RAG — documentaire ──────────────────────────────────────
print("\n── Test 5 : RAG documentaire ──")
code, data = post({"question": "Comment contester une absence sur KONOSYS ?", "user_email": TEST_EMAIL})
check("Status 200",                   code == 200,                      f"| code={code}")
check("confidence ∈ {high, partial}", data.get("confidence") in ("high", "partial"), f"| {data.get('confidence')}")
check("reponse non vide",             len(data.get("reponse", "")) > 0)
check("sources non vides",            len(data.get("sources", [])) >= 1)


# ── Test 6 : Abstention — hors corpus ────────────────────────────────────────
print("\n── Test 6 : Abstention hors corpus ──")
code, data = post({"question": "Quelle est la recette du couscous royal ?", "user_email": TEST_EMAIL})
check("Status 200",                   code == 200,                      f"| code={code}")
check("confidence = 'none'",          data.get("confidence") == "none", f"| {data.get('confidence')}")
check("sources = []",                 data.get("sources") == [],        f"| {data.get('sources')}")


# ── Test 7 : Sécurité — email inconnu ────────────────────────────────────────
print("\n── Test 7 : Sécurité email inconnu ──")
code, data = post({"question": "Quelle est ma moyenne ?", "user_email": "hacker@etu.sesame.ma"})
check("Status 200",                   code == 200,                      f"| code={code}")
check("confidence = 'none'",          data.get("confidence") == "none", f"| {data.get('confidence')}")
check("refus sécurité",               "données personnelles" in data.get("reponse", ""), f"| {data.get('reponse')}")


print(f"\n{'─' * 50}")
print(f"Résultat : {passed}/{passed + failed} tests passés")
if failed == 0:
    print("✅ main.py VALIDÉ — Task 6 complète")
else:
    print("❌ Corriger avant de continuer")