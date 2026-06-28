import json
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL et SUPABASE_KEY doivent être dans .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
DATA_DIR = Path(__file__).parent.parent / "data"

def seed_table(table_name: str, filepath: Path):
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)
    # Insertion par lots de 10 (évite les timeouts)
    for i in range(0, len(data), 10):
        batch = data[i:i+10]
        supabase.table(table_name).upsert(batch).execute()
    print(f"✓ {len(data)} lignes insérées dans '{table_name}'")

def main():
    print("Chargement des données mock dans Supabase...")
    seed_table("etudiants",   DATA_DIR / "etudiants.json")
    seed_table("professeurs", DATA_DIR / "professeurs.json")
    seed_table("documents",   DATA_DIR / "documents_metadata.json")
    print("\nSeed terminé.")

if __name__ == "__main__":
    main()
