#Midi device object super class

import pygame.midi as Midi

class MidiDevice(object):
	"""Super class for both ways connections to Midi devices"""
	temp_data = []
	receiving_sysEx = False
	sysExMsg = []

	def __init__(self, input_id, output_id):
		self.input_id = input_id
		self.output_id = output_id

		# Create streams
		self.inStream = Midi.Input(self.input_id)
		self.outStream = Midi.Output(self.output_id)

	# Function to check if msg is start of SysEx data
	def sysExCheck(self, msg):
		#get the first part of the list, no matter how nested
		while isinstance(msg,list):
			msg = msg[0]
		if msg == int('11110000',2):
			return True
		else:
			return False

	# Function to check if msg is end of SysEx data
	def sysExEOX(self, msg):
		#get the first part of the list, no matter how nested
		while isinstance(msg,list):
			msg = msg[0]
		if msg == int('11110111',2):
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
		if data[0] == int('11110000',2): #Check if a valid sysEx message
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