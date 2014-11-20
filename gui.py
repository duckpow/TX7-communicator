import sys
import pygame.midi as Midi
from PyQt4 import QtCore, QtGui, Qt
from PyQt4.QtCore import SIGNAL

from yamahaX7 import TX7
from midiController import MidiController

'''
GUI for TX7/DX7 Editor
Banders Duckpow 2014


'''

class SliderWithNameAndLabel(QtGui.QWidget):
	"""Creates a slider with name and value label and connects it to the tx7 class"""
	def __init__(self, name, param_number, minMax=[0,99],**kwargs):
		super(SliderWithNameAndLabel, self).__init__()

		if kwargs is not None:
			if 'horizontal' in kwargs.keys():
				if isinstance(kwargs['horizontal'],bool):
					self.horizontal = kwargs['horizontal']
			elif 'vertical' in kwargs.keys():
				if isinstance(kwargs['vertical'],bool):
					self.horizontal = not kwargs['vertical']
			else:
				self.horizontal = True

		self.vertical = not self.horizontal

		self.name = name
		self.param_number = param_number

		self.grid = QtGui.QGridLayout()
		self.setLayout(self.grid)

		self.label = QtGui.QLabel(name)
		self.grid.addWidget(self.label,0 * self.vertical,0 * self.horizontal)

		if self.horizontal:
			self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
		else:
			self.slider = QtGui.QSlider()

		self.slider.setRange(minMax[0],minMax[1])
		self.grid.addWidget(self.slider,1 * self.vertical,1 * self.horizontal)
		self.slider.sliderReleased.connect(self.sendParam)

		self.valueLabel = QtGui.QLabel()
		self.grid.addWidget(self.valueLabel,2 * self.vertical,2 * self.horizontal)
		self.slider.valueChanged.connect(self.valueLabel.setNum)

	def sendParam(self):
		app.tx7.write_param(self.param_number,self.slider.value())

	def updateParam(self, value):
		self.slider.setValue(value)


class ToggleWithName(QtGui.QWidget):
	"""Creates a toggle button with a name label and connects it to the synth class"""
	def __init__(self, name, param_number):
		super(ToggleWithName, self).__init__()
		self.name = name
		self.param_number = param_number

		self.grid = QtGui.QGridLayout()
		self.setLayout(self.grid)

		self.label = QtGui.QLabel(name)
		self.grid.addWidget(self.label,0,0)

		self.toggle = QtGui.QRadioButton()
		self.grid.addWidget(self.toggle,1,0)
		self.toggle.released.connect(self.sendParam)

	def sendParam(self):
		self.tog = self.sender()
		app.tx7.write_param(self.param_number,int(self.tog.isChecked()))

	def updateParam(self, checked):
		self.toggle.setChecked(bool(checked))

class IdentifiableQSlider(QtGui.QSlider):
	"""Addition of index to QSlider that makes it identifiable for a signal"""
	def __init__(self, index):
		super(IdentifiableQSlider, self).__init__()
		self.index = index

	def getIndex(self):
		return self.index

class IdentifiableQDial(QtGui.QDial):
	"""Addition of index to QDial that makes it identifiable for a signal"""
	def __init__(self, index):
		super(IdentifiableQDial, self).__init__()
		self.index = index

	def getIndex(self):
		return self.index

