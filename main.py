# -*- coding: utf-8 -*-
# Copyright (c) 2026 Romain "rom1-dev" FAGONDE
# Distributed under the terms of the MIT License.

import tkinter as tk
from tkinter import colorchooser
import matplotlib.pyplot as plt
import functions, graph_functions
import graph_engine as engine
import webbrowser

graph_type = "Simple" # Choisissez le type de graphe à visualiser (Simple, Orienté, MultiGraph, MultiDiGraph)
draw_layout = "circular" # Choisissez le layout pour la visualisation (spring, circular, random, shell, kamada_kawai)
# custom_positions = {
#     "1": (0, 0),
#     "2": (1, 0),
#     "3": (0, 1),
#     "4": (1, 1),
#     "5": (0.5, 1.5),
#     "6": (1.5, 0.5),
#     "7": (1.5, 1.5),
#     "8": (2, 1)
# }

# Initialisation du graphe de test

G = functions.create_graph(graph_type, {})
layouts = engine.get_layouts()
positions = layouts.get(draw_layout, layouts[draw_layout])(G)
print(positions)

clicked_node = None
released_node = None
hovered_node = None

clicked_edge = None
released_edge = None
hovered_edge = None

shift_pressed = False

offset_x = 0
offset_y = 0

mouse_down = False

mode = "add"

modes = {
    "move": "Déplacement",
    "add": "Ajout",
    "delete": "Suppression",
    "color": "Coloration",
}

def set_mode(new_mode):
    """Change le mode d'interaction actif de l'application.

    Cette fonction met à jour la variable globale `mode` qui contrôle le 
    comportement des outils lors des interactions souris (survol, clic, drag). 
    Elle déclenche également une mise à jour de la barre d'état (*status bar*) 
    pour informer l'utilisateur du nouvel outil sélectionné.

    Args:
        new_mode (str): Le nom du mode à activer. Les valeurs attendues sont :
            - `"move"` : Déplacement des nœuds.
            - `"add"` : Création de nouveaux nœuds et arêtes.
            - `"delete"` : Suppression des nœuds et arêtes.
            - `"color"` : Colorisation des éléments du graphe.
            - `"select_bfs_root"` : Sélection de la racine pour un parcours BFS.
            - `"select_dfs_root"` : Sélection de la racine pour un parcours DFS.
    """
    # modes : "move", "add", "delete", "color"
    global mode
    mode = new_mode
    update_status_bar()

current_color = "#99CCFF" # Couleur par défaut pour le mode "color"

colors = {
    # couleurs personnalisées pour les parcours
    "Sommet": "#99CCFF",
    "Arête": "#00CCCC",
    "Courant": "#FF5733",
    "Avant": "#5BFFFF",
    "Arrière": "#81A54D",
    "Transverse": "#8F476A",
    "Sommet visité": "#FFFECE",
    "Arête de revisite": "#0077FF",
    # couleurs classiques
    "Rouge": "#FF0000",
    "Vert": "#00FF00",
    "Bleu": "#0000FF",
    "Jaune": "#FFFF00",
    "Cyan": "#00FFFF",
    "Magenta": "#FF00FF",
    "Noir": "#000000",
    "Blanc": "#FFFFFF"
}

def set_color(new_color):
    """Définit la couleur active pour l'outil de colorisation.

    Cette fonction met à jour la variable globale `current_color` en extrayant la 
    valeur correspondante depuis le dictionnaire `colors`. Une fois la couleur 
    sélectionnée, elle bascule automatiquement l'application dans le mode `"color"` 
    pour permettre à l'utilisateur de commencer immédiatement à appliquer cette 
    couleur sur le graphe.

    Args:
        new_color (str): La clé correspondant à la couleur souhaitée dans le 
            dictionnaire global `colors` (ex: `"red"`, `"blue"`, etc.).
    """
    global current_color
    if new_color in colors:
        current_color = colors[new_color]
        set_mode("color")  # On bascule en mode colorier après avoir choisi la couleur

def choisir_couleur_avancee():
    """Ouvre une fenêtre native de sélection de couleurs pour une personnalisation avancée.

    Cette fonction utilise `colorchooser.askcolor` de Tkinter pour permettre à 
    l'utilisateur de choisir une couleur parmi une palette complète. Elle initialise 
    la fenêtre avec la couleur actuellement sélectionnée (`current_color`). 
    Si l'utilisateur valide son choix, la valeur hexadécimale est enregistrée 
    dans `current_color` et l'application bascule automatiquement en mode `"color"`. 
    Si l'utilisateur annule, aucune modification n'est apportée.
    """
    global current_color
    # colorchooser.askcolor ouvre la fenêtre native. 
    # color=current_color permet de pré-sélectionner la couleur actuelle.
    couleur_choisie = colorchooser.askcolor(title="Choisissez une couleur", color=current_color)
    
    # askcolor renvoie un tuple : ((R, G, B), "#hex") ou (None, None) si l'utilisateur annule
    if couleur_choisie[1] is not None:
        current_color = couleur_choisie[1]  # On prend la valeur hexadécimale de la couleur choisie
        set_mode("color")  # On bascule en mode colorier après avoir choisi la couleur
        print(f"Nouvelle couleur personnalisée sélectionnée : {current_color}")

