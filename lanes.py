import statistics
from map_operators import funs


# test
"""
 Algorithm:
    ----- localize which lane the car is -----
    1. find all points within a radius from the input coordinate (our car's GPS)
    2. count number of points belonging to each lane
    3. majority of points should belong to the lane that the car currently locates

    ----- calculate distance to the both edges of the lane -----
    4. for all the points found in step 1, only keep points belonging to the lane the car locates (left with k points)
    5. calculate the distance between the car's coordinate and the closest point found in step 4
    6. calculate the distance between the car to the other edge of the lane by subtracting the lane width and distance in step 5

    ----- figure out which marker type the edge of the lane is -----
    1. Query lane types around cart.
    2. Determine the closest point to the left and to the right edges of lane
    3. Output those lane types

    ----- Identify the type and relative position of all limit lines within 10 meters in roadway -----
    1. Query all stop signs within x = 40 degree bearing and 10 meters -> list of points
    2. Calculate the longitude distance of our car to the stop sign (relative position)
    3. to-do (type)
"""


class Lanes:
    """
    Class to store all lane information.
    """

    def __init__(
        self,
        geom,
        seg_id,
        xs_id,
        point_id,
        lane_id,
        width,
        speed_limit,
        lane_color,
        lane_type,
    ):
        self.geom = geom
        self.seg_id = seg_id
        self.xs_id = xs_id
        self.point_id = point_id
        self.lane_id = lane_id
        self.width = width
        self.speed_limit = speed_limit
        self.lane_color = lane_color
        self.lane_type = lane_type

    def lane_types_dict(self):
        lane_types = {
            1: "Thin Dashed Single Line, No Botts Dots",
            2: "Thick Dashed Single Line, No Botts Dots",
            3: "Thin Solid Single Line, No Botts Dots",
            4: "Thick Solid Single Line, No Botts Dots",
            5: "Thin Dashed Double Line, No Botts Dots",
            6: "Thick Dashed Double Line, No Botts Dots",
            7: "Thin Solid Double Line, No Botts Dots",
            8: "Thick Solid Double Line, No Botts Dots",
            9: "Thin Double Left Solid Right Dashed Line, No Botts Dots",
            10: "Thick Double Left Solid Right Dashed Line, No Botts Dots",
            11: "Thin Double Left Dashed Right Solid Line, No Botts Dots",
            12: "Thick Double Left Dashed Right Solid Line, No Botts Dots",
            13: "Thin Dashed Triple Line, No Botts Dots",
            14: "Thick Dashed Triple Line, No Botts Dots",
            15: "Thin Solid Triple Line, No Botts Dots",
            16: "Thick Solid Triple Line, No Botts Dots",
            17: "Dashed Single Line, Botts Dots",
            18: "Solid Single Line, Botts Dots",
            19: "Dashed Double Line, Botts Dots",
            20: "Solid Double Line, Botts Dots",
            21: "Double Left Solid Right Dashed Line, Botts Dots",
            22: "Double Left Dashed Right Solid Line, Botts Dots",
            23: "Dashed Triple Line, Botts Dots",
            24: "Solid Triple Line, Botts Dots",
            25: "Virtual Inferred Line",
        }
        return lane_types

    def dbc_lane_types(type):
        if (
            type == 1
            or type == 2
            or type == 9
            or type == 10
            or type == 13
            or type == 14
        ):
            out = 2
        elif type == 3 or type == 4:
            out = 1
        elif (
            type in range(5, 9) or type == 11 or type == 12 or type == 15 or type == 16
        ):
            out = 5
        elif type in range(17, 25):
            out = 4
        else:
            out = 0
        return out

    def lane_color_dict(self):
        lane_color = {1: "White", 2: "Yellow", 3: "Other", 4: "Unknown"}
        return lane_color

    def dbc_lane_color(color):
        if color == 4:
            out = 0
        else:
            out = color
        return out

    def crossings_type_dict(self):
        cross_type = {
            1: "Overpass/Gantry",
            2: "Tunnel",
            3: "At Grade Rail Road",
            4: "At Grade Road (crosses both directions of traffic)",
            5: "At Grade Access (does not cross both directions of traffic)",
            6: "At Grade Stop Bar",
            7: "At Grade Bike/Pedestrian",
            8: "At Grade Authorized Vehicle (identified only on Controlled Access Roads)",
            9: "At Grade Toll Booth",
            10: "At Grade Movable Bridge",
        }
        return cross_type


