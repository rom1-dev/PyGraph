# -*- coding: utf-8 -*-
# Copyright (c) 2026 Romain "rom1-dev" FAGONDE
# Distributed under the terms of the MIT License.

def largeur(g, i, g_type, col_node, col_edge, waiter, root, popup_widgets):
    """Exécute un parcours en largeur (BFS) sur un graphe avec visualisation pas-à-pas.

    Cette fonction implémente l'algorithme BFS en utilisant une file pour explorer 
    le graphe à partir d'un sommet racine `i`. À chaque étape, elle met à jour 
    l'interface utilisateur via `popup_widgets` et suspend l'exécution via `waiter` 
    pour permettre un suivi visuel interactif. Elle distingue les arêtes de 
    découverte (nouveaux sommets) des arêtes déjà visitées.

    Args:
        g (dict): Liste d'adjacence représentant le graphe.
        i (Hashable): Identifiant du sommet de départ.
        g_type (str): Type du graphe (ex: "MultiDiGraph", "Orienté") influençant 
            la gestion des couleurs des arêtes.
        col_node (callable): Fonction de rappel pour colorer un nœud.
        col_edge (callable): Fonction de rappel pour colorer une arête.
        waiter (callable): Fonction de rappel bloquante attendant une action utilisateur.
        root (tk.Tk): Instance de la fenêtre racine Tkinter.
        popup_widgets (dict): Dictionnaire contenant les `tk.StringVar` de la fenêtre de suivi.

    Returns:
        tuple: Un tuple contenant `(visites, revisites)`, où `visites` est la liste 
            ordonnée des sommets visités et `revisites` la liste des arêtes déjà explorées.
    """
    visites = [i]
    file = [i]
    revisites = []
    
    # Variables pour la popup
    x = i 

    def rafraichir_affichage():
        """Met à jour les labels de la popup avec l'état actuel des files et sommets."""
        if popup_widgets:
            popup_widgets['file_var'].set(f"File : {list(file)}")
            popup_widgets['visites_var'].set(f"Visités : {list(visites)}")
            popup_widgets['sommet_en_cours'].set(f"Sommet en cours : {x}")
            voisinage_x = g[x] if x in g else []
            popup_widgets['voisinage'].set(f"Voisinage : {list(voisinage_x)}")
        root.update()
    
    def color_node(node, color):
        """Applique la couleur au nœud, rafraîchit l'affichage et attend le pas utilisateur."""
        col_node(node, color)
        rafraichir_affichage()
        waiter()

    def color_edge(u, v, color, key=0):
        """Applique la couleur à l'arête, rafraîchit l'affichage et attend le pas utilisateur."""
        col_edge(u, v, color, key=key)
        rafraichir_affichage()
        waiter()

    # Premier rafraîchissement initial
    rafraichir_affichage()

    while file:
        x = file.pop(0)
        print(f"Visite de {x}")
        color_node(x, "#FF5733")  # Colorier le nœud courant en rouge orange
        
        cpt = -1
        if x in g:
            for y in g[x]:
                cpt += 1
                if y not in visites:
                    visites.append(y)
                    file.append(y)
                    print(f"vers {y} ({x}-{y}, {g[x][:cpt].count(y)})")
                    color_edge(x, y, "#FF5733", key=g[x][:cpt].count(y))  # Colorier l'arête de découverte en rouge orange
                else:
                    if g_type in ["MultiDiGraph", "MultiGraph"]:
                        revisites.append((x, y, g[x][:cpt].count(y)))
                    else:
                        revisites.append((x, y))
                        
                    if g_type in ["MultiDiGraph", "Orienté"]:
                        color_edge(x, y, "#0077FF", key=g[x][:cpt].count(y))  # Colorier l'arête en bleu
                    elif x < y:
                        color_edge(x, y, "#0077FF", key=g[x][:cpt].count(y))
                        
        color_node(x, "#FFFECE")  # Colorier le nœud entièrement traité en jaune pâle

    return visites, revisites

