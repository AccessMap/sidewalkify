import math

import numpy as np


def azimuth(point1, point2):
    angle = math.atan2(point2[0] - point1[0], point2[1] - point1[1])
    if angle > 0:
        return angle
    else:
        return angle + 2 * np.pi