class Envelope(QtGui.QWidget):
	"""Envelope Widget. Contains several sliders and their labels"""
	def __init__(self, param_start_index):
		super(Envelope, self).__init__()

		self.firstParam = param_start_index

		self.grid = QtGui.QGridLayout()
		self.setLayout(self.grid)

		self.points = 4

		self.rates = []
		self.rateLabels = []
		self.levels = []
		self.levelLabels = []

		for i in range(self.points):
			self.rates.append(IdentifiableQSlider(i))
			self.rateLabels.append(QtGui.QLabel())

			self.levels.append(IdentifiableQSlider(i+self.points))
			self.levelLabels.append(QtGui.QLabel())

		self.rateLabel = QtGui.QLabel("Rates")
		self.grid.addWidget(self.rateLabel,1,0,1,2)

		for i in range(self.points):
			self.rates[i].setRange(0,99)
			self.grid.addWidget(self.rates[i],2,i)
			self.grid.addWidget(self.rateLabels[i],3,i)
			self.rates[i].valueChanged.connect(self.rateLabels[i].setNum)
			self.rates[i].sliderReleased.connect(self.sendParam)

		self.levelLabel = QtGui.QLabel("Levels")
		self.grid.addWidget(self.levelLabel,4,0,1,2)

		for i in range(self.points):
			self.levels[i].setRange(0,99)
			self.grid.addWidget(self.levels[i],5,i)
			self.grid.addWidget(self.levelLabels[i],6,i)
			self.levels[i].valueChanged.connect(self.levelLabels[i].setNum)
			self.levels[i].sliderReleased.connect(self.sendParam)

	def updateParam(self, rateArray, lvlArray):
		for i in range(self.points):
			self.rates[i].setValue(rateArray[i])
			self.levels[i].setValue(lvlArray[i])

	def sendParam(self):
		#self.sld = None
		self.sld = self.sender()
		app.tx7.write_param(self.firstParam + self.sld.getIndex(), self.sld.value())
		print(self.sld.getIndex(),self.sld.value())
		#app.tx7.write_param(param_number,i)

class TX7Operator(QtGui.QWidget):
	"""One TX7Operator as a QWidget"""
	def __init__(self, index):
		super(TX7Operator, self).__init__()
		self.index = index

		self.grid = QtGui.QGridLayout()
		self.setLayout(self.grid)

		#Create envelope
		self.env = Envelope(21*self.index)
		self.grid.addWidget(self.env,0,0,0,1)

		#Level scaling
		self.parameters = {}

		self.parameters['BreakPoint'] = SliderWithNameAndLabel("Break Point",(self.index + 8),vertical=True)
		self.grid.addWidget(self.parameters['BreakPoint'],0,2)

		self.parameters['LeftDepth'] = SliderWithNameAndLabel("Left Depth",(self.index + 9),vertical=True)
		self.grid.addWidget(self.parameters['LeftDepth'],0,3)

		self.parameters['RightDepth'] = SliderWithNameAndLabel("Right Depth",(self.index + 10),vertical=True)
		self.grid.addWidget(self.parameters['RightDepth'],0,4)

		self.parameters['LeftCurve'] = SliderWithNameAndLabel("Left Curve",(self.index + 11),minMax=[0,3],vertical=True)
		self.grid.addWidget(self.parameters['LeftCurve'],0,5)

		self.parameters['RightCurve'] = SliderWithNameAndLabel("Right Curve",(self.index + 12),minMax=[0,3],vertical=True)
		self.grid.addWidget(self.parameters['RightCurve'],0,6)

		#Other
		self.parameters['key_rateScale'] = SliderWithNameAndLabel("Key Rate scale",(self.index + 13),minMax=[0,7],vertical=True)
		self.grid.addWidget(self.parameters['key_rateScale'],1,2)

		self.parameters['mod_sens_Amp'] = SliderWithNameAndLabel("Amp Mod Sens",(self.index + 14),minMax=[0,3],vertical=True)
		self.grid.addWidget(self.parameters['mod_sens_Amp'],1,3)

		self.parameters['key_vel_sens'] = SliderWithNameAndLabel("Velocity Sens",(self.index + 15),minMax=[0,7],vertical=True)
		self.grid.addWidget(self.parameters['key_vel_sens'],1,4)

		#Pitch
		self.parameters['freq_coarse'] = SliderWithNameAndLabel("Frequency Coarse",(self.index + 18),minMax=[0,31],vertical=True)
		self.grid.addWidget(self.parameters['freq_coarse'],1,5)

		self.parameters['freq_fine'] = SliderWithNameAndLabel("Fine",(self.index + 19),vertical=True)
		self.grid.addWidget(self.parameters['freq_fine'],1,6)

		self.parameters['detune'] = SliderWithNameAndLabel("Detune",(self.index + 20),minMax=[0,14],vertical=True)
		self.grid.addWidget(self.parameters['detune'],1,7)



	def updateAllParam(self):
		self.env.updateParam(app.tx7.operators[self.index]['eg_rate'],app.tx7.operators[self.index]['eg_lvl'])
		for key, obj in self.parameters.iteritems():
			obj.updateParam(app.tx7.operators[self.index][key])


	def sendParam(self):
		pass

