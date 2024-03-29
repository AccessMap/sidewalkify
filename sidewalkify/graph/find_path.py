from typing import List, TypedDict

import networkx as nx

from sidewalkify.geo.cw_distance import cw_distance


# TODO: create more specific edge type?
class Path(TypedDict):
    edges: List[dict]
    nodes: List[str]
    cyclic: bool


def find_path(G: nx.DiGraph, u: str, v: str) -> Path:
    """
    Finds a single path as part of building a combinatorial map corresponding
    to sidewalks.

    :param G: The graph
    :type G: networkx.DiGraph
    :param u: Node at which to start.
    :type u: str
    :param v: First node to choose (u and v describe an edge).
    :type v: str
    It's assumed that edge (u, v) actually exists in the graph.

    """
    path: Path = {
        "edges": [],
        "nodes": [],
        "cyclic": False,
    }

    # Travel the first edge
    G[u][v]["visited"] = 1

    path["edges"].append(G[u][v])
    path["nodes"].append(u)
    path["nodes"].append(v)

    while True:
        u_previous = u
        u = v

        successors = list(G.successors(v))
        if not successors:
            if u == path["nodes"][0]:
                path["cyclic"] = True
            break

        v = min(successors, key=lambda x: _circular_dist(G, u_previous, u, x))

        if G[u][v]["visited"]:
            if u == path["nodes"][0]:
                path["cyclic"] = True
            break

        path["edges"].append(G[u][v])
        path["nodes"].append(v)
        G[u][v]["visited"] = 1

    return path


def _circular_dist(G: nx.DiGraph, u: str, v: str, x: str) -> float:
    if u == x:
        # Should sort last - just make it a big int
        return 1e6
    else:
        return cw_distance((G[u][v]["az2"] + 180) % 360, G[v][x]["az1"])
