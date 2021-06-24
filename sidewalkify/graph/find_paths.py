from typing import List

import networkx as nx

from sidewalkify.graph.find_path import find_path, Path


def find_paths(G: nx.DiGraph) -> List[Path]:
    """Find paths representing a combinatorial map of sidewalks.

    :param G: A graph with edges labeled with 'az1' and 'az2' keys,
              where 'az1' = azimuth out of a node, 'az2' = azimuth into a node.
    :type G: networkx.DiGraph
    :returns: A list of paths (nodes) describing the combinatorial map.
    :rtype: list of nodes

    """
    paths = []
    while True:
        # Pick the next edge (or random - there's no strategy here)
        try:
            gen = (e for e in G.edges(data=True) if not e[2]["visited"])
            u, v, d = next(gen)
        except StopIteration:
            break
        # Start traveling
        paths.append(find_path(G, u, v))
    return paths
