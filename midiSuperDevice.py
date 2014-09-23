#Midi device object super class

import pygame.midi as Midi

class MidiDevice(object):
	"""Super class for both ways connections to Midi devices"""
	SYSEX_START_ID = 0b11110000
	SYSEX_EOX_ID = 0b11110111
	KEY_ON_ID = 0b1001
	KEY_OFF_ID = 0b1000

	YAMAHA_ID = 67

	def __init__(self, **kwargs):
		"""Keywords are 'input_id', 'output_id' and 'chan'"""
		if kwargs is not None:
			if 'input_id' in kwargs.keys():
				self.input_id = kwargs['input_id']
				# Create streams
				self.inStream = Midi.Input(self.input_id)
			#If given an output id, assign it a variable
			if 'output_id' in kwargs.keys():
				self.output_id = kwargs['output_id']
				# Create streams
				self.outStream = Midi.Output(self.output_id)
			if 'chan' in kwargs.keys():
				self.chan = kwargs['chan']
			else:
				#Use chan 0 on default
				self.chan = 0
		else:
			raise Exception("At least on id must be given")

		#Init variables
		self.receiving_sysEx = False
		self.sysExMsg = []
		#Create status messages. Should maybe not be constant for devices, but is sufficient for my needs now.
		self.key_on_status_with_chan = (self.KEY_ON_ID << 4) | self.chan
		self.key_off_status_with_chan = (self.KEY_OFF_ID << 4) | self.chan

	def firstOfNest(self, msg):
		#while isinstance(msg,list):
		#get the first part of the list, no matter how nested
		while isinstance(msg,list):
			msg = msg[0]
		return msg

	def note_check(self,msg):
		msg = self.firstOfNest(msg)
		#Note on and note off messages share the first 3 bits: 100.
		if not msg & 0b01100000:
			return True
		else:
			return False

	# Function to check if msg is start of SysEx data
	def sysExCheck(self, msg):
		if self.firstOfNest(msg) == self.SYSEX_START_ID:
			return True
		else:
			return False

	# Function to check if msg is end of SysEx data
	def sysExEOX(self, msg):
		if self.firstOfNest(msg) == self.SYSEX_EOX_ID:
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
		'''SysEx messages should be given as a list. Including the sysEx status and EOX'''
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
		self.write([[[self.key_on_status_with_chan,noteNumber,velocity],0]])

	def write_noteOff(self,noteNumber,velocity):
		# for testing purposes, exitvelocities disabled
		self.write([[[self.key_off_status_with_chan,noteNumber,0],0]])