def setter(dico):
    """Met à jour partiellement l'état global de l'application.

    Cette fonction permet de modifier de manière ciblée certaines variables 
    globales de l'application via un dictionnaire. Pour chaque clé présente 
    dans `dico`, la variable globale correspondante est mise à jour ; si la 
    clé est absente, la valeur actuelle de la variable est conservée. Cela offre 
    une méthode flexible et centralisée pour propager les changements d'état 
    (clics, modes, positions du graphe, etc.) à travers l'ensemble des modules.

    Args:
        dico (dict): Un dictionnaire contenant les paires clé-valeur des 
            variables d'état à mettre à jour (ex: `{"mouse_down": True, "mode": "add"}`).
    """
    global clicked_node, released_node, mouse_down, hovered_node, mode, offset_x, offset_y, clicked_edge, released_edge, hovered_edge, G, positions, draw_layout, current_color, shift_pressed
    clicked_node = dico.get("clicked_node", clicked_node)
    released_node = dico.get("released_node", released_node)
    mouse_down = dico.get("mouse_down", mouse_down)
    hovered_node = dico.get("hovered_node", hovered_node)
    mode = dico.get("mode", mode)
    offset_x = dico.get("offset_x", offset_x)
    offset_y = dico.get("offset_y", offset_y)
    clicked_edge = dico.get("clicked_edge", clicked_edge)
    released_edge = dico.get("released_edge", released_edge)
    hovered_edge = dico.get("hovered_edge", hovered_edge)
    G = dico.get("G", G)
    positions = dico.get("positions", positions)
    draw_layout = dico.get("draw_layout", draw_layout)
    current_color = dico.get("current_color", current_color)
    shift_pressed = dico.get("shift_pressed", shift_pressed)


def getter():
    """Récupère l'état actuel et les fonctions de rappel de l'application.

    Cette fonction centralise l'accès à l'ensemble des variables globales de 
    l'application ainsi qu'aux fonctions nécessaires au déclenchement des 
    algorithmes de parcours (BFS/DFS). Elle retourne un dictionnaire consolidé, 
    permettant aux autres fonctions d'interroger facilement l'état courant 
    (mode, éléments sélectionnés, graphe, couleurs, etc.) sans dépendre 
    directement de la portée globale.

    Returns:
        dict: Un dictionnaire contenant les variables d'état (ex: `"mode"`, `"G"`, 
            `"positions"`, `"mouse_down"`) et les fonctions de rappel 
            (`"bfs_valid"`, `"dfs_valid"`).
    """
    return {
        "bfs_valid": lancer_parcours_largeur_simple_depuis,
        "dfs_valid": lancer_parcours_profond_simple_depuis,
        "clicked_node": clicked_node,
        "released_node": released_node,
        "mouse_down": mouse_down,
        "hovered_node": hovered_node,
        "mode": mode,
        "offset_x": offset_x,
        "offset_y": offset_y,
        "clicked_edge": clicked_edge,
        "released_edge": released_edge,
        "hovered_edge": hovered_edge,
        "G": G,
        "positions": positions,
        "draw_layout": draw_layout,
        "current_color": current_color,
        "shift_pressed": shift_pressed
    }

root = tk.Tk()
root.title("PyGraphs - Visualisateur Algorithmique de Graphes")

# Génération de la figure Matplotlib à partir du graphe NetworkX
fig = engine.draw_graph_to_fig(G, positions=positions)

canvas_matplotlib = functions.create_graph_canvas(fig, root, G, setter, getter, positions=positions)

# Protocole de fermeture pour s'assurer que les ressources sont libérées correctement
def on_closing():
    """Gère la fermeture propre de l'application.

    Cette fonction est appelée lors de la fermeture de la fenêtre principale. 
    Elle assure une libération complète des ressources :
    - Ferme toutes les fenêtres et figures Matplotlib actives (`plt.close('all')`).
    - Stoppe la boucle d'événements Tkinter (`root.quit()`).
    - Détruit les widgets et ferme la fenêtre principale (`root.destroy()`).

    Cela permet d'éviter les fuites de mémoire et les erreurs de processus lors 
    de la terminaison du programme.
    """
    plt.close('all')  # Ferme toutes les figures Matplotlib en mémoire
    root.quit()       # Arrête le mainloop de Tkinter
    root.destroy()    # Détruit les widgets et libère les ressources

