# app/rag_handler.py
import os
import time
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_supabase: Client = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

# ─── Rotation clés Gemini ─────────────────────────────────────────────────────
# Charge toutes les clés GEMINI_API_KEY_1, _2, _3... disponibles dans .env.
# Sur 429, on tourne vers la clé suivante au lieu d'attendre.
# Si aucune clé numérotée, fallback sur GEMINI_API_KEY (compatibilité).

def _load_gemini_keys() -> list[str]:
    keys = []
    i = 1
    while True:
        key = os.environ.get(f"GEMINI_API_KEY_{i}")
        if not key:
            break
        keys.append(key)
        i += 1
    if not keys:
        keys = [os.environ["GEMINI_API_KEY"]]
    return keys

_GEMINI_KEYS  = _load_gemini_keys()
_key_index    = 0

def _next_key() -> str:
    """Retourne la prochaine clé disponible en rotation circulaire."""
    global _key_index
    key = _GEMINI_KEYS[_key_index % len(_GEMINI_KEYS)]
    _key_index += 1
    return key

def _current_key() -> str:
    """Retourne la clé courante sans avancer l'index."""
    return _GEMINI_KEYS[_key_index % len(_GEMINI_KEYS)]

# ─── URLs et constantes ───────────────────────────────────────────────────────

EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"
GEN_MODEL = "models/gemini-2.5-flash"
GEN_URL   = f"https://generativelanguage.googleapis.com/v1beta/{GEN_MODEL}:generateContent"

SIMILARITY_THRESHOLD = 0.65
SEUIL_BAS  = 0.55
SEUIL_HAUT = 0.65

_doc_titles: dict = {}

def _load_doc_titles():
    global _doc_titles
    if _doc_titles:
        return
    res = _supabase.table("documents").select("id, titre").execute()
    _doc_titles = {row["id"]: row["titre"] for row in (res.data or [])}

# ─── HTTP avec rotation de clés sur 429 ──────────────────────────────────────

def _post_with_retry(url: str, json_body: dict, headers: dict, max_retries: int = 2) -> requests.Response:
    """
    Fix 3 : retry court.
    Fix rotation : sur 429, on tourne la clé Gemini au lieu d'attendre 60s.
    - Tentative 1 : clé courante
    - Si 429 : rotation vers clé suivante, retry immédiat
    - Si encore 429 : HTTPError rapide
    """
    for attempt in range(max_retries):
        try:
            r = requests.post(url, json=json_body, headers=headers, timeout=60)
            if r.status_code == 429:
                if attempt < max_retries - 1:
                    new_key = _next_key()
                    print(f"⚠️ Rate limit 429 — rotation vers clé {(_key_index % len(_GEMINI_KEYS)) + 1}/{len(_GEMINI_KEYS)}...")
                    headers = dict(headers)   # copie pour ne pas muter l'original
                    headers["x-goog-api-key"] = new_key
                    time.sleep(2)             # pause courte avant retry
                    continue
                else:
                    raise requests.exceptions.HTTPError("429 — toutes les clés épuisées")
            r.raise_for_status()
            return r
        except (requests.Timeout, requests.ConnectionError) as e:
            if attempt == max_retries - 1:
                raise
            print(f"⚠️ Erreur réseau, retry {attempt + 1}/{max_retries - 1}...")
            time.sleep(3)
    raise requests.exceptions.HTTPError("Échec après retries")

# ─── Embedding ────────────────────────────────────────────────────────────────

def get_query_embedding(question: str) -> list[float]:
    # taskType RETRIEVAL_QUERY pour la recherche (pas RETRIEVAL_DOCUMENT)
    body = {
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": question}]},
        "taskType": "RETRIEVAL_QUERY",
        "outputDimensionality": 768
    }
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": _current_key()
    }
    r = _post_with_retry(EMBED_URL, body, headers)
    emb = r.json()["embedding"]["values"]
    assert len(emb) == 768, f"Dimension incorrecte : {len(emb)} (attendu 768)"
    return emb

# ─── Retrieval ────────────────────────────────────────────────────────────────

