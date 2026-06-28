import json
import random
import unicodedata
from pathlib import Path

random.seed(42)

OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)


def normalize_name(name: str) -> str:
    """Retire les accents et met en minuscules.
    Pourquoi : un email avec accents casse les requêtes SQL silencieusement."""
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_str = nfkd.encode("ASCII", "ignore").decode("ASCII")
    return ascii_str.lower().replace(" ", ".")


def generate_moyenne() -> float:
    """Distribution normale centrée 12.5, écart-type 2.5, bornée [0, 20].
    Pourquoi pas random.uniform : une distribution plate est irréaliste."""
    while True:
        m = random.gauss(12.5, 2.5)
        if 0 <= m <= 20:
            return round(round(m * 4) / 4, 2)


def generate_statut(moyenne: float) -> str:
    """Statut financier corrélé à la moyenne.
    Pourquoi corrélé : un étudiant en échec a plus de risques de blocage scolarité."""
    if moyenne < 10:
        return random.choices(["BLOQUE", "A_JOUR"], weights=[0.4, 0.6])[0]
    else:
        return random.choices(["BLOQUE", "A_JOUR"], weights=[0.1, 0.9])[0]


PRENOMS = [
    "Ahmed", "Mohamed", "Yassine", "Hamza", "Karim",
    "Ahmed", "Sara", "Fatima", "Nadia", "Zineb",
    "Omar", "Bilal", "Anas", "Ilyas", "Reda",
    "Mariam", "Hajar", "Dounia", "Salma", "Soufiane"
]

NOMS = [
    "Bennani", "El Idrissi", "Tazi", "Chraibi", "Alami",
    "Fassi", "Berrada", "Kettani", "Sekkat", "Lahlou",
    "Benali", "Ouali", "Mansouri", "Zouhair", "Hilal",
    "Cherkaoui", "Benkiran", "El Amrani", "Saidi", "Naciri"
]

FILIERES = ["FTA", "ING", "MANAGEMENT"]
ANNEES = [1, 2, 3]


def generate_etudiants(n: int = 20) -> list:
    etudiants = []
    for i in range(n):
        prenom = PRENOMS[i]
        nom = NOMS[i]
        filiere = random.choice(FILIERES)
        annee = random.choice(ANNEES)
        moyenne = generate_moyenne()
        etudiant = {
            "id": f"ETU{str(i+1).zfill(3)}",
            "nom": nom,
            "prenom": prenom,
            "filiere": filiere,
            "annee": annee,
            "email": f"{normalize_name(prenom)}.{normalize_name(nom)}@etu.sesame.ma",
            "moyenne_generale": moyenne,
            "statut_financier": generate_statut(moyenne)
        }
        etudiants.append(etudiant)
    return etudiants


MATIERES_PAR_FILIERE = {
    "FTA": ["Réseaux & Télécoms", "Administration Systèmes", "Sécurité Informatique"],
    "ING": ["Mathématiques Appliquées", "Algorithmique", "Bases de données"],
    "MANAGEMENT": ["Gestion de Projet", "Marketing Digital", "Finance d'Entreprise"]
}

NOMS_PROFS = [
    ("El Mansouri", "Khalid"), ("Bensouda", "Layla"), ("Rifai", "Hassan"),
    ("Ouazzani", "Nadia"), ("Tahiri", "Youssef"), ("Bouzid", "Amina"),
    ("Hajji", "Rachid"), ("Benkirane", "Samira")
]


def generate_professeurs() -> list:
    profs = []
    filieres = list(MATIERES_PAR_FILIERE.keys())
    for i, (nom, prenom) in enumerate(NOMS_PROFS):
        filiere = filieres[i % 3]
        matieres = random.sample(MATIERES_PAR_FILIERE[filiere], k=1)
        prof = {
            "id": f"PROF{str(i+1).zfill(3)}",
            "nom_complet": f"{prenom} {nom}",
            "departement": filiere,
            "matieres_enseignees": matieres,
            "disponibilite": random.choice(["Lundi-Mercredi", "Mardi-Jeudi", "Sur RDV"]),
            "bio_prof": f"Enseignant en {matieres[0]} au département {filiere}.",
            "email": f"{normalize_name(prenom)}.{normalize_name(nom)}@sesame.ma"
        }
        profs.append(prof)
    return profs


