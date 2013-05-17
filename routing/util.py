
from heapq import heappush, heappop
from math import radians, cos, sin, asin, sqrt

def haversine((lat1, lon1), (lat2, lon2)):
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

def distance(lat1, lon1, lat2, lon2):
    """Returns a fast estimate of the distance between two lat/lon points."""
    return ((lat1 - lat2)**2 + (lon1 - lon2)**2)**.5

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


class HeapSet(object):
    """ 
    A heap that also adds each item to a set for O(1) membership test. 

    If performance is absolutely key, you should use separate heap and set 
    objects directly in the code. Only implements the methods needed by our
    AStar algorithms.
    """
    #__slots__ = ('set', 'heap')
    def __init__(self):
        self.set = set()
        self.heap = []

    def push(self, value, item=None):
        self.set.add(item)
        heappush(self.heap, (value, item))

    def pop(self):
        item, value = heappop(self.heap)
        self.set.discard(item)
        return item, value

    def __contains__(self, item):
        return item in self.set

    def __nonzero__(self):
        return bool(self.heap)
