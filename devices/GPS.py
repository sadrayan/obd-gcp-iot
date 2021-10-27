#!/usr/bin/python
# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO

import serial
import time


# 4349.124818,N,07922.705429,W,231021,211737.0,194.9,0.0,82.1
class GPS:
	def __init__(self):

		self.ser = serial.Serial(port = '/dev/ttyUSB2', baudrate=9600)
		self.ser.flushInput()

		self.power_key = 6
		self.rec_buff = ''
		rec_buff2 = ''
		time_count = 0

	def send_at(self, command, back, timeout):
		self.rec_buff = ''
		self.ser.write((command+'\r\n').encode())
		print(command)
		time.sleep(timeout)
		if self.ser.inWaiting():
			time.sleep(0.01 )
			self.rec_buff = self.ser.read(self.ser.inWaiting())
		if self.rec_buff != '':
			if back not in self.rec_buff.decode():
				print(command + ' ERROR')
				print(command + ' back:\t' + self.rec_buff.decode())
				return 0
			else:
				print(self.rec_buff.decode())
				return 1
		else:
			print('GPS is not ready')
			return 0

	def get_gps_position(self):
		rec_null = True
		answer = 0
		print('Start GPS session...')
		self.rec_buff = ''
		self.send_at('AT+CGPS=1,1','OK',1)
		time.sleep(2)
		while rec_null:
			answer = self.send_at('AT+CGPSINFO','+CGPSINFO: ',1)
			print(answer)
			if 1 == answer:
				answer = 0
				if ',,,,,,' in self.rec_buff:
					print('GPS is not ready')
					rec_null = False
					time.sleep(1)
			else:
				print('error %d'%answer)
				self.rec_buff = ''
				self.send_at('AT+CGPS=0','OK',1)
				return False
			time.sleep(1.5)


	def power_on(self, power_key):
		print('SIM7600X is starting:')
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(power_key,GPIO.OUT)
		time.sleep(0.1)
		GPIO.output(power_key,GPIO.HIGH)
		time.sleep(2)
		GPIO.output(power_key,GPIO.LOW)
		time.sleep(20)
		self.ser.flushInput()
		print('SIM7600X is ready')

	def power_down(self, power_key):
		print('SIM7600X is loging off:')
		GPIO.output(power_key,GPIO.HIGH)
		time.sleep(3)
		GPIO.output(power_key,GPIO.LOW)
		time.sleep(5)
		print('Good bye')

	def run(self):
		try:
			self.power_on(self.power_key)
			self.get_gps_position()
			self.power_down(self.power_key)
		except:
			if self.ser != None:
				self.ser.close()
			self.power_down(self.power_key)
			GPIO.cleanup()
		if self.ser != None:
				self.ser.close()
				GPIO.cleanup()	

# gps = GPS()
# gps.run()
