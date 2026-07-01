# app/sql_handler.py
# Requêtes SQL fixes — zéro text-to-SQL.
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

def get_moyenne(user_email: str) -> dict:
    try:
        res = _supabase.table("etudiants") \
            .select("moyenne_generale") \
            .eq("email", user_email) \
            .execute()
        if not res.data:
            return {'data': None, 'intent': 'moyenne', 'error': 'not_found'}
        return {'data': {'moyenne_generale': res.data[0]['moyenne_generale']}, 'intent': 'moyenne', 'error': None}
    except Exception as e:
        return {'data': None, 'intent': 'moyenne', 'error': str(e)}

def get_statut_financier(user_email: str) -> dict:
    try:
        res = _supabase.table("etudiants") \
            .select("statut_financier") \
            .eq("email", user_email) \
            .execute()
        if not res.data:
            return {'data': None, 'intent': 'statut_financier', 'error': 'not_found'}
        return {'data': {'statut_financier': res.data[0]['statut_financier']}, 'intent': 'statut_financier', 'error': None}
    except Exception as e:
        return {'data': None, 'intent': 'statut_financier', 'error': str(e)}

def get_professeur_matiere(matiere: str) -> dict:
    try:
        if not matiere:
            return {'data': None, 'intent': 'professeur_matiere', 'error': 'matiere_manquante'}
        res = _supabase.table("professeurs") \
            .select("nom_complet, departement") \
            .contains("matieres_enseignees", [matiere]) \
            .execute()
        if not res.data:
            return {'data': None, 'intent': 'professeur_matiere', 'error': 'not_found'}
        return {'data': {'professeurs': res.data}, 'intent': 'professeur_matiere', 'error': None}
    except Exception as e:
        return {'data': None, 'intent': 'professeur_matiere', 'error': str(e)}

def get_filiere(user_email: str) -> dict:
    try:
        res = _supabase.table("etudiants") \
            .select("filiere") \
            .eq("email", user_email) \
            .execute()
        if not res.data:
            return {'data': None, 'intent': 'filiere', 'error': 'not_found'}
        return {'data': {'filiere': res.data[0]['filiere']}, 'intent': 'filiere', 'error': None}
    except Exception as e:
        return {'data': None, 'intent': 'filiere', 'error': str(e)}

def get_annee(user_email: str) -> dict:
    try:
        res = _supabase.table("etudiants") \
            .select("annee") \
            .eq("email", user_email) \
            .execute()
        if not res.data:
            return {'data': None, 'intent': 'annee', 'error': 'not_found'}
        return {'data': {'annee': res.data[0]['annee']}, 'intent': 'annee', 'error': None}
    except Exception as e:
        return {'data': None, 'intent': 'annee', 'error': str(e)}

def get_classement(user_email: str) -> dict:
    """RANK() OVER PARTITION BY filiere — calculé sur toute la table, filtré après."""
    try:
        res = _supabase.rpc("get_classement_etudiant", {"p_email": user_email}).execute()
        if not res.data:
            return {'data': None, 'intent': 'classement', 'error': 'not_found'}
        return {'data': res.data[0], 'intent': 'classement', 'error': None}
    except Exception as e:
        return {'data': None, 'intent': 'classement', 'error': str(e)}
def get_note_matiere(user_email: str, matiere: str) -> dict:
    """SELECT note FROM notes JOIN etudiants WHERE email = :email AND matiere = :matiere"""
    try:
        # Récupérer l'id de l'étudiant
        res_etu = _supabase.table("etudiants").select("id").eq("email", user_email).execute()
        if not res_etu.data:
            return {'data': None, 'intent': 'note_matiere', 'error': 'not_found'}
        etudiant_id = res_etu.data[0]['id']

        res = _supabase.table("notes") \
            .select("note, matiere") \
            .eq("etudiant_id", etudiant_id) \
            .ilike("matiere", f"%{matiere}%") \
            .execute()

        if not res.data:
            return {'data': None, 'intent': 'note_matiere', 'error': 'matiere_introuvable'}  # ← pas not_found
        return {'data': {'note': res.data[0]['note'], 'matiere': res.data[0]['matiere']}, 'intent': 'note_matiere', 'error': None}
    except Exception as e:
        return {'data': None, 'intent': 'note_matiere', 'error': str(e)}

def get_meilleure_matiere(user_email: str) -> dict:
    """Retourne la matière avec la note la plus haute pour cet étudiant."""
    try:
        res_etu = _supabase.table("etudiants").select("id").eq("email", user_email).execute()
        if not res_etu.data:
            return {'data': None, 'intent': 'meilleure_matiere', 'error': 'not_found'}
        etudiant_id = res_etu.data[0]['id']

        res = _supabase.table("notes") \
            .select("note, matiere") \
            .eq("etudiant_id", etudiant_id) \
            .order("note", desc=True) \
            .limit(1) \
            .execute()

        if not res.data:
            return {'data': None, 'intent': 'meilleure_matiere', 'error': 'not_found'}
        return {'data': {'note': res.data[0]['note'], 'matiere': res.data[0]['matiere']}, 'intent': 'meilleure_matiere', 'error': None}
    except Exception as e:
        return {'data': None, 'intent': 'meilleure_matiere', 'error': str(e)}
# ─── Dispatcher ────────────────────────────────────────────────────────────────

def handle_sql(intent: str, params: dict, user_email: str) -> dict:
    """Point d'entrée unique appelé par l'API Flask."""
    if intent == 'note_matiere':
        return get_note_matiere(user_email, params.get('matiere', ''))
    if intent == 'meilleure_matiere':
        return get_meilleure_matiere(user_email)
    if intent == 'moyenne':
        return get_moyenne(user_email)
    if intent == 'statut_financier':
        return get_statut_financier(user_email)
    if intent == 'professeur_matiere':
        return get_professeur_matiere(params.get('matiere', ''))
    if intent == 'filiere':
        return get_filiere(user_email)
    if intent == 'annee':
        return get_annee(user_email)
    if intent == 'classement':
        return get_classement(user_email)
    # Intent inconnu — ne devrait jamais arriver si router.py est correct
    return {'data': None, 'intent': intent, 'error': 'intent_inconnu'}