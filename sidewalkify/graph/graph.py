import numpy as np
from shapely import geometry
import networkx as nx

# TODO: use azimuth_lnglat for [lng,lat] projection, cartesian for flat
from .utils import azimuth_cartesian as azimuth
from .utils import cw_distance


def create_graph(gdf, precision=1, simplify=0.05):
    '''Create a networkx DiGraph given a GeoDataFrame of lines. Every line will
    correspond to two directional graph edges, one forward, one reverse. The
    original line row and direction will be stored in each edge. Every node
    will be where endpoints meet (determined by being very close together) and
    will store a clockwise ordering of incoming edges.

    '''
    # The geometries sometimes have tiny end parts - get rid of those!
    gdf.geometry = gdf.geometry.simplify(simplify)

    G = nx.DiGraph()

    # TODO: converting to string is probably unnecessary - keeping float may be
    # faster
    def make_node(coord, precision):
        return tuple(np.round(coord, precision))

    # Edges are stored as (from, to, data), where from and to are nodes.
    # az1 is the azimuth of the first segment of the geometry (point into the
    # geometry), az2 is for the last segment (pointing out of the geometry)
    def add_edges(row, G):
        geom = row.geometry
        coords = list(geom.coords)
        geom_r = geometry.LineString(coords[::-1])
        coords_r = geom_r.coords
        start = make_node(coords[0], precision)
        end = make_node(coords[-1], precision)

        # Add forward edge
        fwd_attr = {
            'forward': 1,
            'geometry': geom,
            'az1': azimuth(coords[0], coords[1]),
            'az2': azimuth(coords[-2], coords[-1]),
            'offset': row.sw_left,
            'visited': 0,
            'id': row.id
        }
        G.add_edge(start, end, **fwd_attr)

        # Add reverse edge
        rev_attr = {
            'forward': 0,
            'geometry': geom_r,
            'az1': azimuth(coords_r[0], coords_r[1]),
            'az2': azimuth(coords_r[-2], coords_r[-1]),
            'offset': row.sw_right,
            'visited': 0,
            'id': row.id
        }
        G.add_edge(end, start, **rev_attr)

    gdf.apply(add_edges, axis=1, args=[G])

    return G


def find_paths(G):
    '''Find paths representing a combinatorial map of sidewalks.

    :param G: A graph with edges labeled with 'az1' and 'az2' keys,
              where 'az1' = azimuth out of a node, 'az2' = azimuth into a node.
    :type G: networkx.DiGraph
    :returns: A list of paths (nodes) describing the combinatorial map.
    :rtype: list of nodes

    '''
    paths = []
    while True:
        # Pick the next edge (or random - there's no strategy here)
        try:
            gen = (e for e in G.edges(data=True) if not e[2]['visited'])
            u, v, d = next(gen)
        except StopIteration:
            break
        # Start traveling
        paths.append(find_path(G, u, v))
    return paths


def find_path(G, u, v):
    '''
    Finds a single path as part of building a combinatorial map corresponding
    to sidewalks.

    :param G: The graph
    :type G: networkx.DiGraph
    :param u: Node at which to start.
    :type u: str
    :param v: First node to choose (u and v describe an edge).
    :type v: str
    It's assumed that edge (u, v) actually exists in the graph.

    '''
    path = {}
    path['edges'] = []
    path['nodes'] = []

    # Travel the first edge
    G[u][v]['visited'] = 1

    path['edges'].append(G[u][v])
    path['nodes'].append(u)
    path['nodes'].append(v)

    def circular_dist(G, u, v, x):
        if u == x:
            # Should sort last - just make it a big int
            return 1e6
        else:
            return cw_distance((G[u][v]['az2'] + 180) % 360, G[v][x]['az1'])

    while True:
        u_previous = u
        u = v

        successors = list(G.successors(v))
        if not successors:
            break

        v = min(successors, key=lambda x: circular_dist(G, u_previous, u, x))

        if G[u][v]['visited']:
            break

        path['edges'].append(G[u][v])
        path['nodes'].append(v)
        G[u][v]['visited'] = 1

    return path


def graph_workflow(gdf, precision=1):
    G = create_graph(gdf, precision=precision)
    paths = find_paths(G)

    return paths
