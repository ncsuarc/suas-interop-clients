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
        self.ip = str(settings.value('host'))
        self.port = str(settings.value('port'))
        username = str(settings.value('username'))
        password = str(settings.value('password'))

        payload = {'username': username, 'password': password}
        response = self.session.post("http://%s:%s/api/login"%(self.ip, self.port), data = payload, timeout = 5)
        print(response.text)

    def get_missions(self):
        missions = self.session.get('http://%s:%s/api/missions'%(self.ip, self.port))
        return missions.json()

    def get_obstacles(self):
        obstacles = self.session.get('http://%s:%s/api/obstacles'%(self.ip, self.port))
        return obstacles.json()

    def get_targets(self):
        targets = self.session.get('http://%s:%s/api/targets'%(self.ip, self.port))
        return targets.json()

    def delete_target(self, i):
        self.session.delete('http://%s:%s/api/targets/%d/image'%(self.ip, self.port, i))
        self.session.delete('http://%s:%s/api/targets/%d'%(self.ip, self.port, i))

    def post_target(self, target_json, image):
        interop_target_data = self.session.post('http://%s:%s/api/targets'%(self.ip, self.port), json = target_json)
        target_id = interop_target_data.json().get('id')
        img_ret = self.session.post('http://%s:%s/api/targets/%d/image'%(self.ip, self.port, target_id), data = image)
        return target_id

    def send_coord(self, lat, lon, alt, heading):
        coord = {'latitude': lat, 'longitude': lon, 'altitude_msl': alt, 'uas_heading': heading}
        plane_location = self.session.post("http://%s:%s/api/telemetry"%(self.ip, self.port), data = coord)
        print(plane_location.text)


