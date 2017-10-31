import numpy as np
from shapely import geometry
import networkx as nx

from .utils import azimuth


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
            'offset': row.sw_right,
            'id': row.id
        }
        G.add_edge(start, end, **fwd_attr)

        # Add reverse edge
        rev_attr = {
            'forward': 0,
            'geometry': geom_r,
            'az1': azimuth(coords_r[0], coords_r[1]),
            'az2': azimuth(coords_r[-2], coords_r[-1]),
            'offset': row.sw_left,
            'id': row.id
        }
        G.add_edge(end, start, **rev_attr)

    gdf.apply(add_edges, axis=1, args=[G])

    return G


def process_acyclic(G):
    paths = []
    while True:
        # Handle 'endpoint' starts - certainly acyclic
        n = len(paths)
        # We want to start with a dangling node - an edge that terminates.
        # Features of that dangling node:
        #   1) degree of node inputs is 1 or 0
        #   2) degree of node outputs is 1.
        #   3) if degree of node inputs is 1, the input to the node is the
        #      output to the node.

        # Identify candidates first - don't want to create/remove candidates
        # by updating at the same time
        candidates = []
        for node in G.nodes():
            predecessors = list(G.predecessors(node))
            successors = list(G.successors(node))
            in_degree = len(predecessors)
            out_degree = len(successors)

            if out_degree == 1:
                if in_degree == 0:
                    candidates.append(node)
                elif in_degree == 1:
                    if successors == predecessors:
                        candidates.append(node)

        # Create paths for every candidate
        for candidate in candidates:
            # If this point is reached, it's a dangle!
            paths.append(find_path(G, candidate, list(G[candidate])[0]))

        G.remove_nodes_from(list(nx.isolates(G)))
        if n == len(paths):
            # No change since last pass = exhausted attempts
            break
    return paths


def process_cyclic(G):
    paths = []
    while True:
        # Pick the next edge (or random - there's no strategy here)
        try:
            edge = next(iter(G.edges()))
        except StopIteration:
            break
        # Start traveling
        paths.append(find_path(G, edge[0], edge[1], cyclic=True))
        # G.remove_nodes_from(nx.isolates(G))
    return paths


def find_path(G, e1, e2, cyclic=False):
    '''Given a starting edge (e1, e2), travel until one of the following
    conditions is met:
    1) The path terminates (node degree 1)
    2) A node has been revisited (cycle)

    It's assumed that edge (e1, e2) actually exists in the graph.

    '''
    path = {}
    path['edges'] = []
    path['nodes'] = []

    def ccw_dist(az1, az2):
        diff = (az1 + np.pi) % (2 * np.pi) - az2
        if diff < 0:
            diff += 2 * np.pi
        return diff

    # Travel the first edge
    edge_attr = G[e1][e2]
    path['edges'].append(edge_attr)
    path['nodes'].append(e1)
    path['nodes'].append(e2)
    G.remove_edge(e1, e2)
    while True:
        # Want to avoid two things:
        # 1) traveling the same edge again
        # 2) revisiting the last-visited node (doubling back)

        # Prevent doubling back to the same node
        nodes_out = [node for node in G.successors(e2) if node != e1]
        n = len(nodes_out)

        if n == 0:
            # Terminal node reached - could also by cycle (if traveled node
            # was removed)
            break

        e1 = e2

        if n == 1:
            # There's only one choice! Skip azimuth math.
            e2 = nodes_out[0]
            edge_attr = G[e1][e2]
        else:
            # Get the nearest counterclockwise edge - i.e. make rightmost turn.
            az = edge_attr['az2']
            attrs = [(node, G[e1][node]) for node in nodes_out]
            e2, edge_attr = min(attrs,
                                key=lambda x: ccw_dist(az, x[1]['az1']))

        path['edges'].append(edge_attr)
        path['nodes'].append(e2)
        G.remove_edge(e1, e2)

        if cyclic:
            # If this node has been visited before, we've traveled a cycle
            # should stop after traveling this edge
            if e2 == path['nodes'][0]:
                break
        # If path was not cyclic, it will terminate when another terminal
        # edge is found.

    if path['nodes'][0] == path['nodes'][-1]:
        path['cyclic'] = True
    else:
        path['cyclic'] = False

    return path


def path_to_geom(path):
    coords = []
    coords.append(path['edges'][0]['geometry'].coords[0])
    for p in path['edges']:
        coords += p['geometry'].coords[1:]
    return geometry.LineString(coords)


def graph_workflow(gdf, precision=1):
    G = create_graph(gdf, precision=precision)
    acyclic_paths = process_acyclic(G)
    cyclic_paths = process_cyclic(G)
    paths = acyclic_paths + cyclic_paths

    return paths