def lanes_init(cur):
    """
    Get all lanes from MCity maps.

    Arguments:
        cur: conn.cursor()

    Returns:
        lane object with all associated information
    """

    mCity_lanes = Lanes([], [], [], [], [], [], [], [], [])

    cur.execute("select CAST ( geom AS point ) FROM csav3.lane")
    geoms = cur.fetchall()

    # Get geom
    for geo in geoms:
        lon, lat = geo[0][1:-1].replace(",", " ").split()
        mCity_lanes.geom.append((float(lon), float(lat)))

    # Get seg_id
    cur.execute("SELECT segment_id FROM csav3.lane")
    for i in cur.fetchall():
        mCity_lanes.seg_id.append(i[0])

    # Get xs_id
    cur.execute("SELECT xs_id FROM csav3.lane")
    for i in cur.fetchall():
        mCity_lanes.xs_id.append(i[0])

    # Get point_id
    cur.execute("SELECT point_id FROM csav3.lane")
    for i in cur.fetchall():
        mCity_lanes.point_id.append(i[0])

    # Get lane_id
    cur.execute("SELECT lane_id FROM csav3.lane")
    for i in cur.fetchall():
        mCity_lanes.lane_id.append(i[0])

    # Get width
    cur.execute("SELECT width FROM csav3.lane")
    for i in cur.fetchall():
        mCity_lanes.width.append(i[0])

    # Get speed_limit
    cur.execute("SELECT speed_limit FROM csav3.lane")
    for i in cur.fetchall():
        mCity_lanes.speed_limit.append(i[0])

    # Get lane_color
    cur.execute("SELECT color FROM csav3.marker")
    for i in cur.fetchall():
        mCity_lanes.lane_color.append(i[0])

    # Get lane_type
    cur.execute("SELECT type FROM csav3.marker")
    for i in cur.fetchall():
        mCity_lanes.lane_type.append(i[0])

    return mCity_lanes

def get_all_points(cur):
    cur.execute("SELECT CAST(geom AS point), direction, point_id, id_, segment_id FROM csav3.point")
    points = cur.fetchall()
    return points

def get_all_crossings(cur):
    cur.execute("SELECT CAST(geom AS point), id_, segment_id, lane_id, type FROM csav3.crossings")
    crossings = cur.fetchall() 
    return crossings;


def get_pts_within_radius(cur, gps_pos, radius):  # gps_pos is a string of format 'lon, lat'

    """
    Arguments:
        gps_pos: current gps position of the car
        radius: the radius within which all points should be queried

    Returns:
        All points and relevant information from the hd map within 'radius'
    """

    cur.execute("SELECT CAST(geom AS point), lane_id, segment_id, width, geom, speed_limit FROM csav3.lane WHERE ST_DWithin(csav3.lane.geom::geography, ST_MakePoint({})::geography, {});".format(str(gps_pos), str(radius)))
    pts_within_radius = cur.fetchall()

    return pts_within_radius


def locate(pts_within_radius):

    """
    Arguments:
        pts_within_radius: All points and relevant info obtained from the get_pts_within_radius() function.

    Returns:
        Current lane_id and segment_id of the car
    """

    try:
        mode_segId = statistics.mode([i[2] for i in pts_within_radius])
    except:
        mode_segId = pts_within_radius[0][2]

    try:
        mode_laneId = statistics.mode(
            [i[1] for i in pts_within_radius if i[2] == mode_segId]
        )
    except:
        for pt in pts_within_radius:
            if pt[2] == mode_segId:
                mode_laneId = pt[1]
                break

    return mode_laneId, mode_segId