class LFO(QtGui.QWidget):
	"""LFO Widget. Only used once... but this makes things easier to comprehend"""
	def __init__(self,):
		super(LFO, self).__init__()
		
		self.grid = QtGui.QGridLayout()
		self.setLayout(self.grid)

		self.names = ["Speed", "Delay", "Pitch Mod", "Amp Mod"]
		self.nameLabels = []
		self.dials = []
		self.valueLabels = []

		self.headerLabel = QtGui.QLabel("LFO parameters")
		self.grid.addWidget(self.headerLabel,0,0,1,2)

		for index in range(len(self.names)):
			self.current_row = (index/2)*3 + 1
			self.current_column = index%2
			self.nameLabels.append(QtGui.QLabel(self.names[index]))
			self.grid.addWidget(self.nameLabels[index],self.current_row, self.current_column)

			self.dials.append(IdentifiableQDial(index))
			self.dials[index].setRange(0,99)
			self.grid.addWidget(self.dials[index],self.current_row+1, self.current_column)
			self.dials[index].sliderReleased.connect(self.sendParam)

			self.valueLabels.append(QtGui.QLabel())
			self.grid.addWidget(self.valueLabels[index],self.current_row+2, self.current_column)
			self.dials[index].valueChanged.connect(self.valueLabels[index].setNum)

		self.lfoSync = ToggleWithName("LFO Sync", 141)
		self.grid.addWidget(self.lfoSync,1,2)

		self.waveForm = QtGui.QComboBox()
		self.grid.addWidget(self.waveForm,2,2,1,2)
		self.waveForm.addItems(["Triangle","Saw","Rev Saw","Square","Sine"])
		self.waveForm.activated[int].connect(self.sendParamWithArg)

	def sendParamWithArg(self, i):
		app.tx7.write_param(142,i)

	def sendParam(self):
		self.dial = self.sender()
		app.tx7.write_param(self.dial.getIndex()+137,self.dial.value())

	def updateParam(self, lfoParamArray):
		for i in range(4):
			self.dials[i].setValue(lfoParamArray[i])
		self.lfoSync.updateParam(lfoParamArray[4])
		self.waveForm.setCurrentIndex(lfoParamArray[5])
		

