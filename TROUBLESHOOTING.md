# 🚨 TROUBLESHOOTING & COMMON ISSUES

**Document collaboratif** pour éviter de retomber dans les pièges futurs.  
Mis à jour par : SaddemJaber  
Dernière mise à jour : 28 juin 2026

---

## 🎯 Index des Problèmes

1. [PowerShell Git Command Not Found](#problem-1--powershell-git-command-not-found)
2. [Pip.exe Access Denied / Execution Policy](#problem-2--pipexe-access-denied)
3. [Git Remote Repository Not Found](#problem-3--git-remote-repository-not-found)
4. [Terminal PATH Not Updated](#problem-4--terminal-path-not-updated)
5. [Python venv Activation](#problem-5--python-venv-activation-issues)

---

## Problem 1 — PowerShell Git Command Not Found

### 🔴 Symptôme
```
PS C:\...> git push -u origin main
git : Le terme «git» n'est pas reconnu comme nom d'applet de commande...
CommandNotFoundExceptionFul...
```

### ❓ Cause
- Git est installé mais **pas dans le PATH** du terminal PowerShell
- Ou Git n'est pas installé du tout
- Ou PowerShell a ouvert **avant** que le PATH soit mis à jour

### ✅ Solution 1 : Utiliser le chemin absolu (Immédiat)
```powershell
$gitExe = 'C:\Users\SaddemJABER\AppData\Local\Programs\Git\cmd\git.exe'
& $gitExe push -u origin main
```

**Pourquoi ça marche ?**
- On dit explicitement à PowerShell "l'exécutable git est ICI"
- Aucune dépendance au PATH

### ✅ Solution 2 : Créer un alias PowerShell permanent (Recommandé)

**Fichier à créer :**
```
C:\Users\SaddemJABER\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
```

**Contenu :**
```powershell
# Git Alias
Set-Alias -Name git -Value 'C:\Users\SaddemJABER\AppData\Local\Programs\Git\cmd\git.exe' -Scope CurrentUser -Force
```

**Ensuite :**
- Ferme tous les terminaux PowerShell
- Ouvre un nouveau terminal
- `git` fonctionne maintenant partout ! ✅

**Pourquoi c'est mieux ?**
- `git` se charge automatiquement à chaque session
- Pas besoin de chemins absolus
- Plus simple et professionnel

### ✅ Solution 3 : Ajouter Git au PATH Windows (Permanent)
```powershell
$gitDir = 'C:\Users\SaddemJABER\AppData\Local\Programs\Git\cmd'
$oldPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($oldPath -notlike "*Git\cmd*") {
    [Environment]::SetEnvironmentVariable('Path', ($oldPath + ';' + $gitDir), 'User')
}
```

**Puis :**
- Redémarrer l'ordinateur (ou ouvrir un nouveau terminal)
- `git` est reconnu partout

---

## Problem 2 — Pip.exe Access Denied / Execution Policy

### 🔴 Symptôme
```
& 'C:\...\pip.exe' install flask
Le programme «pip.exe» n'a pu s'exécuter: Accès refusé
```

### ❓ Cause
- PowerShell a une **Restricted Execution Policy**
- Elle bloque l'exécution d'exécutables non signés

### ✅ Solution : Utiliser `python -m pip` au lieu de `pip.exe`

**❌ Ne pas faire :**
```powershell
pip install flask
```

**✅ À faire :**
```powershell
python -m pip install flask
# Ou depuis le venv :
.\venv\Scripts\python.exe -m pip install flask
```

**Pourquoi ça marche ?**
- On passe par `python.exe` (qui est approuvé)
- Python lance le module pip en interne
- Aucune restriction d'exécution

**Alternative : Checker l'Execution Policy**
```powershell
Get-ExecutionPolicy
# Si "Restricted", tu pourrais faire :
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Problem 3 — Git Remote Repository Not Found

### 🔴 Symptôme
```
git push -u origin main
fatal: repository 'https://github.com/.../sesamesmart-agent.git' not found
```

### ❓ Cause
- Git a une adresse GitHub correcte
- MAIS le dépôt GitHub n'existe pas encore !
- Le dépôt local est prêt, juste pas le dépôt distant

### ✅ Solution : Créer le dépôt sur GitHub

1. Va sur https://github.com/new
2. Entre le nom : `sesamesmart-agent`
3. Clique "Create repository"
4. Puis :
```powershell
git push -u origin main
```

**Explication :**
- Git ne peut pas pousser vers nulle part
- Il faut que le "endroit distant" existe d'abord

---

## Problem 4 — Terminal PATH Not Updated

### 🔴 Symptôme
```
# Je mets à jour le PATH Windows
[Environment]::SetEnvironmentVariable('Path', ...)

# Mais dans le même terminal :
git --version
git : Le terme «git» n'est pas reconnu...
```

### ❓ Cause
- Les variables d'environnement sont mises à jour au niveau Windows
- MAIS le terminal PowerShell **ouvert avant** ne les recharge pas
- Il garde l'ancienne valeur du PATH en mémoire

### ✅ Solution : Ouvrir un nouveau terminal

- Ferme le terminal actuel
- Ouvre un nouveau PowerShell
- Les variables d'environnement sont rechargées ✅

**Alternative (dans le même terminal) :**
```powershell
# Recharger le PATH manuellement
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

git --version
# Fonctionne maintenant !
```

---

## Problem 5 — Python venv Activation Issues

### 🔴 Symptôme
```
.\venv\Scripts\activate
# Rien ne se passe, pas de (venv) au début du terminal
```

### ❓ Cause
- L'activation fonctionne, mais PowerShell peut avoir une policy restrictive
- Ou le script `activate` n'a pas la bonne permission

### ✅ Solution 1 : Vérifier l'activation (simple)
```powershell
python.exe -c "import sys; print(sys.prefix)"
# Si affiche le chemin vers venv/ → c'est activé ✅
```

### ✅ Solution 2 : Utiliser le venv sans l'activer
```powershell
# Au lieu de l'activer, utilise directement :
.\venv\Scripts\python.exe -c "import flask; print('ok')"
.\venv\Scripts\pip.exe install flask
```

### ✅ Solution 3 : Forcer l'activation PowerShell
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
# Maintenant (venv) devrait apparaître
```

---

## 🛠️ Quick Reference — Les Commandes "Qui Marchent Toujours"

Si tu es bloqué et que tu n'es pas sûr, utilise **TOUJOURS** ces formes :

### Git (depuis le projet)
```powershell
$git = 'C:\Users\SaddemJABER\AppData\Local\Programs\Git\cmd\git.exe'
& $git status
& $git push -u origin main
& $git log --oneline
```

### Python pip
```powershell
python -m pip install package_name
# Ou depuis venv :
.\venv\Scripts\python.exe -m pip install package_name
```

### Python venv
```powershell
python -m venv venv
.\venv\Scripts\python.exe -c "import sys; print('ok')"
.\venv\Scripts\python.exe script.py
```

---

## 📋 Checklist : Avant de Commencer Chaque Session

- [ ] Ouvrir un **nouveau** terminal PowerShell
- [ ] Vérifier que `git` est reconnu : `git --version`
- [ ] Si non → utiliser : `'C:\Users\SaddemJABER\AppData\Local\Programs\Git\cmd\git.exe' --version`
- [ ] Vérifier le venv : `python -c "import sys; print(sys.prefix)"`
- [ ] Si besoin, installer deps : `python -m pip install -r requirements.txt`

---

## 🎓 Leçons Apprises (À Retenir)

| Leçon | Application |
|-------|------------|
| **PATH de PowerShell ≠ PATH Windows** | Redémarrer le terminal après un changement |
| **Chemins absolus = fiable** | Quand on n'est pas sûr, utiliser le chemin complet |
| **Les aliases c'est utile** | Créer un profile.ps1 pour les commandes fréquentes |
| **python -m > appels directs** | `python -m pip` > `pip` (plus compatible) |
| **Le dépôt distant doit exister** | Créer sur GitHub AVANT de pousser |
| **venv ≠ global Python** | Les deux sont différents, utiliser le bon |

---

## 🚀 Si tu rencontres un NOUVEAU problème

1. **Documente-le ici** (ce fichier)
2. **Ajoute la solution** qu'on a trouvée
3. **Fais un commit** : `git commit -m "Add troubleshooting: [problem name]"`
4. **On n'y reviendra plus jamais !**

---

**Dernière mise à jour :** 28 juin 2026  
**Créé par :** SaddemJaber + GitHub Copilot  
**Raison :** "Je n'aime pas retomber dans les erreurs vécues déjà" ❤️

---

## 📞 Questions Fréquentes (FAQ)

**Q: Pourquoi git n'est jamais reconnu ?**
A: PowerShell ne cherche pas dans les dossiers AppData par défaut. Solution : alias PowerShell ou PATH.

**Q: J'ai changé le PATH, pourquoi ça ne marche pas ?**
A: Le terminal ouvert avant le changement n'a pas reloadé. Ouvre un nouveau terminal.

**Q: Comment je sais que mon venv est actif ?**
A: Regarde le début du terminal. Si tu vois `(venv)`, c'est bon. Sinon : `python -c "import sys; print(sys.prefix)"`

**Q: Je peux développer directement sans venv ?**
A: Techniquement oui, mais NON. Le venv c'est pour que le jury puisse reproduire exactement. Sans, c'est du code non-livrable.

**Q: Je peux utiliser Git Bash au lieu de PowerShell ?**
A: Oui, Git Bash a git natif. Mais PowerShell c'est plus moderne.
