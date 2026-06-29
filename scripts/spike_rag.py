"""
spike_rag.py
Spike RAG minimal sur DOC001 (Note KONOSYS)

But:
1. Générer un embedding Gemini valide
2. Insérer 1+ chunks dans Supabase
3. Vérifier que la recherche vectorielle retourne DOC001 en top-1

Prérequis:
- .env contient SUPABASE_URL, SUPABASE_KEY, GEMINI_API_KEY
- la table documents contient DOC001
- la fonction SQL match_chunks(...) existe dans Supabase
"""

import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL et SUPABASE_KEY manquent dans .env")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY manquant dans .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"

def get_embedding(text: str) -> list[float]:
    """
    Appel REST officiel Gemini embeddings.
    On force outputDimensionality=768 pour rester compatible avec pgvector vector(768).
    """
    body = {
        "model": "models/gemini-embedding-001",
        "content": {
            "parts": [
                {"text": text}
            ]
        },
        "taskType": "RETRIEVAL_DOCUMENT",
        "outputDimensionality": 768
    }

    headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": GEMINI_API_KEY
}

    r = requests.post(EMBED_URL, json=body, headers=headers, timeout=60)
    r.raise_for_status()

    data = r.json()
    emb = data["embedding"]["values"]

    assert len(emb) == 768, f"Dimension incorrecte : {len(emb)} (attendu 768)"
    return emb


def get_query_embedding(text: str) -> list[float]:
    """
    Embedding pour la question utilisateur.
    Même modèle, même dimension, taskType adapté à la requête.
    """
    body = {
        "model": "models/gemini-embedding-001",
        "content": {
            "parts": [
                {"text": text}
            ]
        },
        "taskType": "RETRIEVAL_QUERY",
        "outputDimensionality": 768
    }

    headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": GEMINI_API_KEY
}

    r = requests.post(EMBED_URL, json=body, headers=headers, timeout=60)
    r.raise_for_status()

    data = r.json()
    emb = data["embedding"]["values"]

    assert len(emb) == 768, f"Dimension incorrecte question : {len(emb)} (attendu 768)"
    return emb


KONOSYS_TEXT = """
UNIVERSITÉ SESAME
NOTE DE SERVICE
Objet : Gestion et validation des absences étudiantes sur KONOSYS

La présente note a pour objet de préciser les procédures relatives à la gestion
des absences sur la plateforme KONOSYS.

1. SIGNALEMENT DES ABSENCES
Les absences sont enregistrées automatiquement par les enseignants sur KONOSYS
dans les 24h suivant le cours.

2. CONSULTATION DES ABSENCES
L'étudiant peut consulter ses absences via son espace personnel KONOSYS
rubrique "Mes absences".

3. CONTESTATION D'UNE ABSENCE
Pour contester une absence, l'étudiant doit :
- Se connecter à KONOSYS dans un délai de 5 jours ouvrables
- Accéder à la rubrique "Contestation"
- Remplir le formulaire de contestation en joignant les justificatifs nécessaires
- Soumettre la demande pour validation par le responsable pédagogique

4. TRAITEMENT DES CONTESTATIONS
Les contestations sont traitées sous 72h par le service de scolarité.
Une notification est envoyée à l'étudiant après décision.

5. ABSENCES JUSTIFIÉES
Les justificatifs acceptés sont : certificat médical, convocation officielle,
circonstance exceptionnelle validée par l'administration.
""".strip()


def chunk_text(text: str, max_chars: int = 1200) -> list[str]:
    """
    Découpage très simple par paragraphes.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""

    for para in paragraphs:
        candidate = f"{current}\n\n{para}".strip() if current else para
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = para

    if current:
        chunks.append(current)

    return chunks


def ensure_doc_exists():
    doc = supabase.table("documents").select("id").eq("id", "DOC001").execute()
    if not doc.data:
        raise ValueError("DOC001 absent de la table documents. Relance d'abord seed_supabase.py")


def delete_existing_chunks():
    supabase.table("document_chunks").delete().eq("document_id", "DOC001").execute()


def insert_chunks(chunks: list[str], embeddings: list[list[float]]):
    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        supabase.table("document_chunks").insert({
            "document_id": "DOC001",
            "chunk_index": i,
            "content": chunk,
            "token_count": len(chunk.split()),
            "embedding": emb
        }).execute()


def main():
    ensure_doc_exists()

    chunks = chunk_text(KONOSYS_TEXT)
    print(f"✓ {len(chunks)} chunks créés")

    print("Génération des embeddings...")
    embeddings = []
    for i, chunk in enumerate(chunks, start=1):
        emb = get_embedding(chunk)
        embeddings.append(emb)
        print(f"  chunk {i}/{len(chunks)} → {len(emb)} dimensions ✓")

    delete_existing_chunks()
    print("✓ Anciens chunks DOC001 supprimés")

    insert_chunks(chunks, embeddings)
    print(f"✓ {len(chunks)} chunks insérés dans document_chunks")

    test_question = "Comment contester une absence sur KONOSYS ?"
    print(f"\nTest de retrieval : {test_question}")

    q_emb = get_query_embedding(test_question)

    result = supabase.rpc("match_chunks", {
        "query_embedding": q_emb,
        "match_count": 3
    }).execute()

    if not result.data:
        print("⚠️ Aucun résultat retourné par match_chunks")
        return

    print("\n── Top chunks récupérés ──")
    for i, row in enumerate(result.data[:3], start=1):
        doc_id = row.get("document_id", "?")
        similarity = row.get("similarity", 0)
        preview = row.get("content", "")[:140].replace("\n", " ")
        print(f"  #{i} [{doc_id}] sim={similarity:.3f} | {preview}...")

    print("\n── VERDICT ──")
    top_doc = result.data[0].get("document_id")
    if top_doc == "DOC001":
        print("✅ SPIKE RÉUSSI — top-1 chunk vient de DOC001")
        print("→ La stack RAG fonctionne.")
    else:
        print(f"⚠️ top-1 inattendu : {top_doc} (attendu DOC001)")


if __name__ == "__main__":
    main()