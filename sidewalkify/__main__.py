"""Handle data fetching/cleaning tasks automatically. Reads and writes from a
pseudo-database in the filesystem, organized as ./cities/<city>/

"""

from sidewalkify import cli

if __name__ == "__main__":
    cli.sidewalkify()
