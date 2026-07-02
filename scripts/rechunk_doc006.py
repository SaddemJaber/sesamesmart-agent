# scripts/rechunk_doc006.py
# Ré-ingestion ciblée de DOC006 avec chunking par section (===).
# À lancer APRÈS nettoyage manuel via Supabase SQL Editor.
# Usage : .\venv\Scripts\python.exe scripts/rechunk_doc006.py

import os
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

_ROOT       = Path(__file__).parent.parent
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
GEMINI_KEY   = os.environ.get("GEMINI_API_KEY_1") or os.environ["GEMINI_API_KEY"]

supabase   = create_client(SUPABASE_URL, SUPABASE_KEY)
EMBED_URL  = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"
DOC_ID     = "DOC006"
DOC_PATH   = _ROOT / "data" / "corpus" / "doc006_faq_scolarite.txt"


def chunk_by_section(text: str) -> list[dict]:
    """
    Découpe le texte sur les séparateurs === TITRE ===.
    Chaque section devient un chunk indépendant.
    Les lignes d'introduction avant la première section forment le chunk 0.
    """
    lines   = text.splitlines()
    chunks  = []
    current_title  = "Introduction"
    current_lines  = []

    for line in lines:
        if line.startswith("===") and line.endswith("==="):
            # Sauvegarder la section en cours si elle a du contenu
            content = "\n".join(current_lines).strip()
            if content:
                chunks.append({"title": current_title, "content": content})
            current_title = line.strip("= ").strip()
            current_lines = []
        else:
            current_lines.append(line)

    # Dernière section
    content = "\n".join(current_lines).strip()
    if content:
        chunks.append({"title": current_title, "content": content})

    return chunks


def get_embedding(text: str) -> list[float]:
    body = {
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": text}]},
        "taskType": "RETRIEVAL_DOCUMENT",
        "outputDimensionality": 768
    }
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_KEY
    }
    r = requests.post(EMBED_URL, json=body, headers=headers, timeout=60)
    r.raise_for_status()
    emb = r.json()["embedding"]["values"]
    assert len(emb) == 768, f"Dimension incorrecte : {len(emb)}"
    return emb


def main():
    print(f"\n=== Re-chunking {DOC_ID} par sections ===\n")

    if not DOC_PATH.exists():
        print(f"❌ Fichier introuvable : {DOC_PATH}")
        return

    text   = DOC_PATH.read_text(encoding="utf-8")
    chunks = chunk_by_section(text)

    print(f"  ✓ {len(chunks)} sections détectées :")
    for i, c in enumerate(chunks):
        print(f"    chunk {i} — [{c['title']}] — {len(c['content'])} chars")

    print(f"\n  ⚠️  Rappel : supprimer les anciens chunks DOC006 via SQL Editor AVANT de continuer")
    print(f"  Commande SQL : DELETE FROM document_chunks WHERE document_id = 'DOC006';")
    input("\n  Appuie sur ENTRÉE une fois le DELETE exécuté dans Supabase SQL Editor...")

    inserted = 0
    for i, chunk in enumerate(chunks):
        # Embed le titre + contenu pour un meilleur signal sémantique
        text_to_embed = f"{chunk['title']}\n\n{chunk['content']}"
        try:
            emb = get_embedding(text_to_embed)
            supabase.table("document_chunks").insert({
                "document_id": DOC_ID,
                "chunk_index": i,
                "content":     chunk["content"],
                "token_count": len(chunk["content"].split()),
                "embedding":   emb
            }).execute()
            inserted += 1
            print(f"  chunk {i+1}/{len(chunks)} [{chunk['title']}] → 768d ✓")
            time.sleep(2)   # pace RPM
        except Exception as e:
            print(f"  ⚠️  chunk {i+1} échoué : {e}")

    print(f"\n  ✅ {inserted}/{len(chunks)} chunks insérés pour {DOC_ID}")

    # Vérification
    res = supabase.table("document_chunks").select("chunk_index, content").eq("document_id", DOC_ID).execute()
    print(f"\n=== Vérification — {len(res.data)} chunks en base ===")
    for row in res.data:
        print(f"  chunk {row['chunk_index']} — {row['content'][:60]}...")


if __name__ == "__main__":
    main()