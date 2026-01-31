import math
import random
import json
import requests
import polyline
from config import OSRM_URL
from shapely.geometry import LineString, Point

class NoRoute(Exception):
    pass

def find_nearest_point_in_osrm_path(x, y):
    """
    Returns a tuple containing the coordinates of the NEAREST point on the road.
    
    Parameters:
    x and y coordinates of the point

    Return value:
    (x_nearest, y_nearest)
    """
    response = requests.get(f'{OSRM_URL}/nearest/v1/driving/{x},{y}')
    data = response.json()
    new_x = data['waypoints'][0]['location'][0]
    new_y = data['waypoints'][0]['location'][1]

    return new_x, new_y

def find_path_between_points_in_osrm(p1, p2):
    """
    Generates an array containing a sequence of tuples (x, y) that represents adjacent points 
    describing the path to reach p2 from p1.

    Note: It may be possible that there exists no such path. In this case, a NoRoute exception is 
    raised.

    Parameters:
    p1 and p2 - (x ,y) tuples describing the coordinates

    Return value:
    path - [(x1, y1), (x2, y2), ..., (xn, yn)]
    """
    
    x1, y1 = p1
    x2, y2 = p2
    
    # First find the nearest points on the road network
    x1, y1 = find_nearest_point_in_osrm_path(x1, y1)
    x2, y2 = find_nearest_point_in_osrm_path(x2, y2)
    
    response = requests.get(f'{OSRM_URL}/route/v1/driving/{x1},{y1};{x2},{y2}')
    data = response.json()
    
    if data['code'] == "NoRoute":
        raise NoRoute
    else:
        routes = polyline.decode(data['routes'][0]['geometry'])
        path = [(x, y) for y,x in routes]
        return path

def get_random(min, max):
    return min + random.random() * (max - min)

def get_euclidean_distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def interpolate_points(p1, p2, percentage):
    return (p1[0] + (p2[0] - p1[0]) * percentage, p1[1] + (p2[1] - p1[1]) * percentage)

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great-circle distance between two points 
    on the Earth's surface using the Haversine formula.

    Parameters:
    lat1, lon1 : float
        Latitude and Longitude of point 1 in decimal degrees.
    lat2, lon2 : float
        Latitude and Longitude of point 2 in decimal degrees.

    Returns:
    distance : float
        Distance between the two points in kilometers.
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    r = 6371  # Radius of Earth in kilometers. Use 3956 for miles.
    distance = r * c

    return distance * 1000

def is_en_route(p1, p2, p3):
    # Is p3 in the route between p1 and p2?

    """
    Parameters:
    p1 and p2 - (x ,y) sou

    Return value:
    path - [(x1, y1), (x2, y2), ..., (xn, yn)]
    """
    
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    
    # First find the nearest points on the road network
    x1, y1 = find_nearest_point_in_osrm_path(x1, y1)
    x2, y2 = find_nearest_point_in_osrm_path(x2, y2)
    x3, y3 = find_nearest_point_in_osrm_path(x3, y3)

    # Request GeoJSON geometry so we can reliably access ['coordinates'].
    # Without this, OSRM commonly returns an encoded polyline string.
    response = requests.get(
        f'{OSRM_URL}/route/v1/driving/{x1},{y1};{x2},{y2}',
        params={"overview": "full", "geometries": "geojson"},
    )
    data = response.json()
    if isinstance(data, str):
        data = json.loads(data)

    if data.get('code') == "NoRoute":
        raise NoRoute

    geometry = data['routes'][0]['geometry']
    # If OSRM ignored our geometries=geojson param (or a proxy/cached response changed it),
    # geometry may still be an encoded polyline string.
    if isinstance(geometry, str):
        routes = polyline.decode(geometry)
        # polyline.decode returns [(lat, lon), ...]; we use (lon, lat) as x,y
        route_coords = [(lon, lat) for lat, lon in routes]
    else:
        route_coords = geometry['coordinates']
    route = LineString([tuple(coord) for coord in route_coords])
    p = Point(x3, y3)
    
    return route.distance(p) < 0.0001