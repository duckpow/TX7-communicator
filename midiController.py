#midi comtroller

import pygame.midi as Midi

from midiSuperDevice import MidiDevice

class MidiController(MidiDevice):
	"""MidiDevice class """

	def __init__(self, input_id):
		self.input_id = input_id
		MidiDevice.__init__(self,input_id=self.input_id)

	def read_noteMsg(self):
		'''Reads NoteOn and NoteOff messages
		Returns chan note number and velocity as a list
		Note on NoteOff messages: They usually are implemented as NoteOn messages with velocity 0. This is assumed the case. This method won't work for keyboards with exit velocity'''
		midiMsg = MidiDevice.read(self)
		if self.note_check(midiMsg):
			self.chan = midiMsg[0][0][0] & 0b00001111
			self.noteNumber = midiMsg[0][0][1]
			self.velocity = midiMsg[0][0][2]
			return [self.chan, self.noteNumber, self.velocity]
