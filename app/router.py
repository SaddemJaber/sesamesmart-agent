# app/router.py
# Routeur déterministe — zéro LLM.
# Entrée : question (str)
# Sortie : {'route': 'sql'|'rag', 'intent': str|None, 'params': dict}

import re
from typing import Optional

# ─── Patterns par intention ────────────────────────────────────────────────────

_MOYENNE_PATTERNS = [
    r'\bmoyenne\b',
    r'\bma\s+note\b',
    r'\bmes\s+notes\b',
    r'\brésultats?\s+académiques?\b',
]

_STATUT_PATTERNS = [
    r'\bstatut\s+financier\b',
    r'\bmon\s+statut\b',
    r'\bbloqué\b',
    r'\bpaiement\b',
    r'\bà\s+jour\b',
    r'\bfrais\s+de\s+scolarité\b',
]

_PROF_PATTERNS = [
    r'\benseigne\b',
    r'\bprofesseur\b',
    r'\bprof\s+de\b',
    r'\bqui\s+donne\b',
    r'\bqui\s+fait\s+le\s+cours\b',
]


def _matches(question: str, patterns: list) -> bool:
    q = question.lower()
    return any(re.search(p, q) for p in patterns)


def _extract_matiere(question: str) -> Optional[str]:
    """
    Extrait la matière depuis 'Qui enseigne X ?'
    Cherche le groupe nominal après les mots déclencheurs.
    """
    q = question.lower().strip()

    triggers = [
        r'enseigne\s+(?:le[s]?\s+|la\s+|les\s+|l\')?(.+?)[\?\.!]?\s*$',
        r'prof(?:esseur)?\s+de\s+(.+?)[\?\.!]?\s*$',
        r'cours\s+de\s+(.+?)[\?\.!]?\s*$',
        r'qui\s+donne\s+(?:le[s]?\s+|la\s+|les\s+|l\')?(.+?)[\?\.!]?\s*$',
    ]
    for pattern in triggers:
        m = re.search(pattern, q)
        if m:
            matiere = m.group(1).strip()
            return matiere.title()  # "mathématiques" → "Mathématiques"

    return None


def route(question: str) -> dict:
    """
    Route déterministe : 'sql' ou 'rag'.

    Ordre d'évaluation (important — ne pas changer) :
      1. moyenne          → SQL intent 'moyenne'
      2. statut_financier → SQL intent 'statut_financier'
      3. professeur       → SQL intent 'professeur_matiere'
      4. défaut           → RAG

    Pourquoi cet ordre : "ma moyenne en maths" doit router sur 'moyenne',
    pas sur 'professeur_matiere' même si "maths" est présent.
    """
    # Intent 1 — Moyenne
    if _matches(question, _MOYENNE_PATTERNS):
        return {'route': 'sql', 'intent': 'moyenne', 'params': {}}

    # Intent 2 — Statut financier
    if _matches(question, _STATUT_PATTERNS):
        return {'route': 'sql', 'intent': 'statut_financier', 'params': {}}

    # Intent 3 — Professeur / matière
    if _matches(question, _PROF_PATTERNS):
        matiere = _extract_matiere(question)
        params = {'matiere': matiere} if matiere else {}
        return {'route': 'sql', 'intent': 'professeur_matiere', 'params': params}

    # Défaut → RAG (jamais de crash, jamais de None)
    return {'route': 'rag', 'intent': None, 'params': {}}