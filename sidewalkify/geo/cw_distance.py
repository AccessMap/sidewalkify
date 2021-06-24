def cw_distance(az1: float, az2: float) -> float:
    """
    Calculates the 'clockwise' distance between two azimuths, where 0 = North
    and the direction of increasing angle is clockwise.

    :param az1: Azimuth 1.
    :type az1: float
    :param az2: Azimuth 2.
    :type az2: float
    :returns: The angular distance between the azimuths, positive, going
              clockwise.
    :rtype: float

    """
    diff = (az2 - az1) % 360
    return diff
