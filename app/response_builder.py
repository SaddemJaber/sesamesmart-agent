# app/response_builder.py
# Formate la réponse finale en JSON uniforme.
# Toutes les décisions (confidence, abstention, sécurité) sont du code — jamais du LLM.

from app.rag_handler import SEUIL_BAS, SEUIL_HAUT

ABSTENTION_STRICTE  = "Je n'ai pas cette information dans ma base de connaissances."
REPONSE_BLOQUE      = "Pour régulariser votre situation, rapprochez-vous du service de scolarité."
REFUS_SECURITE      = "Je n'ai accès qu'à vos données personnelles."
SOURCE_SQL          = "Base de données académique Sesame"

_PHRASES_ABSTENTION = [
    ABSTENTION_STRICTE,
    REFUS_SECURITE,
    "Je n'ai pas trouvé d'information",
]

def _compute_confidence(top_score: float) -> str:
    if top_score >= SEUIL_HAUT:
        return "high"
    if top_score >= SEUIL_BAS:
        return "partial"
    return "none"

def _compute_suggestions(answer: str, sources: list, top_score: float) -> list:
    if top_score < SEUIL_HAUT or not sources:
        return []
    return [
        "Quelles sont les autres règles à connaître sur ce sujet ?",
        "Y a-t-il des démarches à effectuer auprès de la scolarité ?"
    ]

# ─── Branche RAG ───────────────────────────────────────────────────────────────

def build_rag_response(rag_result: dict) -> dict:
    top_score  = rag_result["top_score"]
    confidence = _compute_confidence(top_score)

    if not rag_result["should_generate"]:
        return {"reponse": ABSTENTION_STRICTE, "sources": [], "suggestions": [], "confidence": "none"}

    if confidence == "partial":
        source = rag_result["sources"][0] if rag_result["sources"] else "source inconnue"
        return {
            "reponse":     f"J'ai trouvé une information partielle sur ce sujet : {rag_result['answer']} Source : {source}.",
            "sources":     rag_result["sources"],
            "suggestions": [],
            "confidence":  "partial"
        }

    reponse     = rag_result["answer"]
    sources     = rag_result["sources"]
    suggestions = _compute_suggestions(rag_result["answer"], rag_result["sources"], top_score)

    if any(phrase in reponse for phrase in _PHRASES_ABSTENTION):
        confidence  = "none"
        sources     = []
        suggestions = []

    return {"reponse": reponse, "sources": sources, "suggestions": suggestions, "confidence": confidence}

# ─── Branche SQL ───────────────────────────────────────────────────────────────

def build_sql_response(sql_result: dict) -> dict:
    if sql_result["error"] == "not_found":
        return {"reponse": REFUS_SECURITE, "sources": [], "suggestions": [], "confidence": "none"}

    if sql_result["error"] and sql_result["error"] != "not_found":
        return {"reponse": ABSTENTION_STRICTE, "sources": [], "suggestions": [], "confidence": "none"}

    data   = sql_result["data"]
    intent = sql_result["intent"]

    if intent == "moyenne":
        moyenne = data.get("moyenne_generale", "?")
        return {
            "reponse":     f"Votre moyenne générale est de {moyenne}/20.",
            "sources":     [SOURCE_SQL],
            "suggestions": ["Quel est mon statut financier ?"],
            "confidence":  "high"
        }

    if intent == "statut_financier":
        statut = data.get("statut_financier", "?")
        reponse = f"Votre statut financier est : BLOQUÉ. {REPONSE_BLOQUE}" if statut == "BLOQUE" else "Votre situation financière est à jour."
        return {"reponse": reponse, "sources": [SOURCE_SQL], "suggestions": ["Quelle est ma moyenne ?"], "confidence": "high"}

    if intent == "professeur_sans_matiere":
        return {
            "reponse":     "Pour trouver un professeur, précisez la matière. Exemple : 'Qui enseigne Algorithmique ?'",
            "sources":     [],
            "suggestions": ["Qui enseigne Algorithmique ?", "Qui enseigne Management ?"],
            "confidence":  "high"
        }

    if intent == "professeur_matiere":
        profs = data.get("professeurs", [])
        if not profs:
            return {"reponse": ABSTENTION_STRICTE, "sources": [], "suggestions": [], "confidence": "none"}
        noms = ", ".join(p["nom_complet"] for p in profs)
        return {"reponse": f"Cette matière est enseignée par : {noms}.", "sources": [SOURCE_SQL], "suggestions": [], "confidence": "high"}

    if intent == "filiere":
        filiere = data.get("filiere", "?")
        return {
            "reponse":     f"Vous êtes inscrit(e) en filière : {filiere}.",
            "sources":     [SOURCE_SQL],
            "suggestions": ["En quelle année suis-je ?"],
            "confidence":  "high"
        }

    if intent == "annee":
        annee = data.get("annee", "?")
        return {
            "reponse":     f"Vous êtes en année {annee}.",
            "sources":     [SOURCE_SQL],
            "suggestions": ["Dans quelle filière suis-je ?"],
            "confidence":  "high"
        }

    if intent == "classement":
        rang    = data.get("rang_filiere", "?")
        total   = data.get("total_filiere", "?")
        filiere = data.get("filiere", "?")
        moyenne = data.get("moyenne_generale", "?")
        return {
            "reponse":     f"Vous êtes classé(e) {rang}e sur {total} étudiants de la filière {filiere} avec une moyenne de {moyenne}/20.",
            "sources":     [SOURCE_SQL],
            "suggestions": ["Quelle est ma moyenne ?"],
            "confidence":  "high"
        }

    if intent == "note_matiere":
        if not data:
            return {"reponse": ABSTENTION_STRICTE, "sources": [], "suggestions": [], "confidence": "none"}
        return {
            "reponse":     f"Votre note en {data['matiere']} est de {data['note']}/20.",
            "sources":     [SOURCE_SQL],
            "suggestions": ["Quelle est ma meilleure matière ?", "Quelle est ma moyenne ?"],
            "confidence":  "high"
        }

    if intent == "meilleure_matiere":
        if not data:
            return {"reponse": ABSTENTION_STRICTE, "sources": [], "suggestions": [], "confidence": "none"}
        return {
            "reponse":     f"Votre meilleure matière est {data['matiere']} avec une note de {data['note']}/20.",
            "sources":     [SOURCE_SQL],
            "suggestions": ["Quelle est ma moyenne ?", "Quel est mon classement ?"],
            "confidence":  "high"
        }

    if intent == "moyenne_promo":
        filiere       = data.get("filiere", "?")
        moyenne_promo = data.get("moyenne_promo", "?")
        nb            = data.get("nb_etudiants", "?")
        return {
            "reponse":     f"La moyenne de la filière {filiere} est de {moyenne_promo}/20 ({nb} étudiants).",
            "sources":     [SOURCE_SQL],
            "suggestions": ["Quel est mon classement ?", "Quelle est ma moyenne ?"],
            "confidence":  "high"
        }

    return {"reponse": ABSTENTION_STRICTE, "sources": [], "suggestions": [], "confidence": "none"}