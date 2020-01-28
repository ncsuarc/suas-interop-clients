import argparse 
from osgeo import ogr
from ARC.interop import Interop

host = "192.168.1.130"
port = "8000"
username = "testuser"
password = "testpass"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-lat","--lat", required=True, type=float)
    parser.add_argument("-lon","--lon", required=True, type=float)
    args = parser.parse_args()
    
    target_point = ogr.Geometry(ogr.wkbPoint)
    target_point.AddPoint(args.lat,args.lon)

    io = Interop(host, port, username, password)
    missions = io.get_missions()
    for mission in missions:
        if bool(mission.get('active')):
            active_mission = mission
            break
    interop_grid_points = active_mission.get('search_grid_points')
    grid_points = [None] * len(interop_grid_points)

    for point in interop_grid_points: 
        grid_points[point.get('order') - 1] = (point.get('latitude'), point.get('longitude'))

    ring = ogr.Geometry(ogr.wkbLinearRing)

    for point in grid_points:
        ring.AddPoint(point[0], point[1])

    ring.AddPoint(grid_points[0][0], grid_points[0][1])
    polygon = ogr.Geometry(ogr.wkbPolygon)  
    polygon.AddGeometry(ring)

    print(polygon.Contains(target_point))
