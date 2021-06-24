from typing import List, Optional

# TODO: add type hints for geopandas
import geopandas as gpd  # type: ignore

# TODO: add type hints for shapely
from shapely.geometry import LineString  # type: ignore

from .trim import trim
from sidewalkify.graph.find_path import Path


def draw_sidewalks(
    paths: List[Path], crs: dict = {"init": "epsg:4326"}, resolution: int = 1
) -> gpd.GeoDataFrame:
    rows = []
    for path in paths:
        for edge in path["edges"]:
            edge["sidewalk"] = edge_to_sidewalk_geom(edge, resolution)

        # Iterate over edges and attach/trim
        # Note: path is cyclic, so we shift the list
        if path["cyclic"]:
            edges_from = path["edges"]
            edges_to = path["edges"][1:] + [path["edges"][0]]
        else:
            edges_from = path["edges"][:-1]
            edges_to = path["edges"][1:]

        for edge1, edge2 in zip(edges_from, edges_to):
            # TODO: should consider totality of previous edges to check for
            # intersection - may be missing overlaps.
            geom1, geom2 = trim(edge1, edge2)
            edge1["sidewalk"] = geom1
            edge2["sidewalk"] = geom2

        for edge in path["edges"]:
            if edge["sidewalk"] is None:
                # Ignore cases of no sidewalk
                continue
            if not edge["sidewalk"].is_valid:
                # Ignore cases where invalid geometry was generated.
                # TODO: log / report so users can find data errors
                continue

            rows.append(
                {
                    "geometry": edge["sidewalk"],
                    "street_id": edge["id"],
                    "forward": edge["forward"],
                }
            )

    gdf = gpd.GeoDataFrame(rows)
    gdf.crs = crs

    return gdf


# TODO: Replace Any with shapely.geometry.LineString
# TODO: add a more specific type for edge data?
def edge_to_sidewalk_geom(edge: dict, resolution: int) -> Optional[LineString]:
    offset = edge["offset"]
    if offset > 0:
        geom = edge["geometry"].parallel_offset(
            offset, "left", resolution=resolution, join_style=1
        )

        if geom.length <= 0:
            return None
        elif geom.type == "MultiLineString":
            # TODO: can this be handled more elegantly? Investigate why the
            # offset algorithm sometimes creates MultiLineStrings and handle
            # cases on a more specific basis.
            coords = []
            for geom in geom.geoms:
                coords += list(geom.coords)
            geom = LineString(coords)
            return geom
        else:
            return geom
    else:
        return None
