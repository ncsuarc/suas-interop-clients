import argparse 

from interop import InterOp

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u","--username", required=True)
    parser.add_argument("-p","--password", required=True)
    parser.add_argument("-ip","--ip", required=True)
    parser.add_argument("-port","--port", required=True)
    args = parser.parse_args()
    io = InterOp(args.username, args.password, args.ip, args.port)
    missions = io.get_missions()
    print('\nMission 0')
    print(missions[0])

    print('\nEmergent')
    print(missions[0].get('emergent_last_known_pos'))

    print('\nOff-Axis')
    print(missions[0].get('off_axis_target_pos'))

    print('\nAir Drop')
    print(missions[0].get('air_drop_pos'))

    obstacles = io.get_obstacles()
    print('\nStationary')
    print(obstacles)
    print('\nStationary')
    print(obstacles.get('stationary_obstacles'))
    print('\nMoving')
    print(obstacles.get('moving_obstacles'))
