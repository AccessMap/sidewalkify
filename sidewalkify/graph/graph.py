import numpy as np
from shapely import geometry
import networkx as nx

# TODO: use azimuth_lnglat for [lng,lat] projection, cartesian for flat
from sidewalkify.geo.azimuth import azimuth_cartesian as azimuth
from sidewalkify.graph.find_paths import find_paths


def create_graph(gdf, precision=1, simplify=0.05):
    """Create a networkx DiGraph given a GeoDataFrame of lines. Every line will
    correspond to two directional graph edges, one forward, one reverse. The
    original line row and direction will be stored in each edge. Every node
    will be where endpoints meet (determined by being very close together) and
    will store a clockwise ordering of incoming edges.

    """
    # The geometries sometimes have tiny end parts - get rid of those!
    gdf.geometry = gdf.geometry.simplify(simplify)
    G = nx.DiGraph()
    gdf.apply(add_edges, axis=1, args=[G, precision])

    return G


# TODO: converting to string is probably unnecessary - keeping float may be
# faster
def make_node(coord, precision):
    return tuple(np.round(coord, precision))


# Edges are stored as (from, to, data), where from and to are nodes.
# az1 is the azimuth of the first segment of the geometry (point into the
# geometry), az2 is for the last segment (pointing out of the geometry)
def add_edges(row, G, precision):
    geom = row.geometry
    coords = list(geom.coords)
    geom_r = geometry.LineString(coords[::-1])
    coords_r = geom_r.coords
    start = make_node(coords[0], precision)
    end = make_node(coords[-1], precision)

    # Add forward edge
    fwd_attr = {
        "forward": 1,
        "geometry": geom,
        "az1": azimuth(coords[0], coords[1]),
        "az2": azimuth(coords[-2], coords[-1]),
        "offset": row.sw_left,
        "visited": 0,
        "id": row.id,
    }
    G.add_edge(start, end, **fwd_attr)

    # Add reverse edge
    rev_attr = {
        "forward": 0,
        "geometry": geom_r,
        "az1": azimuth(coords_r[0], coords_r[1]),
        "az2": azimuth(coords_r[-2], coords_r[-1]),
        "offset": row.sw_right,
        "visited": 0,
        "id": row.id,
    }
    G.add_edge(end, start, **rev_attr)


def graph_workflow(gdf, precision=1):
    G = create_graph(gdf, precision=precision)
    paths = find_paths(G)

    return paths
