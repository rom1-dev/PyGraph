# PyGraph - V1.0.0 (2026) by [Romain FAGONDE](https://github.com/rom1-dev)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Framework: Tkinter](https://img.shields.io/badge/Framework-Tkinter-orange.svg)](https://docs.python.org/3/library/tkinter.html)

Une application logicielle Python complète, interactive et hautement visuelle conçue pour l'enseignement et l'apprentissage de la **Théorie des Graphes** et des structures de données fondamentales. Développée initialement comme un projet de stage académique, elle sert de support de cours universitaire interactif.

---

## Fonctionnalités Principales

### Édition Interactive et Graphique
* **Multi-structures** : Support complet des graphes *Simples*, *Orientés*, *MultiGraph* et *MultiDiGraph*.
* **Édition à la souris** : Création de nœuds par simple clic, tracé d'arêtes dirigées ou non en glissant-déposant (Drag & Drop) d'un sommet à un autre, et suppression rapide des éléments.
* **Layouts dynamiques** : Repositionnement manuel fluide des sommets ou application instantanée d'algorithmes de disposition automatique (`Spring`, `Circular`, `Random`, `Shell`, `Kamada-Kawai`).
* **Rendu de géométries complexes** : Calcul mathématique automatique de la courbure des flèches pour les arêtes parallèles afin d'éviter tout chevauchement visuel.

### Animations Algorithmiques Pas à Pas
Exécutez et observez le comportement interne des algorithmes fondamentaux de parcours. L'avancement est entièrement contrôlé par l'utilisateur à l'aide de la touche **[Barre Espace]** :
1. **Parcours en Largeur (BFS) Généralisé** : Exploration globale de toutes les composantes connexes du graphe.
2. **Parcours en Largeur (BFS) Simple** : Exploration ciblée démarrant d'un sommet racine spécifique choisi graphiquement.
3. **Parcours en Profondeur (DFS) Généralisé** : Exploration récursive complète générant la forêt de parcours.
4. **Parcours en Profondeur (DFS) Simple** : Exploration récursive ciblée depuis un sommet racine.

### Tableaux de Bord de Suivi Événementiel (Popups)
Chaque algorithme ouvre une fenêtre de contrôle Tkinter dédiée qui affiche en temps réel les structures de données sous-jacentes :
* **Suivi de la File (Queue)** pour le BFS, mettant en évidence la logique **FIFO** (First In, First Out).
* **Suivi de la Pile d'appels (Stack)** pour le DFS, illustrant visuellement les phases d'empilement et le mécanisme de **backtracking** (machine arrière).
* **Variables d'état** : Visualisation en temps réel du sommet en cours, de son voisinage direct et de la liste des sommets visités.
* **Coloration différenciée** : Identification immédiate des nœuds courants (Orange), entièrement traités (Rouge Foncé), des arêtes de l'arbre (Vert) et des arêtes de cycle/revisite (Bleu).

### Interopérabilité et I/O
* Sauvegarde et chargement des graphes personnalisés aux formats standard (`.json`, `.adj`).
* Importation de listes ou matrices d'adjacence textuelles via le presse-papiers.
* **Export de code autonome** : Génération automatique du script Python exécutable nécessaire pour recréer le graphe programmatiquement.

---

## Architecture du Projet

Le code source est entièrement découplé et structuré en modules spécialisés :

1. `main.py` : Point d'entrée de l'application. Initialise l'interface Tkinter, l'arbre des menus globaux, et synchronise l'état de l'application via un dictionnaire d'état centralisé (système Getter/Setter).
2. `graph_functions.py` : Moteur algorithmique. Regroupe les implémentations pures et adaptées du BFS et du DFS pour l'injection visuelle pas à pas.
3. `functions.py` : Contrôleur d'événements et modules I/O. Gère le cycle de vie des clics de souris (`on_press`, `on_release`), les raccourcis clavier, la persistance de la configuration d'aide locale au format JSON, et les fenêtres de chargement.
4. `graph_engine.py` : Module graphique bas niveau. Manipule NetworkX et Matplotlib pour générer les tracés géométriques, associer les identifiants d'objets (`gids`) et rafraîchir le canvas.

---

## Installation & Lancement

### Prérequis
L'environnement requiert **Python 3.8** ou une version supérieure.

### Installation des dépendances
Clonez le dépôt, puis installez les bibliothèques requises à l'aide de `pip` :
```bash
git clone [https://github.com/votre-username/visualisateur-graphes.git](https://github.com/votre-username/visualisateur-graphes.git)
cd visualisateur-graphes
pip install networkx matplotlib numpy pyperclip
```

### Exécution

```bash
python main.py
```

---

## Guide de Prise en Main Rapide

1. **Créer un graphe** : Mettez l'application en mode *Ajouter* (Menu Édition) puis cliquez dans la zone blanche pour ajouter des sommets. Glissez d'un sommet à un autre pour créer une arête.
2. **Lancer un parcours simple** : Accédez au menu `Algorithmes`, puis sélectionnez par exemple `Parcours en largeur`. Validez la boîte de dialogue d'instruction, puis **cliquez sur le sommet du graphe** depuis lequel vous souhaitez démarrer l'exploration.
3. **Animer l'algorithme** : Appuyez sur la **[Barre Espace]** pour avancer d'une étape. Observez simultanément la coloration sur le graphe et l'évolution des structures de données dans la popup de suivi.

---

## Licence

Ce projet est distribué sous les termes de la **Licence MIT**. Consultez le fichier [LICENSE](LICENSE) joint pour obtenir le texte juridique complet.

Copyright © 2026 - Code source libre de droits, modifiable et réutilisable à des fins éducatives ou de développement.