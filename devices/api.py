import configparser
from core import Core
from obd_client import OBDClient
from gps_client import GPSClient
import schedule
import json
import time

class CVTClient:

    def __init__(self):
        config = configparser.ConfigParser()		
        config.read("config.ini")
        self.core = Core(config['DEFAULT'])
        
        self.gps_client = GPSClient()
        self.obd_client = OBDClient()

        schedule.every(int(config['DEFAULT']['obd_update_interval_sec'])).seconds.do(self.send_telemetry)
        print('Done creating the Core')

    def get_message(self):
        response = self.obd_client.get_readings()
        response['gps'] = self.gps_client.get_gps_coordinate()
        payload = dict()
        payload['deviceId']     = response['deviceId']
        payload['speed']        = response['speed']
        payload['RPM']          = response['RPM']
        payload['fuel_status']  = response['fuel_status']
        payload['latitude']     = response['gps']['latitude']
        payload['longitude']    = response['gps']['longitude']
        payload['timestamp']    = response['timestamp']
        return json.dumps(payload)

    def send_telemetry(self):
        self.core.publish_message(self.get_message())         


if __name__ == '__main__':
    try:
        client = CVTClient()
        while 1:
            schedule.run_pending()
            pass
    except KeyboardInterrupt:
        print('Shutting down :)')