def largeurG(g, g_type, col_node, col_edge, waiter, root, popup_widgets):
    """Exécute un parcours en largeur (BFS) complet sur un graphe potentiellement non connexe.

    Cette fonction parcourt l'ensemble des sommets du graphe `g`. Pour chaque composante 
    connexe non encore visitée, elle déclenche un BFS. Elle gère la visualisation 
    interactive en temps réel en mettant à jour les composants Tkinter fournis 
    et en marquant les arêtes de découverte (nouveaux sommets) et les arêtes de 
    revisite (sommets déjà visités).

    Args:
        g (dict): Liste d'adjacence représentant le graphe.
        g_type (str): Type du graphe influençant la gestion des clés d'arêtes.
        col_node (callable): Fonction de rappel pour appliquer une couleur à un nœud.
        col_edge (callable): Fonction de rappel pour appliquer une couleur à une arête.
        waiter (callable): Fonction de rappel bloquante pour la pause pas-à-pas.
        root (tk.Tk): Instance de la fenêtre racine Tkinter.
        popup_widgets (dict): Dictionnaire contenant les variables Tkinter (`StringVar`) 
            pour l'affichage dynamique dans la fenêtre de suivi.

    Returns:
        list: La liste des arêtes rencontrées lors de revisites de sommets déjà explorés.
    """


    def rafraichir_affichage():
        """Met à jour l'état visuel de la fenêtre de suivi avec les variables Tkinter."""
        # Plus besoin d'ax.text et de cnv.draw_idle() pour le texte !
        # On met à jour directement les variables de contrôle Tkinter de la popup
        if popup_widgets:
            popup_widgets['file_var'].set(f"File : {list(file)}")
            popup_widgets['visites_var'].set(f"Visités : {list(visites)}")
            popup_widgets['sommet_en_cours'].set(f"Sommet en cours : {x}")
            voisinage_x = g[x] if x in g else []
            popup_widgets['voisinage'].set(f"Voisinage : {list(voisinage_x)}")
        
        root.update()
    
    def color_node(node, color):
        """Applique la couleur au nœud, rafraîchit l'affichage et attend l'utilisateur."""
        col_node(node, color)
        rafraichir_affichage()  # Mise à jour de l'affichage après changement de couleur
        waiter()  # Pause pour visualiser le changement de couleur
    def color_edge(u, v, color, key=0):
        """Applique la couleur à l'arête, rafraîchit l'affichage et attend l'utilisateur."""
        col_edge(u, v, color, key=key)
        rafraichir_affichage()  # Mise à jour de l'affichage après changement de couleur
        waiter()  # Pause pour visualiser le changement de couleur

    foret=[]
    visites=[]
    revisites = []
    for i in g:
        if i not in visites:
            visite=[]
            visites.append(i)
            visite.append(i)
            file=[i]
            while file:
                x=file[0]
                # visites.append(x)
                print(f"Visite de {x}")
                color_node(x, "#FF5733")  # Colorier le nœud visité en rouge orange
                cpt=-1
                for y in g[x]:
                    cpt+=1
                    if y not in visites:
                        visite.append(y)
                        visites.append(y)
                        file.append(y)
                        print(f"vers {y} ({x}-{y}, {g[x][:cpt].count(y)})")
                        color_edge(x, y, "#FF5733", key=g[x][:cpt].count(y))  # Colorier l'arête en rouge orange
                    else:
                        if g_type in ["MultiDiGraph", "MultiGraph"]:
                            revisites.append((x, y, g[x][:cpt].count(y)))
                            print(f"Revisite de {y} ({x}-{y}, {g[x][:cpt].count(y)})")
                        else:
                            revisites.append((x, y))
                            print(f"Revisite de {y} ({x}-{y})")
                        if g_type in ["MultiDiGraph", "Orienté"]:
                            color_edge(x, y, "#0077FF", key=g[x][:cpt].count(y))  # Colorier l'arête en bleu
                        elif x<y:
                            color_edge(x, y, "#0077FF", key=g[x][:cpt].count(y))  # Colorier l'arête en bleu
                file=file[1:]
                # visites.append(x)
                color_node(x, "#FFFECE")  # Colorier le nœud visité en jaune pâle
            foret.append(visite)
    print(visites)
    return revisites

