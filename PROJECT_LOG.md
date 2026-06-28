# SesameSmart — Journal de Projet (Project Log)

**Date de création :** 28 juin 2026  
**Auteur :** SaddemJaber (jabersaddem@gmail.com)  
**Status :** En cours (GitHub push en attente)

---

## 📋 Résumé Exécutif

**Objectif :** Créer un chatbot académique hybride (SQL + RAG) pour Sesame.

**Stack technique :**
- Backend : Flask + Supabase (pgvector)
- IA : Google Gemini (embeddings + génération)
- Versionning : Git + GitHub

**Status actuel :** 
- ✅ Environnement local prêt
- ✅ Dépôt Git initialisé
- ⏳ Dépôt GitHub en attente de création et push

---

## 📅 Chronologie Complète des Actions

### **Étape 1.1 — Créer le dossier et structure de base**

**Commandes exécutées :**
```bash
mkdir sesamesmart-agent
cd sesamesmart-agent
```

**Résultat :**
- ✅ Dossier créé à : `C:\Users\SaddemJABER\Desktop\PFA\sesamesmart-agent`
- ✅ Navigation effective dans le dossier

**Explication :**
- `mkdir` = créer un dossier
- `cd` = naviguer dans le dossier
- C'est le point de départ pour isoler le projet

---

### **Étape 1.2 — Créer l'environnement virtuel Python**

**Commandes exécutées :**
```bash
python -m venv venv
```

**Résultat :**
- ✅ Dossier `venv/` créé (~300MB)
- ✅ Python 3.12.5 isolé dans le projet

**Explication :**
- `python -m venv` = utiliser le module venv de Python
- `venv` = créer un environnement nommé "venv"
- **Pourquoi ?** Chaque projet a ses propres dépendances isolées du système

**Activation :**
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```
→ Fait apparaître `(venv)` au début du terminal

---

### **Étape 1.3 — Créer la structure de dossiers**

**Commandes exécutées :**
```bash
mkdir app data scripts tests
```

**Résultat :**
```
sesamesmart-agent/
├── app/        ← Code Flask (API, routes)
├── data/       ← Données et fichiers
├── scripts/    ← Scripts utilitaires (generate_mock_data.py)
├── tests/      ← Tests unitaires
└── venv/       ← Environnement Python
```

**Explication :**
- Chaque dossier a une responsabilité claire
- **Règle d'ingénierie :** Organisation = maintenabilité

---

### **Étape 1.4 — Créer `requirements.txt`**

**Fichier créé :**
```txt
flask
supabase
google-generativeai
python-dotenv
```

**Pourquoi ces 4 et aucun autre ?**
1. `flask` → serveur web
2. `supabase` → base de données + pgvector
3. `google-generativeai` → API Gemini (embeddings + génération)
4. `python-dotenv` → charger les variables `.env`

**Pas de :** torch, sentence-transformers, langchain, faiss, etc.
→ Décision : zéro embeddings locaux, tout via Gemini API

**Installation :**
```bash
pip install -r requirements.txt
```

**Résultat :**
- ✅ Flask 3.1.3 installé
- ✅ Supabase 2.31.0 installé
- ✅ google-generativeai 0.8.6 installé
- ✅ python-dotenv 1.2.2 installé

**Vérification :**
```bash
python -c "import flask, supabase; print('ok')"
→ ok ✅
```

---

### **Étape 1.5 — Créer `.gitignore`**

**Fichier créé :**
```gitignore
venv/
__pycache__/
*.pyc
.env
```

**Explication ligne par ligne :**
- `venv/` → Ne PAS tracer le dossier virtuel (trop volumineux)
- `__pycache__/` → Fichiers Python compilés (inutiles)
- `*.pyc` → Fichiers compilés (même chose)
- `.env` → **CRITIQUE** — Bloque tes clés Gemini/Supabase de partir sur GitHub

**Risque si absent :** N'importe qui peut utiliser tes clés API et faire des appels à tes frais.

---

### **Étape 1.6 — Créer `.env` et `.env.example`**

**Fichier `.env` (privé — jamais committé) :**
```env
SUPABASE_URL=
SUPABASE_KEY=
GEMINI_API_KEY=
```

**Fichier `.env.example` (public — toujours committé) :**
```env
SUPABASE_URL=
SUPABASE_KEY=
GEMINI_API_KEY=
```

**Explication :**
- `.env` = tes vraies clés (ignoré par git)
- `.env.example` = template vide (documenté publiquement)
- Collègues/jury voient "quelles variables existent" sans tes secrets

---

### **Étape 1.7 — Créer `README.md`**

**Fichier créé :**
```markdown
# SesameSmart — Chatbot académique hybride (SQL + RAG)

