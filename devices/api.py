import configparser
from core import Core
from obd_client import OBDClient

def main():
    config = configparser.ConfigParser()		
    config.read("config.ini")
    core = Core(config['DEFAULT'])
    print('Done creating the Core')
    obd_client = OBDClient()
    print(obd_client.get_readings())
    core.publish_message(obd_client.get_readings())



if __name__ == '__main__':
    main()
    while 1:
        pass