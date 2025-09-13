# Maestria Web Application

## Description

Cette application web a été développée dans le cadre du projet **MAESTRIA**.  
Elle permet de charger des fichiers CSV/XLSX, de calculer différents scores et de générer des graphiques pour chaque patient.

Le backend est construit en **Flask (Python)** et le frontend en **HTML/CSS/JavaScript**.  
Les graphiques sont générés avec **Plotly** et sauvegardés en PNG.

---

## Fonctionnalités principales

- **Upload de données** : chargement de fichiers CSV ou Excel, avec orientation en lignes ou colonnes.
- **Fichier par défaut** : possibilité d’utiliser un CSV par défaut inclus dans le projet.
- **Calcul de scores** : 
  - ECG
  - Clinique
  - Métabolites
  - Score combiné
- **Formulaires manuels** pour saisir directement les valeurs des variables.
- **Visualisation** : génération de graphiques au format PNG affichés dans le navigateur.
- **Téléchargement** : chaque graphique peut être téléchargé individuellement.
- **Nettoyage automatique** des fichiers uploadés après un délai.

---

## Structure du projet

```
maestria-app/
│
├── app.py                # Point d’entrée Flask, définition des routes
├── functions.py          # Fonctions utilitaires (lecture CSV, génération de graphiques, traitement des données)
├── score.py              # Fonctions de calcul des différents scores
│
├── static/               # Contient les ressources statiques
│   ├── styles.css        # Feuille de style principale
│   ├── scripts.js        # Scripts JavaScript
│   ├── default.csv       # Exemple de fichier CSV
│   └── ...               # Images, logos, PDF
│
├── templates/            # Templates HTML rendus par Flask
│   ├── maestria.html     # Page d’accueil du projet
│   ├── home.html         # Menu principal (choix des modèles)
│   ├── E_strain.html     # Upload CSV + formulaire ECG/Clinique/Métabolites
│   ├── exemple2.html     # Formulaire AF progression
│   ├── exemple3.html     
│   ├── data_formats.html # Exemples de formats CSV
│   ├── plot.html         # Résultats après upload CSV
│   └── display_graph.html# Résultats après saisie manuelle
│
├── uploads/              # Dossier temporaire pour les fichiers uploadés
└── README.md             # Documentation
```

---

## Routes Flask principales

- `/` : page d’accueil (`maestria.html`)
- `/home` : menu principal
- `/index` : formulaire et upload pour le score ECG/Clinique/Métabolites
- `/exemple2` : formulaire AF Progression
- `/upload` : upload CSV/XLSX et génération des graphiques
- `/submit-answers` : calcul des scores depuis le formulaire ECG/Clinique/Métabolites
- `/submit-answers-af` : calcul du score AF depuis le formulaire AF progression
- `/display-graph` : affichage des graphiques générés
- `/data_formats` : exemples de formats CSV
- `/error` : page d’erreur

---

## Installation

### Prérequis

- Python 3.8+
- pip (gestionnaire de paquets)
- virtualenv (fortement recommandé)

### Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### Installer les dépendances

Installer les dépendances avec  :

```bash
pip install -r requirements.txt
```

---

## Lancement de l’application

```bash
python app.py
```

Par défaut, l’application sera accessible sur :

```
http://0.0.0.0:5000
```

---

## Organisation du code

- `app.py`  
  Contient les routes Flask, la logique d’upload, de nettoyage des sessions et d’intégration avec les fonctions utilitaires.
- `functions.py` 
  - `read_csv_with_encoding` : lecture des CSV (auto-détection encodage/délimiteur).
  - `generate_score_plot` : génération de graphiques avec Plotly.
  - `process_data_1` : traitement des fichiers CSV/XLSX et calcul des scores.
- `score.py`  
  Définit les fonctions de calcul des scores : 
  - `score_ECG`
  - `score_Clinical`
  - `score_Metabolites`
  - `score_AF`
- **Templates HTML**  
  Utilisent Jinja2 pour afficher dynamiquement les graphiques et formulaires.
- **Static files** 
  - `styles.css` : mise en page générale (sidebar, formulaires, boutons, graphes).
  - `scripts.js` : gestion de l’UI (activation des boutons, menu, upload).

---

## Points techniques importants

- Les fichiers uploadés sont stockés dans `uploads/<session_id>/`.
- Les graphiques sont enregistrés dans `static/plots1` et `static/plots2`.
- Protection par `session_id` pour éviter les conflits multi-utilisateurs.