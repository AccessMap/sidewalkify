'''Handle data fetching/cleaning tasks automatically. Reads and writes from a
pseudo-database in the filesystem, organized as ./cities/<city>/

'''

import click
import geopandas as gpd

from . import graph
from . import draw


@click.command()
@click.argument('infile')
@click.argument('outfile')
def sidewalkify(infile, outfile):
    gdf = gpd.read_file(infile)
    crs = gdf.crs
    paths = graph.graph_workflow(gdf)
    sidewalks = draw.draw_sidewalks(paths, crs=crs)
    sidewalks.to_file(outfile)

if __name__ == '__main__':
    sidewalkify()
