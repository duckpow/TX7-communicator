# handler class for TX7

import pygame.midi as Midi

from midiSuperDevice import MidiDevice

class TX7(MidiDevice):
	"""Handler class for connections to TX7 or DX7"""

	operators = []
	get_patch_message = []

	current_patch_name = ""

	def __init__(self, input_id, output_id):
		self.input_id = input_id
		self.output_id = output_id
		MidiDevice.__init__(self,input_id,output_id)

		for i in range(6):
			self.operators.append(TX7Operator())

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

class TX7Operator(object):

	on = False
	eg_rate = [0,0,0,0]
	eg_lvl = [0,0,0,0]
	key_lvlScale_array = [0,0,0,0,0]
	key_rateScale = 0
	mod_sens_Amp = 0
	key_vel_sens = 0
	output_lvl = 0
	osc_mode = 0
	freq_array = [0,0,0]

	allParam = []

	def __init__(self):
		self.on=1

	def set_on(self,msg):
		if isinstance(msg,bool):
			self.on = msg

	def setParam(self,data):
		if isinstance(data,list):
			if len(data) == 21:
				self.eg_rate = data[0:4]
				self.eg_lvl = data[4:8]
				self.key_lvlScale_array = data[8:13]
				self.key_rateScale = data[13]
				self.mod_sens_Amp = data[14]
				self.key_vel_sens = data[15]
				self.output_lvl = data[16]
				self.osc_mode = data[17]
				self.freq_array = data[18,21]

	def getParam(self):
		allParam = []
		for i in self.eg_rate:
			self.allParam.append(i)
		for i in self.eg_lvl:
			self.allParam.append(i)
		for i in self.key_lvlScale_array:
			self.allParam.append(i)
		self.allParam.append(self.key_rateScale)
		self.allParam.append(self.mod_sens_Amp)
		self.allParam.append(self.key_vel_sens)
		self.allParam.append(self.output_lvl)
		self.allParam.append(self.osc_mode)
		for i in self.freq_array:
			self.allParam.append(i)
		return self.allParam