POC d'un assistant étudiant pour Sesame.
- Backend : Flask + Supabase (pgvector)
- IA : Google Gemini (text-embedding-004, gemini-1.5-flash)
- Architecture : routeur SQL / RAG + abstention stricte
```

**Raison :** Documentation du projet pour le jury et futurs collègues

---

### **Étape 1.8 — Initialiser Git et premier commit**

**Commandes exécutées :**
```bash
git init
git add .
git commit -m "Initial setup: structure projet, venv, dependencies, env template"
```

**Résultat :**
```
[master 4ce63e5] Initial setup...
 4 files changed, 17 insertions(+)
 create mode 100644 .env.example
 create mode 100644 .gitignore
 create mode 100644 README.md
 create mode 100644 requirements.txt
```

**Explication :**
- `git init` → créer le dossier `.git/` (historique local)
- `git add .` → ajouter tous les fichiers (sauf ceux ignorés par `.gitignore`)
- `git commit -m "..."` → enregistrer cet état avec un message
- **4 files tracked** → seuls les fichiers essentiels, pas `venv/` ni `.env`

---

### **Étape 1.9 — Configurer Git Identity**

**Commandes exécutées :**
```bash
git config --global user.name "SaddemJaber"
git config --global user.email "jabersaddem@gmail.com"
```

**Résultat :**
- ✅ Nom d'utilisateur : SaddemJaber
- ✅ Email : jabersaddem@gmail.com

**Puis :** Réécriture du commit initial avec la nouvelle identité
```bash
git commit --amend --reset-author --no-edit
```

**Résultat :**
```
[master 4ce63e5] Initial setup...
 (ancien hash : 08397b0 → nouveau hash : 4ce63e5)
```

---

### **Étape 1.10 — Connexion à GitHub (Git Remote)**

**Commandes exécutées :**
```bash
git remote add origin https://github.com/SaddemJaber/sesamesmart-agent.git
git branch -M main
```

**Explication :**
- `git remote add origin ...` → ajouter l'adresse du dépôt GitHub
- `git branch -M main` → renommer `master` en `main` (convention GitHub)

**Résultat :**
- ✅ Dépôt distant associé
- ✅ Branche principale nommée `main`

---

### **Étape 1.11 — Validation des 4 Checks**

**Check 1 : Dépendances installées**
```bash
python -c "import flask, supabase; print('ok')"
→ ok ✅
```

**Check 2 : `.env` ignoré par Git**
```bash
git status
→ .env n'apparaît PAS ✅
```

**Check 3 : `.env.example` committé**
```bash
git log
→ "4 files changed" (contient .env.example) ✅
```

**Check 4 : Au moins 1 commit**
```bash
git log --oneline
→ 4ce63e5 (HEAD -> main) Initial setup... ✅
```

---

## 🚨 Problèmes Rencontrés et Solutions

### **Problème 1 : Terminal PowerShell Restrictif**

**Symptôme :**
```
Impossible d'exécuter pip.exe : Accès refusé
```

**Cause :**
- Politique d'exécution PowerShell = `Restricted`
- Ne pouvait pas lancer `.exe` directement

**Solution appliquée :**
```bash
# Au lieu de : pip install ...
# Utiliser :
python.exe -m pip install ...
```
→ Contourner la restriction en passant par Python

---

### **Problème 2 : Git non trouvé au départ**

**Symptôme :**
```
git : Le terme «git» n'est pas reconnu comme nom d'applet de commande
```

**Cause :**
- Git était installé en "user mode" (AppData)
- Le chemin n'était pas dans le PATH du terminal

**Solution appliquée :**
```bash
# Ajouter Git au PATH utilisateur Windows
$gitDir = 'C:\Users\SaddemJABER\AppData\Local\Programs\Git\cmd'
[Environment]::SetEnvironmentVariable('Path', $oldPath + ';' + $gitDir, 'User')

