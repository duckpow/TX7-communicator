# handler class for TX7

import pygame.midi as Midi

from midiSuperDevice import MidiDevice

class TX7(MidiDevice):
	"""Handler class for connections to TX7 or DX7"""

	def __init__(self, input_id, output_id):
		self.input_id = input_id
		self.output_id = output_id
		MidiDevice.__init__(self, input_id=self.input_id, output_id=self.output_id)

		#Create operator instances for saving
		self.operators = []
		for i in range(6):
			self.operators.append({'Operator': i})

		#for i in range(6):
		#	self.operators.append(TX7Operator())

		self.SUBSTATE_DUMP_REQUEST = 0b0010
		self.FORMAT_NUMBER = 0
		self.substate_dump_byte = self.SUBSTATE_DUMP_REQUEST << 4 | self.chan 


		#Get current patch on start up
		#This message requests patch data from TX7 (should work on DX7 as well)
		self.get_patch_message = [self.SYSEX_START_ID, self.YAMAHA_ID, self.substate_dump_byte, self.FORMAT_NUMBER, self.SYSEX_EOX_ID]
		self.get_patch()

		#Set patch variable to a default	
		self.pitch_eg_rate = [0,0,0,0]
		self.pitch_eg_lvl = [0,0,0,0]

		self.param_dict = {}

		self.LFO = [0,0,0,0,0,0]

		self.current_patch_name = ""

	def get_patch(self):
		self.write_SysEx(self.get_patch_message)

	#The TX7 and DX7 uses 2 bytes to tell how long the messages is.
	#The last 7 bit of each number is combined to one 14 bit number. 
	def sysEx_MSLS_byte(self,byte1,byte2):
		b1 = byte1 & 0b01111111
		b2 = byte2 & 0b01111111
		return (b1 << 7) | (b2)

	#Should be used to read bits of which operators were on off
	def testBit(self,int_type,offset):
		mask = 1 << offset
		return int_type & mask

	def sysEx_parser(self, msg):
		print("SysEx received")
		self.msg_len = 0
		msg.pop(0) #remove status byte
		if(msg[0] == 67): #Test if a Yamaha device
			msg.pop(0) #remove manufactor byte
			if msg[0] == 0 and msg[1] == 0: #check substate, chan # and format
				msg.pop(0) #remove substate and chan #
				msg.pop(0) #remove format
				self.msg_len = self.sysEx_MSLS_byte(msg[0],msg[1])
				msg.pop(0) #remove MS byte
				msg.pop(0) #remove LS byte
				print("Length of message: " + str(self.msg_len))
				if self.msg_len == 155:
					print("Single patch received")
					print("Name of patch: ")
					self.current_patch_name = ""
					for i in msg[145:self.msg_len]:
						self.current_patch_name += chr(i)
					print(self.current_patch_name)
					#Transfer data to dictionaries
					for op in range(6):
						self.index = op * 21
						self.operators[op]['eg_rate'] = msg[0+self.index:4+self.index]
						self.operators[op]['eg_lvl'] = msg[self.index+4:self.index+8]
						self.operators[op]['key_lvlScale_array'] = msg[self.index+8:self.index+13]
						self.operators[op]['key_rateScale'] = msg[self.index+13]
						self.operators[op]['mod_sens_Amp'] = msg[self.index+14]
						self.operators[op]['key_vel_sens'] = msg[self.index+15]
						self.operators[op]['output_lvl'] = msg[self.index+16]
						self.operators[op]['osc_mode'] = msg[self.index+17]
						self.operators[op]['freq_array'] = msg[self.index+18:self.index+21]
						#Operators stored in reverse order...
						# Print parameters to console
						print("Operator %d: " % (6-op))
						print("Parameters:")
						for key in self.operators[op]:
							if key != 'Operator':
								print("   " + key + ": " + str(self.operators[op][key]))

					self.pitch_eg_rate = msg[126:130]
					self.pitch_eg_lvl = msg[130:134]
					self.LFO = msg[137:143]

					self.param_dict['algorithm'] = msg[134]
					self.param_dict['feedback'] = msg[135]
					self.param_dict['osc_sync'] = msg[136]
					self.param_dict['mod_sens_pitch'] = msg[143]
					self.param_dict['transpose'] = msg[144]

				elif self.msg_len == 4096:
					print("Received all patches \n No current action")

			else:
				print(msg)
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

	def combine_groupParam_bytes(self,param_number,group_number):
		# Parameter number (9bit int) is split over 2 bytes and combined with the group number:
		self.lower_param_bits = param_number & 0b001111111
		self.upper_param_bits = param_number >> 7
		return (group_number << 2) | self.upper_param_bits, self.lower_param_bits

	def write_param(self,param_number,value, group_number = 0):
		'''This function has no checking if the value is whitin accepted range og the parameter'''
		#Substate and channel uses the same byte.
		self.substate = 1
		self.substate_chan_byte = (self.substate << 4) | self.chan
		
		if param_number < 156:
			self.third_byte, self.fourth_byte = self.combine_groupParam_bytes(param_number,group_number)
		else:
			raise Exception("Invalid parameter number")

		self.write_SysEx(
			[self.SYSEX_START_ID,
			self.YAMAHA_ID,
			self.substate_chan_byte,
			self.third_byte,
			self.fourth_byte,
			value,
			self.SYSEX_EOX_ID])

	def change_name(self, new_name):
		'''This method takes a string up to 10 characters'''
		if isinstance(new_name,str):
			self.str_len = len(new_name)
			if self.str_len < 11:
				for i, c in enumerate(new_name):
					self.write_param(145 + i,ord(c))
				#Put in blank spaces
				for i in range(10-self.str_len):
					self.write_param(145 + self.str_len+i,ord(" "))
					#print("working?" + str(self.str_len+i)) #Debugging
			else:
				print("Name to long")
		else:
			print("not a string")


class TX7Operator(object):
	''' Not in use! '''
	#Object for storing operator data for TX7/DX7
	#Only used inside TX7 class

	def __init__(self):
		self.on = False
		self.eg_rate = [0,0,0,0]
		self.eg_lvl = [0,0,0,0]
		self.key_lvlScale_array = [0,0,0,0,0]
		self.key_rateScale = 0
		self.mod_sens_Amp = 0
		self.key_vel_sens = 0
		self.output_lvl = 0
		self.osc_mode = 0
		self.freq_array = [0,0,0]

		self.allParam = []
		self.on= False

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
				self.freq_array = data[18:21]

	def getParam(self):
		self.allParam = []
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

