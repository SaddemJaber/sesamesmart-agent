# tests/test_rag_handler.py
# Nécessite : hotspot téléphone + .env correct + Supabase avec les 9 chunks

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.rag_handler import handle_rag, retrieve, get_query_embedding, SEUIL_BAS

print("=== Tests rag_handler.py ===\n")
print("⚠️  Assure-toi : hotspot téléphone activé + bonne clé API dans .env\n")

passed = 0
failed = 0

def check(label, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  ✅  {label}")
        passed += 1
    else:
        print(f"  ❌  {label} {detail}")
        failed += 1


# ── Test 1 : Retrieval KONOSYS ────────────────────────────────────────────────
print("── Test 1 : Retrieval KONOSYS ──")
try:
    chunks = retrieve("Comment contester une absence sur KONOSYS ?", top_k=3)
    check("Retrieve retourne ≥1 chunk",       len(chunks) >= 1,                     f"| nb={len(chunks)}")
    if chunks:
        check("Top-1 = DOC001",               chunks[0]["document_id"] == "DOC001", f"| doc={chunks[0]['document_id']}")
        check("Top-1 score > 0.65",           chunks[0]["similarity"]  >  0.65,    f"| score={chunks[0]['similarity']:.3f}")
        check("Chunk a clé 'content'",        "content"        in chunks[0])
        check("Chunk a clé 'document_titre'", "document_titre" in chunks[0])
except Exception as e:
    check("Retrieve ne crash pas", False, f"| exception={e}")


# ── Test 2 : handle_rag documentaire ─────────────────────────────────────────
print("\n── Test 2 : handle_rag question documentaire ──")
try:
    r = handle_rag("Comment contester une absence sur KONOSYS ?")
    check("should_generate = True",   r["should_generate"] is True,    f"| {r['should_generate']}")
    check("Answer non vide",          len(r["answer"]) > 0,            f"| answer={r['answer'][:60]!r}")
    check("Sources non vides",        len(r["sources"]) >= 1,          f"| sources={r['sources']}")
    check("top_score ≥ SEUIL_BAS",   r["top_score"] >= SEUIL_BAS,     f"| score={r['top_score']:.3f}")
except Exception as e:
    check("handle_rag documentaire ne crash pas", False, f"| exception={e}")


# ── Test 3 : handle_rag hors corpus ──────────────────────────────────────────
print("\n── Test 3 : handle_rag question hors corpus ──")
try:
    r = handle_rag("Quelle est la recette du couscous royal ?")
    check("should_generate = False",  r["should_generate"] is False,   f"| {r['should_generate']}")
    check("Answer vide",              r["answer"] == "",                f"| answer={r['answer']!r}")
    check("Sources vides",            r["sources"] == [],               f"| sources={r['sources']}")
    check("top_score < SEUIL_BAS",   r["top_score"] < SEUIL_BAS,      f"| score={r['top_score']:.3f}")
except Exception as e:
    check("handle_rag hors corpus ne crash pas", False, f"| exception={e}")


# ── Test 4 : Dimension embedding ─────────────────────────────────────────────
print("\n── Test 4 : Dimension embedding ──")
try:
    emb = get_query_embedding("test dimension")
    check("Embedding = 768 dimensions", len(emb) == 768, f"| dim={len(emb)}")
except AssertionError as e:
    check("Assertion dimension 768", False, f"| {e}")
except Exception as e:
    check("get_query_embedding ne crash pas", False, f"| exception={e}")


print(f"\n{'─' * 50}")
print(f"Résultat : {passed}/{passed + failed} tests passés")
if failed == 0:
    print("✅ rag_handler.py VALIDÉ — tu peux passer à response_builder.py")
else:
    print("❌ Corriger avant de continuer")