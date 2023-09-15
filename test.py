import HDMapsModule as maps
import lanes

def load():
    return maps.HDMapsModule()
A  = load()

latlon = [-83.69793437, 42.30088060]

limit_lines = lanes.get_limit_lines(A.cur, latlon, 1, 4562327, 0)
print(limit_lines)