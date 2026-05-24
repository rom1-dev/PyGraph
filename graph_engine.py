# -*- coding: utf-8 -*-
# Copyright (c) 2026 Romain "rom1-dev" FAGONDE
# Distributed under the terms of the MIT License.

import networkx as nx
import matplotlib.pyplot as plt
import math


NODE_COLOR = '#99CCFF'
EDGE_COLOR = '#00CCCC'
NODE_BORDER_COLOR = '#FF6633'

NODE_SIZE = 500
EDGE_WIDTH = 2

def get_layouts():
    """
    Fournit une correspondance entre des noms de styles et les algorithmes 
    de disposition (layout) de NetworkX.

    Cette fonction centralise les algorithmes de positionnement disponibles 
    pour assurer une cohérence visuelle lors du dessin des graphes.

    Returns:
        dict[str, callable]: Un dictionnaire où les clés sont les noms des layouts 
            (ex: 'spring', 'circular') et les valeurs sont les fonctions 
            correspondantes de la bibliothèque NetworkX.

    Example:
        >>> layouts = get_layouts()
        >>> pos = layouts['circular'](mon_graphe)
    """
    return {
        "spring": nx.spring_layout,
        "circular": nx.circular_layout,
        "random": nx.random_layout,
        "shell": nx.shell_layout,
        "kamada_kawai": nx.kamada_kawai_layout
    }

def calculate_edge_rad(u, v, key, pos, base_rad=0.15):
    """Calcule le facteur de courbure (`rad`) pour une arête dans un multigraphe.

    Cette fonction détermine la courbure nécessaire pour dessiner plusieurs arêtes 
    reliant les mêmes sommets sans qu'elles ne se chevauchent. Elle utilise une 
    logique d'alternance symétrique autour de 0 (0, +rad, -rad, +2rad, -2rad, ...) 
    et normalise la valeur en fonction de la distance euclidienne entre les nœuds 
    `u` et `v` pour maintenir une courbure visuellement cohérente, quelle que 
    soit la longueur du lien.

    Args:
        u (Hashable): Identifiant du premier nœud.
        v (Hashable): Identifiant du second nœud.
        key (int): Clé unique de l'arête dans le multigraphe (utilisée pour 
            différencier les arêtes parallèles).
        pos (dict): Dictionnaire associant chaque nœud à ses coordonnées 
            `[x, y]`.
        base_rad (float, optional): Le facteur de courbure de base pour une 
            distance unitaire. Valeur par défaut : 0.15.

    Returns:
        float: Le facteur de courbure (`rad`) à appliquer pour l'arête donnée, 
            permettant un tracé courbe adapté à la géométrie du graphe.
    """
    # return 0.15 * ((key + 1 >> 1) if key & 1 else -(key >> 1)) # alternative sans tenir compte de la distance entre les nœuds
    pos_u = pos[u]
    pos_v = pos[v]
    dist = max(math.hypot(pos_v[0] - pos_u[0], pos_v[1] - pos_u[1]), 0.1)
    
    # Logique d'alternance : 0, 0.15, -0.15, 0.30, -0.30...
    index_factor = (key + 1) // 2 if key & 1 else -(key // 2)
    return (base_rad / dist) * index_factor

