import csv
import datetime
import json
import os

from interop_clients import InteropClient


def run(
    client: InteropClient,
    save: bool,
    interval: float,
    record_time: int,
    save_directory: str,
    csv_path: str,
) -> None:
    if save:
        saveData = True
        if not (interval and record_time):
            raise ValueError(
                "Interval and Record Time are required when saving data"
            )
            saveData = False
        if save_directory:
            saveDir = save_directory
        else:
            saveDir = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    else:
        saveData = False

    mission = client.get_missions()
    if saveData:
        if not os.path.isdir(saveDir):
            if os.path.exists(saveDir):
                raise ValueError(
                    "Save directory %s already exists and is not a directory"
                    % saveDir
                )
            else:
                os.mkdir(saveDir)
        with open(os.path.join(saveDir, "missions.txt"), "w") as mission_file:
            mission_file.write(json.dumps(mission))

    active_mission = mission
    print("\nEmergent")
    print(active_mission.get("emergentLastKnownPos"))

    print("\nOff-Axis")
    print(active_mission.get("offAxisOdlcPos"))

    print("\nAir Drop")
    print(active_mission.get("airDropPos"))

    if csv:
        with open(csv_path, "w") as csvFile:
            csvWriter = csv.writer(csvFile)
            interop_waypoints = active_mission.get("waypoints")

            for point in interop_waypoints:
                csvWriter.writerow(
                    [point["latitude"], point["longitude"], point["altitude"]]
                )
