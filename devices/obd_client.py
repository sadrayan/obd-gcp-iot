import obd
import json
import configparser
import datetime

class OBDClient:
    def __init__(self):
        config = configparser.ConfigParser()		
        config.read("config.ini")
        self.config = config['DEFAULT']

        self.connection = obd.OBD('/dev/pts/3') 


    def get_readings(self):
        response = self.connection.query(obd.commands.SPEED)         
        payload = dict()
        payload['deviceId'] = self.config['device_id']
        payload['timestamp'] = datetime.datetime.strftime(datetime.datetime.utcnow(), '%Y-%m-%d %H:%M:%S')
        payload['speed'] = str(response.value.to('kph'))
        return json.dumps(payload)