root.protocol("WM_DELETE_WINDOW", on_closing)

# Fonction pour charger un graphe depuis un fichier et mettre à jour la visualisation
def on_load():
    """Charge un graphe depuis un fichier externe et met à jour l'interface.

    Cette fonction appelle le module de chargement pour récupérer un graphe 
    et ses positions associées. Si le chargement réussit, elle remplace 
    l'instance du canevas graphique actuel par un nouveau canevas configuré 
    pour le graphe importé. Enfin, elle déclenche un redessin complet de 
    la figure pour actualiser l'affichage.

    La fonction met à jour les variables globales `G`, `positions` et 
    `canvas_matplotlib` pour maintenir la cohérence de l'état de l'application.
    """
    global G, positions, canvas_matplotlib
    new_G, new_pos = functions.load_graph()
    if new_G is not None:
        G = new_G
        positions = new_pos
        # On redessine sur la figure existante
        fig = canvas_matplotlib.figure
        functions.delete_graph_canvas(canvas_matplotlib)
        canvas_matplotlib = functions.create_graph_canvas(fig, root, G, setter, getter, positions=positions)
        engine.draw_graph_to_fig(G, positions=positions, fig=fig)
        canvas_matplotlib.draw()

def on_new(graph_type="Simple"):
    """Réinitialise l'application avec un nouveau graphe vide.

    Cette fonction crée une nouvelle instance de graphe selon le type spécifié, 
    calcule ses positions initiales via le moteur de mise en page (*layout engine*), 
    puis rafraîchit totalement le canevas d'affichage. Elle remplace l'ancien 
    canevas par un nouveau, lié au nouveau graphe et à ses positions, pour garantir 
    une interface propre et prête pour une nouvelle session.

    Args:
        graph_type (str, optional): Le type de graphe à créer (ex: "Simple", 
            "MultiGraph"). Valeur par défaut : "Simple".
    """
    global G, positions, canvas_matplotlib
    G = functions.create_graph(graph_type, {})
    layouts = engine.get_layouts()
    positions = layouts.get(draw_layout, layouts[draw_layout])(G)
    fig = canvas_matplotlib.figure
    functions.delete_graph_canvas(canvas_matplotlib)
    canvas_matplotlib = functions.create_graph_canvas(fig, root, G, setter, getter, positions=positions)
    engine.draw_graph_to_fig(G, positions=positions, fig=fig)
    canvas_matplotlib.draw()

def on_import():
    """Importe un graphe à partir d'une source externe et recalcule sa disposition.

    Cette fonction sollicite le module d'importation pour obtenir un nouveau 
    graphe. Si l'importation réussit, elle applique automatiquement un algorithme 
    de placement (layout) via le moteur de rendu pour organiser les nœuds, 
    puis rafraîchit l'interface graphique en recréant le canevas Matplotlib 
    avec cette nouvelle configuration.

    Les variables globales `G`, `positions` et `canvas_matplotlib` sont mises 
    à jour pour refléter l'état du graphe importé.
    """
    global G, positions, canvas_matplotlib
    new_G = functions.import_graph()
    if new_G is not None:
        G = new_G
        layouts = engine.get_layouts()
        positions = layouts.get(draw_layout, layouts[draw_layout])(G)
        fig = canvas_matplotlib.figure
        functions.delete_graph_canvas(canvas_matplotlib)
        canvas_matplotlib = functions.create_graph_canvas(fig, root, G, setter, getter, positions=positions)
        engine.draw_graph_to_fig(G, positions=positions, fig=fig)
        canvas_matplotlib.draw()

def on_layout_change(new_layout):
    """Met à jour l'algorithme de disposition (layout) du graphe et rafraîchit l'affichage.

    Cette fonction modifie la stratégie de placement des nœuds en fonction du 
    nouveau layout choisi. Elle recalcule les coordonnées (`positions`) à 
    appliquer au graphe actuel, puis force la reconstruction du canevas 
    Matplotlib pour refléter cette nouvelle géométrie visuelle.

    Args:
        new_layout (str): Le nom de l'algorithme de disposition à appliquer 
            (ex: `"spring"`, `"circular"`, `"kamada_kawai"`).
    """
    global draw_layout, positions, canvas_matplotlib
    draw_layout = new_layout
    layouts = engine.get_layouts()
    positions = layouts.get(draw_layout, layouts[draw_layout])(G)
    fig = canvas_matplotlib.figure
    functions.delete_graph_canvas(canvas_matplotlib)
    canvas_matplotlib = functions.create_graph_canvas(fig, root, G, setter, getter, positions=positions)
    engine.draw_graph_to_fig(G, positions=positions, fig=fig)
    canvas_matplotlib.draw()