def profRec(g, i, g_type, visite, ordrevisite, pile_appels, color_node, color_edge, popup_widgets, root, g_raw):
    """Effectue une exploration récursive en profondeur (DFS) d'un graphe.

    Cette fonction est le cœur récursif du parcours en profondeur. Elle gère la 
    visite des sommets, maintient l'état de la pile d'appels pour la visualisation, 
    et délègue la coloration des nœuds et des arêtes aux fonctions de rappel 
    fournies. Elle distingue les arêtes menant à des nœuds non visités (découverte) 
    de celles menant à des nœuds déjà visités (revisite).

    Args:
        g (dict): Liste d'adjacence simplifiée.
        i (Hashable): Sommet courant en cours de traitement.
        g_type (str): Type du graphe (ex: "MultiDiGraph", "Orienté").
        visite (set): Ensemble des sommets déjà visités.
        ordrevisite (list): Liste ordonnée des sommets explorés.
        pile_appels (list): Pile représentant les appels récursifs actifs.
        color_node (callable): Rappel pour colorer un nœud.
        color_edge (callable): Rappel pour colorer une arête.
        popup_widgets (dict): Widgets Tkinter pour mettre à jour l'interface.
        root (tk.Tk): Fenêtre racine pour rafraîchir l'interface (`root.update`).
        g_raw (dict): Liste d'adjacence brute (permettant de gérer les clés multiples 
            pour les multigraphes).
    """
    if i not in visite:
        print("On traite", i, "en première visite")
        visite.add(i)
        ordrevisite.append(i)
        pile_appels.append(i)  # On empile le sommet au début du traitement
        
        # Coloration : Première découverte (Rouge Orange)
        color_node(i, "#FF5733")
        
        cpt = -1
        if i in g_raw:
            for j in g_raw[i]:
                cpt += 1
                if j not in visite:
                    print("Visite de", j)
                    # Coloration : Arête de découverte (Rouge Orange)
                    color_edge(i, j, "#FF5733", key=g_raw[i][:cpt].count(j))
                    
                    # Appel récursif
                    profRec(g, j, g_type, visite, ordrevisite, pile_appels, color_node, color_edge, popup_widgets, root, g_raw)
                else:
                    print("Revisite de", j)
                    key_val = g_raw[i][:cpt].count(j)
                    
                    # Coloration : Arête de revisite (Bleu)
                    if g_type in ["MultiDiGraph", "Orienté"]:
                        color_edge(i, j, "#0077FF", key=key_val)
                    elif i < j:
                        color_edge(i, j, "#0077FF", key=key_val)
                        
        # Fin du traitement du sommet : on le dépile et on le marque comme traité (Jaune pâle)
        pile_appels.pop()
        color_node(i, "#FFFECE")
    else:
        return

def profond(g, i, g_type, col_node, col_edge, waiter, root, popup_widgets):
    """Lance un parcours en profondeur (DFS) depuis un sommet racine.

    Cette fonction initialise les structures nécessaires au suivi de l'algorithme 
    DFS (ensemble des sommets visités, liste d'ordre de visite et pile d'appels 
    récursifs) et définit les fonctions de rappel pour la mise à jour visuelle 
    en temps réel. Elle orchestre l'exécution en appelant `profRec`.

    Args:
        g (dict): Liste d'adjacence du graphe.
        i (Hashable): Identifiant du sommet de départ.
        g_type (str): Type du graphe influençant la gestion des couleurs.
        col_node (callable): Rappel pour colorer un nœud.
        col_edge (callable): Rappel pour colorer une arête.
        waiter (callable): Rappel bloquant pour gérer la progression pas-à-pas.
        root (tk.Tk): Instance de la fenêtre racine Tkinter.
        popup_widgets (dict): Widgets Tkinter contenant les variables de suivi 
            (`pile_var`, `visites_var`).

    Returns:
        list: La liste ordonnée des sommets visités durant le parcours.
    """
    visite = set()
    ordrevisite = []
    pile_appels = []  # Utilisé pour suivre la stack de récursion sur la popup

    def rafraichir_affichage():
        """Met à jour les variables Tkinter de la popup avec l'état de la pile et des visites."""
        if popup_widgets:
            popup_widgets['pile_var'].set(f"Pile (Stack) : {list(pile_appels)}")
            popup_widgets['visites_var'].set(f"Visités : {list(ordrevisite)}")
        root.update()
    
    def color_node(node, color):
        """Applique la couleur au nœud, rafraîchit l'interface et marque une pause."""
        col_node(node, color)
        rafraichir_affichage()
        waiter()

    def color_edge(u, v, color, key=0):
        """Applique la couleur à l'arête, rafraîchit l'interface et marque une pause."""
        col_edge(u, v, color, key=key)
        rafraichir_affichage()
        waiter()

    # Premier rafraîchissement à vide
    rafraichir_affichage()

    # Lancement de la récursion
    profRec(g, i, g_type, visite, ordrevisite, pile_appels, color_node, color_edge, popup_widgets, root, g)
    
    return ordrevisite

