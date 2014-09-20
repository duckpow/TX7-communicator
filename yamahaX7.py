# handler class for TX7

import pygame.midi as Midi

from midiSuperDevice import MidiDevice

class TX7(MidiDevice):
	"""Handler class for connections to TX7 or DX7"""

	get_patch_message = []

	current_patch_name = ""

	def __init__(self, input_id, output_id):
		self.input_id = input_id
		self.output_id = output_id
		MidiDevice.__init__(self,input_id,output_id)
		#Get current patch on start up
		#This message requests patch data from TX7 (should work on DX7 as well)
		self.get_patch_message = [self.SYSEX_START_ID, self.YAMAHA_ID, 32, 0, self.SYSEX_EOX_ID]
		self.get_patch()

	def get_patch(self):
		self.write_SysEx(self.get_patch_message)

	#The TX7 and DX7 uses 2 bytes to tell how long the messages is.
	#The last 7 bit of each number is combined to one 14 bit number. 
	def sysEx_MSLS_byte(self,byte1,byte2):
		b1 = byte1 & 0b01111111
		b2 = byte2 & 0b01111111
		return (b1 << 7) | (b2)

	def sysEx_parser(self, msg):
		print("SysEx received")
		msg_len = 0
		msg.pop(0) #remove status byte
		if(msg[0] == 67): #Test if a Yamaha device
			msg.pop(0) #remove manufactor byte
			if msg[0] == 0  and msg[1] == 0: #check substate, chan # and format
				msg.pop(0)
				msg.pop(0)
				msg_len = self.sysEx_MSLS_byte(msg[0],msg[1])
				msg.pop(0)
				msg.pop(0)
				print("Length of message: " + str(msg_len))
				if msg_len == 155:
					print("Single patch received")
					print("Name of patch: ")
					current_patch_name = ""
					for i in msg[145:msg_len]:
						self.current_patch_name += chr(i)
					print(self.current_patch_name)
				elif msg_len == 4096:
					print("Received all patches \n No current action")

				print(msg)
			else:
				print("Not recognized")
		else:
			print("Not a Yamaha device and then not a TX7/DX7")



	def read(self):
		midiMsg = MidiDevice.read(self)
		#Check if a midi message or pending
		if isinstance(midiMsg,list):
			#Check type of message
			if self.sysExCheck(midiMsg):
				self.sysEx_parser(midiMsg)
			else:
				print(midiMsg)
		else:
			return 0
