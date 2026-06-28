#!/usr/bin/env python3
"""Vérification de la connexion Supabase et des données chargées"""

from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

s = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 50)
print("✅ VÉRIFICATION DES DONNÉES SUPABASE")
print("=" * 50)

# Test 1: Étudiants
print("\n📚 ÉTUDIANTS (3 premiers):")
r = s.table('etudiants').select('id,nom,prenom,filiere,moyenne_generale').limit(3).execute()
for e in r.data:
    print(f"   - {e['prenom']} {e['nom']} ({e['filiere']}, moy: {e['moyenne_generale']})")

# Test 2: Professeurs
print("\n👨‍🏫 PROFESSEURS (2 premiers):")
r = s.table('professeurs').select('id,nom_complet,departement').limit(2).execute()
for p in r.data:
    print(f"   - {p['nom_complet']} ({p['departement']})")

# Test 3: Documents
print("\n📄 DOCUMENTS:")
r = s.table('documents').select('id,titre,rag_readiness').execute()
for d in r.data:
    print(f"   - {d['titre']} (RAG: {d['rag_readiness']})")

# Test 4: Comptes
print("\n📊 TOTAUX:")
etudiants_count = s.table('etudiants').select('*', count='exact').execute().count
professeurs_count = s.table('professeurs').select('*', count='exact').execute().count
documents_count = s.table('documents').select('*', count='exact').execute().count

print(f"   - {etudiants_count} étudiants ✓")
print(f"   - {professeurs_count} professeurs ✓")
print(f"   - {documents_count} documents ✓")

print("\n" + "=" * 50)
print("✅ CONNEXION SUPABASE FONCTIONNELLE")
print("=" * 50)
