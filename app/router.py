# app/router.py
# Routeur déterministe — zéro LLM.
# Entrée : question (str)
# Sortie : {'route': 'sql'|'rag', 'intent': str|None, 'params': dict}


import re
from typing import Optional

# ─── Patterns par intention ────────────────────────────────────────────────────

_NOTE_MATIERE_PATTERNS = [
    r'\bma\s+note\s+en\b',
    r'\bma\s+note\s+de\b',
    r'\bcombien\s+j\'?ai\s+en\b',
    r'\bj\'?ai\s+eu\s+en\b',
    r'\bmon\s+résultat\s+en\b',
]

_MEILLEURE_MATIERE_PATTERNS = [
    r'\bmeilleure\s+mati[eè]re\b',
    r'\bmeilleur\s+résultat\b',
    r'\bmeilleure\s+note\b',
    r'\ben\s+quoi\s+je\s+suis\s+le\s+meilleur\b',
]

_MOYENNE_PATTERNS = [
    r'\bmoyenne\b',
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

_FILIERE_PATTERNS = [
    r'\bma\s+fili[eè]re\b',
    r'\bquelle\s+fili[eè]re\b',
    r'\bmon\s+d[eé]partement\b',
]

_ANNEE_PATTERNS = [
    r'\bmon\s+ann[eé]e\b',
    r'\bquelle\s+ann[eé]e\b',
    r'\ben\s+quelle\s+ann[eé]e\b',
]

_CLASSEMENT_PATTERNS = [
    r'\bclassement\b',
    r'\bmon\s+rang\b',
    r'\bje\s+suis\s+class[eé]\b',
    r'\bma\s+position\b',
    r'\bcombien\s+d\'[eé]tudiants\b',
    r'\brang\s+dans\b',
]

_PROF_SANS_MATIERE_PATTERNS = [
    r'\bmes\s+professeurs?\b',
    r'\bmes\s+profs?\b',
    r'\bqui\s+sont\s+mes\s+profs?\b',
    r'\bquels\s+profs?\b',
    r'\bliste.{0,10}profs?\b',
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
    """Extrait la matière depuis 'Qui enseigne X ?'"""
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
            return m.group(1).strip().title()
    return None

def _extract_matiere_note(question: str) -> Optional[str]:
    """Extrait la matière depuis 'ma note en X' ou 'j'ai eu en X'."""
    q = question.lower().strip()
    triggers = [
        r'note\s+en\s+(.+?)[\?\.!]?\s*$',
        r'note\s+de\s+(.+?)[\?\.!]?\s*$',
        r'ai\s+en\s+(.+?)[\?\.!]?\s*$',
        r'eu\s+en\s+(.+?)[\?\.!]?\s*$',
        r'résultat\s+en\s+(.+?)[\?\.!]?\s*$',
    ]
    for pattern in triggers:
        m = re.search(pattern, q)
        if m:
            return m.group(1).strip().title()
    return None

def route(question: str) -> dict:
    """
    Ordre d'évaluation (ne pas changer) :
      0. note_matiere     — AVANT moyenne (collision 'ma note' supprimée de moyenne)
      0b. meilleure_matiere
      1. moyenne
      2. statut_financier
      3. classement       — AVANT filiere (collision "classement dans ma filière")
      4. filiere
      5. annee
      6a. professeur_sans_matiere
      6b. professeur_matiere
      7. défaut → RAG
    """
    # Intent 0 — Note par matière (AVANT moyenne)
    if _matches(question, _NOTE_MATIERE_PATTERNS):
        matiere = _extract_matiere_note(question)
        return {'route': 'sql', 'intent': 'note_matiere', 'params': {'matiere': matiere or ''}}

    # Intent 0b — Meilleure matière
    if _matches(question, _MEILLEURE_MATIERE_PATTERNS):
        return {'route': 'sql', 'intent': 'meilleure_matiere', 'params': {}}

    # Intent 1 — Moyenne
    if _matches(question, _MOYENNE_PATTERNS):
        return {'route': 'sql', 'intent': 'moyenne', 'params': {}}

    # Intent 2 — Statut financier
    if _matches(question, _STATUT_PATTERNS):
        return {'route': 'sql', 'intent': 'statut_financier', 'params': {}}

    # Intent 3 — Classement (AVANT filière)
    if _matches(question, _CLASSEMENT_PATTERNS):
        return {'route': 'sql', 'intent': 'classement', 'params': {}}

    # Intent 4 — Filière
    if _matches(question, _FILIERE_PATTERNS):
        return {'route': 'sql', 'intent': 'filiere', 'params': {}}

    # Intent 5 — Année
    if _matches(question, _ANNEE_PATTERNS):
        return {'route': 'sql', 'intent': 'annee', 'params': {}}

    # Intent 6a — Professeur sans matière
    if _matches(question, _PROF_SANS_MATIERE_PATTERNS):
        return {'route': 'sql', 'intent': 'professeur_sans_matiere', 'params': {}}

    # Intent 6b — Professeur avec matière
    if _matches(question, _PROF_PATTERNS):
        matiere = _extract_matiere(question)
        params = {'matiere': matiere} if matiere else {}
        return {'route': 'sql', 'intent': 'professeur_matiere', 'params': params}

    # Défaut → RAG
    return {'route': 'rag', 'intent': None, 'params': {}}