class MainWindow(QtGui.QWidget):
	"""MainWindow for displaying and changing parameters"""
	def __init__(self):
		super(MainWindow, self).__init__()
		self.initUI()

	def initUI(self):
		self.grid = QtGui.QGridLayout()
		self.setLayout(self.grid)

		#Name of patch
		self.patch_text = QtGui.QLabel('Patch Name:')
		self.grid.addWidget(self.patch_text,0,0)
		self.name_box = QtGui.QLineEdit(self)
		self.name_box.setMaxLength(10)
		self.name_box.editingFinished.connect(self.patchNameChanged)
		self.grid.addWidget(self.name_box,0,1)

		self.params = {}

		#Algorithm
		self.params['algorithm'] = SliderWithNameAndLabel("Algorithm",134,minMax=[0,31],horizontal=True)
		self.grid.addWidget(self.params['algorithm'],1,0,1,3)

		#Misc
		self.params['feedback'] = SliderWithNameAndLabel("Feedback",135,minMax=[0,7],vertical=True)
		self.grid.addWidget(self.params['feedback'],0,3,3,1)

		self.params['osc_sync'] = ToggleWithName("Osc Sync",136)
		self.grid.addWidget(self.params['osc_sync'],0,4)

		self.params['mod_sens_pitch'] = SliderWithNameAndLabel("Mod Sens. Pitch",143,minMax=[0,7],vertical=True)
		self.grid.addWidget(self.params['mod_sens_pitch'],1,4,2,1)

		self.params['transpose'] = SliderWithNameAndLabel("Transpose",144, minMax=[0,48],vertical=True)
		self.grid.addWidget(self.params['transpose'],0,5,3,1)

		#Pitch Envelope
		self.pitchEnv = Envelope(126)
		self.grid.addWidget(self.pitchEnv,2,0,2,1)

		#LFO
		self.lfo = LFO()
		self.grid.addWidget(self.lfo,2,1,2,1)

		self.setGeometry(500,500,550,550)
		self.setWindowTitle('TX7 editor')
		self.show()

		#Operators
		self.op = TX7Operator(0)
		self.grid.addWidget(self.op,4,0,2,5)
		
	def drawCircle(self, on=0):
		'''Not currently used '''
		self.brush = QtGui.QBrush(QtGui.QColor(0,on,0))
		self.circle = self.scene.addEllipse(10,20,10,10, brush=self.brush)

	def midiReceived(self):
		#Set color on
		self.drawCircle(255)
		#Set color off afer a delay... doesn't work as intended!
		#self.oneShotTimer = QtCore.QTimer.singleShot(50,self.drawCircle)

	def noMidiReceived(self):
		self.drawCircle(0)

	def updateFromData(self):
		'''
			Update function for the displayed data
			Goes trough the TX7 object and and updates the data (once finished)
		'''
		self.name_box.setText(app.tx7.current_patch_name)
		for key in self.params:
			self.params[key].updateParam(app.tx7.param_dict[key])
		#self.algorithm.updateParam(app.tx7.algorithm)
		#self.feedback.updateParam(app.tx7.feedback)
		#self.oscSync.updateParam(app.tx7.osc_sync)
		#self.algorithm_slider.setValue(app.tx7.algorithm)
		#self.algorithm_value.setNum(self.algorithm_slider.value())
		self.op.updateAllParam()
		self.pitchEnv.updateParam(app.tx7.pitch_eg_rate,app.tx7.pitch_eg_lvl)
		self.lfo.updateParam(app.tx7.LFO)

	def patchNameChanged(self):
		app.tx7.change_name(str(self.name_box.text()))

	def algorithmChanged(self):
		''' No longer used'''
		self.algorithm_value.setNum(self.algorithm_slider.value())
		app.tx7.write_param(app.tx7.algorithm_parameter, self.algorithm_slider.value())


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
		self.midiIn = None
		self.midiOut = None
		self.midiCntrl = None
		self.ledTimer = 0
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
		print("launching...") #debugging
		self.tx7 = TX7(int(self.midiIn),int(self.midiOut))
		self.keyboard = MidiController(int(self.midiCntrl))
		self.mainWindow = MainWindow()
		self.startEventTimer()
		self.pop_up.close()
		
	def startEventTimer(self):
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.midiUpdate)
		self.timer.start(2) #Delay should be low enough that no lag is felt.

	def midiUpdate(self):
		#The midi update event
		#TX7 takes priority
		if self.tx7.poll():
			self.ledTimer = 30
			#Data should always be read if poll returns true
			self.data = self.tx7.read()
			self.mainWindow.updateFromData()
			# print("Recieved from TX7") #debugging
		elif self.keyboard.poll():
			#self.mainWindow.midiReceived()
			self.data = self.keyboard.read()
			self.tx7.write(self.data)
			#print("Recieved from keyboard" + str(self.data)) #debugging

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