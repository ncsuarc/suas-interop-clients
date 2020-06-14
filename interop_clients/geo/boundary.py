from osgeo import ogr  # type: ignore

from interop_clients import api


def in_search_grid(mission: api.Mission, lat: float, lon: float) -> bool:
    """Check if point is within the boundary of an active mission.

    Args:
        mission: Mission to check the search grid of.
        lat: Latitude of coordinate to check.
        lon: Longitude of coordinate to check.

    Returns:
        True if point is within boundary, otherwise false
    """
    target_point = ogr.Geometry(ogr.wkbPoint)
    target_point.AddPoint(lat, lon)

    grid_points = mission["search_grid_points"]
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for point in grid_points:
        ring.AddPoint(point["latitude"], point["longitude"])
    ring.AddPoint(grid_points[0]["latitude"], grid_points[0]["longitude"])

    polygon = ogr.Geometry(ogr.wkbPolygon)
    polygon.AddGeometry(ring)

    return polygon.Contains(target_point)
