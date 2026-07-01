# app/main.py
# API Flask — point d'entrée unique.
# POST /api/chat → assemble router + sql_handler + rag_handler + response_builder

from flask import Flask, request, jsonify
from dotenv import load_dotenv

from app.router           import route
from app.sql_handler      import handle_sql
from app.rag_handler      import handle_rag
from app.response_builder import build_sql_response, build_rag_response

load_dotenv()

app = Flask(__name__)


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Corps attendu : {"question": "...", "user_email": "...", "user_role": "etudiant"}
    Retour        : {"reponse": "...", "sources": [...], "suggestions": [...], "confidence": "..."}
    """
    body = request.get_json(silent=True)

    # ── Validation entrée ──────────────────────────────────────────────────────
    if not body:
        return jsonify({"error": "Corps JSON manquant"}), 400

    question   = (body.get("question") or "").strip()
    user_email = (body.get("user_email") or "").strip()
    user_role  = body.get("user_role", "etudiant")

    if not question:
        return jsonify({"error": "Champ 'question' manquant ou vide"}), 400

    if not user_email:
        return jsonify({"error": "Champ 'user_email' manquant ou vide"}), 400

    # ── Routage ────────────────────────────────────────────────────────────────
    routing = route(question)

    # ── Branche SQL ────────────────────────────────────────────────────────────
    if routing["route"] == "sql":
        sql_result = handle_sql(routing["intent"], routing["params"], user_email)
        response   = build_sql_response(sql_result)

    # ── Branche RAG ────────────────────────────────────────────────────────────
    else:
        try:
            rag_result = handle_rag(question, top_k=3, user_role=user_role)
            response   = build_rag_response(rag_result)
        except Exception:
            # Erreur API Gemini (429 rate limit, timeout, etc.) — jamais de 500
            response = {
                "reponse":     "Le service est temporairement indisponible. Veuillez réessayer dans quelques secondes.",
                "sources":     [],
                "suggestions": [],
                "confidence":  "none"
            }

    return jsonify(response), 200


@app.route("/health", methods=["GET"])
def health():
    """Endpoint de vérification rapide — utilisé par le test d'intégration."""
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    # debug=False en prod — debug=True uniquement pour le développement local
    app.run(host="0.0.0.0", port=5000, debug=True)
