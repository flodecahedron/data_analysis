# Projet d'analyse de données

Ce projet permet de traiter automatiquement les données issues 
d'un fichier de résultats en prenant en compte les conditions expérimentales. 
Il permet de générer des fichiers de synthèse propres et 
de produire des figures les plus lisibles et pertinentes possibles 
afin de permettre une analyse plus aisée des résultats obtenus.

------------------------------------------------------------------------

## Structure du projet

    project/
    │
    ├── backend/
    │   ├── __init__.py
    │   ├── data_processing.py      # Extraction, nettoyage de la base de données et calculs à partir des données
    │   ├── save_fig.py             # Génération des figures comparatives
    │   ├── condition_manager.py    # Mise à jour du fichier JSON contenant les conditions récurrentes
    │   └── well_map.py             # Carte de répartition des solutions sur la plaque
    │
    ├── frontend/
    │    ├── __init__.py
    │    ├── main_app.py            # Point d'entrée du programme
    │    ├── ui_home.py             # Interface d'accueil de l'application
    │    ├── ui_assign.py           # Interface d'assignation des solutions aux différents puits de la plaque expérimentale
    │    └── ui_run_backend.py      # Interface d'import du fichier texte de données et de lancement de l'analyse
    │
    ├── data/               
    │    ├── conditions.json    # Contient les conditions récurrentes
    │    └── PlateResults.txt   # Fichier texte contenant les données brutes à traiter
    │
    ├── results/            # Résultats CSV et figures générés automatiquement (dossier crée portant le nom de l'exp traitée)
    │
    ├── requirements.txt    # Dépendances Python nécessaires
    └── README.md           # Ce fichier

------------------------------------------------------------------------

## Modules principaux

### `backend/data_preprocessing.py`

-   Identifie automatiquement :
    -   Le nom de la plaque
    -   La ligne où commence le tableau de données

### `backend/data_processing.py`

-   Nettoie et harmonise les colonnes
-   Détecte automatiquement les colonnes **Area** et **Time** même si leur nom change
-   Génère :
    -   `results_sorted.csv`
    -   `results_plot.csv`
-   Produit :
    -   Time_h
    -   Area_t0
    -   Closure (%)

### `backend/save_fig.py`

-   Figures organisées par groupe de condition
-   Groupes de contrôles visibles dans toutes les figures
-   Gradient de couleur basé sur la concentration

### `frontend/`

-   Interface Tkinter structurée en fenêtres séparées
-   Lecture/sauvegarde du wellmap
-   Visualisation de plaque avec couleurs condition + surlignage des
    contrôles

------------------------------------------------------------------------

## Installation des dépendances

Installer les packages nécessaires :

    pip install -r requirements.txt

------------------------------------------------------------------------

## Lancer le programme

Depuis la racine du projet, exécuter :

    python -m frontend.main_app

L'interface permet ensuite de:

1. Visualiser la plaque et charger une répartition existante ou en créer une nouvelle en fonction de l'expérience
2. Importer un fichier TXT brut de données à analyser
3. Lancer le traitement et générer les figures

------------------------------------------------------------------------

## Données d'entrée

-   Fichier TXT brut contenant les données à analyser de format suivant:

[...]
Plate Name	'Plate_name'
[...]
[Data]
[...]

------------------------------------------------------------------------

## Résultats produits

1.  **CSV triés et nettoyés**
    -   Fermeture moyenne
    -   STD
    -   Par condition et par heure
2.  **Figures**
    -   Ligne par condition
    -   Gradient de couleur par concentration
    -   Contrôles visibles et différenciés dans chaque figure

------------------------------------------------------------------------