def retrieve(question: str, top_k: int = 2) -> list[dict]:
    """Fix 2 : top_k réduit de 3 → 2. Moins de bruit dans le contexte LLM."""
    _load_doc_titles()
    embedding = get_query_embedding(question)
    embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"

    res = _supabase.rpc(
        "match_chunks",
        {"query_embedding": embedding_str, "match_count": top_k}
    ).execute()

    chunks = []
    for row in (res.data or []):
        doc_id = row.get("document_id", "")
        chunks.append({
            "content":        row.get("content", ""),
            "similarity":     float(row.get("similarity", 0.0)),
            "document_id":    doc_id,
            "document_titre": _doc_titles.get(doc_id, "Document inconnu")
        })
    return chunks

def _select_relevant(chunks: list[dict], top_score: float) -> list[dict]:
    """
    Fix 2 : sélection stricte.
    - Top chunk : toujours gardé.
    - 2e chunk : gardé seulement si écart avec top ≤ 0.03.
    - Résultat : 1 ou 2 chunks max, jamais 3.
    """
    if not chunks:
        return []
    relevant = [chunks[0]]
    if len(chunks) > 1:
        gap = top_score - chunks[1]["similarity"]
        if chunks[1]["similarity"] >= SEUIL_BAS and gap <= 0.03:
            relevant.append(chunks[1])
    return relevant

# ─── Génération ───────────────────────────────────────────────────────────────

def _extract_text(data: dict) -> str:
    candidates = data.get("candidates", [])
    if not candidates:
        return ""
    parts = candidates[0].get("content", {}).get("parts", [])
    return "\n".join(p["text"] for p in parts if p.get("text")).strip()

def generate_answer(question: str, chunks: list[dict], user_role: str = "etudiant") -> str:
    context = "\n\n".join(
        f"[Extrait {i} — Source : {c['document_titre']}]\n{c['content']}"
        for i, c in enumerate(chunks, 1)
    )
    prompt = f"""Tu es SesameSmart, assistant académique de l'école Sesame. Tu réponds UNIQUEMENT en français.

RÈGLE 1 — OBLIGATOIRE : Le contexte ci-dessous contient des extraits de documents officiels Sesame. Tu DOIS répondre en utilisant ces informations.

RÈGLE 2 — INTERDICTION : Il t'est INTERDIT d'écrire "Je n'ai pas cette information dans ma base de connaissances" si le contexte contient des informations pertinentes. Cette phrase est réservée UNIQUEMENT aux cas où le contexte est totalement vide ou hors sujet.

RÈGLE 3 : Si l'information est partielle, commence par "D'après les documents disponibles :" puis donne ce que tu as.

RÈGLE 4 : Réponds en 3-5 lignes maximum. Utilise des bullet points si la réponse est une liste.

Utilisateur actuel : {user_role}

CONTEXTE (documents officiels Sesame) :
{context}

QUESTION : {question}

Réponse directe :"""

    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 512}
    }
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": _current_key()
    }
    r = _post_with_retry(GEN_URL, body, headers)
    answer = _extract_text(r.json())
    return answer if answer else "Je n'ai pas cette information dans ma base de connaissances."

# ─── Point d'entrée ───────────────────────────────────────────────────────────

def handle_rag(question: str, top_k: int = 2, user_role: str = "etudiant") -> dict:
    if len(question.strip()) < 8:
        return {
            "chunks": [], "top_score": 0.0,
            "answer": "Veuillez formuler une question complète.",
            "sources": [], "should_generate": False
        }

    chunks = retrieve(question, top_k=top_k)

    if not chunks:
        return {"chunks": [], "top_score": 0.0, "answer": "", "sources": [], "should_generate": False}

    top_score = chunks[0]["similarity"]

    if top_score < SEUIL_BAS:
        return {"chunks": chunks, "top_score": top_score, "answer": "", "sources": [], "should_generate": False}

    relevant = _select_relevant(chunks, top_score)
    answer   = generate_answer(question, relevant, user_role=user_role)
    sources  = list(dict.fromkeys(c["document_titre"] for c in relevant))

    return {"chunks": chunks, "top_score": top_score, "answer": answer, "sources": sources, "should_generate": True}