def draw_graph_to_fig(G, layout_name="spring", positions=None, fig=None):
    """
    Génère une figure Matplotlib représentant un graphe (simple ou multigraphe).

    Cette fonction gère automatiquement les couleurs personnalisées des nœuds et des arêtes 
    via les attributs de données 'color'. Elle supporte également les MultiGraphs en 
    courbant les arêtes multiples pour éviter les superpositions.

    Args:
        G (nx.Graph | nx.MultiGraph | nx.DiGraph | nx.MultiDiGraph): L'instance du graphe 
            NetworkX à dessiner.
        layout_name (str, optional): Le nom de l'algorithme de disposition (layout) à utiliser 
            (ex: 'spring', 'circular', etc.). Si inconnu, utilise 'spring' par défaut.
        positions (dict, optional): Un dictionnaire de positions pour les nœuds. Si None, 
            utilise l'algorithme de disposition spécifié.
        fig (plt.Figure, optional): Une figure Matplotlib existante à réutiliser. Si None,
            une nouvelle figure sera créée.

    Returns:
        matplotlib.figure.Figure: L'objet figure contenant le dessin du graphe, 
            prêt à être affiché ou sauvegardé.

    Example:
        >>> fig = draw_graph_to_fig(mon_graphe, 'spring')
        >>> plt.show()
    """
    # nettoyage de la figure avant de dessiner (si elle existe déjà)
    if fig is None:
        fig = plt.figure(figsize=(5, 4))
        ax = fig.add_subplot(111)
        limits = None
    else:
        ax = fig.gca() # Récupère l'axe actuel
        limits = (ax.get_xlim(), ax.get_ylim())  # Sauvegarde les limites actuelles de l'axe
        ax.cla()       # Efface uniquement le contenu de l'axe
    
    ax.set_aspect('equal', adjustable='datalim') # Assure que les unités sont égales sur les axes x et y pour éviter la distorsion du graphe

    ax.axis('off')  # Masquer les axes pour une meilleure visualisation du graphe
    ax.set_xlim(-1.5, 1.5)  # Limites par défaut pour les graphes non positionnés
    ax.set_ylim(-1.5, 1.5)

    layouts = get_layouts()
    if positions is not None:
        pos = positions
    else:
        try:
            pos = layouts.get(layout_name, nx.spring_layout)(G)
        except:
            pos = nx.spring_layout(G)

    is_multigraph = isinstance(G, (nx.MultiGraph, nx.MultiDiGraph))

    # Dessin des nœuds
    node_colors = [G.nodes[n].get('color', NODE_COLOR) for n in G.nodes()]
    border_colors = [G.nodes[n].get('border_color', NODE_BORDER_COLOR) for n in G.nodes()]
    nodes = nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=NODE_SIZE, 
                           edgecolors=border_colors, linewidths=EDGE_WIDTH, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold', ax=ax)

    nodes.set_picker(5)  # Activer la sélection des nœuds avec une tolérance de 5 points

    # Dessin des arêtes
    if is_multigraph:
        edges = []
        for i, (u, v, key, data) in enumerate(G.edges(keys=True, data=True)):
            rad = calculate_edge_rad(u, v, key, pos)

            # rad = 0.15 * ((key + 1 >> 1) if key & 1 else -(key >> 1)) # alternative sans tenir compte de la distance entre les nœuds
            edge = nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], connectionstyle=f'arc3, rad={rad}',
                                   edge_color=data.get('color', EDGE_COLOR), width=EDGE_WIDTH, arrows=True, ax=ax, min_source_margin=10, min_target_margin=10)
            
            # attribution d'un gid unique à chaque arête pour la sélection
            if isinstance(edge, list):
                for e in edge: 
                    e.set_gid(f"edge_{u}_{v}_{key}")
            else:
                edge.set_gid(f"edge_{u}_{v}_{key}")

            edges.append(edge)
    else:
        edge_colors = [data.get('color', EDGE_COLOR) for u, v, data in G.edges(data=True)]
        edges = nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=EDGE_WIDTH, arrows=True, ax=ax, min_source_margin=10, min_target_margin=10)

    # Activer la sélection des arêtes avec une tolérance de 10 points
    if isinstance(edges, list):
        for edge in edges:
            if isinstance(edge, list):
                for e in edge:
                    e.set_picker(10)
            else:
                edge.set_picker(10)
    else:
        edges.set_picker(10)

    if limits:
        # Restaurer les limites de l'axe
        ax.set_xlim(limits[0])  
        ax.set_ylim(limits[1])
    else:
        ax.margins(0.1)  # Ajouter une marge pour éviter que les nœuds soient coupés
    fig.tight_layout(pad=0)
    return fig