def color_node(node, color):
    """Applique une couleur spécifique à un nœud du graphe et met à jour l'affichage.

    Cette fonction modifie l'attribut de couleur du nœud spécifié dans le graphe 
    `G`. Elle utilise ensuite le moteur de rendu pour redessiner le graphe sur 
    la figure existante, garantissant une mise à jour fluide de l'interface 
    sans avoir à reconstruire le widget du canevas.

    Args:
        node (Hashable): L'identifiant du nœud à colorer.
        color (str): Le code couleur (hexadécimal ou nom standard) à appliquer 
            au nœud.
    """
    global G, canvas_matplotlib, positions
    # On convertit en string car NetworkX stocke souvent les IDs en str dans ton code
    node_str = str(node) 
    if node_str in G:
        functions.set_node_color(G, node_str, color)
        # On redessine sur la figure EXISTANTE sans supprimer le canvas
        fig = canvas_matplotlib.figure
        engine.draw_graph_to_fig(G, positions=positions, fig=fig)
        canvas_matplotlib.draw_idle()

def color_edge(u, v, color, key=0):
    """Applique une couleur spécifique à une arête du graphe et met à jour l'affichage.

    Cette fonction modifie l'attribut de couleur d'une arête spécifique identifiée 
    par ses nœuds terminaux `u` et `v`. Pour les multigraphes, elle utilise 
    le paramètre `key` pour cibler l'arête précise en cas de liaisons multiples 
    entre les mêmes sommets. Comme pour les nœuds, elle déclenche un rafraîchissement 
    optimisé de la figure existante.

    Args:
        u (Hashable): Identifiant du nœud de départ de l'arête.
        v (Hashable): Identifiant du nœud d'arrivée de l'arête.
        color (str): Le code couleur (hexadécimal ou nom standard) à appliquer.
        key (int, optional): La clé unique de l'arête dans le cas d'un multigraphe. 
            Valeur par défaut : 0.
    """
    global G, canvas_matplotlib, positions
    u_s, v_s = str(u), str(v)
    if G.has_edge(u_s, v_s):
        functions.set_edge_color(G, u_s, v_s, color, key=key)
        fig = canvas_matplotlib.figure
        engine.draw_graph_to_fig(G, positions=positions, fig=fig)
        canvas_matplotlib.draw_idle()

def reset_colors():
    """Réinitialise les couleurs de tous les éléments du graphe à leurs valeurs par défaut.

    Cette fonction appelle le module utilitaire pour restaurer les attributs de 
    couleur originaux de tous les nœuds et arêtes contenus dans le graphe `G`. 
    Une fois la réinitialisation effectuée au niveau des données, elle rafraîchit 
    l'interface graphique pour refléter cet état visuel initial.
    """
    global G, canvas_matplotlib, positions
    functions.reset_colors(G)
    fig = canvas_matplotlib.figure
    engine.draw_graph_to_fig(G, positions=positions, fig=fig)
    canvas_matplotlib.draw_idle()

step_trigger = tk.BooleanVar(value=False)

def wait_for_space():
    """Suspend l'exécution jusqu'à ce que l'utilisateur appuie sur la touche Espace.

    Cette fonction bloque l'exécution du thread courant en attendant que la 
    variable Tkinter `step_trigger` soit mise à jour. Elle est utilisée pour 
    implémenter une exécution pas-à-pas des algorithmes, permettant à l'utilisateur 
    de contrôler la progression de la visualisation.

    Note :
        Cette fonction doit être appelée dans un thread séparé du thread 
        principal (mainloop) de Tkinter pour éviter de geler l'interface graphique.
    """
    # On réinitialise la variable au cas où
    step_trigger.set(False)
    # On attend que la variable passe à True[cite: 11]
    root.wait_variable(step_trigger)

def trigger_next_step(event):
    """Déclenche la poursuite de l'exécution d'un algorithme.

    Cette fonction est conçue pour être liée à un événement clavier (ex: touche Espace). 
    Elle met à jour la variable `step_trigger` à `True`, ce qui libère l'attente 
    générée par `root.wait_variable` dans la fonction `wait_for_space`.

    Args:
        event (tk.Event): L'objet événement généré par Tkinter lors de la pression 
            de la touche associée.
    """
    step_trigger.set(True)

# On lie l'événement 'Espace' à la fonction trigger
root.bind('<space>', trigger_next_step)