def get_lane_features(pts_within_radius, mode_laneId, mode_seg_id, gps_pos, car_bear):

    """
    Arguments:
        pts_within_radius: All points and relevant info obtained from the get_pts_within_radius() function.
        mode_laneId: current lane_id of the car
        mode_seg_id: current segment_id of the car
        gps_pos: current gps position of the car
        car_bear: bearing angle of the car

    Returns:
        min_dist: distance to the nearest road edge
        is_right: whether the min_dist is to the right edge of the road or not (bool)
        lane_width: width of the lane
        min_geom: geomtery of the point from which min_dist is calculated
        opp_geom: geometry of the point on the opposite side to min_geom
        current_speed: current speed limit of the lane
    """

    pts_dist = [i for i in pts_within_radius if i[1] == mode_laneId]
    possible_pts_opp = [
        i for i in pts_within_radius if i[1] == mode_laneId and i[2] == mode_seg_id
    ]
    gps_lon = str(gps_pos).split(",")[0][1:]
    gps_lat = str(gps_pos).split(",")[1][:-1]
    min_dist = float("inf")
    min_index = -1

    for i, point in enumerate(pts_dist):
        lon = point[0].split(",")[0][1:]
        lat = point[0].split(",")[1][:-1]
        dist = funs.distance(float(gps_lat), float(lat), float(gps_lon), float(lon))
        if dist < min_dist:
            min_dist = dist
            min_index = i

    lane_width = pts_dist[min_index][-3]
    min_geom = pts_dist[min_index][-2]
    current_speed = pts_dist[min_index][-1]

    _, _, is_right = funs.component_dist(
        car_bear,
        funs.bearing(
            float(gps_lat),
            float(pts_dist[min_index][0].split(",")[0][1:]),
            float(gps_lon),
            float(pts_dist[min_index][0].split(",")[1][:-1]),
        ),
        min_dist,
    )

    pts_opp = []
    for point in possible_pts_opp:
        lon = point[0].split(",")[0][1:]
        lat = point[0].split(",")[1][:-1]

        _, long, right = funs.component_dist(
            car_bear,
            funs.bearing(float(gps_lat), float(lat), float(gps_lon), float(lon)),
            funs.distance(float(gps_lat), float(lat), float(gps_lon), float(lon)),
        )
        if right != is_right:
            pts_opp.append([point, abs(long), right])

    min_long_dist = float("inf")
    min_long_idx = -1
    for i, point in enumerate(pts_opp):
        if point[1] < min_long_dist:
            min_long_dist = point[1]
            min_long_idx = i
    opp_geom = ([])  # just for the try except block, delete this line after removing the try except block
    try:
        opp_geom = pts_opp[min_long_idx][0][-1]
    except:
        # print("\nCurrent algorithm for lane color and type does not take into account this edge case!!!")
        opp_geom = min_geom

    return min_dist, is_right, lane_width, min_geom, opp_geom, current_speed


def get_color_and_type(cur, geom):  # gps_pos is a string of format 'lon, lat'

    """
    Arguments:
        geom: geomtry of the point whose color and type is needed
    Returns:
        nearest_marker: this contains the color and type information
    """

    cur.execute(
        "SELECT type, color FROM csav3.marker WHERE CAST(geom AS text)='{}'".format(
            geom
        )
    )
    nearest_marker = cur.fetchall()

    return nearest_marker