def generate_documents_metadata() -> list:
    return [
        {
            "id": "DOC001",
            "titre": "Note de service — Gestion et validation des absences sur KONOSYS",
            "type": "note",
            "source": "Note de Service - Gestion et validation des absences étudiantes sur KONOSYS (4).pdf",
            "filiere": None,
            "access_level": "etudiant",
            "rag_readiness": "excellent",
            "rag_suitable": True,
            "preprocessing_needed": False,
            "preprocessing_notes": "",
            "test_case": {
                "question": "Comment contester une absence sur KONOSYS ?",
                "expected_behavior": "answer_with_source",
                "source_doc_id": "DOC001"
            }
        },
        {
            "id": "DOC002",
            "titre": "Règlement Intérieur Département FTA (RI-SCO-02)",
            "type": "reglement",
            "source": "RI-SCO-02 Reglement Interieur Département FTA.pdf",
            "filiere": "FTA",
            "access_level": "etudiant",
            "rag_readiness": "good",
            "rag_suitable": True,
            "preprocessing_needed": True,
            "preprocessing_notes": "Nettoyer les lignes de pagination isolées entre les articles",
            "test_case": {
                "question": "Quelles sont les règles de comportement en salle de cours ?",
                "expected_behavior": "answer_with_source",
                "source_doc_id": "DOC002"
            }
        },
        {
            "id": "DOC003",
            "titre": "Charte de l'étudiant Sesame",
            "type": "charte",
            "source": "CHARTE DE L'ÉTUDIANT SESAME.pptx.pdf",
            "filiere": None,
            "access_level": "etudiant",
            "rag_readiness": "moyenne",
            "rag_suitable": True,
            "preprocessing_needed": True,
            "preprocessing_notes": "Retirer toutes les balises [Visual Elements] et [Image: ...] — bruit PPT",
            "test_case": {
                "question": "Quelles sont les règles pendant un examen ?",
                "expected_behavior": "partial_answer_degraded",
                "source_doc_id": "DOC003"
            }
        },
        {
            "id": "DOC004",
            "titre": "Email — Processus de réinscription",
            "type": "email",
            "source": "Messagerie SESAME - Clarification concernant le processus de réinscription.pdf",
            "filiere": None,
            "access_level": "etudiant",
            "rag_readiness": "faible",
            "rag_suitable": True,
            "preprocessing_needed": True,
            "preprocessing_notes": "Extraire uniquement le corps de l'email — retirer From/To/Date, URLs, signatures",
            "test_case": {
                "question": "Comment fonctionne le processus de réinscription ?",
                "expected_behavior": "answer_with_source",
                "source_doc_id": "DOC004"
            }
        },
        {
            "id": "DOC005",
            "titre": "Email — Validation attestation de présence et diplôme",
            "type": "email",
            "source": "Messagerie SESAME - Informations importantes – Validation de l'attestation de présence et du diplôme.pdf",
            "filiere": None,
            "access_level": "etudiant",
            "rag_readiness": "faible",
            "rag_suitable": True,
            "preprocessing_needed": True,
            "preprocessing_notes": "Extraire le corps utile — contient du texte arabe, retirer entêtes et signatures",
            "test_case": {
                "question": "Comment obtenir une attestation de présence ?",
                "expected_behavior": "answer_with_source",
                "source_doc_id": "DOC005"
            }
        }
    ]


def main():
    print("Génération des données mock SesameSmart...")

    etudiants = generate_etudiants(20)
    with open(OUTPUT_DIR / "etudiants.json", "w", encoding="utf-8") as f:
        json.dump(etudiants, f, ensure_ascii=False, indent=2)
    bloques = sum(1 for e in etudiants if e["statut_financier"] == "BLOQUE")
    print(f"✓ {len(etudiants)} étudiants générés")
    print(f"  → {bloques} BLOQUÉ(s) / {len(etudiants) - bloques} À JOUR")

    profs = generate_professeurs()
    with open(OUTPUT_DIR / "professeurs.json", "w", encoding="utf-8") as f:
        json.dump(profs, f, ensure_ascii=False, indent=2)
    print(f"✓ {len(profs)} professeurs générés")

    docs = generate_documents_metadata()
    with open(OUTPUT_DIR / "documents_metadata.json", "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    print(f"✓ {len(docs)} documents référencés")

    print("\nFichiers créés dans data/")
    print("  - data/etudiants.json")
    print("  - data/professeurs.json")
    print("  - data/documents_metadata.json")


if __name__ == "__main__":
    main()
