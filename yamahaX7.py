# handler class for TX7

import pygame.midi as Midi

class TX7(object):
	"""Handler class for connections to TX7 or DX7"""



	def __init__(self, input_id, output_id):
		self.input_id = input_id
		self.output_id = output_id

		inStream = Midi.Input(self.input_id)
		outStream = Midi.Input(self.output_id)

	
