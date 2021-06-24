import numpy as np
from shapely import geometry
import networkx as nx

# TODO: use azimuth_lnglat for [lng,lat] projection, cartesian for flat
from sidewalkify.geo.azimuth import azimuth_cartesian as azimuth


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
    d_f = {
        "forward": 1,
        "geometry": row["geometry"],
        "offset": row["sw_left"],
    }

    geom_r = geometry.LineString(row["geometry"].coords[::-1])
    d_r = {
        "forward": 0,
        "geometry": geom_r,
        "offset": row["sw_right"],
    }

    for d in [d_f, d_r]:
        d["visited"] = 0
        d["id"] = row["id"]

        d["az1"] = azimuth(d["geometry"].coords[0], d["geometry"].coords[1])
        d["az2"] = azimuth(d["geometry"].coords[-2], d["geometry"].coords[-1])

    u_f = make_node(d_f["geometry"].coords[0], precision)
    v_f = make_node(d_f["geometry"].coords[-1], precision)
    u_r = make_node(d_r["geometry"].coords[0], precision)
    v_r = make_node(d_r["geometry"].coords[-1], precision)

    # FIXME: this is a very slow way to add edges - instead, use the .add_edges
    # method in batches
    G.add_edge(u_f, v_f, **d_f)
    G.add_edge(u_r, v_r, **d_r)