def parcours_en_largeur_generalise():
    """Lance une visualisation interactive de l'algorithme de parcours en largeur (BFS).

    Cette fonction crée une fenêtre éphémère (`Toplevel`) qui sert de tableau de 
    bord pour suivre en temps réel la progression du BFS sur le graphe `G`. 
    Elle initialise les variables Tkinter nécessaires à l'affichage des états 
    internes (file d'attente, nœuds visités, sommet courant, voisinage).

    L'algorithme est exécuté via le module `graph_functions`. La fonction 
    assure une exécution sécurisée en verrouillant la fermeture de la fenêtre 
    pendant l'animation et en restaurant les contrôles de la fenêtre une fois 
    le parcours terminé.

    Note :
        La fonction utilise `wait_for_space` comme rappel pour permettre à 
        l'utilisateur de contrôler la vitesse de progression étape par étape.
    """
    global G

    popup = tk.Toplevel(root)
    popup.title("Suivi du Parcours en Largeur")
    popup.geometry("400x150")
    popup.attributes('-topmost', True) # Garde la popup au premier plan

    # Empêcher l'utilisateur de fermer brutalement la popup pendant l'animation
    # (ce qui provoquerait un crash Tkinter)
    popup.protocol("WM_DELETE_WINDOW", lambda: None)

    # 2. Déclaration des variables Tkinter de contrôle
    file_var = tk.StringVar(value="File : []")
    visites_var = tk.StringVar(value="Visités : []")
    sommet_en_cours = tk.StringVar(value="Sommet en cours : None")
    voisinage = tk.StringVar(value="Voisinage : []")

    # 3. Création des Widgets graphiques dans la popup
    lbl_title = tk.Label(popup, text="Algorithme BFS en cours...", font=("Arial", 12, "bold"))
    lbl_title.pack(pady=10)

    lbl_file = tk.Label(popup, textvariable=file_var, font=("Courier", 10), fg="blue", anchor="w", justify="left")
    lbl_file.pack(fill="x", padx=15, pady=2)

    lbl_visites = tk.Label(popup, textvariable=visites_var, font=("Courier", 10), fg="green", anchor="w", justify="left")
    lbl_visites.pack(fill="x", padx=15, pady=2)

    lbl_sommet = tk.Label(popup, textvariable=sommet_en_cours, font=("Courier", 10), fg="red", anchor="w", justify="left")
    lbl_sommet.pack(fill="x", padx=15, pady=2)

    lbl_voisinage = tk.Label(popup, textvariable=voisinage, font=("Courier", 10), fg="purple", anchor="w", justify="left")
    lbl_voisinage.pack(fill="x", padx=15, pady=2)

    # On regroupe les variables dans un dictionnaire pour l'envoyer en entrée
    popup_widgets = {
        'file_var': file_var,
        'visites_var': visites_var,
        'sommet_en_cours': sommet_en_cours,
        'voisinage': voisinage
    }

    if G is not None:
        g=functions.get_adjacency_list(G)
        # g={1: [2, 3, 4], 2: [], 3: [2, 2], 4: [1, 3]} # graphe de test
        revisites = graph_functions.largeurG(g, functions.get_graph_type(G), color_node, color_edge, wait_for_space, root, popup_widgets)
        
        # 1. On change le titre pour indiquer que c'est fini
        lbl_title.config(text="Parcours en largeur terminé !", fg="darkgreen")
        
        # 2. On réactive la croix rouge de la fenêtre pour qu'elle détruise la popup
        popup.protocol("WM_DELETE_WINDOW", popup.destroy)
        
        # 3. On ajoute un bouton de fermeture directement dans la popup
        btn_fermer = tk.Button(popup, text="Fermer", command=popup.destroy, bg="#E0E0E0")
        btn_fermer.pack(pady=10)

def parcours_en_profondeur_generalise():
    """Lance une visualisation interactive de l'algorithme de parcours en profondeur (DFS).

    Cette fonction crée une fenêtre éphémère (`Toplevel`) dédiée au suivi de 
    l'exécution du DFS. Elle initialise les composants Tkinter permettant de 
    visualiser l'évolution de la pile (stack) et la liste des sommets visités 
    en temps réel.

    La fonction orchestre le lancement de l'algorithme via `graph_functions.profondG`, 
    en lui transmettant les fonctions de rappel nécessaires pour colorer les éléments 
    du graphe et gérer la progression pas-à-pas. Comme pour le BFS, la fermeture 
    de la fenêtre de suivi est verrouillée durant l'exécution pour assurer la 
    stabilité du processus.

    Note :
        Le parcours génère une forêt de recherche (ou un arbre si le graphe est 
        connexe), qui est affichée dans la console une fois l'algorithme terminé.
    """
    global G, draw_layout, positions, canvas_matplotlib
    
    if G is not None:
        # 1. Création de la fenêtre Pop-up dédiée au DFS
        popup = tk.Toplevel(root)
        popup.title("Suivi du Parcours en Profondeur (DFS)")
        popup.geometry("450x160")
        popup.attributes('-topmost', True)
        popup.protocol("WM_DELETE_WINDOW", lambda: None) # Bloque la fermeture pendant le run

        # Variables Tkinter
        pile_var = tk.StringVar(value="Pile (Stack) : []")
        visites_var = tk.StringVar(value="Visités : []")

        # Layout de la Popup
        lbl_title = tk.Label(popup, text="Algorithme DFS en cours...", font=("Arial", 12, "bold"))
        lbl_title.pack(pady=10)

        lbl_pile = tk.Label(popup, textvariable=pile_var, font=("Courier", 10), fg="purple", anchor="w", justify="left")
        lbl_pile.pack(fill="x", padx=15, pady=2)

        lbl_visites = tk.Label(popup, textvariable=visites_var, font=("Courier", 10), fg="green", anchor="w", justify="left")
        lbl_visites.pack(fill="x", padx=15, pady=2)

        popup_widgets = {
            'pile_var': pile_var,
            'visites_var': visites_var
        }

        # 2. Récupération de la liste d'adjacence et exécution
        g = functions.get_adjacency_list(G)
        
        # Lance le pont vers profRec
        foret = graph_functions.profondG(
            g, 
            functions.get_graph_type(G), 
            color_node, 
            color_edge, 
            wait_for_space, 
            root, 
            popup_widgets=popup_widgets
        )
        
        print("Forêt de parcours en profondeur terminée :", foret)

        # 3. Réactivation de la fermeture de la popup après la fin de l'algorithme
        lbl_title.config(text="Parcours en profondeur terminé !", fg="darkgreen")
        popup.protocol("WM_DELETE_WINDOW", popup.destroy)
        
        btn_fermer = tk.Button(popup, text="Fermer", command=popup.destroy)
        btn_fermer.pack(pady=5)