# Ou utiliser le chemin absolu :
'C:\Users\SaddemJABER\AppData\Local\Programs\Git\cmd\git.exe' status
```
→ Git trouvé via chemin absolu ou PATH mis à jour

---

### **Problème 3 : Git pas reconnu dans les terminaux ouverts avant le PATH update**

**Symptôme :**
```
git : Le terme «git» n'est pas reconnu...
```
(Même après installation et ajout au PATH)

**Cause :**
- PowerShell avait ouvert ses sessions avant la mise à jour du PATH
- Les variables d'environnement mises à jour n'étaient pas chargées

**Solution appliquée :**
- Ouvrir un nouveau terminal PowerShell (qui charge le PATH mis à jour)
- Ou utiliser le chemin absolu dans le terminal existant

---

### **Problème 4 : Dépôt GitHub n'existait pas encore**

**Symptôme :**
```bash
git push -u origin main
→ fatal: repository not found
```

**Cause :**
- On avait configuré Git pour pointer vers `https://github.com/SaddemJaber/sesamesmart-agent.git`
- Mais le dépôt n'existait pas encore sur GitHub

**Solution en cours :**
- Créer le dépôt vide sur GitHub.com
- Puis lancer le push

---

## ✅ État Actuel du Projet

### **Local (100% ✅)**
```
✅ Dossier projet créé
✅ Environnement virtuel Python
✅ Dépendances installées (Flask, Supabase, Gemini, dotenv)
✅ Structure de dossiers (app, data, scripts, tests)
✅ Fichiers essentiels (.gitignore, .env, .env.example, README.md)
✅ Dépôt Git initialisé
✅ Premier commit enregistré
✅ Git identity configurée (SaddemJaber)
✅ Branche main créée
✅ Remote origin associé
```

### **GitHub (⏳ En attente)**
```
⏳ Créer le dépôt vide sur github.com/new
⏳ Pousser le code (git push -u origin main)
⏳ Vérifier la visibilité publique
```

---

## 📝 Prochaines Étapes (À faire après GitHub)

**Tâche 2 — Mock Data :**
- Créer `scripts/generate_mock_data.py`
- Générer des données de test (cours, étudiants, QA pairs)
- Préparer les fixtures pour la base de données

**Tâche 3 — Configuration Supabase :**
- Créer les tables (courses, students, qa_pairs, embeddings)
- Configurer pgvector
- Charger les mock data

**Tâche 4 — API Flask :**
- Créer les routes de base
- Intégrer Gemini API
- Tester les endpoints

---

## 🔧 Commandes de Référence Rapide

**Activer le venv :**
```bash
venv\Scripts\activate
```

**Installer les dépendances :**
```bash
pip install -r requirements.txt
```

**Vérifier le status Git :**
```bash
git status
```

**Faire un commit :**
```bash
git add .
git commit -m "Message descriptif"
```

**Pousser vers GitHub :**
```bash
git push -u origin main
```

**Voir l'historique :**
```bash
git log --oneline
```

---

## 📊 Statistiques du Projet

| Métrique | Valeur |
|----------|--------|
| Commits | 1 |
| Fichiers tracés | 4 |
| Dépendances | 4 |
| Lignes de code | ~15 |
| Status | Local ✅ / GitHub ⏳ |

---

## 🎯 Conclusion de la Tâche 1

**Qu'on a réussi :**
- Mise en place d'un projet professionnel avec venv
- Isolation correcte des secrets et des dépendances
- Versionning Git configuré et fonctionnel
- Identité GitHub associée
- Structure de base solide

**Ce qui reste :**
- Créer le dépôt GitHub
- Pousser le code

**Apprendre de cette Tâche :**
- L'importance du `.gitignore` pour les secrets
- L'isolation via `venv` pour la reproductibilité
- La structure de dossiers pour la maintenabilité
- Git est un outil essentiel pour tout projet

---

**Fin de Tâche 1 ✅**  
**Début Tâche 2 ⏳**  
**Auteur :** SaddemJaber  
**Dernière mise à jour :** 28 juin 2026
