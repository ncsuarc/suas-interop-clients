from interop_clients import Interop
from osgeo import ogr


def check_point(io: Interop, lat: float, lon: float) -> bool:
    """
    Check if point is within the boundary of an active mission.

    Args:
        io: The Interop object.
        lat: The float value of your Latitude coordinate.
        lon: The float value of your Longitude coordinate.

    Returns:
        True if point is within boundary, otherwise false
    """
    target_point = ogr.Geometry(ogr.wkbPoint)
    target_point.AddPoint(lat, lon)

    missions = io.get_missions()
    for mission in missions:
        if bool(mission.get("active")):
            active_mission = mission
            break
    interop_grid_points = active_mission.get("search_grid_points")
    grid_points = [None] * len(interop_grid_points)

    for point in interop_grid_points:
        grid_points[point.get("order") - 1] = (
            point.get("latitude"),
            point.get("longitude"),
        )

    ring = ogr.Geometry(ogr.wkbLinearRing)

    for point in grid_points:
        ring.AddPoint(point[0], point[1])

    ring.AddPoint(grid_points[0][0], grid_points[0][1])
    polygon = ogr.Geometry(ogr.wkbPolygon)
    polygon.AddGeometry(ring)

    return polygon.Contains(target_point)