def preparer_parcours_largeur_simple():
    """Initialise le mode de sélection pour le parcours en largeur (BFS).

    Cette fonction vérifie si le graphe est valide et non vide. Si c'est le cas, 
    elle bascule l'application dans le mode `select_bfs_root`, permettant 
    à l'utilisateur de choisir graphiquement le nœud de départ du parcours. 
    Une boîte de dialogue informe l'utilisateur de cette étape nécessaire.
    """
    global mode
    if G is not None and len(G.nodes) > 0:
        set_mode("select_bfs_root")
        tk.messagebox.showinfo("BFS Simple", "Veuillez cliquer sur le sommet de départ dans le graphe.")

def lancer_parcours_largeur_simple_depuis(sommet_depart):
    """Exécute et visualise un parcours en largeur (BFS) depuis un sommet donné.

    Cette fonction initialise l'environnement de suivi BFS après qu'un utilisateur 
    a sélectionné un point de départ. Elle effectue les conversions nécessaires 
    sur l'identifiant du sommet, crée une fenêtre de suivi dédiée avec mise à jour 
    dynamique des variables d'état (file, sommets visités, voisinage), puis lance 
    le moteur d'algorithme.

    Args:
        sommet_depart (Union[int, str]): L'identifiant du nœud sélectionné comme 
            racine du parcours.
    """
    global G, draw_layout, positions, canvas_matplotlib
    
    # Conversion du sommet sélectionné selon le type des clés de votre dictionnaire d'adjacence
    # get_adjacency_list renvoie des entiers si int_values=True (par défaut)
    try:
        depart = int(sommet_depart)
    except ValueError:
        depart = sommet_depart

    # 1. Création de la Popup dédiée
    popup = tk.Toplevel(root)
    popup.title(f"BFS Simple - Départ : {depart}")
    popup.geometry("400x200")
    popup.attributes('-topmost', True)
    popup.protocol("WM_DELETE_WINDOW", lambda: None)

    file_var = tk.StringVar(value="File : []")
    visites_var = tk.StringVar(value="Visités : []")
    sommet_var = tk.StringVar(value="Sommet en cours : -")
    voisinage_var = tk.StringVar(value="Voisinage : []")

    lbl_title = tk.Label(popup, text="Algorithme BFS Simple...", font=("Arial", 12, "bold"))
    lbl_title.pack(pady=5)

    tk.Label(popup, textvariable=sommet_var, font=("Arial", 10, "bold"), fg="darkorange", anchor="w").pack(fill="x", padx=15)
    tk.Label(popup, textvariable=voisinage_var, font=("Courier", 10), fg="purple", anchor="w").pack(fill="x", padx=15)
    tk.Label(popup, textvariable=file_var, font=("Courier", 10), fg="blue", anchor="w").pack(fill="x", padx=15)
    tk.Label(popup, textvariable=visites_var, font=("Courier", 10), fg="green", anchor="w").pack(fill="x", padx=15)

    popup_widgets = {
        'file_var': file_var,
        'visites_var': visites_var,
        'sommet_en_cours': sommet_var,
        'voisinage': voisinage_var
    }

    # 2. Exécution du parcours
    g = functions.get_adjacency_list(G)
    
    # On force une petite vérification si le sommet est bien dans la liste d'adjacence
    if depart not in g:
        # Tente en version chaîne de caractères si l'entier n'y est pas
        depart = str(sommet_depart)

    visites, revisites = graph_functions.largeur(
        g, depart, functions.get_graph_type(G), 
        color_node, color_edge, wait_for_space, root, popup_widgets
    )

    # 4. Finalisation de la popup
    lbl_title.config(text="Parcours terminé !", fg="darkgreen")
    popup.protocol("WM_DELETE_WINDOW", popup.destroy)
    tk.Button(popup, text="Fermer", command=popup.destroy).pack(pady=5)

