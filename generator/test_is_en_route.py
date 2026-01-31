#!/usr/bin/env python3
"""
Quick test for is_en_route (util/__init__.py).

Usage (from repo root):
  python generator/test_is_en_route.py

Requires: OSRM running (e.g. on localhost:5001) and config with valid coordinates.
"""

import sys

# Allow running from repo root or from generator/
if __name__ == "__main__" and "generator" not in sys.path:
    try:
        import config
    except ImportError:
        sys.path.insert(0, "generator")

import config
from util import is_en_route, find_path_between_points_in_osrm, NoRoute


def _latlon_to_xy(lat, lon):
    """Config uses (lat, lon); is_en_route expects (x, y) = (lon, lat)."""
    return (lon, lat)


def test_is_en_route():
    # Use first and last of MAGIN_HOTSPOTS as route endpoints (config uses lat, lon)
    hotspots = getattr(config, "MAGIN_HOTSPOTS", None) or getattr(config, "REAL_MAGIN_HOTSPOTS", [])
    if len(hotspots) < 2:
        print("Need at least 2 points in config.MAGIN_HOTSPOTS (or REAL_MAGIN_HOTSPOTS).")
        return False

    p1_latlon = hotspots[0]
    p2_latlon = hotspots[-1]
    p1 = _latlon_to_xy(*p1_latlon)
    p2 = _latlon_to_xy(*p2_latlon)

    try:
        path = find_path_between_points_in_osrm(p1, p2)
    except NoRoute:
        print("NoRoute between first and last hotspot; try different points.")
        return False
    except Exception as e:
        print("OSRM / network error:", e)
        return False

    if len(path) < 2:
        print("Path too short.")
        return False

    # Point on route: use midpoint of the path (path is already (lon, lat))
    mid = len(path) // 2
    p3_on_route = path[mid]

    # Point off route: shift midpoint slightly so it's not on the road
    off_lon, off_lat = p3_on_route[0] + 0.0005, p3_on_route[1] + 0.0005
    p3_off_route = (off_lon, off_lat)

    ok = True

    # Test 1: point on route should return True
    try:
        result = is_en_route(p1, p2, p3_on_route)
        if result is True:
            print("PASS: is_en_route(p1, p2, point_on_route) == True")
        else:
            print("FAIL: is_en_route(p1, p2, point_on_route) should be True, got", result)
            ok = False
    except Exception as e:
        print("FAIL: is_en_route(p1, p2, point_on_route) raised:", e)
        ok = False

    # Test 2: point off route should return False
    try:
        result = is_en_route(p1, p2, p3_off_route)
        if result is False:
            print("PASS: is_en_route(p1, p2, point_off_route) == False")
        else:
            print("FAIL: is_en_route(p1, p2, point_off_route) should be False, got", result)
            ok = False
    except Exception as e:
        print("FAIL: is_en_route(p1, p2, point_off_route) raised:", e)
        ok = False

    return ok


if __name__ == "__main__":
    print("Testing is_en_route (requires OSRM on", getattr(config, "OSRM_URL", "localhost:5001") + ")...")
    success = test_is_en_route()
    print("Done." if success else "Some tests failed.")
    sys.exit(0 if success else 1)
