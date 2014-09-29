'''
GUI for TX7 Editor
Banders Duckpow 2014


'''

import sys
import pygame.midi as Midi
from PyQt4 import QtCore, QtGui, Qt
from PyQt4.QtCore import SIGNAL

from yamahaX7 import TX7
from midiController import MidiController

class MainWindow(QtGui.QMainWindow):
	"""MainWindow for displaying and changing parameters"""
	def __init__(self):
		super(MainWindow, self).__init__()
		self.initUI()

	def initUI(self):
		self.welcomeText = QtGui.QLabel('working', self)
		#self.addWidget(self.welcomeText)

		self.setGeometry(500,500,550,550)
		self.setWindowTitle('Main Window')
		self.show()
		

class Pop_Up(QtGui.QWidget):
	"""Initial UI for setting midi connections"""
	def __init__(self):
		super(Pop_Up, self).__init__()
		self.initUI()

	def initUI(self):
		#Grid layout is easy
		self.grid = QtGui.QGridLayout()
		self.setLayout(self.grid)

		#Midi in block
		self.midiIn_text = QtGui.QLabel('Choose midi input device: ',self)
		self.grid.addWidget(self.midiIn_text,0,0)
		self.midiInDevices = QtGui.QComboBox(self)
		self.grid.addWidget(self.midiInDevices,0,1)
		self.midiInDevices.activated[str].connect(self.setMidiIn)

		#Midi out block
		self.midiOut_text = QtGui.QLabel('Choose midi output device: ',self)
		self.grid.addWidget(self.midiOut_text,1,0)
		self.midiOutDevices = QtGui.QComboBox(self)
		self.grid.addWidget(self.midiOutDevices,1,1)
		self.midiOutDevices.activated[str].connect(self.setMidiOut)

		#Midi controller block
		self.midiCntrl_text = QtGui.QLabel('Choose midi controller device: ',self)
		self.grid.addWidget(self.midiCntrl_text,2,0)
		self.midiCntrlDevices = QtGui.QComboBox(self)
		self.grid.addWidget(self.midiCntrlDevices,2,1)
		self.midiCntrlDevices.activated[str].connect(self.setMidiCntrl)

		#Ok button
		self.okButton = QtGui.QPushButton("OK",self)
		self.grid.addWidget(self.okButton,3,1)
		self.okButton.clicked.connect(self.buttonClicked)

		#TODO: Implement quit button

		self.setGeometry(300,300,250,150)
		self.setWindowTitle('Midi devices')
		self.show()

	def addMidiInDevice(self, device):
		self.midiInDevices.insertItem(999,device)
		self.midiCntrlDevices.insertItem(999,device)

	def addMidiOutDevice(self, device):
		self.midiOutDevices.insertItem(999,device)

	def setMidiIn(self, i):
		app.midiIn = int(i[0])

	def setMidiOut(self, i):
		app.midiOut = int(i[0])

	def setMidiCntrl(self, i):
		app.midiCntrl = int(i[0])

	def buttonClicked(self):
		if app.midiIn != app.midiCntrl:
			app.launchMainWindow()

class App(Qt.QApplication):
	"""
	Main class for the App
	Handles spawning of windows and event loops (implemented using QTimer)
	"""
	def __init__(self, *args):
		Qt.QApplication.__init__(self, *args)
		#super(App, self).__init__(*args)
		self.midiIn = None
		self.midiOut = None
		self.midiCntrl = None
		self.initApp()

	def initApp(self):
		Midi.init()
		self.device_count = Midi.get_count()
		#Check if there are any midi devices
		if self.device_count > 0:
			#Spawn window
			self.pop_up = Pop_Up()
			self.connect(self, SIGNAL("lastWindowClosed()"), self.byebye)
			for device in range(self.device_count):
				self.temp = Midi.get_device_info(device)
				if self.temp[2] and not self.temp[3]:
					self.pop_up.addMidiInDevice(str(device) + " " + self.temp[1])
				elif self.temp[3] and not self.temp[2]:
					self.pop_up.addMidiOutDevice(str(device) + " " + self.temp[1])
		else:
			self.byebye()

	def launchMainWindow(self):
		print("launching...")
		print(self.midiIn)
		print(self.midiOut)
		print(self.midiCntrl)
		self.tx7 = TX7(int(self.midiIn),int(self.midiOut))
		self.keyboard = MidiController(int(self.midiCntrl))
		self.startEventTimer()
		self.mainWindow = MainWindow()
		self.pop_up.close()
		
	def startEventTimer(self):
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.midiUpdate)
		self.timer.start(2) #Delay should be low enough that no lag is felt.

	def midiUpdate(self):
		if self.tx7.poll():
			#Data should always be read if poll returns true
			self.data = self.tx7.read()
			print("Recieved from TX7")
		elif self.keyboard.poll():
			self.data = self.keyboard.read()
			print("Recieved from keyboard" + str(self.data))


	def byebye(self):
		self.exit(0)
		

def main(args):
	'''
	called when the program starts.
	Sets app to global and creates the app
	Handles exit
	'''
	global app
	app = App(args)
	sys.exit(app.exec_())


if __name__ == '__main__':
	main(sys.argv)