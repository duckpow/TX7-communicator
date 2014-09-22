#midi comtroller

import pygame.midi as Midi

from midiSuperDevice import MidiDevice

class MidiController(MidiDevice):
	"""MidiDevice class """

	def __init__(self, input_id):
		self.input_id = input_id
		MidiDevice.__init__(self,input_id=self.input_id)

	def read_noteMsg(self):
		midiMsg = MidiDevice.read(self)
		if self.note_check(midiMsg):
			print(midiMsg)
			return midiMsg
		#if isinstance(midiMsg,list):
