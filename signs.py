from map_operators import funs
import numpy as np


class signs:
    """
    Class to store all traffic sign information, include geometry (where it is), sign type, and sign id.
    """

    # Dictionary for sign types
    signID2str = {
        1: "Yield Sign",
        2: "Stop Sign",
        3: "Vertical RYG Traffic Light",
        4: "Horizontal Stack RYG",
        5: "Vertical Stack RYG with Indicator",
        6: "Horizontal Stack RYG with Indicator",
        7: "Red Traffic Light",
        8: "Yellow Traffic Light",
    }

    def __init__(self, geom, Type, ln_id, seg_id):
        self.geom = geom
        self.Type = Type
        self.ln_id = ln_id
        self.seg_id = seg_id



def dbc_traffic_signals(type):
    if type == 3 or type == 4 or type == 7 or type == 8:
        out = 3
    elif type == 5:
        out = 4
    elif type == 6:
        out = 5
    else:
        out = 3
    return out


def dbc_sign_types(type):
    if type == 1:
        return 4
    if type == 2:
        return 3
    return 0


def signs_init(cur):
    """
    Get all relevant traffic sign data from MCity maps.

    Arguments:
        cur: conn.cursor()

    Returns:
        signs object with all associated information
    """
    mCity_signs = signs([], [], [], [])

    cur.execute("select CAST ( geom AS point ) FROM csav3.signs")
    geoms = cur.fetchall()

    for geo in geoms:
        lon, lat = geo[0][1:-1].replace(",", " ").split()
        mCity_signs.geom.append((float(lon), float(lat)))  # want to switch to (lat, lon)?

    # Get sign type
    cur.execute("SELECT type FROM csav3.signs")
    types = cur.fetchall()

    for kind in types:
        mCity_signs.Type.append(kind[0])

    # Get sign lane id
    cur.execute("SELECT lane_id FROM csav3.signs")
    ln_ids = cur.fetchall()

    for i in ln_ids:
        mCity_signs.ln_id.append(i[0])

    # Get segment ID
    cur.execute("SELECT segment_id FROM csav3.signs")
    segment_ids = cur.fetchall()

    for i in segment_ids:
        mCity_signs.seg_id.append(i[0])

    return mCity_signs


class detected_sign:
    def __init__(
        self, count, segID, laneID, Type, lat_dist, lon_dist, relevant, observe
    ):
        self.count = count
        self.segID = segID
        self.laneID = laneID
        self.Type = Type
        self.lat_dist = lat_dist
        self.lon_dist = lon_dist
        self.relevant = relevant
        self.observe = observe


def observe(detectedSigns: detected_sign):
    """
    Check to see if the sign should be observed.
    This only applies to traffic lights at the moment.
    """
    lat_list = []
    observe_count = []
    for det in detectedSigns:
        if not det.relevant:
            det.observe = False

        if det.Type in range(3, 8):
            if det.relevant:
                lat_list.append(abs(det.lat_dist))
                observe_count.append(det.count)

    try:
        minIndex = np.argmin(lat_list)
        observe_index = observe_count[minIndex]

        for i, det in enumerate(detectedSigns):
            if det.relevant:
                if det.Type in range(3, 8):
                    if i == observe_index:
                        det.observe = True
                    else:
                        det.observe = False
    except:
        print("Try-except statement for an edge case here !!")

    return detectedSigns


def is_relevant(car_sID, car_lnID, obj_sID, obj_lnID):
    """
    Check to see if an object is relevant.
    relevant = it applies to the same road and lane that the car is on.
    """
    if car_sID == obj_sID and car_lnID == obj_lnID:
        is_rel = True
    else:
        is_rel = False
    return is_rel


def filterNearby(
    signs_object,
    lat1,
    lon1,
    detection_distance,
    car_bearing,
    detection_hfov,
    car_laneID,
    car_segID,
):
    detected = []
    count = 0
    for i, s in enumerate(signs_object.geom):
        dist = funs.distance(lat1, s[1], lon1, s[0])
        if dist <= detection_distance:  # Check if a sign is within detection_distance
            object_bearing = funs.bearing(lat1, s[1], lon1, s[0])
            lat_dist, lon_dist, is_right = funs.component_dist(car_bearing, object_bearing, dist)
            if is_right:
                lat_dist = lat_dist * -1
            if (abs(object_bearing - car_bearing) <= detection_hfov / 2):  # Check if sign is within detection_hfov
                relevant = is_relevant(car_segID, car_laneID, signs_object.seg_id[i], signs_object.ln_id[i])
                detected.append(
                    detected_sign(
                        count,
                        signs_object.seg_id[i],
                        signs_object.ln_id[i],
                        signs_object.Type[i],
                        lat_dist,
                        lon_dist,
                        relevant,
                        [],
                    )
                )
                count += 1

    return detected
