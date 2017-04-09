## README

1. Add table of contents to README
2. Add links to CLI vs. Python library use in Usage section
3. Add links when referring to outside libraries, e.g. `DiGraph`.
4. Add extended installation instructions for more platforms (installing GDAL,
   using conda, etc).

## Features

#### Reprojection

It's currently assumed that the input files are in a projection in meters. If
this is not the case, could offer a way to automatically project to something
like UTM (or provide a reprojection parameter).

#### Object-oriented design for data structures

Evaluate OO for data structures in this module. Specifically, the `edges`
object in the graph and the paths creates in the graph module. This will make
it easier to specify the input/output of the various functions and autodoc.

#### Catch negative `sw_right`/`left` values

Currently, we expect an offset of `0` to indicate that no sidewalk is present.
We should also allow a negative value to mean this (e.g. -1).

#### Read from / write to database

These features could be added separately, starting with reading. Both will
use the `geopandas` interface for connecting to a PostGIS database (don't
support anything `geopandas` doesn't).

To read from the database, this info is required:
1. A connection string (write access not necessary, only read)
2. The table to use

These optional arguments could also be handy:
1. geometry column name, if it differs from the `geopandas` default (is that
'geom'?)
2. An SQL SELECT statement for querying the database. This would be useful when
the table is particularly large or complex, and I think it's technically what
`geopandas` wants as its input, aside from a database connection. This would
allow the user to not actually have a properly-formatted database table, but
create one on-the-fly for use with sidewalkify.
