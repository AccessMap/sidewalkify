"""Handle data fetching/cleaning tasks automatically. Reads and writes from a
pseudo-database in the filesystem, organized as ./cities/<city>/

"""

import click

# TODO: Add type hints for geopandas
import geopandas as gpd  # type: ignore

from . import graph
from . import draw


@click.command()
@click.argument("infile")
@click.argument("outfile")
@click.option("--driver", default="GeoJSON")
@click.option("--precision", default=1)
def sidewalkify(
    infile: str, outfile: str, driver: str, precision: int
) -> None:
    gdf = gpd.read_file(infile)
    crs = gdf.crs

    G = graph.create_graph(gdf, precision=precision)
    paths = graph.find_paths(G)

    sidewalks = draw.draw_sidewalks(paths, crs=crs)
    sidewalks.to_file(outfile, driver=driver)
