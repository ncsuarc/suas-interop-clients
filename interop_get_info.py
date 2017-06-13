import argparse 
import os
import json
import csv
import time
import datetime

from ARC.interop import Interop

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--save', action='store_true',  help='Save interop data?')
    parser.add_argument('-i', '--interval', help='Interval in seconds between requests to the interop server', type=float)
    parser.add_argument('-r', '--record-time', help='Time in seconds to record data from the interop server', type=int)
    parser.add_argument('-d', '--save-directory', help='The name of the directory to save in')
    parser.add_argument('-csv', '--csv', help='The name of the csv file to save waypoints in')
    args = parser.parse_args()
    if args.save:
        saveData = True
        if not (args.interval and args.record_time):
            raise ValueError('Interval and Record Time are required when saving data')
            saveData = False
        if args.save_directory:
            saveDir = args.save_directory
        else:
            saveDir = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    else:
        saveData = False
    io = Interop()

    missions = io.get_missions()
    if saveData:
        if not os.path.isdir(saveDir):
            if os.path.exists(saveDir):
                raise ValueError("Save directory %s already exists and is not a directory" % saveDir)
            else:
                os.mkdir(saveDir)
        with open(os.path.join(saveDir, 'missions.txt'), 'w') as mission_file:
            mission_file.write(json.dumps(missions))

    for mission in missions:
        if bool(mission.get('active')):
            active_mission = mission
            break

    print('\nEmergent')
    print(active_mission.get('emergent_last_known_pos'))

    print('\nOff-Axis')
    print(active_mission.get('off_axis_target_pos'))

    print('\nAir Drop')
    print(active_mission.get('air_drop_pos'))

    if args.csv:
        with open(args.csv, 'w') as csvFile:
            csvWriter = csv.writer(csvFile)
            interop_waypoints = active_mission.get('search_grid_points')
            waypoints = [None] * len(interop_waypoints)

            for point in interop_waypoints:
                waypoints[point.get('order') - 1] = [point.get('latitude'), point.get('longitude'), point.get('altitude_msl')]
            for point in waypoints:
                csvWriter.writerow(point)

    obstacles = io.get_obstacles()
    if saveData:
        with open(os.path.join(saveDir, 'stationary.txt'), 'w') as stationary_file:
            stationary_file.write(json.dumps(obstacles.get('stationary_obstacles')))
        with open(os.path.join(saveDir, 'moving.txt'), 'w') as moving_file:
            startTime = datetime.datetime.now()
            while (datetime.datetime.now() - startTime).total_seconds() < args.record_time:
                obstacles = io.get_obstacles()
                moving_obstacles = obstacles.get('moving_obstacles')
                moving_file.write('\n--------\n' + str(datetime.datetime.now()) + '\n')
                moving_file.write(json.dumps(moving_obstacles))
                time.sleep(args.interval)
