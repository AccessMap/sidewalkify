# Sidewalkify

`sidewalkify` is a Python library and command line application for drawing
sidewalk lines from street centerline data.

## Introduction

Sidewalk data is often recorded as metadata for street lines,
such as whether a sidewalk is on the left or the right side, and at what
distance. This method of storage is good for questions such as, 'what streets
have sidewalks?', but are not as good for knowing exactly where a sidewalk is
and how it connects to other sidewalks (e.g., places to cross the street,
curb ramps, etc).

## Installation
clone file locally where osm_sidewalk_staging main file is and 

`pip install sidewalkify` locally

`sidewalkify` requires the `click`, `networkx` and `geopandas` libraries.
`geopandas` requires GDAL to read and write files, so you also need to install
GDAL tools for your system.

Python 2: though this package is currently marked as Python 3-only, it should
work on Python 2 as well. However, we do not currently support issues related
to Python 2.

## Usage

Once installed, `sidewalkify` is available both as a command line application
and a Python library.

#### CLI

Example:

    sidewalkify <input.shp> <output.shp>

##### Arguments

The input file can be any file type readable by `geopandas.read_file`, which
should be anything readable by `fiona`, i.e. GDAL.

The input file must have two metadata columns: `sw_right` and `sw_left`. The
values in these columns must be the offset distance of the sidewalk. A negative
value indicates the nonexistence of the sidewalk on that side of the street.

For example, you could also use a GeoJSON input file:

    sidewalkify <input.geojson> <output.shp>

#### Python Library

`sidewalkify` can also be used as a Python library so that you can build your
own scripts or write libraries on top of `sidewalkify`. We recommend that you
read the Architecture section before using the `sidewalkify` library API.

The `sidewalkify` library consists of two modules:

##### `sidewalkify.graph`

The `graph` module provides functions for creating a digraph of potential
sidewalk edges and processing them into paths. i.e., for a city that has
sidewalks on all streets, all of the connected sidewalk paths will be found.

###### `sidewalkify.graph.create_graph(gdf, precision=1)`:

`create_graph` is a function that takes a GeoDataFrame (`gdf`) and creates a
`networkx` `DiGraph`, where the edges are dictionaries with these keys:
* `forward`: A boolean (`True`, `False`) for whether the edge travels along
the same path as the original geometry, or is the reverse path.
* `geometry`: the original geometry (a `shapely` `LineString`) of the street
centerline, in the direction of the edge (i.e., the geometry gets reversed
when `forward` is `False`).
* `az1`: The azimuth (angle starting at North, going clockwise, in radians)
of the first segment of the geometry, i.e. the direction in which the street is
initially pointing.
* `az2`: The azimuth of the last segment of the geometry, i.e. the direction in
which the geometry is finally pointing.
* `offset`: The offset, in meters, of the sidewalk. This always indicates a
right-hand offset - the `sw_right` column value is used for `forward=True`
edges, the `sw_left` column value is used for `forward=False` edges. A value of
`0` (or a negative value, such as `-1`) means that no sidewalk exists for this
geometry, and none will be drawn.
* `id`: This is copied from the original dataset.

Vertices of the graph are coordinates where streets meet (like an intersection)
or terminate (a dead end). The decision to group street endpoints at a
particular vertex is determined by the `precision` parameter: coordinates will
be rounded to the `precision` decimal place, then grouped by that rounded
coordinate. So, e.g., these two endpoint coordinates will share the vertex at
`(-122.3, -47.8)` when `precision` is `1`:

    (-122.2947728, -47.764472)
    (-122.3477481, -47.758871)

Example:
    import geopandas as gpd
    import sidewalkify as sdw

    gdf = gpd.read_file('./test.shp')

    G = sdw.graph.create_graph(gdf)

The resulting digraph (`G`) can be accessed with the standard methods available
to a `networkx` `DiGraph`. For example, to find the edge from

###### `sidewalkify.graph.process_acyclic(G)`:

`process_acyclic(G)` will create a list of acyclic paths (lists of edges) from
the graph created by `create_graph`. Once `process_acyclic` has completed, only
cyclic paths should remain in G. *Important*: The edges used to create paths
will be removed from `G` in-place.

###### `sidewalkify.graph.process_cyclic(G)`:

`process_cyclic(G)` will create a list of cyclic paths (lists of edges) from
the graph created by `create_graph`.

*Important*: `process_cyclic` assumes that only cyclic paths remain in the
graph. If a non-cylic path exists, process_acylic may enter an infinite loop.

*Important*: The edges used to create paths will be removed from `G` in-place.

###### `sidewalkify.graph.graph_workflow(gdf, precision=1)`:

`graph_workflow(gdf, precision=1)` carries out all of the steps above, in order, creating
a single list of paths. The `precision` argument is passed to `create_graph`.

##### `sidewalkify.draw`

The `draw` module creates the actual sidewalk lines once the sidewalk paths
have been found using the `graph` module.

###### `sidewalkify.draw.draw_sidewalks(paths, crs=4326)`

The `draw_sidewalks` function draws (relatively) clean, connect sidewalk lines.
It requires input in the form output by `sidewalkify.graph.graph_workflow`.

By default, the new sidewalk lines are assumed to be in the 4326 CRS (WGS84,
or lat-lon). You can override this by setting a new CRS, for example:

    gdf2 = sdw.draw.draw_sidewalks(paths, crs=26910)

This would ensure that the files created are in the right project. In this
case, NAD83 for Washington, United States (in meters).

## Architecture

`sidewalkify` combines two methods for drawing sidewalks.

#### Parallel offsets
`sidewalkify` uses standard parallel offset algorithms (the `parallel_offset`
method in `shapely`) for drawing an initial approximation of sidewalk
locations. The offsets must be pre-coded into the input data as `sw_right` or
`sw_left` fields, in meters.

#### Graph-based cleanup
Initially, the parallel offset lines are not completely accurate: they extend
as far as the street does, which can result in sidewalks that criss-cross and
flow over into the street (overshoots), or don't connect when they should
(undershoots).

To clean up the overshoots and undershoots, `sidewalkify` trims the extra bits
(dangles) of overshoots and connects undershoots by either drawing connecting
lines or snapping endpoints together. But without knowing the way in which the
sidewalks are supposed to be connected (e.g. sidewalk A leads into sidewalk B),
this can result in several errors. For example, sidewalks that extend around
and under an overpass can be self-intersecting and would normally be detected
as an overshoot and erroneously broken. Or, very short segments of sidewalk
can result in the wrong sidewalks being connected simply due to spatial
proximity.

To select the right sidewalks to connect, `sidewalkify` constructs a street
graph (using a `networks` digraph), where each edge represents part of a
potential sidewalk path. Consecutive edges of this graph are the sidewalks that
should be considered for merging (overshoots and undershoots), with all others
ignored.

For a standard city block with good coverage, `sidewalkify` will find a cyclic
path, eventually constructing a closed rectangle. For a similar block that
contains a dead end, `sidewalkify` will still find a cyclic path, but the
resulting sidewalk will (by default) be broken at the end of the dead end. In
addition, `sidewalkify` will create an open (non-cyclic) set of sidewalks when
the path would not be cyclic, such as a sidewalk near a coastline.

# License

Dual-licensed MIT and Apache 2.0. You can treat this project as being licensed
under one or the other, depending on your preference.