def preparer_parcours_profondeur_simple():
    """Initialise le mode de sélection pour le parcours en profondeur (DFS).

    Cette fonction vérifie la validité du graphe actuel. Si le graphe contient 
    des nœuds, elle bascule l'application dans le mode `select_dfs_root`, 
    permettant à l'utilisateur de choisir graphiquement le nœud racine pour le DFS. 
    Une boîte de dialogue guide l'utilisateur dans cette étape.
    """
    global mode
    if G is not None and len(G.nodes) > 0:
        set_mode("select_dfs_root")
        tk.messagebox.showinfo("DFS Simple", "Veuillez cliquer sur le sommet de départ pour le parcours en profondeur.")

def lancer_parcours_profond_simple_depuis(sommet_depart):
    """Exécute et visualise un parcours en profondeur (DFS) depuis un sommet donné.

    Cette fonction initialise l'interface de suivi du DFS après que l'utilisateur 
    a sélectionné un sommet de départ. Elle configure une fenêtre dédiée 
    affichant en temps réel l'état de la pile de récursion et la liste des 
    sommets visités.

    L'algorithme est ensuite exécuté via le module `graph_functions`, en utilisant 
    les fonctions de rappel pour la mise à jour visuelle des éléments du graphe 
    et la progression contrôlée par l'utilisateur.

    Args:
        sommet_depart (Union[int, str]): L'identifiant du nœud sélectionné comme 
            racine du parcours en profondeur.
    """
    global G, draw_layout, positions, canvas_matplotlib
    
    try:
        depart = int(sommet_depart)
    except ValueError:
        depart = sommet_depart

    # 1. Création de la Popup dédiée au DFS Simple
    popup = tk.Toplevel(root)
    popup.title(f"DFS Simple - Départ : {depart}")
    popup.geometry("450x160")
    popup.attributes('-topmost', True)
    popup.protocol("WM_DELETE_WINDOW", lambda: None) # Bloque la fermeture pendant le calcul

    pile_var = tk.StringVar(value="Pile (Stack) : []")
    visites_var = tk.StringVar(value="Visités : []")

    lbl_title = tk.Label(popup, text="Algorithme DFS Simple en cours...", font=("Arial", 12, "bold"))
    lbl_title.pack(pady=10)

    tk.Label(popup, textvariable=pile_var, font=("Courier", 10), fg="purple", anchor="w", justify="left").pack(fill="x", padx=15, pady=2)
    tk.Label(popup, textvariable=visites_var, font=("Courier", 10), fg="green", anchor="w", justify="left").pack(fill="x", padx=15, pady=2)

    popup_widgets = {
        'pile_var': pile_var,
        'visites_var': visites_var
    }

    # 2. Récupération de la liste d'adjacence et exécution
    g = functions.get_adjacency_list(G)
    if depart not in g:
        depart = str(sommet_depart)

    ordrevisite = graph_functions.profond(
        g, depart, functions.get_graph_type(G),
        color_node, color_edge, wait_for_space, root, popup_widgets=popup_widgets
    )

    print(f"Parcours DFS Simple depuis {depart} terminé. Ordre :", ordrevisite)

    # 3. Finalisation de la popup
    lbl_title.config(text="Parcours en profondeur terminé !", fg="darkgreen")
    popup.protocol("WM_DELETE_WINDOW", popup.destroy)
    
    btn_fermer = tk.Button(popup, text="Fermer", command=popup.destroy)
    btn_fermer.pack(pady=5)

def afficher_a_propos():
    """Affiche une boîte de dialogue d'information sur l'application.

    Cette fonction présente les détails techniques de l'outil (version, auteurs, 
    technologies utilisées et conditions de licence) à travers une fenêtre 
    modale native Tkinter. Elle permet à l'utilisateur d'obtenir rapidement 
    des informations sur le projet.
    """
    tk.messagebox.showinfo(
        "À propos de l'application",
        "PyGraph\n"
        "Version 1.0.0 (2026)\n\n"
        "Développé avec passion pour l'apprentissage des structures de données.\n\n"
        "Technologies utilisées :\n"
        "• Python 3\n"
        "• Tkinter (Interface Graphique)\n"
        "• NetworkX (Modélisation)\n"
        "• Matplotlib (Rendu Graphique)\n\n"
        "Licence : Open Source (Licence MIT)\n"
        "Copyright © 2026 Romain FAGONDE.\n"
        "Le code source est libre de modification et de partage."
    )
        
