import HDMapsModule as maps
import lanes
from map_operators import funs

# API Imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"], # Replace with your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load():
    return maps.HDMapsModule()
A  = load()

@app.get('/limit-lanes')
def query_crossings():
    all_crossings = lanes.get_all_crossings(A.cur)
    json_crossings = {}
    for crossing in all_crossings:
        lat = crossing[0].split(',')[0][1:]
        lng = crossing[0].split(',')[1][:-1]
        json_crossings[str(crossing[1])] = {"latitude": lat, "longitude": lng, "segment_id": crossing[2], "lane_id": crossing[3], "type": crossing[4]}
    return json_crossings

@app.get('/lane-points')
def read_lane_points():
    full_lane_points = lanes.get_all_lanes(A.cur)
    partial_lane_points = {}
    for point in full_lane_points:
        lat = point[0].split(',')[0][1:]
        lng = point[0].split(',')[1][:-1]
        partial_lane_points[str(point[3])] = {"latitude": lat, "longitude": lng, "direction": str(point[1]), "point_id": str(point[2]), "segment_id": str(point[4])}
    return partial_lane_points



