import geopandas as gpd
from sidewalkify import draw, graph


INFILE = "./tests/data/uw_streets.geojson"
EXPECTED_FILE = "./tests/data/uw_sidewalks_expected_output.geojson"
PRECISION = 1


def test_sidewalkify():
    gdf = gpd.read_file(INFILE)
    expected_sidewalks = gpd.read_file(EXPECTED_FILE)
    expected_geoms = list(expected_sidewalks.geometry)
    crs = gdf.crs

    G = graph.create_graph(gdf, precision=PRECISION)
    paths = graph.find_paths(G)

    sidewalks = draw.draw_sidewalks(paths, crs=crs)
    for idx, sidewalk_row in sidewalks.iterrows():
        assert sidewalk_row["geometry"] in expected_geoms
