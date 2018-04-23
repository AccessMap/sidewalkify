import geopandas as gpd
from .trim import trim


def draw_sidewalks(paths, crs={'init': 'epsg:4326'}, resolution=1):
    def edge_to_sidewalk_geom(edge):
        offset = edge['offset']
        if offset > 0:
            geom = edge['geometry'].parallel_offset(offset, 'left',
                                                    resolution=resolution,
                                                    join_style=1)

            if geom.length <= 0:
                return None
            else:
                return geom
        else:
            return None

        return geom

    rows = []
    for path in paths:
        for edge in path['edges']:
            edge['sidewalk'] = edge_to_sidewalk_geom(edge)

        # Iterate over edges and attach/trim
        # Note: path is cyclic, so we shift the list
        edges_from = path['edges']
        edges_to = path['edges'][1:] + [path['edges'][0]]
        for edge1, edge2 in zip(edges_from, edges_to):
            # TODO: should consider totality of previous edges to check for
            # intersection - may be missing overlaps.
            geom1, geom2 = trim(edge1, edge2)
            edge1['sidewalk'] = geom1
            edge2['sidewalk'] = geom2

        for edge in path['edges']:
            if edge['sidewalk'] is None:
                # Ignore cases of no sidewalk
                continue
            if not edge['sidewalk'].is_valid:
                # Ignore cases where invalid geometry was generated.
                # TODO: log / report so users can find data errors
                continue

            rows.append({
              'geometry': edge['sidewalk'],
              'street_id': edge['id'],
              'forward': edge['forward']
            })

    gdf = gpd.GeoDataFrame(rows)
    gdf.crs = crs

    return gdf
