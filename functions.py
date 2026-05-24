# -*- coding: utf-8 -*-
# Copyright (c) 2026 Romain "rom1-dev" FAGONDE
# Distributed under the terms of the MIT License.

import networkx as nx
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import graph_engine as engine
import matplotlib.pyplot as plt
import numpy as np
import math
import json
from tkinter import filedialog, messagebox
import ast
import pyperclip
import networkx as nx
import os
import webbrowser

CONFIG_FILE = "config.json"
WEBSITE_URL = "https://github.com/rom1-dev/PyGraph/releases"

def load_config():
    """Charge le fichier de configuration JSON de l'application.

    Tente de lire le fichier de configuration global. Si le fichier n'existe pas 
    ou qu'une erreur survient lors de la lecture (JSON invalide, etc.), la fonction 
    renvoie une configuration par défaut.

    Returns:
        dict: Un dictionnaire contenant les paramètres de configuration. 
              Renvoie `{"show_welcome": True}` par défaut en cas d'erreur ou d'absence du fichier.
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"show_welcome": True}
    return {"show_welcome": True}

def save_config(config):
    """Sauvegarde la configuration actuelle dans le fichier JSON.

    Prend un dictionnaire de configuration et l'écrit au format JSON dans le 
    fichier global. Les erreurs d'écriture ou d'accès au fichier sont capturées 
    et affichées dans la console pour éviter de bloquer l'application.

    Args:
        config (dict): Le dictionnaire contenant les paramètres de configuration 
            à enregistrer.
    """
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la configuration : {e}")

def afficher_popup_aide(root):
    """Affiche une fenêtre pop-up d'aide et de bienvenue pour PyGraphs.

    Cette fenêtre présente les commandes fondamentales de l'application (ajout, 
    déplacement, suppression, coloriage de graphes et exécution d'algorithmes). 
    Elle inclut également une case à cocher permettant à l'utilisateur de 
    masquer cette aide lors des prochains lancements, en mettant à jour la 
    configuration globale.

    Args:
        root (tk.Tk | tk.Toplevel): La fenêtre parente Tkinter par rapport à 
            laquelle la pop-up sera centrée ou rattachée.
    """
    popup = tk.Toplevel(root)
    popup.title("Guide d'utilisation & Informations importantes")
    popup.geometry("500x350")  # Légèrement agrandi pour le lien
    popup.resizable(False, False)
    popup.attributes('-topmost', True)

    # 1. Titre
    lbl_titre = tk.Label(popup, text="Bienvenue dans PyGraphs !", font=("Arial", 12, "bold"), fg="#0055A5")
    lbl_titre.pack(pady=10)

    # 2. Cadre du bas (Bouton et Case à cocher)
    bottom_frame = tk.Frame(popup)
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=15)

    config = load_config()
    ne_plus_afficher_var = tk.BooleanVar(value=not config.get("show_welcome", True))

    def valider_fermeture():
        """Met à jour les préférences de l'utilisateur et ferme la pop-up.

        Lit l'état de la case à cocher "Ne plus afficher", met à jour le 
        dictionnaire de configuration, sauvegarde les modifications sur le disque 
        et détruit la fenêtre pop-up.
        """
        config["show_welcome"] = not ne_plus_afficher_var.get()
        save_config(config)
        popup.destroy()

    chk_box = tk.Checkbutton(bottom_frame, text="Ne plus afficher", variable=ne_plus_afficher_var)
    chk_box.pack(side=tk.LEFT)

    btn_ok = tk.Button(bottom_frame, text="Compris !", width=12, bg="#007ACC", fg="white", command=valider_fermeture)
    btn_ok.pack(side=tk.RIGHT)

    # 3. LIEN VERS LE SITE WEB (Placé juste au-dessus du bandeau du bas)
    def ouvrir_site(event=None):
        """Ouvre le site Web ou le dépôt GitHub du projet dans le navigateur.

        Args:
            event (tk.Event, optional): L'événement de clic de souris envoyé par 
                le bind de Tkinter. Par défaut à None.
        """
        webbrowser.open(WEBSITE_URL)  # Remplacer par votre vraie URL

    lbl_site = tk.Label(popup, text="Suivez les dernières mises à jour sur GitHub", 
                        font=("Arial", 10, "underline"), fg="#0066CC", cursor="hand2")
    lbl_site.pack(side=tk.BOTTOM, pady=5)
    lbl_site.bind("<Button-1>", ouvrir_site)

    # 4. Zone de texte explicative au milieu
    txt_info = tk.Text(popup, wrap=tk.WORD, font=("Arial", 10), bg=popup.cget("bg"), bd=0, highlightthickness=0, height=11)
    instructions = (
        "Voici les commandes fondamentales pour manipuler vos graphes :\n\n"
        "• Mode Ajouter : Cliquez dans le vide pour créer un sommet. Glissez d'un sommet à un autre pour créer une arête.\n"
        "• Mode Déplacer : Glissez-déposez un sommet pour réorganiser le layout.\n"
        "• Mode Supprimer : Cliquez sur un sommet ou une arête pour le/la retirer.\n"
        "• Mode Colorier : Cliquez sur un sommet ou une arête pour changer sa couleur.\n"
        "• Clavier : Maintenez la touche [ ⇑ Maj. ] pour colorier les bordures des sommets.\n"
        "• Algorithmes : Lancez un parcours (BFS/DFS) depuis le menu. Pour les parcours simples, "
        "cliquez sur le sommet de départ une fois l'alerte validée.\n\n"
        "Pendant un parcours, utilisez la [Barre Espace] pour avancer pas-à-pas."
    )
    txt_info.insert(tk.END, instructions)
    txt_info.config(state=tk.DISABLED)
    txt_info.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)

def verifier_et_afficher_accueil(root):
    """Vérifie les préférences de l'utilisateur et affiche la pop-up d'aide si nécessaire.

    Charge la configuration depuis le fichier JSON. Si le paramètre `show_welcome` 
    est vrai (ou s'il est absent), la fenêtre d'aide est programmée pour s'ouvrir 
    après un court délai afin de laisser le temps à l'interface principale de se charger.

    Args:
        root (tk.Tk | tk.Toplevel): La fenêtre principale de l'application.
    """
    config = load_config()
    if config.get("show_welcome", True):
        # Utiliser un léger after pour s'assurer que la fenêtre principale est bien initialisée
        root.after(100, lambda: afficher_popup_aide(root))

def get_adjacency_list(G, int_values=True, sorted_keys=True):
    """Génère la liste d'adjacence d'un graphe NetworkX.

    Cette fonction extrait les voisins de chaque sommet et construit un dictionnaire 
    représentant la liste d'adjacence. Elle gère à la fois les graphes simples, 
    les graphes orientés et les multigraphes (en préservant les arêtes multiples). 
    Elle permet également de transtyper les identifiants des sommets en entiers 
    et de trier le résultat final.

    Args:
        G (nx.Graph | nx.DiGraph | nx.MultiGraph | nx.MultiDiGraph): Le graphe 
            NetworkX à analyser.
        int_values (bool, optional): Si True, convertit les identifiants des 
            sommets en entiers (`int`). Valeur par défaut : True.
        sorted_keys (bool, optional): Si True, trie le dictionnaire par clés 
            (sommets) et trie également la liste des voisins de chaque sommet. 
            Valeur par défaut : True.

    Returns:
        dict[any, list]: Un dictionnaire où les clés sont les sommets et les 
            valeurs sont des listes contenant leurs sommets adjacents.
    """
    adj_list = {}
    
    # Fonction locale pour gérer la conversion à la volée
    def conv(node):
        """Convertit l'identifiant d'un sommet en entier si option activée.

        Args:
            node (any): L'identifiant du sommet à convertir.

        Returns:
            int | any: Le sommet converti en entier, ou inchangé selon les 
                paramètres de la fonction parente.
        """
        return int(node) if int_values else node

    # Case 1: Multigraphes (on doit boucler sur les arêtes pour garder les doublons)
    if isinstance(G, (nx.MultiGraph, nx.MultiDiGraph)):
        for node in G.nodes():
            adj_list[conv(node)] = []
        for u, v in G.edges(): # Pas besoin de keys=True si on ne se sert pas de la clé
            adj_list[conv(u)].append(conv(v))
            if not G.is_directed() and u != v:
                adj_list[conv(v)].append(conv(u))
                
    # Case 2: Graphes simples (on utilise l'API de NetworkX, beaucoup plus rapide)
    else:
        for node in G.nodes():
            adj_list[conv(node)] = [conv(n) for n in G.neighbors(node)]

    # Application du tri global si demandé
    if sorted_keys:
        return {k: sorted(v) for k, v in sorted(adj_list.items())}
        
    return adj_list

def save_graph(G, positions):
    """Exporte le graphe et les positions de ses sommets dans un fichier JSON personnalisé.

    Ouvre une boîte de dialogue Tkinter (`asksaveasfilename`) permettant à 
    l'utilisateur de choisir l'emplacement et le nom du fichier (avec l'extension 
    par défaut `.gph`). La fonction sérialise ensuite la structure du graphe via 
    NetworkX et convertit les coordonnées des positions en listes pour assurer 
    la compatibilité JSON avant l'écriture.

    Args:
        G (nx.Graph | nx.DiGraph | nx.MultiGraph | nx.MultiDiGraph): Le graphe 
            NetworkX à sauvegarder.
        positions (dict): Un dictionnaire associant chaque identifiant de sommet 
            à ses coordonnées spatiales (ex: `{node_id: (x, y)}`).
    """
    file_path = filedialog.asksaveasfilename(
        defaultextension=".gph", # Extension par défaut
        filetypes=[("Fichier Graphe", "*.gph"), ("Tous les fichiers", "*.*")],
        title="Enregistrer le projet de graphe"
    )
    if not file_path:
        return

    # Structure de données identique à l'étape précédente
    data = {
        "graph": nx.node_link_data(G),
        "positions": {node: list(pos) for node, pos in positions.items()}
    }

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        messagebox.showinfo("Succès", "Projet enregistré avec succès !")
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'enregistrer : {e}")

def load_graph():
    """Charge et reconstruit un projet de graphe depuis un fichier JSON sauvegardé.

    Ouvre une boîte de dialogue Tkinter (`askopenfilename`) pour permettre à 
    l'utilisateur de sélectionner un fichier `.gph`. La fonction désérialise 
    les données pour reconstruire le graphe NetworkX sous sa forme d'origine 
    et convertit les listes de coordonnées stockées en tuples exploitables 
    pour le positionnement des sommets.

    Returns:
        tuple: Un couple `(G, positions)` où :
            - G (nx.Graph | None): Le graphe NetworkX reconstruit, ou `None` en cas d'erreur/annulation.
            - positions (dict | None): Le dictionnaire des coordonnées des sommets `{node_id: (x, y)}`, 
              ou `None` en cas d'erreur/annulation.
    """
    file_path = filedialog.askopenfilename(
        filetypes=[("Fichier Graphe", "*.gph")], # Filtre sur votre extension
        title="Ouvrir un projet de graphe"
    )
    if not file_path:
        return None, None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        G = nx.node_link_graph(data["graph"])
        positions = {node: tuple(pos) for node, pos in data["positions"].items()}
        
        return G, positions
    except Exception as e:
        messagebox.showerror("Erreur", "Le fichier est corrompu ou n'est pas un projet valide.")
        return None, None

def ask_import_settings(dict_keys, bool_keys):
    """Affiche une boîte de dialogue pour configurer l'importation d'un graphe.

    Cette fonction crée une fenêtre modale (`Toplevel`) permettant à l'utilisateur 
    de sélectionner la variable contenant le dictionnaire du graphe, et de 
    définir si le graphe est orienté ou s'il s'agit un multi-graphe. Ces deux derniers 
    paramètres peuvent être définis manuellement (via une case à cocher) ou être 
    liés dynamiquement à une variable booléenne existante.

    Args:
        dict_keys (list[str]): Liste des noms des variables disponibles de type 
            dictionnaire (pour le choix du graphe).
        bool_keys (list[str]): Liste des noms des variables disponibles de type 
            booléen (pour l'orientation ou le type de graphe).

    Returns:
        dict: Un dictionnaire contenant les paramètres d'importation validés :
            - `"variable"` (str): Le nom de la variable du graphe sélectionnée.
            - `"is_directed"` (bool | str): Booléen si configuré manuellement, 
              ou le nom de la variable booléenne associée.
            - `"is_multi"` (bool | str): Booléen si configuré manuellement, 
              ou le nom de la variable booléenne associée.
    """
    settings = {}
    dialog = tk.Toplevel()
    dialog.title("Paramètres d'importation")
    dialog.grab_set()

    main_frame = tk.Frame(dialog, padx=20, pady=20)
    main_frame.pack(fill="both", expand=True)

    # --- 1. CHOIX DU DICTIONNAIRE ---
    tk.Label(main_frame, text="Variable du graphe (dict) :", font=('Arial', 10, 'bold')).pack(anchor="w")
    var_selection = tk.StringVar(value=dict_keys[0] if dict_keys else "")
    tk.OptionMenu(main_frame, var_selection, *dict_keys).pack(fill="x", pady=(0, 20))

    def create_toggle_section(parent, label_text, bool_keys):
        """Crée une section d'interface graphique dynamique (Manuel ou Variable).

        Génère un groupe de widgets comprenant des boutons radio pour basculer 
        entre le mode "Manuel" (qui affiche une Checkbutton) et le mode "Variable" 
        (qui affiche un OptionMenu contenant les variables booléennes disponibles).

        Args:
            parent (tk.Frame): Le cadre Tkinter parent dans lequel injecter la section.
            label_text (str): Le titre textuel de la section.
            bool_keys (list[str]): Liste des variables de type booléen à proposer.

        Returns:
            dict: Un dictionnaire contenant les variables de contrôle Tkinter :
                - `"mode"` (tk.StringVar): Le mode sélectionné ("Manuel" ou "Variable").
                - `"manual"` (tk.BooleanVar): L'état de la case à cocher manuelle.
                - `"var_name"` (tk.StringVar): Le nom de la variable sélectionnée dans le menu.
        """
        tk.Label(parent, text=label_text, font=('Arial', 10, 'bold')).pack(anchor="w")
        
        # Variables de contrôle
        mode_var = tk.StringVar(value="Manuel")
        manual_val = tk.BooleanVar(value=False)
        var_name_val = tk.StringVar(value=bool_keys[0] if bool_keys else "")

        container = tk.Frame(parent)
        container.pack(fill="x", pady=(0, 15))

        # Sélecteur de mode (RadioButtons pour plus de clarté que l'OptionMenu)
        radio_frame = tk.Frame(container)
        radio_frame.pack(side="top", fill="x")
        tk.Radiobutton(radio_frame, text="Manuel", variable=mode_var, value="Manuel").pack(side="left")
        if bool_keys:
            tk.Radiobutton(radio_frame, text="Variable", variable=mode_var, value="Variable").pack(side="left")

        # Zone d'entrée dynamique
        input_frame = tk.Frame(container)
        input_frame.pack(side="top", fill="x", padx=20)

        # Widgets
        check = tk.Checkbutton(input_frame, text="Oui (True)", variable=manual_val)
        if bool_keys:
            menu = tk.OptionMenu(input_frame, var_name_val, *bool_keys)

        def update_view(*args):
            """Ajuste dynamiquement l'affichage des widgets selon le mode choisi.

            Masque les éléments inutilisés et affiche le widget correspondant au 
            mode actif (case à cocher pour Manuel, menu déroulant pour Variable), 
            puis recalcule la taille de la fenêtre de dialogue.
            """
            # On nettoie
            check.pack_forget()
            if bool_keys: menu.pack_forget()

            # On affiche selon le mode
            if mode_var.get() == "Manuel":
                check.pack(side="left")
            else:
                if bool_keys: menu.pack(side="left")
            
            # Ajustement dynamique de la taille
            dialog.update_idletasks()
            dialog.geometry("")

        mode_var.trace_add("write", update_view)
        update_view() # Init

        return {"mode": mode_var, "manual": manual_val, "var_name": var_name_val}

    # Création des deux sections
    dir_controls = create_toggle_section(main_frame, "Orienté (Directed) :", bool_keys)
    multi_controls = create_toggle_section(main_frame, "Multi-graphe :", bool_keys)

    def confirm():
        """Valide les choix, remplit le dictionnaire final et ferme la fenêtre.

        Cette fonction récupère l'état de chaque section (en résolvant si la 
        valeur est brute ou s'il s'agit d'un nom de variable), alimente le 
        dictionnaire `settings` défini dans la portée parente, puis détruit la boîte 
        de dialogue pour débloquer l'exécution.
        """
        settings["variable"] = var_selection.get()
        
        # Résolution Directed
        if dir_controls["mode"].get() == "Manuel":
            settings["is_directed"] = dir_controls["manual"].get()
        else:
            settings["is_directed"] = dir_controls["var_name"].get()

        # Résolution Multi
        if multi_controls["mode"].get() == "Manuel":
            settings["is_multi"] = multi_controls["manual"].get()
        else:
            settings["is_multi"] = multi_controls["var_name"].get()

        dialog.destroy()

    tk.Button(main_frame, text="Importer le Graphe", command=confirm, 
              height=2, bg="#d1ffd1", font=('Arial', 10, 'bold')).pack(fill="x", pady=(10, 0))
    
    dialog.update_idletasks()
    dialog.geometry("")
    dialog.wait_window()
    return settings

def import_graph_from_python_resilient(file_path):
    """Analyse un fichier Python et en extrait les variables dictionnaires et booléennes.

    Cette fonction lit un script Python de manière résiliente en utilisant le module 
    `ast` (Abstract Syntax Tree). Elle isole chaque instruction au plus haut niveau 
    du code et l'exécute de manière indépendante. Si une ligne ou un bloc lève une 
    erreur (dépendance manquante, erreur d'exécution), il est ignoré afin de pouvoir 
    quand même récupérer les variables statiques (comme les dictionnaires de graphes) 
    déclarées ailleurs dans le fichier.

    Args:
        file_path (str): Le chemin absolu ou relatif vers le fichier Python à analyser.

    Returns:
        dict: Un dictionnaire contenant deux sous-dictionnaires :
            - `"dict_vars"` (dict): Les variables du script qui sont des dictionnaires 
              (hors variables système internes).
            - `"bool_vars"` (dict): Les variables du script qui sont des booléens.
            Renvoie un dictionnaire vide `{}` si le fichier ne peut pas être lu.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        # On analyse le code pour obtenir une liste d'instructions (nœuds)
        tree = ast.parse(source_code)
        
        # Dictionnaire qui contiendra les variables valides
        local_vars = {}

        for node in tree.body:
            try:
                # On compile et exécute chaque instruction isolément
                # mode='exec' permet d'exécuter l'instruction
                code_obj = compile(ast.Module(body=[node], type_ignores=[]), '<string>', 'exec')
                exec(code_obj, {}, local_vars)
            except Exception:
                # Si cette ligne foire (ex: division par zéro, import manquant), 
                # on passe simplement à la suivante.
                continue

        # Filtrage des dictionnaires (ton code habituel)
        dict_vars = {k: v for k, v in local_vars.items() if isinstance(v, dict) and not k.startswith("__")}
        bool_vars = {k: v for k, v in local_vars.items() if isinstance(v, bool) and not k.startswith("__")}
        
        return {"dict_vars": dict_vars, "bool_vars": bool_vars}

    except Exception as e:
        messagebox.showerror("Erreur de lecture", f"Impossible de lire le fichier : {e}")
        return {}

# importation depuis json ou python
def import_graph():
    """Gère l'interface d'importation de graphes depuis un fichier JSON ou Python.

    Ouvre une boîte de dialogue Tkinter (`askopenfilename`) permettant à l'utilisateur
    de sélectionner un fichier au format `.json` ou `.py`. 
    
    - Si le fichier est un JSON : Extrait directement la structure, l'orientation 
      et la multiplicité du graphe pour le reconstruire.
    - Si le fichier est un script Python : Appelle l'analyseur résilient pour lister 
      les variables, ouvre une fenêtre de dialogue pour laisser l'utilisateur choisir 
      la structure à importer, résout les types (orienté, multi, simple) et génère 
      le graphe adéquat.

    Returns:
        nx.Graph | nx.DiGraph | nx.MultiGraph | nx.MultiDiGraph | None: Le graphe 
        NetworkX initialisé et configuré selon les données importées, ou `None` 
        en cas d'erreur de lecture, de format non supporté ou d'annulation.
    """
    file_path = filedialog.askopenfilename(
        filetypes=[("Fichiers supportés", "*.json *.py"), ("JSON files", "*.json"), ("Python files", "*.py")],
        title="Importer un graphe"
    )
    if not file_path:
        return None

    if file_path.endswith('.json'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            graph_data = data.get("graph")
            is_multi = data.get("is_multigraph", False)
            is_dir = data.get("is_directed", False)
            graph_type = "MultiDiGraph" if is_multi and is_dir else "MultiGraph" if is_multi else "DiGraph" if is_dir else "Simple"
            G = create_graph(graph_type, graph_data)
            return G
        except Exception as e:
            messagebox.showerror("Erreur", "Le fichier JSON est corrompu ou n'est pas un projet valide.")
            return None
    elif file_path.endswith('.py'):
        try:
            vars_data = import_graph_from_python_resilient(file_path)
            dict_vars = vars_data.get("dict_vars", {})
            bool_vars = vars_data.get("bool_vars", {})

            if not dict_vars:
                messagebox.showerror("Erreur", "Aucun dictionnaire trouvé dans le fichier.")
                return None

            # 3. On demande à l'utilisateur de choisir la variable à utiliser et les options du graphe
            user_choices = ask_import_settings(list(dict_vars.keys()), list(bool_vars.keys()))

            if not user_choices["variable"]:
                return None

            # 4. Construction du type de graphe
            is_multi = user_choices["is_multi"] if isinstance(user_choices["is_multi"], bool) else bool_vars.get(user_choices["is_multi"], False)
            is_dir = user_choices["is_directed"] if isinstance(user_choices["is_directed"], bool) else bool_vars.get(user_choices["is_directed"], False)
            # print(f"DEBUG: {user_choices=}, {is_multi=}, {is_dir=}")
            graph_type = "MultiDiGraph" if is_multi and is_dir else "MultiGraph" if is_multi else "DiGraph" if is_dir else "Simple"
            
            # 5. Création
            graph_data = dict_vars[user_choices["variable"]]
            G = create_graph(graph_type, graph_data)
            return G

        except Exception as e:
            messagebox.showerror("Erreur Python", f"Impossible d'analyser le fichier : {e}")
            return None
    else:
        messagebox.showerror("Erreur", "Format de fichier non supporté.")
        return None

def export_graph_to_json(G):
    """Exporte la liste d'adjacence et les propriétés structurelles du graphe en JSON.

    Ouvre une boîte de dialogue Tkinter (`asksaveasfilename`) permettant à 
    l'utilisateur de choisir un emplacement de sauvegarde (extension `.json`). 
    La fonction génère ensuite un dictionnaire contenant la liste d'adjacence 
    du graphe (via `get_adjacency_list`) ainsi que des indicateurs booléens sur 
    son orientation et sa multiplicité, facilitant sa réimportation ultérieure.

    Args:
        G (nx.Graph | nx.DiGraph | nx.MultiGraph | nx.MultiDiGraph): Le graphe 
            NetworkX à exporter.
    """
    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        title="Exporter le graphe vers JSON"
    )
    data = {
        "graph": get_adjacency_list(G),
        "is_directed": G.is_directed(),
        "is_multigraph": isinstance(G, (nx.MultiGraph, nx.MultiDiGraph))
    }
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        messagebox.showinfo("Succès", "Graphe exporté avec succès !")
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'exporter : {e}")

def ask_export_settings(confirm_text="Exporter"):
    """Affiche une boîte de dialogue pour configurer l'exportation d'un graphe en code Python.

    Cette fonction ouvre une fenêtre modale (`Toplevel`) permettant à l'utilisateur 
    de choisir le nom de la variable cible et de décider s'il souhaite inclure 
    des métadonnées ou envelopper la structure du graphe dans une fonction Python. 
    Les champs de saisie sont validés pour s'assurer qu'ils respectent la syntaxe 
    des identifiants Python valides avant de fermer la fenêtre.

    Args:
        confirm_text (str, optional): Le texte à afficher sur le bouton de 
            validation. Valeur par défaut : "Exporter".

    Returns:
        dict: Un dictionnaire contenant les options d'exportation configurées :
            - `"variable_name"` (str | None): Le nom validé de la variable, ou `None` si annulé.
            - `"include_metadata"` (bool): True s'il faut ajouter les propriétés structurelles.
            - `"include_function"` (bool): True si le graphe doit être généré dans une fonction.
            - `"function_name"` (str): Le nom de la fonction d'exécution (si activée).
    """
    settings = {"variable_name": None}
    
    dialog = tk.Toplevel()
    dialog.title("Paramètres d'exportation")
    dialog.grab_set()

    # Conteneur principal pour appliquer un padding global
    main_frame = tk.Frame(dialog, padx=10, pady=10)
    main_frame.pack(fill="both", expand=True)

    # 1. Nom de la variable
    tk.Label(main_frame, text="Nom de la variable :").pack(pady=(0, 5))
    var_entry = tk.Entry(main_frame)
    var_entry.insert(0, "G") # Valeur par défaut
    var_entry.pack(pady=5)

    # 2. Métadonnées
    meta_var = tk.BooleanVar(value=True)
    tk.Checkbutton(main_frame, text="Inclure les métadonnées", variable=meta_var).pack(anchor="w")

    # 3. Section Fonction (Dynamique)
    func_var = tk.BooleanVar(value=False)
    tk.Checkbutton(main_frame, text="Inclure une fonction d'exécution", variable=func_var).pack(anchor="w")

    # Frame qui contient les champs de la fonction (cachée par défaut)
    func_extra_frame = tk.Frame(main_frame)
    
    tk.Label(func_extra_frame, text="Nom de la fonction :").pack(pady=(10, 0))
    func_name_entry = tk.Entry(func_extra_frame)
    func_name_entry.insert(0, "nom_fonction")
    func_name_entry.pack(pady=5)

    def toggle_func_fields(*args):
        """Affiche ou masque dynamiquement les champs de saisie de la fonction.

        Selon l'état de la case à cocher `func_var`, cette fonction injecte ou 
        retire les widgets du conteneur principal, puis force Tkinter à recalculer 
        la taille de la fenêtre de dialogue pour l'ajuster parfaitement au contenu.
        """
        if func_var.get():
            func_extra_frame.pack(fill="x", before=btn_confirm)
        else:
            func_extra_frame.pack_forget()
        
        # Astuce : Force la fenêtre à se redimensionner selon son contenu
        dialog.update_idletasks()
        dialog.geometry("") 

    # On surveille les changements de func_var
    func_var.trace_add("write", toggle_func_fields)

    def confirm():
        """Valide les saisies de l'utilisateur et enregistre la configuration.

        Vérifie que le nom de la variable (et celui de la fonction si elle est 
        activée) constituent des identifiants Python valides (pas d'espaces, de 
        caractères spéciaux interdits ou de départ par un chiffre). Si tout est 
        correct, met à jour le dictionnaire `settings` et détruit la pop-up.
        """
        var_name = var_entry.get().strip()
        func_name = func_name_entry.get().strip()
        
        if not var_name.isidentifier():
            messagebox.showerror("Erreur", "Le nom de la variable n'est pas valide.")
            return
        if func_var.get() and not func_name.isidentifier():
            messagebox.showerror("Erreur", "Le nom de la fonction n'est pas valide.")
            return

        settings.update({
            "variable_name": var_name,
            "include_metadata": meta_var.get(),
            "include_function": func_var.get(),
            "function_name": func_name
        })
        dialog.destroy()

    btn_confirm = tk.Button(main_frame, text=confirm_text, command=confirm, bg="#e1e1e1")
    btn_confirm.pack(pady=20)

    # Initialisation de la taille au départ
    dialog.update_idletasks()
    dialog.geometry("") 
    
    dialog.wait_window()
    return settings

def graph_to_python(G, confirm_text="Exporter"):
    """Génère une chaîne de caractères contenant le code Python représentant le graphe.

    Cette fonction récupère la liste d'adjacence du graphe, interroge l'utilisateur 
    via une boîte de dialogue pour obtenir ses préférences de nommage et d'options, 
    puis assemble dynamiquement les blocs de code. Elle peut inclure des variables de 
    métadonnées (orientation, multiplicité) et un exemple d'appel de fonction selon 
    la configuration choisie.

    Args:
        G (nx.Graph | nx.DiGraph | nx.MultiGraph | nx.MultiDiGraph): Le graphe 
            NetworkX à transcrire en code Python.
        confirm_text (str, optional): Le texte personnalisé à afficher sur le 
            bouton de la boîte de dialogue des paramètres. Valeur par défaut : "Exporter".

    Returns:
        str: Une chaîne de caractères multi-lignes contenant le code Python généré, 
            prêt à être sauvegardé ou affiché.
    """
    data = get_adjacency_list(G)
    settings = ask_export_settings(confirm_text=confirm_text)
    content = []

    if settings["include_metadata"]:
        content.append(f"is_directed = {G.is_directed()}")
        content.append(f"is_multigraph = {isinstance(G, (nx.MultiGraph, nx.MultiDiGraph))}\n")
    content.append(f"{settings['variable_name']} = {data}")
    if settings["include_function"]:
        content.append(f"print({settings['function_name']}({settings['variable_name']}))")

    return "\n".join(content)

def export_graph_to_python(G):
    """Génère le code Python du graphe et l'enregistre dans un script `.py`.

    Cette fonction ouvre une boîte de dialogue Tkinter (`asksaveasfilename`) pour 
    permettre à l'utilisateur de choisir l'emplacement et le nom de son futur script. 
    Elle appelle ensuite la fonction `graph_to_python` pour configurer et générer 
    le code source (contenant la liste d'adjacence et les métadonnées éventuelles) 
    avant d'écrire le tout dans le fichier de manière sécurisée.

    Args:
        G (nx.Graph | nx.DiGraph | nx.MultiGraph | nx.MultiDiGraph): Le graphe 
            NetworkX à exporter sous forme de script Python.
    """
    file_path = filedialog.asksaveasfilename(
        defaultextension=".py",
        filetypes=[("Python files", "*.py"), ("All files", "*.*")],
        title="Exporter le graphe vers Python"
    )

    content = graph_to_python(G)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        messagebox.showinfo("Succès", "Graphe exporté avec succès !")
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'exporter : {e}")

def copy_graph_to_clipboard_adjacency(G):
    """Convertit la liste d'adjacence du graphe en texte et la copie dans le presse-papiers.

    Génère le dictionnaire de la liste d'adjacence du graphe via `get_adjacency_list`, 
    le sérialise sous forme de chaîne de caractères, puis utilise la bibliothèque 
    `pyperclip` pour l'envoyer dans le presse-papiers du système. Une notification 
    visuelle informe l'utilisateur du succès ou de l'échec de l'opération.

    Args:
        G (nx.Graph | nx.DiGraph | nx.MultiGraph | nx.MultiDiGraph): Le graphe 
            NetworkX dont on souhaite copier la liste d'adjacence.
    """
    content = str(get_adjacency_list(G))
    try:
        pyperclip.copy(content)
        messagebox.showinfo("Succès", "Liste d'adjacence copiée dans le presse-papiers !")
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de copier : {e}")

def copy_graph_to_clipboard_python(G):
    """Génère le code Python du graphe et le copie dans le presse-papiers.

    Cette fonction appelle `graph_to_python` en configurant le bouton de validation 
    sur "Copier". Elle récupère le script Python généré (incluant potentiellement 
    les métadonnées et la structure enveloppée) et utilise la bibliothèque 
    `pyperclip` pour l'injecter dans le presse-papiers du système.

    Args:
        G (nx.Graph | nx.DiGraph | nx.MultiGraph | nx.MultiDiGraph): Le graphe 
            NetworkX à transcrire et à copier sous forme de code Python.
    """
    content = graph_to_python(G, confirm_text="Copier")
    try:
        pyperclip.copy(content)
        messagebox.showinfo("Succès", "Graphe copié dans le presse-papiers !")
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de copier : {e}")

def get_graph_type(G):
    """Détermine le type de graphe (Simple, Orienté, MultiGraph, MultiDiGraph) à partir d'une instance NetworkX."""
    if isinstance(G, nx.MultiDiGraph):
        return "MultiDiGraph"
    elif isinstance(G, nx.MultiGraph):
        return "MultiGraph"
    elif isinstance(G, nx.DiGraph):
        return "Orienté"
    else:
        return "Simple"

def create_graph(graph_type_str, data):
    """
    Instancie un objet graphe NetworkX spécifique en fonction du type demandé.

    Cette fonction convertit une structure de données (généralement une liste 
    d'adjacence) en un objet graphe utilisable par les algorithmes de NetworkX.

    Args:
        graph_type_str (str): Le type de graphe souhaité. 
            Options : "Simple", "Orienté", "MultiGraph". 
            Toute autre valeur retournera un "MultiDiGraph" par défaut.
        data (dict[str, list[str]]): Les données du graphe sous forme de 
            dictionnaire (nœud: liste de voisins).

    Returns:
        nx.Graph | nx.DiGraph | nx.MultiGraph | nx.MultiDiGraph: Une instance 
            de graphe correspondant au type spécifié.

    Example:
        >>> test_data = get_test_data()["Simple"]
        >>> G = create_graph("Simple", test_data)
        >>> type(G)
        <class 'networkx.classes.graph.Graph'>
    """
    if graph_type_str == "Simple": return nx.Graph(data)
    elif graph_type_str == "Orienté": return nx.DiGraph(data)
    elif graph_type_str == "MultiGraph": return nx.MultiGraph(data)
    else: return nx.MultiDiGraph(data)

def set_node_color(G, node, color):
    """
    Attribue une couleur spécifique à un nœud donné dans le graphe.

    Cette fonction modifie l'attribut de données 'color' du nœud. Cette valeur 
    sera ensuite utilisée lors du rendu visuel par la fonction de dessin.

    Args:
        G (nx.Graph | nx.DiGraph | nx.MultiGraph | nx.MultiDiGraph): L'instance du graphe NetworkX contenant le nœud.
        node (str | int): L'identifiant du nœud à modifier.
        color (str): Une chaîne représentant la couleur (ex: 'red', '#FF5733', 'blue').

    Returns:
        None: La fonction modifie le graphe en place.

    Example:
        >>> G = nx.Graph([('1', '2')])
        >>> set_node_color(G, '1', 'red')
        >>> print(G.nodes['1']['color'])
        'red'
    """
    if node in G:
        G.nodes[node]['color'] = color

def set_node_border_color(G, node, color):
    """
    Attribue une couleur de bordure spécifique à un nœud donné dans le graphe.

    Cette fonction modifie l'attribut de données 'border_color' du nœud. Cette 
    valeur peut être utilisée pour différencier visuellement les nœuds lors du rendu.

    Args:
        G (nx.Graph | nx.DiGraph | nx.MultiGraph | nx.MultiDiGraph): L'instance du graphe NetworkX contenant le nœud.
        node (str | int): L'identifiant du nœud à modifier.
        color (str): Une chaîne représentant la couleur de bordure (ex: 'black', '#333333').

    Returns:
        None: La fonction modifie le graphe en place.

    Example:
        >>> G = nx.Graph([('1', '2')])
        >>> set_node_border_color(G, '1', 'black')
        >>> print(G.nodes['1']['border_color'])
        'black'
    """
    if node in G:
        G.nodes[node]['border_color'] = color

def set_edge_color(G, u, v, color, key=0):
    """
    Attribue une couleur à une arête spécifique du graphe.

    Gère à la fois les graphes simples et les multigraphes. Pour les multigraphes, 
    l'identifiant 'key' permet de cibler une arête précise entre deux nœuds.

    Args:
        G (nx.Graph | nx.DiGraph | nx.MultiGraph | nx.MultiDiGraph): L'instance du graphe NetworkX.
        u (str | int): Le nœud source de l'arête.
        v (str | int): Le nœud destination de l'arête.
        color (str): La couleur à appliquer (ex: 'red', '#00FF00').
        key (int, optional): L'identifiant de l'arête (utile uniquement pour 
            les MultiGraph/MultiDiGraph). Par défaut à 0.

    Returns:
        None: La fonction modifie le graphe en place.

    Example:
        >>> G = nx.MultiGraph()
        >>> G.add_edge('A', 'B', key=0)
        >>> G.add_edge('A', 'B', key=1)
        >>> set_edge_color(G, 'A', 'B', 'blue', key=1)
    """
    if G.has_edge(u, v):
        if isinstance(G, (nx.MultiGraph, nx.MultiDiGraph)):
            G.edges[u, v, key]['color'] = color
        else:
            G.edges[u, v]['color'] = color

def reset_colors(G):
    """
    Réinitialise les couleurs de tous les nœuds et arêtes du graphe aux valeurs par défaut.

    Cette fonction parcourt l'intégralité du graphe pour harmoniser son apparence 
    en utilisant les constantes globales `NODE_COLOR` et `EDGE_COLOR`.

    Args:
        G (nx.Graph | nx.DiGraph | nx.MultiGraph | nx.MultiDiGraph): L'instance du graphe NetworkX à réinitialiser.

    Returns:
        None: La fonction modifie le graphe en place.

    Example:
        >>> set_node_color(G, '1', 'red')
        >>> reset_colors(G)
        >>> # Tous les éléments ont retrouvé leur couleur d'origine
    """
    for node in G.nodes(): G.nodes[node]['color'] = engine.NODE_COLOR 
    for node in G.nodes(): G.nodes[node]['border_color'] = engine.NODE_BORDER_COLOR
    for u, v, data in G.edges(data=True): data['color'] = engine.EDGE_COLOR

def split_dico(dico):
    """
    Transforme un dictionnaire de listes en une liste de dictionnaires unitaires.

    Cette fonction "éclate" les valeurs du dictionnaire. Si les listes de valeurs 
    sont de longueurs inégales, les entrées manquantes sont complétées par `None`.

    Args:
        dico (dict[str, list]): Un dictionnaire où chaque clé pointe vers une 
            liste d'éléments (ex: des attributs de nœuds ou d'arêtes).

    Returns:
        list[dict]: Une liste de dictionnaires. Le i-ème dictionnaire contient 
            le i-ème élément de chaque liste du dictionnaire d'origine.

    Example:
        >>> data = {"A": [1, 2], "B": [10, 20, 30]}
        >>> split_dico(data)
        [
            {"A": 1, "B": 10},
            {"A": 2, "B": 20},
            {"A": None, "B": 30}
        ]
    """
    return [{key: (values[i] if i < len(values) else None) for key, values in dico.items()} for i in range(max(len(v) for v in dico.values()))]

def create_submenu(parent_menu, submenu_dict):
    """
    Génère de manière récursive une hiérarchie de menus Tkinter à partir d'un dictionnaire.

    Si une valeur dans le dictionnaire est elle-même un dictionnaire, la fonction 
    crée un sous-menu (cascade). Sinon, elle crée une commande finale (bouton).

    Args:
        parent_menu (tk.Menu): L'objet menu parent (barre de menu ou sous-menu) 
            auquel les éléments seront attachés.
        submenu_dict (dict[str, dict | callable]): Un dictionnaire où :
            - La clé est le libellé (label) affiché dans le menu.
            - La valeur est soit une fonction (command) à exécuter, soit un 
              dictionnaire pour définir un nouveau niveau de sous-menu.

    Returns:
        None: La fonction modifie l'objet `parent_menu` par effet de bord.

    Example:
        >>> menu_config = {
        ...     "Fichier": {"Ouvrir": action_ouvrir, "Quitter": root.quit},
        ...     "Aide": {"A propos": action_propos}
        ... }
        >>> create_submenu(barre_menu, menu_config)
    """
    for label, command in submenu_dict.items():
        if isinstance(command, dict):
            submenu = tk.Menu(parent_menu, tearoff=0)
            create_submenu(submenu, command)
            parent_menu.add_cascade(label=label, menu=submenu)
        else:
            parent_menu.add_command(label=label, command=command)

def distance_point_to_segment(p, v, w):
    """Calcule la distance la plus courte entre un point et un segment de droite.

    Cette fonction détermine la distance minimale entre un point `p` et un segment 
    délimité par deux points `v` et `w`. Elle utilise la projection orthogonale 
    du point sur la droite contenant le segment, en restreignant le facteur de 
    projection `t` à l'intervalle `[0, 1]` pour s'assurer que la projection reste 
    bien sur le segment lui-même (et non sur son prolongement).

    Args:
        p (array_like): Les coordonnées du point cible (ex: `[x, y]` ou `(x, y)`).
        v (array_like): Les coordonnées du premier sommet du segment.
        w (array_like): Les coordonnées du second sommet du segment.

    Returns:
        float: La distance euclidienne minimale entre le point `p` et le segment `[v, w]`.
    """
    p, v, w = np.array(p), np.array(v), np.array(w)
    if np.all(v == w): return np.linalg.norm(p - v)
    l2 = np.sum((v - w)**2)
    t = max(0, min(1, np.dot(p - v, w - v) / l2))
    projection = v + t * (w - v)
    return np.linalg.norm(p - projection)

def distance_point_to_arc(p, v, w, rad):
    """Calcule la distance la plus courte entre un point et un arc de cercle.

    Cette fonction modélise un arc de cercle reliant les sommets `v` et `w` avec 
    une courbure définie par `rad` (similaire à l'approche `arc3` de Matplotlib). 
    Si la courbure est presque nulle, elle bascule automatiquement sur un calcul 
    de distance par rapport à un segment droit. Elle valide également si le point 
    cible se trouve du bon côté de la corde et dans les limites géométriques de l'arc.

    Args:
        p (array_like): Les coordonnées du point cible (ex: `[x, y]` ou `(x, y)`).
        v (array_like): Les coordonnées du point de départ de l'arc.
        w (array_like): Les coordonnées du point d'arrivée de l'arc.
        rad (float): Le facteur de courbure de l'arc (le rayon et le sens dépendent de sa valeur).

    Returns:
        float: La distance minimale entre le point `p` et l'arc de cercle, 
            ou `float('inf')` si le point est hors des limites ou du mauvais côté de l'arc.
    """
    if abs(rad) < 0.005: # Seuil de tolérance pour considérer l'arc comme une droite
        return distance_point_to_segment(p, v, w)
    
    p, v, w = np.array(p), np.array(v), np.array(w)
    chord = w - v
    L = np.linalg.norm(chord)
    if L < 1e-6: return np.linalg.norm(p - v)

    # 1. Calcul de la géométrie de l'arc (identique à Matplotlib arc3)
    h = rad * L / 2.0
    R = ((L**2 / 4.0) + h**2) / (2.0 * h)
    
    midpoint = (v + w) / 2.0
    # Vecteur perpendiculaire à la corde
    perp = np.array([-chord[1], chord[0]]) / L
    center = midpoint + perp * (R - h)
    
    # 2. Distance au cercle complet
    dist_to_circle = abs(np.linalg.norm(p - center) - abs(R))

    # 3. Validation : Le point doit être du même côté de la corde que l'arc
    # On utilise le signe du produit vectoriel 2D
    def get_side(point, start, end):
        """Calcule la position relative d'un point par rapport à une droite orientée.

        Utilise la composante Z du produit vectoriel 2D pour déterminer si le point 
        se trouve à gauche, à droite ou sur la droite reliant `start` à `end`.

        Args:
            point (np.ndarray): Le point à tester.
            start (np.ndarray): Le point d'origine du vecteur de référence.
            end (np.ndarray): Le point d'arrivée du vecteur de référence.

        Returns:
            float: Une valeur positive si le point est d'un côté, négative de l'autre, 
                et 0 s'ils sont parfaitement colinéaires.
        """
        return (end[1] - start[1]) * (point[0] - start[0]) - (end[0] - start[0]) * (point[1] - start[1])

    side_arc = np.sign(rad)
    side_point = np.sign(get_side(p, v, w))

    # Si le point n'est pas du côté de la courbure, on rejette (hitbox fantôme sur la corde)
    if side_point != side_arc and abs(rad) > 0.01:
        return float('inf')

    # 4. Vérification des limites de l'arc (ne pas dépasser les nœuds)
    # On vérifie si la projection du point sur la corde est bien entre v et w
    dot_product = np.dot(p - v, w - v) / (L**2)
    if 0 <= dot_product <= 1:
        return dist_to_circle
    
    return float('inf')

def get_element_under_mouse(event, G, positions):
    """Identifie le nœud ou l'arête du graphe situé sous le curseur de la souris.

    Cette fonction analyse la position du curseur lors d'un événement Matplotlib. 
    Elle effectue d'abord une recherche de collision avec les nœuds (prioritaires) 
    en calculant la distance euclidienne. Si aucun nœud n'est survolé, elle teste 
    la proximité avec les arêtes en prenant en compte la courbure dynamique (arcs) 
    si le graphe est un multigraph, ou des segments droits classiques sinon. Les 
    seuils de tolérance dépendent des dimensions graphiques définies dans `engine`.

    Args:
        event (matplotlib.backend_bases.MouseEvent): L'événement de souris capturé 
            par Matplotlib (clic, survol, etc.).
        G (nx.Graph | nx.DiGraph | nx.MultiGraph | nx.MultiDiGraph): Le graphe 
            NetworkX affiché à l'écran.
        positions (dict): Un dictionnaire associant chaque nœud à ses coordonnées 
            2D `[x, y]`.

    Returns:
        dict: Un dictionnaire contenant l'élément détecté sous la forme :
            - `"node"` (Hashable | None): L'identifiant du nœud survolé, ou `None`.
            - `"edge"` (tuple | None): L'arête survolée sous forme de tuple `(u, v)` 
              ou `(u, v, key)` pour un multigraph, ou `None` si rien n'est détecté.
    """
    if event.inaxes is None or event.xdata is None or event.ydata is None:
        return {"node": None, "edge": None}

    mouse_pos = (event.xdata, event.ydata)
    
    # Sensibilité basée sur vos constantes globales
    edge_sensitivity = engine.EDGE_WIDTH / 100.0 # Ajustez en fonction de l'épaisseur des arêtes dans votre dessin
    node_sensitivity = engine.NODE_SIZE / 5000.0 # Ajustez en fonction de la taille des nœuds dans votre dessin

    # 1. Nœuds
    for node, pos in positions.items():
        if math.hypot(mouse_pos[0] - pos[0], mouse_pos[1] - pos[1]) < node_sensitivity:
            # print(math.hypot(mouse_pos[0] - pos[0], mouse_pos[1] - pos[1]))
            return {"node": node, "edge": None}

    # 2. Arêtes
    closest_edge, min_dist = None, float('inf')
    is_multi = G.is_multigraph()
    edges_to_check = G.edges(keys=True) if is_multi else G.edges()

    for edge_data in edges_to_check:
        u, v = edge_data[0], edge_data[1]
        
        if is_multi:
            # Synchronisation automatique via engine
            rad = engine.calculate_edge_rad(u, v, edge_data[2], positions)
            dist = distance_point_to_arc(mouse_pos, positions[u], positions[v], rad)
        else:
            dist = distance_point_to_segment(mouse_pos, positions[u], positions[v])
        
        if dist < edge_sensitivity and dist < min_dist:
            min_dist = dist
            closest_edge = edge_data

    return {"node": None, "edge": closest_edge}

def get_next_available_id(G):
    """Détermine le plus petit identifiant entier positif disponible pour un nouveau nœud.

    Cette fonction parcourt tous les sommets existants du graphe et isole ceux dont 
    l'identifiant est un entier (ou convertible en entier). Elle cherche ensuite, 
    par incrémentation successive à partir de 1, le premier nombre entier qui n'est 
    pas encore utilisé comme identifiant, garantissant ainsi l'absence de doublons.

    Args:
        G (nx.Graph | nx.DiGraph | nx.MultiGraph | nx.MultiDiGraph): Le graphe 
            NetworkX dans lequel le nouveau nœud sera inséré.

    Returns:
        str: Le plus petit identifiant numérique disponible, converti sous 
            forme de chaîne de caractères (ex: `"1"`, `"2"`, etc.).
    """
    # On extrait les IDs actuels en les convertissant en entiers
    # On filtre les IDs qui ne sont pas transformables en int pour éviter les crashs
    current_ids = set()
    for n in G.nodes():
        try:
            current_ids.add(int(n))
        except ValueError:
            continue
    
    new_id = 1
    while new_id in current_ids:
        new_id += 1
    return str(new_id)

def reindex_multigraph_edges(G):
    """Réindexe de manière séquentielle les clés des arêtes d'un multigraphe.

    Cette fonction supprime temporairement toutes les arêtes du multigraphe pour les 
    réinsérer une à une en réinitialisant leurs clés de distinction (`key`) à partir 
    de 0 pour chaque paire de sommets `(u, v)`. Cela permet de "boucher les trous" 
    dans les index après des suppressions d'arêtes multiples, garantissant un 
    séquençage propre (0, 1, 2, ...). Les attributs associés à chaque arête sont préservés.

    Args:
        G (nx.Graph | nx.DiGraph | nx.MultiGraph | nx.MultiDiGraph): Le graphe 
            NetworkX à réindexer. La fonction n'agit que s'il s'agit d'un `MultiGraph` 
            ou d'un `MultiDiGraph`.

    Returns:
        bool: `True` si au moins une arête a changé d'index (de clé), 
            `False` si aucune modification n'a été nécessaire ou si le graphe n'est 
            pas un multigraphe.
    """
    if not isinstance(G, (nx.MultiGraph, nx.MultiDiGraph)):
        return False

    # On récupère toutes les arêtes avec leurs données
    edges = list(G.edges(keys=True, data=True))
    G.remove_edges_from(edges)
    
    has_changed = False
    next_key = {}

    for u, v, old_key, data in edges:
        pair = (u, v)
        new_key = next_key.get(pair, 0)
        
        # Si la nouvelle clé est différente de l'ancienne, on marque le changement
        if new_key != old_key:
            has_changed = True
            
        G.add_edge(u, v, key=new_key, **data)
        next_key[pair] = new_key + 1
        
    return has_changed

def on_pick(event, canvas_matplotlib, G, draw_layout, positions=None):
    pass

def on_press(event, canvas_matplotlib, getter, setter):
    """Gère l'événement de pression du clic de souris sur le canevas de dessin.

    Cette fonction est déclenchée lorsque l'utilisateur clique sur le graphique. 
    Elle met à jour l'état global en signalant que le bouton est enfoncé et 
    identifie l'élément (nœud ou arête) situé sous le curseur. Si un nœud est 
    cliqué, elle calcule un décalage géométrique (`offset_x`, `offset_y`) entre 
    les coordonnées exactes du nœud et la position du clic afin de garantir 
    un déplacement fluide lors d'un futur glisser-déplacer (*drag*).

    Args:
        event (matplotlib.backend_bases.MouseEvent): L'événement de clic de 
            souris fourni par Matplotlib.
        canvas_matplotlib (matplotlib.backends.backend_tkagg.FigureCanvasTkAgg): Le 
            canevas Matplotlib intégré dans l'interface Tkinter.
        getter (callable): Une fonction de rappel (*callback*) retournant le 
            dictionnaire d'état actuel de l'application (contenant `"G"`, 
            `"positions"`, etc.).
        setter (callable): Une fonction de rappel (*callback*) permettant de 
            mettre à jour partiellement le dictionnaire d'état de l'application.
    """
    if event.xdata is None or event.ydata is None: return
    setter({"mouse_down": True})
    variables = getter()
    G = variables["G"]
    positions = variables["positions"]

    elements = get_element_under_mouse(event, G, positions)
    
    # On met à jour l'état avec le nœud ou l'arête cliquée
    setter({
        "clicked_node": elements["node"],
        "clicked_edge": elements["edge"]
    })
    
    
    # Logique d'offset pour le drag (seulement pour les nœuds)
    if elements["node"] is not None:
        ax = event.inaxes
        nodes_col = next(c for c in ax.get_children() if isinstance(c, plt.matplotlib.collections.PathCollection))
        try:
            node_index = list(G.nodes()).index(elements["node"])
        except ValueError:
            print(f"\033[38;2;255;0;0mWarning: Node {elements['node']} not found in graph nodes list.\033[0m")
            setter({"offset_x": 0, "offset_y": 0})
            return
        node_x, node_y = nodes_col.get_offsets()[node_index]
        setter({"offset_x": node_x - event.xdata, "offset_y": node_y - event.ydata})
    
    # variables = getter()

    print(f"clicked node : {elements['node']}, clicked edge : {elements['edge']}")

def on_release(event, canvas_matplotlib, getter, setter):
    """Gère l'événement de relâchement du clic de souris sur le canevas.

    Cette fonction est déclenchée lorsque l'utilisateur relâche le bouton de la 
    souris. Elle désactive l'indicateur de clic enfoncé et exécute des actions 
    spécifiques selon le mode interactif actuellement sélectionné dans l'application :

    - **Mode "add"** : Crée un nœud isolé (clic et relâchement dans le vide), 
      ajoute un nœud lié à un autre (drag depuis un nœud vers le vide) ou crée 
      une arête entre deux nœuds existants (drag d'un nœud à un autre).
    - **Mode "delete"** : Supprime le nœud ou l'arête se trouvant sous le curseur 
      au moment du relâchement, puis réindexe proprement les clés si c'est un multigraphe.
    - **Mode "color"** : Applique la couleur sélectionnée au nœud ou à l'arête 
      survolée. Si la touche Shift est enfoncée, modifie la bordure du nœud au lieu 
      de son arrière-plan.
    - **Modes "select_bfs_root" / "select_dfs_root"** : Identifie le nœud sélectionné 
      comme racine pour lancer l'algorithme de parcours associé (BFS ou DFS), puis 
      bascule l'interface en mode "move" pour geler les modifications pendant l'exécution.

    Après chaque modification structurelle ou visuelle, la figure Matplotlib est 
    redessinée de manière asynchrone (`draw_idle`).

    Args:
        event (matplotlib.backend_bases.MouseEvent): L'événement de relâchement de 
            souris fourni par Matplotlib.
        canvas_matplotlib (matplotlib.backends.backend_tkagg.FigureCanvasTkAgg): Le 
            canevas Matplotlib intégré dans l'interface Tkinter.
        getter (callable): Une fonction de rappel (*callback*) retournant le 
            dictionnaire d'état actuel de l'application.
        setter (callable): Une fonction de rappel (*callback*) permettant de 
            mettre à jour l'état de l'application.
    """
    variables = getter()
    if not variables["mouse_down"]: return
    setter({"mouse_down": False})
    if event.xdata is None or event.ydata is None: return

    variables = getter()
    G = variables["G"]
    positions = variables["positions"]
    

    elements = get_element_under_mouse(event, G, positions)

    # On met à jour l'état avec le nœud ou l'arête cliquée
    setter({
        "released_node": elements["node"],
        "released_edge": elements["edge"]
    })

    variables = getter()

    print(f"released node : {elements['node']}, released edge : {elements['edge']}")

    if variables["mode"] == "add":
        c_node = variables.get("clicked_node")
        r_node = variables.get("released_node")

        # clic dans le vide et relâche dans le vide => création d'un nœud
        if c_node is None and r_node is None:
            new_node = get_next_available_id(G)
            G.add_node(new_node)
            positions[new_node] = (event.xdata, event.ydata)
            print(f"Added node {new_node} at position ({event.xdata}, {event.ydata})")
        
        # clic sur un nœud et relâche dans le vide => création d'un nœud + arête
        elif c_node is not None and r_node is None:
            new_node = get_next_available_id(G)
            G.add_node(new_node)
            G.add_edge(c_node, new_node)
            positions[new_node] = (event.xdata, event.ydata)
            print(f"Added node {new_node} and edge ({c_node}, {new_node}) at position ({event.xdata}, {event.ydata})")
        
        # clic sur un nœud et relâche sur un autre nœud => création d'une arête
        elif c_node is not None and r_node is not None and c_node != r_node:
            G.add_edge(c_node, r_node)
            print(f"Added edge ({c_node}, {r_node})")
        
        # mise à jour de la figure après modification du graphe
        fig = event.canvas.figure
        engine.draw_graph_to_fig(G, layout_name=variables.get("draw_layout"), fig=fig, positions=positions)
        event.canvas.draw_idle()
    elif variables["mode"] == "delete": # suppression uniquement au relâchement du clic si aucun mouvement de souris
        modified = False

        # suppression du nœud relâché, sinon suppression de l'arête relâchée
        if elements["node"] is not None and elements["node"] in G:
            G.remove_node(elements["node"])
            if elements["node"] in positions:
                del positions[elements["node"]]
            print(f"Deleted node {elements['node']}")
            modified = True
        
        elif elements["edge"] is not None:
            u, v = elements["edge"][0], elements["edge"][1]
            # si c'est un multigraphe, il faut aussi le key pour identifier l'arête
            if G.is_multigraph():
                key = elements["edge"][2]
                G.remove_edge(u, v, key=key)
                print(f"Deleted edge ({u}, {v}, {key})")
            else:
                G.remove_edge(u, v)
                print(f"Deleted edge ({u}, {v})")
            modified = True
        
        # réindexation des arêtes pour les multigraphes après suppression
        if G.is_multigraph():
            modified = modified or reindex_multigraph_edges(G)
        
        # mise à jour de la figure après modification du graphe
        if modified:
            fig = event.canvas.figure
            engine.draw_graph_to_fig(G, layout_name=variables.get("draw_layout"), fig=fig, positions=positions)
            event.canvas.draw_idle()
    elif variables["mode"] == "color":
        modified = False

        # colorisation du nœud relâché, sinon colorisation de l'arête relâchée
        if elements["node"] is not None and elements["node"] in G:
            if variables["shift_pressed"]: # avec shift => colorisation de la bordure au lieu du remplissage
                set_node_border_color(G, elements["node"], variables["current_color"])
            else:
                set_node_color(G, elements["node"], variables["current_color"])
            print(f"Colored node {elements['node']} in {variables['current_color']}")
            modified = True
        
        elif elements["edge"] is not None:
            u, v = elements["edge"][0], elements["edge"][1]
            # si c'est un multigraphe, il faut aussi le key pour identifier l'arête
            if G.is_multigraph():
                key = elements["edge"][2]
                set_edge_color(G, u, v, variables["current_color"], key=key)
                print(f"Colored edge ({u}, {v}, {key}) in {variables['current_color']}")
            else:
                set_edge_color(G, u, v, variables["current_color"])
                print(f"Colored edge ({u}, {v}) in {variables['current_color']}")
            modified = True
        
        # mise à jour de la figure après modification du graphe
        if modified:
            fig = event.canvas.figure
            engine.draw_graph_to_fig(G, layout_name=variables.get("draw_layout"), fig=fig, positions=positions)
            event.canvas.draw_idle()
    elif variables["mode"] == "select_bfs_root":
        if elements["node"] is not None:
            # On remet temporairement le mode sur "move" (ou un mode neutre) pour bloquer les clics pendant l'algo
            setter({"mode": "move"}) 
            getter()["bfs_valid"](elements["node"])
        return
    elif variables["mode"] == "select_dfs_root":
        if elements["node"] is not None:
            # On remet temporairement le mode sur "move" (ou un mode neutre) pour bloquer les clics pendant l'algo
            setter({"mode": "move"}) 
            getter()["dfs_valid"](elements["node"])
        return


def on_motion(event, canvas_matplotlib, getter, setter):
    """Gère l'événement de mouvement de la souris sur le canevas de dessin.

    Cette fonction assure deux rôles principaux selon l'état de la souris :
    1. **En permanence (survol)** : Identifie le nœud ou l'arête se trouvant sous le 
       curseur pour mettre à jour l'état de survol (`hovered_node`, `hovered_edge`).
    2. **Bouton enfoncé (glisser / drag)** : Exécute des actions continues selon le 
       mode interactif sélectionné :
       - **Mode "move"** : Déplace le nœud cliqué en mettant à jour ses coordonnées 
         2D à l'aide de la position de la souris et de l'offset de capture calculé 
         au clic initial.
       - **Mode "delete"** : Agit comme une gomme en supprimant à la volée tout nœud 
         ou arête survolé pendant le déplacement.
       - **Mode "color"** : Agit comme un pinceau en colorant en continu les éléments 
         survolés avec la couleur active (remplissage ou bordure selon la touche Shift).

    En cas de modification en continu, la figure Matplotlib est redessinée de manière 
    asynchrone et optimisée à l'aide de `draw_idle`.

    Args:
        event (matplotlib.backend_bases.MouseEvent): L'événement de mouvement de 
            souris fourni par Matplotlib.
        canvas_matplotlib (matplotlib.backends.backend_tkagg.FigureCanvasTkAgg): Le 
            canevas Matplotlib intégré dans l'interface Tkinter.
        getter (callable): Une fonction de rappel (*callback*) retournant le 
            dictionnaire d'état actuel de l'application.
        setter (callable): Une fonction de rappel (*callback*) permettant de 
            mettre à jour l'état de l'application.
    """
    variables = getter()

    G = variables["G"]
    positions = variables["positions"]
    draw_layout = variables["draw_layout"]

    elements = get_element_under_mouse(event, G, positions)
    
    
    # if elements["node"] != variables.get("hovered_node") or elements["edge"] != variables.get("hovered_edge"):
    #     print(f"hovered node : {elements['node']}, hovered edge : {elements['edge']}")

    # On met à jour le nœud survolé dans le main
    setter({
        "hovered_node": elements["node"],
        "hovered_edge": elements["edge"]
    })

    if not variables["mouse_down"]: return
    if event.xdata is None or event.ydata is None: return

    # MOVE NODE
    if variables["mode"]=="move":
        if variables["clicked_node"] is None: return
        # Mise à jour de la position du nœud avec les coordonnées de la souris + offset
        node = variables["clicked_node"]
        positions[node] = (event.xdata + variables["offset_x"], event.ydata + variables["offset_y"])

        # On récupère la figure et on redessine
        fig = canvas_matplotlib.figure
        engine.draw_graph_to_fig(G, layout_name=draw_layout, fig=fig, positions=positions)
        
        # refresh du canvas
        canvas_matplotlib.draw_idle()
    elif variables["mode"]=="delete":
        if not variables["mouse_down"] : return # suppression uniquement au maintient du clic

        # suppression du nœud survolé, sinon suppression de l'arête survolée
        if elements["node"] is not None and elements["node"] in G:
            G.remove_node(elements["node"])
            if elements["node"] in positions:
                del positions[elements["node"]]
            print(f"Deleted node {elements['node']}")

        elif elements["edge"] is not None:
            u, v = elements["edge"][0], elements["edge"][1]
            # si c'est un multigraphe, il faut aussi le key pour identifier l'arête
            if G.is_multigraph():
                key = elements["edge"][2]
                G.remove_edge(u, v, key=key)
                print(f"Deleted edge ({u}, {v}, {key})")
            else:
                G.remove_edge(u, v)
                print(f"Deleted edge ({u}, {v})")
            # refresh du canvas
            canvas_matplotlib.draw_idle()
        
        # mise à jour de la figure après modification du graphe
        fig = canvas_matplotlib.figure
        engine.draw_graph_to_fig(G, layout_name=draw_layout, fig=fig, positions=positions)
        canvas_matplotlib.draw_idle()
    elif variables["mode"] == "color":
        if not variables["mouse_down"] : return # colorisation uniquement au maintient du clic

        # colorisation du nœud survolé, sinon colorisation de l'arête survolée
        if elements["node"] is not None and elements["node"] in G:
            if variables["shift_pressed"]: # avec shift => colorisation de la bordure au lieu du remplissage
                set_node_border_color(G, elements["node"], variables["current_color"])
            else:
                set_node_color(G, elements["node"], variables["current_color"])
            print(f"Colored node {elements['node']} in {variables['current_color']}")
        
        elif elements["edge"] is not None:
            u, v = elements["edge"][0], elements["edge"][1]
            # si c'est un multigraphe, il faut aussi le key pour identifier l'arête
            if G.is_multigraph():
                key = elements["edge"][2]
                set_edge_color(G, u, v, variables["current_color"], key=key)
                print(f"Colored edge ({u}, {v}, {key}) in {variables['current_color']}")
            else:
                set_edge_color(G, u, v, variables["current_color"])
                print(f"Colored edge ({u}, {v}) in {variables['current_color']}")

        # mise à jour de la figure après modification du graphe
        fig = canvas_matplotlib.figure
        engine.draw_graph_to_fig(G, layout_name=draw_layout, fig=fig, positions=positions)
        canvas_matplotlib.draw_idle()
    

    # print(f"Souris en mouvement sur la figure aux coordonnées ({event.x}, {event.y})")

def on_key_press(event, setter, getter):
    """Gère l'événement d'enfoncement d'une touche du clavier.

    Cette fonction détecte l'activation de touches spécifiques pour modifier 
    le comportement de l'interface ou des outils en temps réel. Par exemple, 
    lorsque la touche Shift est enfoncée, elle passe l'indicateur `shift_pressed` 
    à `True` dans l'état global, ce qui permet à d'autres outils (comme le mode 
    de colorisation) d'adapter leurs actions (ex: colorer la bordure plutôt que 
    le fond du nœud).

    Args:
        event (matplotlib.backend_bases.KeyEvent): L'événement clavier capturé 
            par Matplotlib contenant la touche manipulée.
        setter (callable): Une fonction de rappel (*callback*) permettant de 
            mettre à jour l'état de l'application.
        getter (callable): Une fonction de rappel (*callback*) retournant le 
            dictionnaire d'état actuel de l'application.
    """
    if event.key == "shift":
        setter({"shift_pressed": True})

def on_key_release(event, setter, getter):
    """Gère l'événement de relâchement d'une touche du clavier.

    Cette fonction intercepte le moment où l'utilisateur relâche une touche pour 
    rétablir le comportement par défaut de l'interface. En particulier, lorsque 
    la touche Shift est relâchée, l'indicateur `shift_pressed` repasse à `False` 
    dans l'état global, désactivant ainsi les actions secondaires associées à 
    cette touche (comme la colorisation des bordures de nœuds).

    Args:
        event (matplotlib.backend_bases.KeyEvent): L'événement clavier capturé 
            par Matplotlib contenant la touche qui vient d'être relâchée.
        setter (callable): Une fonction de rappel (*callback*) permettant de 
            mettre à jour l'état de l'application.
        getter (callable): Une fonction de rappel (*callback*) retournant le 
            dictionnaire d'état actuel de l'application.
    """
    if event.key == "shift":
        setter({"shift_pressed": False})

def create_graph_canvas(fig, root, G, setter, getter, draw_layout=None, positions=None):
    """Initialise le canevas Matplotlib dans Tkinter et y connecte tous les événements interactifs.

    Cette fonction crée le pont entre Matplotlib et l'interface graphique Tkinter 
    à l'aide de `FigureCanvasTkAgg`. Elle intègre le composant visuel dans la fenêtre 
    principale (`root`) avec un redimensionnement élastique (`expand=True`), puis 
    lie les événements natifs de Matplotlib (clics, relâchements, mouvements de souris 
    et pressions de touches clavier) à leurs fonctions de rappel (*callbacks*) respectives.

    Args:
        fig (matplotlib.figure.Figure): La figure Matplotlib contenant le dessin du graphe.
        root (tk.Tk | tk.Frame): Le composant parent Tkinter dans lequel le canevas doit être injecté.
        G (nx.Graph | nx.DiGraph | nx.MultiGraph | nx.MultiDiGraph): Le graphe NetworkX sous-jacent.
        setter (callable): La fonction de rappel permettant de modifier l'état global.
        getter (callable): La fonction de rappel permettant de lire l'état global.
        draw_layout (str, optional): Le nom de la disposition de graphe par défaut à utiliser. 
            Valeur par défaut : None.
        positions (dict, optional): Le dictionnaire initial des coordonnées `[x, y]` des nœuds. 
            Valeur par défaut : None.

    Returns:
        matplotlib.backends.backend_tkagg.FigureCanvasTkAgg: L'objet canevas Matplotlib créé, 
            permettant de piloter les rafraîchissements futurs de l'affichage.
    """
    canvas_matplotlib = FigureCanvasTkAgg(fig, master=root)
    canvas_widget = canvas_matplotlib.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    # On connecte l'événement
    data = (canvas_matplotlib, getter, setter)
    canvas_matplotlib.mpl_connect('pick_event', lambda event: on_pick(event, canvas_matplotlib, G, draw_layout, positions))
    canvas_matplotlib.mpl_connect('button_press_event', lambda event: on_press(event, *data))
    canvas_matplotlib.mpl_connect('button_release_event', lambda event: on_release(event, *data))
    canvas_matplotlib.mpl_connect('motion_notify_event', lambda event: on_motion(event, *data))
    canvas_matplotlib.mpl_connect('key_press_event', lambda event: on_key_press(event, setter, getter))
    canvas_matplotlib.mpl_connect('key_release_event', lambda event: on_key_release(event, setter, getter))

    return canvas_matplotlib

def delete_graph_canvas(canvas):
    """Supprime et détruit le canevas Matplotlib de l'interface graphique.

    Cette fonction vérifie si le canevas existe, puis détruit physiquement le 
    widget Tkinter associé (`get_tk_widget().destroy()`). C'est une étape cruciale 
    pour garantir une gestion propre de la mémoire et éviter les erreurs de 
    redessin lors du remplacement ou de la suppression de la zone d'affichage du graphe.

    Args:
        canvas (matplotlib.backends.backend_tkagg.FigureCanvasTkAgg | None): Le 
            canevas à supprimer, ou `None` si aucun canevas n'est actuellement actif.
    """
    if canvas is not None:
        canvas.get_tk_widget().destroy()

if __name__ == "__main__":
    dico = {"A": [1, 2, 3], "B": [4, 5], "C": [6]}
    print(split_dico(dico))
