# handler class for TX7

import pygame.midi as Midi

from midiSuperDevice import MidiDevice

class TX7(MidiDevice):
	"""Handler class for connections to TX7 or DX7"""

	#This message request patch data from TX7 (should work on DX7 as well)
	get_patch_message = [240, 67, 32, 0,247]

	def __init__(self, input_id, output_id):
		self.input_id = input_id
		self.output_id = output_id
		MidiDevice.__init__(self,input_id,output_id)
		#Get current patch on start up
		self.get_patch()

	def get_patch(self):
		self.write_SysEx(self.get_patch_message)

	def read(self):
		midiMsg = MidiDevice.read(self)
		#Check if a midi message or pending
		print(midiMsg)
		if isinstance(midiMsg,list):
			#Check type of message
			if self.sysExCheck(midiMsg):
				print("SysEx received")
			else:
				print(midiMsg)
		else:
			return 0
