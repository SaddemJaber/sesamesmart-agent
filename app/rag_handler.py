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

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

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


def _post_with_retry(url: str, json_body: dict, headers: dict, max_retries: int = 3) -> requests.Response:
    # Retry sur erreurs réseau ET sur 429 (rate limit) — jamais sur 404/401/403
    last_exception = None
    for attempt in range(max_retries):
        try:
            r = requests.post(url, json=json_body, headers=headers, timeout=60)
            if r.status_code == 429:
                wait = 10 * (attempt + 1)  # 10s, 20s, 30s
                print(f"⚠️ Rate limit 429, attente {wait}s avant retry {attempt + 1}/{max_retries}...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r
        except (requests.Timeout, requests.ConnectionError) as e:
            last_exception = e
            if attempt == max_retries - 1:
                raise
            print(f"⚠️ Erreur réseau, retry {attempt + 1}/{max_retries}...")
            time.sleep(3)
    raise requests.exceptions.HTTPError(f"429 rate limit après {max_retries} retries")


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
        "x-goog-api-key": GEMINI_API_KEY
    }
    r = _post_with_retry(EMBED_URL, body, headers)
    emb = r.json()["embedding"]["values"]
    assert len(emb) == 768, f"Dimension incorrecte : {len(emb)} (attendu 768)"
    return emb


def retrieve(question: str, top_k: int = 3) -> list[dict]:
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


def _extract_text(data: dict) -> str:
    # Extraction défensive — certains candidats peuvent ne pas avoir de parts.text
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
        "x-goog-api-key": GEMINI_API_KEY
    }
    r = _post_with_retry(GEN_URL, body, headers)
    answer = _extract_text(r.json())
    return answer if answer else "Je n'ai pas cette information dans ma base de connaissances."


def handle_rag(question: str, top_k: int = 3, user_role: str = "etudiant") -> dict:
    # Garde-fou : questions trop courtes non interprétables
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

    relevant = [c for c in chunks if c["similarity"] >= SEUIL_BAS]
    answer  = generate_answer(question, relevant, user_role=user_role)
    sources = list(dict.fromkeys(c["document_titre"] for c in relevant))

    return {"chunks": chunks, "top_score": top_score, "answer": answer, "sources": sources, "should_generate": True}