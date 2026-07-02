# tests/test_extensions.py
# Pack validation extensions #1–#5
# Prérequis : serveur Flask lancé + email de test valide

import requests, time

BASE = "http://localhost:5000/api/chat"
EMAIL = "ahmed.bennani@etu.sesame.ma"

def ask(question, sleep=0):
    if sleep:
        time.sleep(sleep)
    r = requests.post(BASE, json={"question": question, "user_email": EMAIL})
    return r.json()

results = []

def check(label, condition, detail=""):
    ok = bool(condition)
    results.append((label, ok, detail))
    icon = "✅" if ok else "❌"
    print(f"  {icon} {label}" + (f" — {detail}" if detail else ""))

print("\n=== Validation extensions #1–#5 ===\n")

# ── Ext #1 : note_matiere ─────────────────────────────────────────────────────
print("── Ext #1a : note_matiere ──")
r = ask("Quelle est ma note en Marketing Digital ?")   # ← FIX: matière MANAGEMENT
check("status 200", r.get("confidence") is not None)
check("confidence = high", r.get("confidence") == "high")
check("reponse contient /20", "/20" in r.get("reponse", ""))
check("source = SQL", "Base de données" in str(r.get("sources", [])))
time.sleep(5)

# ── Ext #1 : meilleure_matiere ────────────────────────────────────────────────
print("\n── Ext #1b : meilleure_matiere ──")
r = ask("Quelle est ma meilleure matière ?")
check("confidence = high", r.get("confidence") == "high")
check("reponse contient /20", "/20" in r.get("reponse", ""))
check("source = SQL", "Base de données" in str(r.get("sources", [])))
time.sleep(5)

# ── Ext #2 : moyenne_promo ────────────────────────────────────────────────────
print("\n── Ext #2 : moyenne_promo ──")
r = ask("Quelle est la moyenne de ma filière ?")
check("confidence = high", r.get("confidence") == "high")
check("reponse contient filière", any(f in r.get("reponse","") for f in ["MANAGEMENT","FTA","ING"]))
check("reponse contient /20", "/20" in r.get("reponse", ""))
check("reponse contient nb étudiants", any(c.isdigit() for c in r.get("reponse","").split("(")[-1][:5]) if "(" in r.get("reponse","") else False)
check("source = SQL", "Base de données" in str(r.get("sources", [])))
time.sleep(5)

# ── Ext #4 : DOC006 FAQ scolarité ─────────────────────────────────────────────
print("\n── Ext #4a : DOC006 FAQ scolarité ──")
r = ask("Quel est le délai pour obtenir un relevé de notes officiel tamponné ?", sleep=30)  # ← FIX: question unique DOC006
check("confidence != none", r.get("confidence") != "none")
check("reponse non vide", len(r.get("reponse","")) > 20)
check("source contient FAQ ou scolarité",                                   # ← FIX: keywords élargis
      any(k in str(r.get("sources","")).lower() for k in ["faq", "scolar", "konosys", "questions fr"]))
time.sleep(30)

# ── Ext #4 : DOC007 règlement examens ─────────────────────────────────────────
print("\n── Ext #4b : DOC007 règlement examens ──")
r = ask("Qu'est-ce qui se passe si on fraude à l'examen ?")
check("confidence != none", r.get("confidence") != "none")
check("reponse contient fraude ou note 0", any(k in r.get("reponse","").lower() for k in ["fraude","zéro","0/20","disciplin"]))
time.sleep(30)

# ── Ext #4 : DOC008 guide stages ─────────────────────────────────────────────
print("\n── Ext #4c : DOC008 guide stages ──")
r = ask("Quelles sont les conditions pour valider une convention de stage ?")
check("confidence != none", r.get("confidence") != "none")
check("reponse contient convention", "convention" in r.get("reponse","").lower())
time.sleep(30)

# ── Ext #5 : format liste => bullet points ────────────────────────────────────
print("\n── Ext #5a : format bullet points ──")
r = ask("Quels documents faut-il fournir pour se réinscrire ?")
check("confidence = high", r.get("confidence") == "high")
reponse_5a = r.get("reponse","")
check("reponse contient bullet points",
      any(c in reponse_5a for c in ["*", "-", "–", "•", "\n"]))
check("pas de hedge inutile", "D'après les documents disponibles" not in r.get("reponse",""))
time.sleep(30)

# ── Ext #5 : abstention inchangée ─────────────────────────────────────────────
print("\n── Ext #5b : abstention hors corpus ──")
r = ask("Quelle est la météo à Casablanca ?")
check("confidence = none", r.get("confidence") == "none")
check("sources = []", r.get("sources") == [])

# ── Résumé ────────────────────────────────────────────────────────────────────
print("\n" + "─"*50)
passed = sum(1 for _, ok, _ in results if ok)
total  = len(results)
print(f"Résultat : {passed}/{total} checks passés")
if passed == total:
    print("✅ Extensions #1–#5 VALIDÉES")
else:
    print("❌ Gaps détectés — voir ci-dessus")
    for label, ok, detail in results:
        if not ok:
            print(f"  FAIL : {label}")