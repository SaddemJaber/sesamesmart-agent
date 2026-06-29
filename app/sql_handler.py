# app/sql_handler.py
# 3 requêtes SQL fixes — zéro text-to-SQL.
# Entrée : intent (str) + params (dict) + user_email (str)
# Sortie : dict avec 'data', 'intent', 'error'

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_supabase: Client = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

# ─── Sécurité ──────────────────────────────────────────────────────────────────
# Toutes les requêtes étudiants filtrent sur user_email.
# Un étudiant ne peut pas voir les données d'un autre.
# Le refus est géré ici (0 lignes retournées) → response_builder détecte et refuse.


def get_moyenne(user_email: str) -> dict:
    """SELECT moyenne_generale FROM etudiants WHERE email = :email"""
    try:
        res = _supabase.table("etudiants") \
            .select("moyenne_generale") \
            .eq("email", user_email) \
            .execute()

        if not res.data:
            return {'data': None, 'intent': 'moyenne', 'error': 'not_found'}

        return {
            'data': {'moyenne_generale': res.data[0]['moyenne_generale']},
            'intent': 'moyenne',
            'error': None
        }
    except Exception as e:
        return {'data': None, 'intent': 'moyenne', 'error': str(e)}


def get_statut_financier(user_email: str) -> dict:
    """SELECT statut_financier FROM etudiants WHERE email = :email"""
    try:
        res = _supabase.table("etudiants") \
            .select("statut_financier") \
            .eq("email", user_email) \
            .execute()

        if not res.data:
            return {'data': None, 'intent': 'statut_financier', 'error': 'not_found'}

        return {
            'data': {'statut_financier': res.data[0]['statut_financier']},
            'intent': 'statut_financier',
            'error': None
        }
    except Exception as e:
        return {'data': None, 'intent': 'statut_financier', 'error': str(e)}


def get_professeur_matiere(matiere: str) -> dict:
    """SELECT nom_complet FROM professeurs WHERE matieres_enseignees @> ARRAY[:matiere]"""
    try:
        if not matiere:
            return {'data': None, 'intent': 'professeur_matiere', 'error': 'matiere_manquante'}

        res = _supabase.table("professeurs") \
            .select("nom_complet, departement") \
            .contains("matieres_enseignees", [matiere]) \
            .execute()

        if not res.data:
            return {'data': None, 'intent': 'professeur_matiere', 'error': 'not_found'}

        return {
            'data': {'professeurs': res.data},
            'intent': 'professeur_matiere',
            'error': None
        }
    except Exception as e:
        return {'data': None, 'intent': 'professeur_matiere', 'error': str(e)}


# ─── Dispatcher ────────────────────────────────────────────────────────────────

def handle_sql(intent: str, params: dict, user_email: str) -> dict:
    """
    Point d'entrée unique appelé par l'API Flask.
    Dispatche vers la bonne fonction selon l'intent.
    """
    if intent == 'moyenne':
        return get_moyenne(user_email)

    if intent == 'statut_financier':
        return get_statut_financier(user_email)

    if intent == 'professeur_matiere':
        matiere = params.get('matiere', '')
        return get_professeur_matiere(matiere)

    # Intent inconnu — ne devrait jamais arriver si router.py est correct
    return {'data': None, 'intent': intent, 'error': 'intent_inconnu'}