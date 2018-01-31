import requests
import sys
if (sys.version_info > (3, 0)):
    from PyQt5.QtCore import QSettings
else:
    import sip
    sip.setapi('QVariant', 2)
    from PyQt4.QtCore import QSettings

class Interop(object):
    """Send plane location

    """
    def __init__(self):
        self.session = requests.session()
        settings = QSettings("ARC", "PCC Interop Plugin")
        self.host = str(settings.value('host'))
        self.port = str(settings.value('port'))
        username = str(settings.value('username'))
        password = str(settings.value('password'))

        payload = {'username': username, 'password': password}
        self.session.post("http://%s:%s/api/login"%(self.host, self.port),
                          data=payload, timeout=5).raise_for_status()

    def get_missions(self):
        missions = self.session.get('http://%s:%s/api/missions'%(self.host, self.port))
        missions.raise_for_status()
        return missions.json()

    def get_obstacles(self):
        obstacles = self.session.get('http://%s:%s/api/obstacles'%(self.host, self.port))
        obstacles.raise_for_status()
        return obstacles.json()

    def get_targets(self):
        targets = self.session.get('http://%s:%s/api/targets'%(self.host, self.port))
        targets.raise_for_status()
        return targets.json()

    def delete_target(self, i):
        self.session.delete('http://%s:%s/api/targets/%d/image'
                            %(self.host, self.port, i)).raise_for_status()
        self.session.delete('http://%s:%s/api/targets/%d'
                            %(self.host, self.port, i)).raise_for_status()

    def post_target(self, target_json, image):
        target_data = self.session.post('http://%s:%s/api/targets'
                                        %(self.host, self.port),
                                        json=target_json)
        target_data.raise_for_status()
        target_id = target_data.json().get('id')
        self.session.post('http://%s:%s/api/targets/%d/image'
                          %(self.host, self.port, target_id),
                          data=image).raise_for_status()
        return target_id

    def send_coord(self, lat, lon, alt, heading):
        coord = {'latitude': lat, 'longitude': lon, 'altitude_msl': alt, 'uas_heading': heading}
        plane_location = self.session.post("http://%s:%s/api/telemetry"%(self.host, self.port), data = coord)
        plane_location.raise_for_status()