def profRecG(g, i, g_type, visite, ordrevisite, pile_appels, color_node, color_edge, popup_widgets, root, g_raw):
    """Effectue une exploration récursive en profondeur (DFS) généralisée.

    Cette fonction récursive explore un sommet `i` et ses descendants. Elle maintient 
    l'état de la pile d'appels pour la visualisation et délègue la mise à jour 
    graphique aux fonctions de rappel fournies. Elle est conçue pour fonctionner 
    au sein d'un parcours complet de graphe, en gérant la distinction entre les 
    nouvelles découvertes et les arêtes de revisite.

    Args:
        g (dict): Liste d'adjacence simplifiée du graphe.
        i (Hashable): Sommet racine de l'exploration actuelle.
        g_type (str): Type du graphe influençant la gestion des clés d'arêtes.
        visite (set): Ensemble mutable des sommets déjà visités.
        ordrevisite (list): Liste cumulative des sommets explorés.
        pile_appels (list): Pile représentant la profondeur de récursion actuelle.
        color_node (callable): Rappel pour colorer un nœud.
        color_edge (callable): Rappel pour colorer une arête.
        popup_widgets (dict): Widgets Tkinter pour la mise à jour de l'interface.
        root (tk.Tk): Fenêtre racine utilisée pour le rafraîchissement.
        g_raw (dict): Liste d'adjacence brute permettant de gérer les multigraphes.
    """
    if i not in visite:
        print("On traite", i, "en première visite")
        visite.add(i)
        ordrevisite.append(i)
        pile_appels.append(i) # On entre dans le sommet, on l'ajoute à la pile
        
        # Coloration en Rouge Orange : première découverte du sommet
        color_node(i, "#FF5733")
        
        cpt = -1
        # On utilise g_raw[i] pour avoir la liste brute des voisins avec doublons (pour le calcul du cpt/multigraphe)
        if i in g_raw:
            for j in g_raw[i]:
                cpt += 1
                if j not in visite:
                    print("Visite de", j)
                    # Coloration en Rouge Orange : arête de découverte
                    color_edge(i, j, "#FF5733", key=g_raw[i][:cpt].count(j))
                    
                    # Appel récursif
                    profRecG(g, j, g_type, visite, ordrevisite, pile_appels, color_node, color_edge, popup_widgets, root, g_raw)
                else:
                    print("Revisite de", j)
                    # Détermination du type d'arête de revisite (Multi ou simple)
                    key_val = g_raw[i][:cpt].count(j)
                    
                    # Coloration en Bleu : arête déjà explorée
                    if g_type in ["MultiDiGraph", "Orienté"]:
                        color_edge(i, j, "#0077FF", key=key_val)
                    elif i < j:
                        color_edge(i, j, "#0077FF", key=key_val)
                        
        # Fin de traitement du sommet : on le dépile et on le colore en jaune pâle
        pile_appels.pop()
        color_node(i, "#FFFECE")
    else:
        return

def profondG(g, g_type, col_node, col_edge, waiter, root, popup_widgets):
    """Exécute un parcours en profondeur (DFS) complet sur toutes les composantes 
    connexes d'un graphe.

    Cette fonction orchestre l'exploration exhaustive du graphe `g`. Elle itère sur 
    chaque sommet non visité pour lancer une exploration récursive (via `profRecG`), 
    permettant de construire une forêt de recherche (ensemble d'arbres DFS). Elle 
    assure la mise à jour dynamique de l'interface utilisateur tout au long du 
    processus grâce aux fonctions de rappel fournies.

    Args:
        g (dict): Liste d'adjacence du graphe.
        g_type (str): Type du graphe influençant la logique des arêtes.
        col_node (callable): Rappel pour colorer un nœud.
        col_edge (callable): Rappel pour colorer une arête.
        waiter (callable): Rappel bloquant pour la progression pas-à-pas.
        root (tk.Tk): Instance de la fenêtre racine Tkinter.
        popup_widgets (dict): Widgets Tkinter pour le suivi de la pile et des visites.

    Returns:
        list: Une liste de listes, où chaque sous-liste représente l'ordre de 
            visite des sommets pour un arbre spécifique de la forêt.
    """
    foret = []
    visite = set()
    pile_appels = [] # Représente la pile d'exécution pour la popup
    
    # On garde une trace globale pour que rafraichir_affichage y ait accès
    ordrevisite_global = []

    def rafraichir_affichage():
        """Met à jour l'affichage de la pile et des sommets visités dans la popup."""
        if popup_widgets:
            popup_widgets['pile_var'].set(f"Pile (Stack) : {list(pile_appels)}")
            popup_widgets['visites_var'].set(f"Visités : {list(ordrevisite_global)}")
        root.update()
    
    def color_node(node, color):
        """Applique la couleur au nœud, rafraîchit l'affichage et attend l'utilisateur."""
        col_node(node, color)
        rafraichir_affichage()
        waiter()

    def color_edge(u, v, color, key=0):
        """Applique la couleur à l'arête, rafraîchit l'affichage et attend l'utilisateur."""
        col_edge(u, v, color, key=key)
        rafraichir_affichage()
        waiter()

    # Premier rafraîchissement initial
    rafraichir_affichage()

    for i in g:
        if i not in visite:
            ordrevisite = []
            
            # Lancement de la récursion en lui passant toutes les fonctions de dessin
            profRecG(g, i, g_type, visite, ordrevisite, pile_appels, color_node, color_edge, popup_widgets, root, g)
            
            foret.append(ordrevisite)
            # On accumule dans la liste globale pour l'affichage de la popup
            ordrevisite_global.extend(ordrevisite)
            rafraichir_affichage()
            
    return foret