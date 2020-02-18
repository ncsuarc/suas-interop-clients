import json

import requests


class Interop(object):
    """Send plane location

    """

    def __init__(self, host, port, username, password):
        self.session = requests.session()
        self.host = host
        self.port = port
        username = username
        password = password

        payload = {"username": username, "password": password}
        payload = json.dumps(payload)
        self.session.post(
            "http://%s:%s/api/login" % (self.host, self.port), data=payload
        ).raise_for_status()

    def get_missions(self, mission_id=1):
        missions = self.session.get(
            "http://%s:%s/api/missions/%s" % (self.host, self.port, mission_id)
        )
        missions.raise_for_status()
        return missions.json()

    def get_obstacles(self):
        obstacles = self.session.get(
            "http://%s:%s/api/obstacles" % (self.host, self.port)
        )
        obstacles.raise_for_status()
        return obstacles.json()

    def get_targets(self):
        targets = self.session.get(
            "http://%s:%s/api/targets" % (self.host, self.port)
        )
        targets.raise_for_status()
        return targets.json()

    def delete_target(self, i):
        try:
            self.session.delete(
                "http://%s:%s/api/odlcs/%d/image" % (self.host, self.port, i)
            ).raise_for_status()
        except Exception as e:
            print(repr(e))
        self.session.delete(
            "http://%s:%s/api/odlcs/%d" % (self.host, self.port, i)
        ).raise_for_status()

    def post_target(self, target_json, image):
        target_data = self.session.post(
            "http://%s:%s/api/targets" % (self.host, self.port),
            json=target_json,
        )
        try:
            target_data.raise_for_status()
        except:
            print(target_data.text)
            raise

        target_id = target_data.json().get("id")
        self.session.post(
            "http://%s:%s/api/targets/%d/image"
            % (self.host, self.port, target_id),
            data=image,
        ).raise_for_status()
        return target_id

    def send_coord(self, lat, lon, alt, heading):
        coord = {
            "latitude": lat,
            "longitude": lon,
            "altitude": alt,
            "heading": heading,
        }
        coord = json.dumps(coord)
        plane_location = self.session.post(
            "http://%s:%s/api/telemetry" % (self.host, self.port), data=coord
        )
        plane_location.raise_for_status()
