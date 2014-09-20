# handler class for TX7

import pygame.midi as Midi

from midiSuperDevice import MidiDevice

class TX7(MidiDevice):
	"""Handler class for connections to TX7 or DX7"""

	def __init__(self, input_id, output_id):
		self.input_id = input_id
		self.output_id = output_id
		MidiDevice.__init__(self,input_id,output_id)
		
	# # Function to check if msg is start of SysEx data
	# def sysExCheck(self, msg):
	# 	#get the first part of the list, no matter how nested
	# 	while isinstance(msg,list):
	# 		msg = msg[0]
	# 	if msg == int('11110000',2):
	# 		print("receiving SysEx")
	# 		return True
	# 	else:
	# 		return False

	# # Function to check if msg is end of SysEx data
	# def sysExEOX(self, msg):
	# 	#get the first part of the list, no matter how nested
	# 	while isinstance(msg,list):
	# 		msg = msg[0]
	# 	if msg == int('11110111',2):
	# 		return True
	# 	else:
	# 		return False

	# # Function to handle SysEx data
	# def appendSysEx(self, msg):
	# 	for entry in msg[0][0]:
	# 		self.sysExMsg.append(entry)
	# 		if self.sysExEOX(entry):
	# 			print(self.sysExMsg) #Print message
	# 			#self.parseSysEx(sysExMsg)
	# 			self.sysExMsg[:] = [] #Del message here! Bloody scope!!!
	# 			return False
	# 	return True

	# def poll(self):
	# 	return self.inStream.poll()

	# def read(self):
	# 	self.temp_data = self.inStream.read(1)
	# 	if self.receiving_sysEx:
	# 		self.receiving_sysEx = self.appendSysEx(self.temp_data)
	# 	else:
	# 		if self.sysExCheck(self.temp_data):
	# 			self.receiving_sysEx = self.appendSysEx(self.temp_data)
	# 			if not self.receiving_sysEx:
	# 				return self.sysExMsg
	# 			else:
	# 				return 0
	# 		else:
	# 			return self.temp_data


