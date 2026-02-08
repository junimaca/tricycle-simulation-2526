"""
Helper functions that are used in generating actual scenarios.
"""

import random

import config
import entities
import util
from config import KALAYAAN_AVE, MAPAGKAWANGGAWA_ST, MAGINHAWA_ST, MALINGAP_ST
from shapely import get_coordinates
from shapely.geometry import LineString, Point

from util import NoRoute

major_roads = {
    "Kalayaan Avenue": LineString([(lon, lat) for lat, lon in KALAYAAN_AVE]),
    "Mapagkawanggawa St": LineString([(lon, lat) for lat, lon in MAPAGKAWANGGAWA_ST]),
    "Maginhawa St": LineString([(lon, lat) for lat, lon in MAGINHAWA_ST]),
    "Malingap St": LineString([(lon, lat) for lat, lon in MALINGAP_ST]),
}

def get_random(min, max):
    return min + random.random() * (max - min)

def gen_random_point():
    "Returns a random point in the map. It is likely you will NOT be using this directly."

    x = util.get_random(config.TOP_LEFT_X, config.BOT_RIGHT_X)
    y = util.get_random(config.BOT_RIGHT_Y, config.TOP_LEFT_Y)
    return entities.Point(x, y)

def gen_random_valid_point():
    "Returns a random point in the map that is on the road"

    point_raw = gen_random_point()
    point = entities.Point(*util.find_nearest_point_in_osrm_path(point_raw.x, point_raw.y))
    return point

def get_nearest_major_road(coords):
    "Returns the nearest major road to the point"

    p = Point(coords.x, coords.y)
    candidate_point = None
    min_distance = float('inf')
    nearest_road = ""

    for name, road in major_roads.items():
        candidate_point = road.interpolate(road.project(p))
        d = p.distance(candidate_point)
        if d < min_distance:
            nearest_road = name
            min_distance = d

    return nearest_road

def passenger_spawn_major_only():
    "Returns a random point in the map that is on the major road"

    point_A = gen_random_point()
    p = Point(point_A.x, point_A.y) 

   
    closest_point = None
    min_distance = float('inf')

    for line in major_roads.values():
        candidate_point = line.interpolate(line.project(p))
        d = p.distance(candidate_point)

        if d < min_distance:
            min_distance = d
            closest_point = candidate_point

    if closest_point is None:
        raise ValueError("major_roads is empty; cannot spawn on major road")

    return entities.Point(*util.find_nearest_point_in_osrm_path(closest_point.x, closest_point.y))

def get_valid_points(points):
    "Returns a list of valid points based on provided list. Each point in the list must be in (y,x)"
    return [entities.Point(*util.find_nearest_point_in_osrm_path(p[1], p[0])) for p in points]

def get_random_valid_point(points):
    "Returns a random point that is based from the provided list. Each point in the list must be in (y,x)"

    point_raw = random.choice(points)
    point = entities.Point(*util.find_nearest_point_in_osrm_path(point_raw[1], point_raw[0]))
    return point

def gen_random_bnf_roam_path():
    "Returns a back-n-forth path in the map"

    while True:
        point_1 = gen_random_valid_point()
        point_2 = gen_random_valid_point()

        try:
            # must have p1 -> p2
            util.find_path_between_points_in_osrm(point_1.toTuple(), point_2.toTuple())
            # must have p2 -> p1
            util.find_path_between_points_in_osrm(point_2.toTuple(), point_1.toTuple())

            return entities.Cycle(point_1, point_2)
        except NoRoute:
            continue

def gen_random_bnf_roam_path_with_points(*points):
    "Returns a back-n-forth path that contains the points"

    if len(points) == 0:
        return gen_random_bnf_roam_path()
    elif len(points) == 1:
        while True:
            point_1 = points[0]
            point_2 = gen_random_point()

            try:
                # must have p1 -> p2
                util.find_path_between_points_in_osrm(point_1.toTuple(), point_2.toTuple())
                # must have p2 -> p1
                util.find_path_between_points_in_osrm(point_2.toTuple(), point_1.toTuple())

                return entities.Cycle(point_1, point_2)
            except NoRoute:
                continue
    elif len(points) == 2:
        util.find_path_between_points_in_osrm(points[0].toTuple(), points[1].toTuple())
        util.find_path_between_points_in_osrm(points[1].toTuple(), points[0].toTuple())
        return entities.Cycle(points[0], points[1])
    else:
        for i in range(len(points)-1):
            util.find_path_between_points_in_osrm(points[i].toTuple(), points[i+1].toTuple())
            util.find_path_between_points_in_osrm(points[i+1].toTuple(), points[i].toTuple())
        return entities.Cycle(points[0], points[1])

def gen_major_road_roam_path(road_name):
    coords = get_coordinates(major_roads[road_name])
    endpoint_1 = entities.Point(*util.find_nearest_point_in_osrm_path(*coords[0]))
    endpoint_2 = entities.Point(*util.find_nearest_point_in_osrm_path(*coords[-1]))
    return gen_random_bnf_roam_path_with_points(endpoint_1, endpoint_2)
    
