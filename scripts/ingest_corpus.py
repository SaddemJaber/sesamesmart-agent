"""
ingest_corpus.py
Task 4 — Prétraitement et ingestion des 5 documents dans document_chunks

Sources :
- DOC001, DOC002 : extraction depuis vrais PDFs via pdfplumber
- DOC003, DOC004, DOC005 : fichiers .txt propres dans data/corpus/
"""

import os
import re
import requests
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
import pdfplumber

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"

PDF_DIR  = Path("C:/Users/SaddemJABER/Desktop/PFA")
TXT_DIR  = Path("data/corpus")
TXT_DIR.mkdir(parents=True, exist_ok=True)

# ── Mapping documents ────────────────────────────────────────────────────────
DOCUMENTS = [
    {
        "id": "DOC001",
        "source_type": "txt",
        "path": TXT_DIR / "doc001_konosys.txt"
    },
    {
        "id": "DOC002",
        "source_type": "txt",
        "path": TXT_DIR / "doc002_ri_fta.txt"
    },
    {
        "id": "DOC003",
        "source_type": "txt",
        "path": TXT_DIR / "doc003_charte.txt"
    },
    {
        "id": "DOC004",
        "source_type": "txt",
        "path": TXT_DIR / "doc004_reinscription.txt"
    },
    {
        "id": "DOC005",
        "source_type": "txt",
        "path": TXT_DIR / "doc005_attestation.txt"
    },
]


def extract_pdf(path: Path) -> str:
    """Extraction texte depuis PDF avec nettoyage basique."""
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # Nettoyer les lignes de pagination isolées (ex: "1", "2", "- 3 -")
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        stripped = line.strip()
        # Ignorer les lignes qui ne contiennent qu'un numéro de page
        if re.match(r'^[-–—]?\s*\d+\s*[-–—]?$', stripped):
            continue
        if stripped:
            cleaned.append(stripped)

    return "\n".join(cleaned)


def extract_txt(path: Path) -> str:
    """Lecture directe d'un fichier texte propre."""
    return path.read_text(encoding="utf-8")


def chunk_text(text: str, max_chars: int = 1500) -> list:
    """
    Découpage par paragraphes avec fallback taille fixe.
    Cible : chunks entre 300 et 1500 chars.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 50]
    chunks = []
    current = ""

    for para in paragraphs:
        candidate = f"{current}\n\n{para}".strip() if current else para
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)
            # Si le paragraphe seul est trop long, découpage forcé
            if len(para) > max_chars:
                words = para.split()
                sub = ""
                for word in words:
                    if len(sub) + len(word) < max_chars:
                        sub += " " + word if sub else word
                    else:
                        if sub:
                            chunks.append(sub)
                        sub = word
                if sub:
                    current = sub
            else:
                current = para

    if current:
        chunks.append(current)

    return chunks


def get_embedding(text: str, retries: int = 3) -> list:
    """Embedding REST Gemini — RETRIEVAL_DOCUMENT. Retry automatique sur timeout."""
    body = {
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": text}]},
        "taskType": "RETRIEVAL_DOCUMENT",
        "outputDimensionality": 768
    }
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }
    for attempt in range(1, retries + 1):
        try:
            r = requests.post(EMBED_URL, json=body, headers=headers, timeout=120)
            r.raise_for_status()
            emb = r.json()["embedding"]["values"]
            assert len(emb) == 768, f"Dimension incorrecte : {len(emb)}"
            return emb
        except requests.exceptions.Timeout:
            print(f"    ⏳ Timeout (tentative {attempt}/{retries}), retry...")
            if attempt == retries:
                raise
    raise RuntimeError("Tous les retries épuisés")


def ingest_document(doc: dict):
    doc_id = doc["id"]
    path = doc["path"]

    print(f"\n── {doc_id} : {path.name} ──")

    if not path.exists():
        print(f"  ⚠️  Fichier introuvable : {path}")
        return

    # Extraction
    if doc["source_type"] == "pdf":
        text = extract_pdf(path)
    else:
        text = extract_txt(path)

    print(f"  ✓ Texte extrait : {len(text)} caractères")

    # Chunking
    chunks = chunk_text(text)
    print(f"  ✓ {len(chunks)} chunks créés")

    # Suppression anciens chunks (idempotence)
    supabase.table("document_chunks").delete().eq("document_id", doc_id).execute()

    # Embedding + insertion
    inserted = 0
    for i, chunk in enumerate(chunks):
        try:
            emb = get_embedding(chunk)
            supabase.table("document_chunks").insert({
                "document_id": doc_id,
                "chunk_index": i,
                "content": chunk,
                "token_count": len(chunk.split()),
                "embedding": emb
            }).execute()
            inserted += 1
            print(f"  chunk {i+1}/{len(chunks)} → 768d ✓")
        except Exception as e:
            print(f"  ⚠️  chunk {i+1} échoué : {e}")

    print(f"  ✅ {inserted}/{len(chunks)} chunks insérés pour {doc_id}")


def main():
    print("=== Task 4 — Ingestion corpus SesameSmart ===\n")

    for doc in DOCUMENTS:
        ingest_document(doc)

    # Vérification finale
    print("\n=== Vérification finale ===")
    result = supabase.table("document_chunks").select("document_id", count="exact").execute()
    print(f"Total chunks dans Supabase : {result.count}")

    from collections import Counter
    counts = Counter(row["document_id"] for row in result.data)
    for doc_id, n in sorted(counts.items()):
        print(f"  {doc_id} : {n} chunks")

    print("\n✅ Ingestion terminée.")


if __name__ == "__main__":
    main()