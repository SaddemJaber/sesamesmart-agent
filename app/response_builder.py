# app/response_builder.py
# Formate la réponse finale en JSON uniforme.
# Toutes les décisions (confidence, abstention, sécurité) sont du code — jamais du LLM.

from app.rag_handler import SEUIL_BAS, SEUIL_HAUT

ABSTENTION_STRICTE  = "Je n'ai pas cette information dans ma base de connaissances."
REPONSE_BLOQUE      = "Pour régulariser votre situation, rapprochez-vous du service de scolarité."
REFUS_SECURITE      = "Je n'ai accès qu'à vos données personnelles."
SOURCE_SQL          = "Base de données académique Sesame"

# Phrases produites par le LLM indiquant une abstention — confidence doit être forcée à none
_PHRASES_ABSTENTION = [
    ABSTENTION_STRICTE,
    REFUS_SECURITE,
    "Je n'ai pas trouvé d'information",
]


def _compute_confidence(top_score: float) -> str:
    # Calculé depuis le score — jamais auto-déclaré par le LLM.
    if top_score >= SEUIL_HAUT:
        return "high"
    if top_score >= SEUIL_BAS:
        return "partial"
    return "none"


def _compute_suggestions(answer: str, sources: list, top_score: float) -> list:
    # Suggestions seulement si réponse normale avec sources — jamais sur contexte mince.
    if top_score < SEUIL_HAUT or not sources:
        return []
    return [
        "Quelles sont les autres règles à connaître sur ce sujet ?",
        "Y a-t-il des démarches à effectuer auprès de la scolarité ?"
    ]


# ─── Branche RAG ──────────────────────────────────────────────────────────────

def build_rag_response(rag_result: dict) -> dict:
    """
    Construit la réponse finale depuis le résultat de handle_rag().
    """
    top_score = rag_result["top_score"]
    confidence = _compute_confidence(top_score)

    # Abstention stricte
    if not rag_result["should_generate"]:
        return {
            "reponse":     ABSTENTION_STRICTE,
            "sources":     [],
            "suggestions": [],
            "confidence":  "none"
        }

    # Réponse partielle
    if confidence == "partial":
        source = rag_result["sources"][0] if rag_result["sources"] else "source inconnue"
        return {
            "reponse":     f"J'ai trouvé une information partielle sur ce sujet : {rag_result['answer']} Source : {source}.",
            "sources":     rag_result["sources"],
            "suggestions": [],
            "confidence":  "partial"
        }

    # Réponse normale
    reponse     = rag_result["answer"]
    sources     = rag_result["sources"]
    suggestions = _compute_suggestions(rag_result["answer"], rag_result["sources"], top_score)

    # Fix confidence : si le LLM a produit une phrase d'abstention, corriger confidence
    if any(phrase in reponse for phrase in _PHRASES_ABSTENTION):
        confidence  = "none"
        sources     = []
        suggestions = []

    return {
        "reponse":     reponse,
        "sources":     sources,
        "suggestions": suggestions,
        "confidence":  confidence
    }


# ─── Branche SQL ──────────────────────────────────────────────────────────────

def build_sql_response(sql_result: dict) -> dict:
    """
    Construit la réponse finale depuis le résultat de handle_sql().

    Règles hardcodées (décisions de code, pas du LLM) :
    - BLOQUE → phrase actionnable ajoutée automatiquement
    - not_found → refus de sécurité (RLS a bloqué ou email inconnu)
    - sources → label neutre, jamais de nom de table interne
    """

    # Refus de sécurité — RLS a retourné 0 lignes
    if sql_result["error"] == "not_found":
        return {
            "reponse":     REFUS_SECURITE,
            "sources":     [],
            "suggestions": [],
            "confidence":  "none"
        }

    # Erreur technique
    if sql_result["error"] and sql_result["error"] != "not_found":
        return {
            "reponse":     ABSTENTION_STRICTE,
            "sources":     [],
            "suggestions": [],
            "confidence":  "none"
        }

    data   = sql_result["data"]
    intent = sql_result["intent"]

    # Intent : moyenne
    if intent == "moyenne":
        moyenne = data.get("moyenne_generale", "?")
        return {
            "reponse":     f"Votre moyenne générale est de {moyenne}/20.",
            "sources":     [SOURCE_SQL],
            "suggestions": ["Quel est mon statut financier ?"],
            "confidence":  "high"
        }

    # Intent : statut_financier
    if intent == "statut_financier":
        statut = data.get("statut_financier", "?")
        if statut == "BLOQUE":
            reponse = f"Votre statut financier est : BLOQUÉ. {REPONSE_BLOQUE}"
        else:
            reponse = "Votre situation financière est à jour."
        return {
            "reponse":     reponse,
            "sources":     [SOURCE_SQL],
            "suggestions": ["Quelle est ma moyenne ?"],
            "confidence":  "high"
        }

    # Intent : professeur_sans_matiere — réponse guidée
    if intent == "professeur_sans_matiere":
        return {
            "reponse":     "Pour trouver un professeur, précisez la matière. Exemple : 'Qui enseigne Algorithmique ?'",
            "sources":     [],
            "suggestions": ["Qui enseigne Algorithmique ?", "Qui enseigne Management ?"],
            "confidence":  "high"
        }

    # Intent : professeur_matiere
    if intent == "professeur_matiere":
        profs = data.get("professeurs", [])
        if not profs:
            return {
                "reponse":     ABSTENTION_STRICTE,
                "sources":     [],
                "suggestions": [],
                "confidence":  "none"
            }
        noms = ", ".join(p["nom_complet"] for p in profs)
        return {
            "reponse":     f"Cette matière est enseignée par : {noms}.",
            "sources":     [SOURCE_SQL],
            "suggestions": [],
            "confidence":  "high"
        }

    # Intent inconnu — ne devrait pas arriver
    return {
        "reponse":     ABSTENTION_STRICTE,
        "sources":     [],
        "suggestions": [],
        "confidence":  "none"
    }
    if intent == "filiere":
        filiere = data.get("filiere", "?")
        return {
            "reponse": f"Vous êtes inscrit(e) en filière : {filiere}.",
            "sources": [SOURCE_SQL],
            "suggestions": ["En quelle année suis-je ?"],
            "confidence": "high"
        }

    if intent == "annee":
        annee = data.get("annee", "?")
        return {
            "reponse": f"Vous êtes en année {annee}.",
            "sources": [SOURCE_SQL],
            "suggestions": ["Dans quelle filière suis-je ?"],
            "confidence": "high"
        }