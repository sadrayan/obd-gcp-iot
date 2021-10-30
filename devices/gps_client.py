import serial
import time
import pynmea2
from datetime import datetime


# https://www.engineersgarage.com/articles-raspberry-pi-neo-6m-gps-module-interfacing/
# $GPGLL,Latitude,DirLat,Longitude,DirLongitude,hhmmss:ss,A,cs<CR><LF>

class GPSClient:
	def __init__(self):

		self.ser = serial.Serial(port = '/dev/ttyUSB2', baudrate=9600, timeout=5)
		self.ser.flushInput()

		self.start_session()
	
	def start_session(self):
		# Turn on GPS?
		self.ser.write(('AT+CGPS=1,1'+'\r\n').encode())
		print('Starting GPS Session...')
		time.sleep(5)

	def get_gps_coordinate(self):
		
		while 1:
			try:
				self.ser.write(('AT+CGPSINFO'+'\r\n').encode())
				time.sleep(0.5)
				line = self.ser.readline().decode('ascii', errors='replace')
				gsp_response = dict()
				# print(line) 
				if ',,,,,,' in line:
					print('GPS is not ready')
					self.start_session()
					# time.sleep(1)
					continue

				if '+CGPSINFO:' in line:
					print(line)
					nmeaobj = pynmea2.parse('$GPGLL,' + line.split(' ')[1].strip())
					# print(nmeaobj.fields)
					gsp_response['latitude']  = self.decode(nmeaobj.lat, nmeaobj.lat_dir)      		# ±dd.dddddd            [-90.000000,90.000000]
					gsp_response['longitude'] = self.decode(nmeaobj.lon, nmeaobj.lon_dir)		    # ±ddd.dddddd           [-180.000000,80.000000]
					gsp_response['lat_dir']   = nmeaobj.lat_dir
					gsp_response['lon_dir']   = nmeaobj.lon_dir
					gsp_response['latitude_dds']   = {'latitude_minutes'  : nmeaobj.latitude_minutes,  'latitude_seconds' : nmeaobj.latitude_seconds}
					gsp_response['longitude_dds']  = {'longitude_minutes' : nmeaobj.longitude_minutes, 'longitude_seconds': nmeaobj.longitude_seconds}
					# gsp_response['altitude'] = 0.0     # in meters
					# gsp_response['speed'] = 0.0        # km/h [0,999.99]
					gsp_response['timestamp'] = str(datetime.utcnow()) 
					# print(gsp_response)
					print('https://www.google.com/maps?q={},{}'.format(gsp_response['latitude'], gsp_response['longitude']))
					return gsp_response
			except pynmea2.ParseError as e:
				print('Parse error: {}'.format(e))
				continue
			except serial.SerialException as e:
				print('Device error: {}'.format(e))
				break

	# Convert NMEA absolute position to decimal degrees
	# "ddmm.mmmm" or "dddmm.mmmm" really is D+M/60,
	# then negated if quadrant is 'W' or 'S'
	def decode(self, coord, dir):
		#Converts DDDMM.MMMMM > DD deg MM.MMMMM min
		x = coord.split(".")
		head = x[0]
		tail = x[1]
		deg = head[0:-2]
		min = head[-2:]
		result = float(deg) + (float(min + "." + tail) / 60)
		if 'W' == dir or 'S' == dir:
			result = -result 
		return  result
		# return deg + " deg " + min + "." + tail + " min"
