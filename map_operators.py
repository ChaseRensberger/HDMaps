from math import radians, cos, sin, asin, sqrt, atan2
from cmath import pi


class funs:
    @staticmethod
    def distance(lat1, lat2, lon1, lon2):
        """
        Calculate distance [meters] between two points(lat1, lon1), (lat2, lon2).

        Arguments:
            lat1, lon1: float
                Location of first point
            lat2, lon2: float
                Location of second point

        Return:
            Distance (float) from point 1 to point 2
        """
        # The math module contains a function named
        # radians which converts from degrees to radians.
        lon1 = radians(lon1)
        lon2 = radians(lon2)
        lat1 = radians(lat1)
        lat2 = radians(lat2)

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

        c = 2 * asin(sqrt(a))

        # Radius of earth in meters. Use 3956 for miles
        r = 6371000

        # calculate the result
        return c * r

    # Bearing Function
    @staticmethod
    def bearing(lat1, lat2, lon1, lon2):
        """
        Calculate bearing [degrees] between two points(lat1, lon1), (lat2, lon2) relative to north.

        Arguments:
            lat1, lon1: float
                Location of first point
            lat2, lon2: float
                Location of second point

        Return:
            Bearing (float) from point 1 to point 2
            0 -> +180 = N -> S CW
            0 -> -180 = N -> S CCW
        """
        lon1 = radians(lon1)
        lon2 = radians(lon2)
        lat1 = radians(lat1)
        lat2 = radians(lat2)

        x = cos(lat2) * sin(lon2 - lon1)
        y = cos(lat1) * sin(lat2) - (sin(lat1) * cos(lat2) * cos(lon2 - lon1))
        b = atan2(x, y) * (180 / pi)

        # if b < 0:
        #     b = 360 + b
        return b  # Returns bearing in deg

    @staticmethod
    def component_dist(car_bear, obj_bear, mag_dist):
        delta = car_bear - obj_bear
        if delta >= 0:
            is_right = False
        else:
            is_right = True

        lat_dist = round(mag_dist * sin(radians(abs(delta))), 3)
        lon_dist = round(mag_dist * cos(radians(abs(delta))), 3)
        lon_dist = lon_dist - 1.15  # Subtract cart length

        return lat_dist, lon_dist, is_right
