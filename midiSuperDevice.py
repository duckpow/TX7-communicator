#Midi device object super class

import pygame.midi as Midi

class MidiDevice(object):
	"""Super class for both ways connections to Midi devices"""
	SYSEX_START_ID = 0b11110000
	SYSEX_EOX_ID = 0b11110111
	KEY_ON_ID = 0b1001
	KEY_OFF_ID = 0b1000

	YAMAHA_ID = 67

	key_on_status_with_chan = 0
	key_off_status_with_chan = 0

	temp_data = []
	receiving_sysEx = False
	sysExMsg = []

	def __init__(self, input_id, *args):
		"""Expects it's first argument to be an input_id, the second (optional) an output_id, and the third (optional) the channel number"""
		self.input_id = input_id
		#If given an output id, assign it a variable
		if len(args)>0:
			self.output_id = args[0]

		#If given a midi channel, use it. Else use 0 as default.
		if len(args)>1:
			chan = args[1]
		else:
			chan = 0

		#Create status messages. Should maybe not be constant for devices, but is sufficient for my needs now.
		self.key_on_status_with_chan = (self.KEY_ON_ID << 4) | chan
		self.key_off_status_with_chan = (self.KEY_OFF_ID << 4) | chan

		# Create streams
		self.inStream = Midi.Input(self.input_id)

		print(locals())

		if self.output_id != None:
			self.outStream = Midi.Output(self.output_id)

	# Function to check if msg is start of SysEx data
	def sysExCheck(self, msg):
		#get the first part of the list, no matter how nested
		while isinstance(msg,list):
			msg = msg[0]
		if msg == self.SYSEX_START_ID:
			return True
		else:
			return False

	# Function to check if msg is end of SysEx data
	def sysExEOX(self, msg):
		#get the first part of the list, no matter how nested
		while isinstance(msg,list):
			msg = msg[0]
		if msg == self.SYSEX_EOX_ID:
			return True
		else:
			return False

	# Function to handle SysEx data
	def appendSysEx(self, msg):
		for entry in msg[0][0]:
			self.sysExMsg.append(entry)
			if self.sysExEOX(entry):
				return False
		return True

	#Check if there is data
	def poll(self):
		return self.inStream.poll()

	def write(self, data):
		self.outStream.write(data)

	#Due to pygame.midi 's strange way of hanling midi we format our sysEx message list in blocks of 4 plus 0 time codes
	def write_SysEx(self, data):
		if self.sysExCheck(data[0]): #Check if a valid sysEx message
			outgoing_msg = []
			while len(data) > 4:
				outgoing_msg.append([data[0:4],0])
				for i in range(4):
					data.pop(0)
			outgoing_msg.append([data,0])
			self.write(outgoing_msg)
		else:
			print("Not a valid SysEx message")

	#Read with a handling of SysEx messages
	def read(self):
		self.temp_data = self.inStream.read(1)

		if self.receiving_sysEx:
			self.receiving_sysEx = self.appendSysEx(self.temp_data)
			# if end of exchange
			if not self.receiving_sysEx:
				# return the message
				return self.sysExMsg
			else:
				return 0 # report that we are still receiving
		else:
			if self.sysExCheck(self.temp_data):
				print("receiving SysEx")
				self.sysExMsg[:] = []
				self.receiving_sysEx = self.appendSysEx(self.temp_data)
				return 0 # report that we are receiving
			else:
				return self.temp_data

	def write_noteOn(self,noteNumber,velocity):
		self.write(self,[[[key_on_status_with_chan,noteNumber,velocity],0]])

	def write_noteOff(self,noteNumber,velocity):
		# for testing purposes, exitvelocities disabled
		self.write(self,[[[key_off_status_with_chan,noteNumber,0],0]])
