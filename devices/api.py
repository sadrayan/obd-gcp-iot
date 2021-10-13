import configparser
from core import Core
from obd_client import OBDClient
import schedule
import time

def main():
    config = configparser.ConfigParser()		
    config.read("config.ini")
    core = Core(config['DEFAULT'])
    print('Done creating the Core')

    obd_client = OBDClient()
    core.publish_message(obd_client.get_readings())
    schedule.every(int(config['DEFAULT']['obd_update_interval_sec'])).seconds.do(core.publish_message, obd_client.get_readings())

if __name__ == '__main__':
    main()
    while 1:
        schedule.run_pending()
        pass