# menu

# dictionnaires de structure pour les menus et sous-menus (les fonctions associées sont à implémenter : remplacer les None par les fonctions correspondantes)

couleurs = functions.split_dico({"Rouge": [None, None], "Vert": [None, None], "Bleu": [None, None], "Jaune": [None, None], "Cyan": [None, None], "Magenta": [None, None], "Noir": [None, None], "Blanc": [None, None]})

menus = {
    "Fichier" : {
        "Nouveau" : {
            "Simple" : lambda: on_new("Simple"), 
            "Orienté" : lambda: on_new("Orienté"), 
            "Multi" : lambda: on_new("MultiGraph"), 
            "Multi Orienté" : lambda: on_new("MultiDiGraph")
        }, 
        "Ouvrir" : on_load, 
        "Enregistrer" : lambda : functions.save_graph(G, positions), 
        "Importer" : on_import, 
        "Exporter" : {
            "Vers Json" : lambda: functions.export_graph_to_json(G), 
            "Vers python" : lambda: functions.export_graph_to_python(G)
        }, 
        "Copier vers le presse-papiers" : {
            "Liste d'adjacence" : lambda : functions.copy_graph_to_clipboard_adjacency(G), 
            "Code python" : lambda : functions.copy_graph_to_clipboard_python(G)
        }, 
        "Quitter" : on_closing
    },
    "Édition" : {
        "Déplacer" : lambda : set_mode("move"), 
        "Ajouter" : lambda : set_mode("add"), 
        "Supprimer" : lambda : set_mode("delete"),
        "Colorier" : {
            "Sommet" : lambda: set_color("Sommet"),
            "Arête" : lambda: set_color("Arête"),
            "Courant" : lambda: set_color("Courant"),
            "Avant" : lambda: set_color("Avant"),
            "Arrière" : lambda: set_color("Arrière"),
            "Transverse" : lambda: set_color("Transverse"),
            "Sommet visité" : lambda: set_color("Sommet visité"),
            "Arête de revisite" : lambda: set_color("Arête de revisite"),
            "---" : None,
            "Rouge" : lambda: set_color("Rouge"),
            "Vert" : lambda: set_color("Vert"),
            "Bleu" : lambda: set_color("Bleu"),
            "Jaune" : lambda: set_color("Jaune"),
            "Cyan" : lambda: set_color("Cyan"),
            "Magenta" : lambda: set_color("Magenta"),
            "Noir" : lambda: set_color("Noir"),
            "Blanc" : lambda: set_color("Blanc"),
            "Couleur personnalisée..." : choisir_couleur_avancee
        },
        "Réinitialiser les couleurs" : reset_colors
    },
    "Algorithmes" : {
        "Parcours en largeur" : preparer_parcours_largeur_simple,
        "Parcours en profondeur" : preparer_parcours_profondeur_simple,
        "Parcours en largeur généralisé" : parcours_en_largeur_generalise,
        "Parcours en profondeur généralisé" : parcours_en_profondeur_generalise
    },
    "Affichage" : {
        "Layout" : {
            "Spring" : lambda: on_layout_change("spring"), 
            "Circular" : lambda: on_layout_change("circular"), 
            "Random" : lambda: on_layout_change("random"), 
            "Shell" : lambda: on_layout_change("shell"), 
            "Kamada-Kawai" : lambda: on_layout_change("kamada_kawai")
        }
    },
    "Aide" : {
        "Guide d'utilisation" : lambda: functions.afficher_popup_aide(root),
        "Mises à jour" : lambda: webbrowser.open(functions.WEBSITE_URL),
        "À propos" : afficher_a_propos
    }
}

# Création du menu à partir de la structure définie ci-dessus
menubar = tk.Menu(root)

for menu_label, submenu_dict in menus.items():
    menu = tk.Menu(menubar, tearoff=0)
    functions.create_submenu(menu, submenu_dict)
    menubar.add_cascade(label=menu_label, menu=menu)

root.config(menu=menubar)

# montrer le mode en bas de la fenêtre
status_bar = tk.Label(root, text=f"Mode : {modes.get(mode, 'Aucun')}", bd=1, relief=tk.SUNKEN, anchor=tk.W)
def update_status_bar():
    """Met à jour la barre d'état pour refléter le mode d'interaction actuel.

    Cette fonction récupère la description lisible du mode en cours via le 
    dictionnaire `modes` et met à jour le widget `status_bar` pour informer 
    l'utilisateur de l'état actuel de l'application (ex: "Mode : Édition", 
    "Mode : Sélection BFS").
    """
    status_bar.config(text=f"Mode : {modes.get(mode, 'Aucun')}")
status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    


functions.verifier_et_afficher_accueil(root)
root.mainloop()