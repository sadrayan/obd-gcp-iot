import obd
import json
import configparser
import datetime

class OBDClient:
    def __init__(self):
        config = configparser.ConfigParser()		
        config.read("config.ini")
        self.config = config['DEFAULT']

        self.connection = obd.OBD('/dev/pts/2') 


    def get_readings(self):       
        payload = dict()
        payload['deviceId'] = self.config['device_id']
        payload['timestamp'] = datetime.datetime.strftime(datetime.datetime.utcnow(), '%Y-%m-%d %H:%M:%S')
        payload['speed'] = str(self.connection.query(obd.commands.SPEED).value.to('kph'))
        payload['fuel_status'] = str(self.connection.query(obd.commands.FUEL_STATUS).value)
        payload['RPM'] = str(self.connection.query(obd.commands.RPM).value)
        payload['fuel_level'] = str(self.connection.query(obd.commands.FUEL_LEVEL).value)
        payload['fuel_type'] = str(self.connection.query(obd.commands.FUEL_TYPE).value)
        return json.dumps(payload)
