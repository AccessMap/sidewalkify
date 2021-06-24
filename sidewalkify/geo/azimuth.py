import math
from typing import Tuple


Coordinate = Tuple[float, float]


def azimuth_lnglat(p1: Coordinate, p2: Coordinate) -> float:
    """
    Calculates the bearing between two lng-lat points.

    :param p1: (lng, lat) coordinates of first point. Can be any iterable.
    :type p1: length 2 iterable
    :param p2: (lng, lat) coordinates of second point. Can be any iterable.
    :type p2: length 2 iterable
    :returns: The bearing, in degrees. Increases in clockwise direction.
    :rtype: float

    """
    if (len(p1) != 2) or (len(p2) != 2):
        raise TypeError("Only length-2 iterables are supported as arguments.")

    lat1 = math.radians(p1[1])
    lat2 = math.radians(p2[1])

    dlon = math.radians(p2[0] - p1[0])

    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (
        math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    )

    initial_bearing = math.atan2(x, y)

    # Convert to degrees and put north
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing


def azimuth_cartesian(p1: Coordinate, p2: Coordinate) -> float:
    """
    Calculates the bearing between two projected points on a square-ish 2D
    plane (i.e., a map projection with identical xy units)

    :param p1: (x, y) coordinates of first point. Can be any iterable.
    :type p1: length 2 iterable
    :param p2: (x, y) coordinates of second point. Can be any iterable.
    :type p2: length 2 iterable
    :returns: The bearing, in degrees. Increases in clockwise direction.
    :rtype: float

    """
    if (len(p1) != 2) or (len(p2) != 2):
        raise TypeError("Only length-2 iterables are supported as arguments.")

    angle = math.atan2(p2[0] - p1[0], p2[1] - p1[1])

    # Convert to degrees and put north
    degrees = math.degrees(angle)
    bearing = (degrees + 360) % 360

    return bearing