def get_speed_limits(cur, gps_pos, lane, seg, car_bear, current_speed_limit):

    """
    Arguments:
        gps_pos: current gps position of the car
        lane: current lane_id of the car
        seg: current segment_id of the car
        car_bear: bearing angle of the car
        current_speed_limit: current speed limit where the car is

    Returns:
        pts_in_laneline: all points that are ahead of the car in the lane's line
        dist_speed_limit_change: distance (in m) to the next speed limit change point
        new_speed_limit: new speed limit, if there is a change
    """

    cur.execute(
        "SELECT CAST(geom AS point), speed_limit FROM csav3.lane WHERE csav3.lane.lane_id = {} \
                AND csav3.lane.segment_id = {} AND ABS({} - degrees(ST_Azimuth(ST_SetSRID(ST_MakePoint{},4326), \
                csav3.lane.geom))) < 90 AND ST_DWithin(csav3.lane.geom::geography, ST_MakePoint{}::geography, 40) \
                ".format(
            lane, seg, car_bear, gps_pos, gps_pos
        )
    )
    pts_in_laneline = (
        cur.fetchall()
    )  # this query is to get all pts that are ahead of us in the current lane line

    # print(gps_pos)
    # index 0 is lat/lon, 1 is speed limit
    # gps_lon = str(gps_pos).split(',')[0][1:]
    # gps_lat = str(gps_pos).split(',')[1][:-1]
    gps_lon = gps_pos[0]
    gps_lat = gps_pos[1]

    dist_list = []
    for point in pts_in_laneline:
        # print(point)
        lon, lat = float(point[0].split(",")[0][1:]), float(point[0].split(",")[1][:-1])
        lat_dist, lon_dist, is_right = funs.component_dist(
            car_bear,
            funs.bearing(float(gps_lat), lat, float(gps_lon), lon),
            funs.distance(float(gps_lat), lat, float(gps_lon), lon),
        )
        dist_list.append([lon_dist, point[1]])

    first_arg = lambda pt: pt[0]
    dist_list.sort(key=first_arg)
    # print(dist_list)
    dist_speed_limit_change = None
    new_speed_limit = None
    for i, point in enumerate(dist_list):
        if point[1] != current_speed_limit:
            dist_speed_limit_change = point[0]
            new_speed_limit = point[1]
            break

    return pts_in_laneline, dist_speed_limit_change, new_speed_limit



def get_limit_lines(cur, gps_pos, lane, seg, car_bear):

    """
    Arguments:
        gps_pos: current gps position of the car
        lane: current lane_id of the car
        seg: current segment_id of the car
        car_bear: bearing angle of the car

    Returns:
        pts_lon_limit[min_lon_idx][0][1]: type index of the limit line
        min_lon_dist: distance to the limit line in metres
    """

    gps_lon = gps_pos[0]
    gps_lat = gps_pos[1]

    cur.execute(
        "SELECT CAST(geom AS point), type FROM csav3.crossings \
                                WHERE \
                                ST_DWithin(csav3.crossings.geom::geography, ST_MakePoint({})::geography, 10)".format(str(gps_lon) + ', ' + str(gps_lat))
    )
    pts_in_laneline = (
        cur.fetchall()
    )  # this query is to get all pts that are ahead of us in the current lane line

    pts_lon_limit = []
    for point in pts_in_laneline:
        lon = point[0].split(",")[0][1:]
        lat = point[0].split(",")[1][:-1]

        lati, long, right = funs.component_dist(
            car_bear,
            funs.bearing(float(gps_lat), float(lat), float(gps_lon), float(lon)),
            funs.distance(float(gps_lat), float(lat), float(gps_lon), float(lon)),
        )

        pts_lon_limit.append((point, long))

    try:
        min_lon_dist = float("inf")
        min_lon_idx = -1
        for i, point in enumerate(pts_lon_limit):
            if point[1] < min_lon_dist:
                min_lon_dist = point[1]
                min_lon_idx = i
        pts_lon_limit_check = pts_lon_limit[min_lon_idx][0][1]

    except:
        pts_lon_limit_check = None

    return pts_lon_limit_check, min_lon_dist
