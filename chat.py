# chat.py
# Interface conversationnelle locale — nécessite Flask lancé sur 127.0.0.1:5000.
# Entrée : questions en français via terminal
# Sortie : réponses du chatbot SesameSmart

import re
import sys
import requests

BASE_URL       = "http://127.0.0.1:5000/api/chat"
EMAIL_RE       = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$")
REFUS_SECURITE = "Je n'ai accès qu'à vos données personnelles."

# ─── Couleurs terminal ─────────────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

HELP_MSG = f"""
{BOLD}=== Aide SesameSmart ==={RESET}
Questions SQL (données personnelles) :
  {CYAN}- Quelle est ma moyenne ?{RESET}
  {CYAN}- Quel est mon statut financier ?{RESET}
  {CYAN}- Qui enseigne les Mathématiques ?{RESET}

Questions RAG (documents institutionnels) :
  {CYAN}- Comment fonctionne la réinscription ?{RESET}
  {CYAN}- Quelles sont les règles pendant un examen ?{RESET}
  {CYAN}- Comment contester une absence sur KONOSYS ?{RESET}

Commandes :
  {CYAN}/help{RESET}     affiche cette aide
  {CYAN}/history{RESET}  affiche les questions de la session
  {CYAN}1 ou 2{RESET}    relance une suggestion
  {CYAN}quit{RESET}      quitte le chat
"""

# ─── Validation format email ───────────────────────────────────────────────────
def _get_email() -> str:
    while True:
        email = input("Ton email étudiant (@etu.sesame.ma) : ").strip()
        if EMAIL_RE.match(email):
            return email
        print(f"{RED}❌ Format invalide. Exemple : ahmed.bennani@etu.sesame.ma{RESET}")

# ─── Vérification email contre la base ────────────────────────────────────────
def _verify_email(email: str) -> bool:
    # Teste l'email avec une requête SQL neutre — si refus sécurité → email inconnu
    try:
        r = requests.post(
            BASE_URL,
            json={"question": "Quelle est ma moyenne ?", "user_email": email},
            timeout=15
        )
        data = r.json()
        if data.get("confidence") == "none" and REFUS_SECURITE in data.get("reponse", ""):
            return False
        return True
    except requests.exceptions.ConnectionError:
        print(f"{RED}❌ Serveur Flask non disponible. Lance : .\\venv\\Scripts\\python.exe -m app.main{RESET}")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"{RED}❌ Timeout — vérifie ton hotspot téléphone (WiFi école bloque Gemini){RESET}")
        sys.exit(1)

# ─── Affichage réponse selon confidence ───────────────────────────────────────
def _print_response(data: dict) -> list[str]:
    confidence  = data.get("confidence", "none")
    reponse     = data.get("reponse", "")
    sources     = data.get("sources", [])
    suggestions = data.get("suggestions", [])

    if confidence == "high":
        print(f"\n{GREEN}{BOLD}✅ Bot :{RESET} {reponse}")
    elif confidence == "partial":
        print(f"\n{YELLOW}{BOLD}⚠️  Bot (réponse partielle) :{RESET} {reponse}")
    else:
        print(f"\n{RED}{BOLD}❌ Bot :{RESET} {reponse}")

    if sources and confidence != "none":
        print(f"{CYAN}📄 Sources : {', '.join(sources)}{RESET}")

    if suggestions and confidence == "high":
        print(f"\n{BOLD}💡 Suggestions :{RESET}")
        for i, s in enumerate(suggestions, 1):
            print(f"  {CYAN}[{i}]{RESET} {s}")

    return suggestions

# ─── Boucle principale ────────────────────────────────────────────────────────
def main() -> None:
    print(f"\n{BOLD}=== SesameSmart Chat ==={RESET}")
    print("Réservé aux étudiants Sesame.")
    print(f"Tape {CYAN}/help{RESET} pour les exemples de questions\n")

    # ── Étape 1 : validation format ───────────────────────────────────────────
    email = _get_email()

    # ── Étape 2 : vérification contre la base ─────────────────────────────────
    print(f"{YELLOW}Vérification de votre email...{RESET}")
    if not _verify_email(email):
        print(f"\n{RED}❌ Email non reconnu dans la base Sesame.{RESET}")
        print("Ce chat est réservé aux étudiants enregistrés.")
        print("Contactez la scolarité si vous pensez qu'il s'agit d'une erreur.")
        sys.exit(0)

        print(f"{GREEN}✅ Bienvenue ! Connecté en tant que {email}{RESET}")
    print(f"{CYAN}Je réponds sur : vos données académiques (moyenne, statut, professeurs),")
    print(f"les règlements, absences, réinscription et examens Sesame.")
    print(f"Je ne réponds pas aux questions hors périmètre Sesame.{RESET}\n")

    last_suggestions: list[str] = []
    history: list[tuple[str, str]] = []

    while True:
        question = input("Ta question : ").strip()

        if question.lower() == "quit":
            print("À bientôt !")
            break

        if not question:
            continue

        # ── Commandes spéciales ───────────────────────────────────────────────
        if question == "/help":
            print(HELP_MSG)
            continue

        if question == "/history":
            if not history:
                print(f"{YELLOW}Aucune question posée pour l'instant.{RESET}")
            else:
                print(f"\n{BOLD}Historique de la session :{RESET}")
                for i, (q, c) in enumerate(history, 1):
                    icon = "✅" if c == "high" else "⚠️" if c == "partial" else "❌"
                    print(f"  {icon} [{i}] {q}")
            print()
            continue

        # ── Suggestion cliquable : taper 1 ou 2 ──────────────────────────────
        if question in ("1", "2") and last_suggestions:
            idx = int(question) - 1
            if idx < len(last_suggestions):
                question = last_suggestions[idx]
                print(f"{CYAN}→ Question relancée : {question}{RESET}")

        # ── Appel API ─────────────────────────────────────────────────────────
        try:
            r = requests.post(
                BASE_URL,
                json={"question": question, "user_email": email},
                timeout=30
            )

            # ── Gestion HTTP 400 ──────────────────────────────────────────────
            if r.status_code == 400:
                err = r.json().get("error", "Requête invalide")
                print(f"{RED}❌ Erreur 400 : {err}{RESET}")
                print()
                continue

            data = r.json()
            last_suggestions = _print_response(data)
            history.append((question, data.get("confidence", "none")))

        except requests.exceptions.ConnectionError:
            print(f"{RED}❌ Serveur Flask non disponible. Lance : .\\venv\\Scripts\\python.exe -m app.main{RESET}")
        except requests.exceptions.Timeout:
            print(f"{RED}❌ Timeout — vérifie ton hotspot téléphone (WiFi école bloque Gemini){RESET}")
        except Exception as e:
            print(f"{RED}❌ Erreur inattendue : {e}{RESET}")

        print()

if __name__ == "__main__":
    main()
