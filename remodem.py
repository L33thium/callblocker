#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os, time, serial

debug = None
done = False
class modem:
	def __init__(self):
		self.ser = serial.Serial(
			port = '/dev/ttyACM0',
			baudrate = 115200,
			parity = serial.PARITY_NONE,
			stopbits = serial.STOPBITS_ONE,
			bytesize = serial.EIGHTBITS,
			timeout = 0
		)
	def chatLog(self, data=None):
		if data:
			home=os.environ["HOME"]
			file=home+"/"+"chat.log"
			f=open(file, "a")
			f.write(data+"\n")
			f.close()
			if debug: print data
	def callLog(self, data=None):
		if data:
			home=os.environ["HOME"]
			file=home+"/"+"call.log"
			f=open(file, "a")
			f.write(data+"\n")
			f.close()
	def reset(self):
		self.at([["AT", "OK"], ["ATZ", "OK"], ["AT+VCID=1", "OK"]])
	def read(self):
		#buff = ""
		#data = ""
		#tout = 1
		#tic = time.clock()
		data = self.ser.readline()
		if data:
			data = data.rstrip()
			self.chatLog(data)
			#print data
			return data
	def at(self, commands=[]):
		while len(commands) > 0:
			cmd = commands.pop(0)
			self.ser.write("\r%s\r" % cmd[0])
			#answer = self.read()
			#print cmd[0]
			#ct = 0
			#while not answer:
			#	time.sleep(1)
			#	if len(cmd[1]) > 0:
			#		while not cmd[1] == answer:
			#			print cmd[1], "waiting"
			#			#self.ser.write("\r%s\r" % cmd[0])
			#			answer = self.read()
			#			if ct == 5: print "error"; exit()
			#			ct +=1
			time.sleep(.1)
	def answer(self):
		self.ser.write("\rATA\r")
	def hangup(self):
		self.ser.write("\rATH\r")
	def send(self, bytes=b""):
		self.ser.write(bytes)
		time.sleep(.1)

def anon():
	modem.at([["AT+FCLASS=8", "OK"], ["AT+VLS=1", "OK"], ["AT+VTX", ""]])
	time.sleep(1)
	with open('/home/pi/test.wav', 'rb') as file:
		snd = file.read(1024)
		while not snd == b"":
			#modem.send([snd])
			snd = file.read(1024)
			modem.send(snd)
		modem.send("\x10\x21\x03\rATH\r")
		#modem.send("\x10\x03")
		#modem.at([["\x10\x03", ""], ["ATH", "OK"]])
	time.sleep(1)
	modem.reset()
	
def fax():
	modem.at([["AT+FCLASS=1", "OK"], ["ATA", "OK"]])
	time.sleep(20)
	modem.send("\x10\x21\x03\rATH\r")

	# init modem
modem = modem()
modem.reset()

with open("/home/pi/black.list", "r") as black:
	blacklist = black.readlines()

# main loop
while done == False:
	data  = modem.read()
	time.sleep(.1)
	if data and "NMBR" in data:
		if data[7:]+"\n" in blacklist:
			modem.callLog(time.strftime("%d/%m/%Y, %H:%M:%S")+" - "+data[7:].rstrip()+" - Rejeté")
			fax()
		else:
			modem.callLog(time.strftime("%d/%m/%Y, %H:%M:%S")+" - "+data[7:].rstrip())
