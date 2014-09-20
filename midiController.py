#midi comtroller

import pygame.midi as Midi

from midiSuperDevice import MidiDevice

class MidiController(MidiDevice):
	"""MidiDevice class """

	def __init__(self, input_id):
		self.input_id = input_id