# AppCNV
![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](http://www.repostatus.org/badges/latest/active.svg) 
![Work on Linux System](https://img.shields.io/badge/Linux-OK-ligthgreen) ![Doesnt Work on Windows System](https://img.shields.io/badge/Windows-OK-ligthgreen) ![](https://img.shields.io/badge/MacOS-not_tested-lightgrey)

## Description du projet

Le but de ce projet est de fournir aux biologistes une application permettant de traiter les fichiers issus du pipeline d'analyse de l'outil [*control-freec*](https://github.com/BoevaLab/FREEC). L'application permet, d'un coté, d'utiliser une méthode brute et basique de recherche de segments en se basant sur les fichiers de ratios issus de *control-freec* et de l'autre d'uliser les fichiers de prédictions de CNVs pour générer les Copy Numbers Profiles normalisés et bruts. Cette dernière méthode génère un fichier compilant les CNVs significatifs (p-value $\leqslant$ 0.05) et passant un critère de nombre de Copy Number Alterations.

Les deux méthodes permettent de générer un fichier contenant les statistiques pour chaque chromosomes pour chaque échantillons soumis.

Elles permettent également d'annoter les segments les noms des gènes chevauchant la variation grâce à un fichier d'annotation du génome humain (GENCODE Human - Release 19 (GRCh37.p13))

Le fichier d'annotation du génome humain est filtré pour ne garder que les gènes connus codant pour des protéines. Cela permet de réduire sa taille et donc d'accélérer le processus.

## Installation

Télécharger l'archive ```AppCNV_<windows10 oo linux>.<zip ou tar.xz>``` et décompresser la.
Ajouter un raccourcis sur votre bureau pointant vers le fichier exécutable dans ```AppCNV_<windows10 ou linux>/dist```.
Ou cliquer simplement sur le fichier ```AppCNV_<windows10 ou linux>/dist/AppCNV(.exe)```

## Building from source

Pour cela vous avez besoin d'installer l'environnement Python et [pyinstaller](https://pyinstaller.org/en/stable/).

1. Cloner le répertoire :
```
git clone https://github.com/RomainLevergeois/AppCNV.git
```

2. Vérifier le fonctionnement du code source (packages manquants par exemple) en lançant l'application :
```
# Windows
cd AppCNV/scripts/
python interface.py

# Linux
cd AppCNV/scripts/
python3 interface.py
```

3. Lancer la compilation
```
pyinstaller --onefile -w -n AppCNV --hidden-import matplotlib.backends.backend_svg interface.py
```
Vous pouvez utiliser ```-c``` au lieu de ```-w``` pour ouvrir une console avec l'exécutable.

4. Déplacer les dossiers nécessaires :
```
# Linux
cd AppCNV/
mv img/ scripts/
mv param_data/ scripts/
```

## Perspectives

De nombreuses améliorations sont en cours :
- Ajout d'un autre type d'entrée avec une sélection multiple des dossiers
- Précision des modules Python utilisés lors de la compilation afin de réduire la taille des fichiers exécutables
- Ajout d'une icône
- Parallélisation du traitement des fichiers (pour l'instant un par un)
- Permettre l'enregistrement des segments normalisés pour chaque échantillons (.seg)
- Améliorations de la lisibilité et optimisation du code source