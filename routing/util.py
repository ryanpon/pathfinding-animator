
from math import radians, cos, sin, asin, sqrt

def minkowski(x1, y1, x2, y2, p=2**.5):
    return (abs(x2 - x1) ** p + abs(y2 - y1) ** p) ** (1/p)

def euclidean(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** .5

def manhattan(x1, y1, x2, y2):
    return abs(x2 - x1) + abs(y2 - y1)

def octile(x1, y1, x2, y2):
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    return max(dx, dy) + (2**.5 - 1) * min(dx, dy)

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2]) 
    # haversine formula 
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km 

def bearing(lat1, lon1, lat2, lon2, positive):
    """Given lat/lons, returns absolute bearing from first to second."""
    import math
    d_lon = lon2 - lon1
    y_val = math.sin(d_lon) * math.cos(lat2)
    x_val = (math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * 
             math.cos(lat2) * math.cos(d_lon))
    bearing = math.degrees(math.atan2(y_val, x_val))
    if positive and bearing < 0:
        bearing = 360 + bearing
    return bearing

def bearing_angle(brng1, brng2):
    """Returns the smallest angle between two bearings."""
    if (brng1 >= 0 and brng2 >= 0 or brng1 <= 0 and brng2 <= 0):
        return abs(brng1 - brng2)
    else:
        if brng1 < 0:
            result = abs(180 + brng1) + (180 - brng2)
        elif brng1 > 0:
            result = abs(180 + brng2) + (180 - brng1)
        if result > 180:
            result = abs(result - 360)
        return result

def path_len(coords_list):
    """Given a list of (lat,lng) tuples, returns the length in km"""
    if not len(coords_list): return 0
    length = 0
    prev_lat, prev_lng = coords_list[0]
    for lat,lng in coords_list:
        length += haversine(prev_lat, prev_lng, lat, lng)
        prev_lat, prev_lng = lat, lng
    return length