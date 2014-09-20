# Midi experiments in python
# aka What the hell am I doing

#Something with my TX7

# Need a midi lib
import pygame.midi as Midi

#global variables

done = False
receivingSysEx = False
sysExMsg = []

# Function to check if msg is start of SysEx data
def sysExCheck(msg):
	#get the first part of the list, no matter how nested
	while isinstance(msg,list):
		msg = msg[0]
	if msg == int('11110000',2):
		print("receiving SysEx")
		return True
	else:
		return False

# Function to check if msg is end of SysEx data
def sysExEOX(msg):
	#get the first part of the list, no matter how nested
	while isinstance(msg,list):
		msg = msg[0]
	if msg == int('11110111',2):
		return True
	else:
		return False

# Function to handle SysEx data
def appendSysEx(msg):
	for entry in msg[0][0]:
		sysExMsg.append(entry)
		if sysExEOX(entry):
			print(sysExMsg) #Print messag
			parseSysEx(sysExMsg)
			sysExMsg[:] = [] #Del message here! Bloody scope!!!
			return False
	return True

#translate message to something useful
def parseSysEx(msg):
	manufactorer_ID = msg[1]
	patchData = msg[6:(len(msg)-2)]
	osc6 = patchData[0:21]
	print(osc6)

	#Do something with the data here!

	#patchFile = open('patchFile.txt','w')
	#patchFile.write(str(manufactorer_ID) + "\n")
	#for entry in patchData:
	#	patchFile.write(str(entry) + "\n")
	#patchFile.close()


#Main program
def main():
	# Init midi lib
	Midi.init()

	done = False
	receivingSysEx = False
	sysExMsg = []

	#get info on devices
	print("Midi-devices found:")
	for device in range(Midi.get_count()):
		temp = Midi.get_device_info(device) #get info on midi devices
		io = ""

		#Check if input or output
		if temp[2] and not temp[3]:
			io = "Input"
		elif temp[3] and not temp[2]:
			io = "Output"
		else:
			io = "Unrecognized"

		#Print info
		print(io, "Device #", device, temp[1])

	#Prompt user for devices
	input_id = raw_input("Choose midi input device #: ")
	output_id = raw_input("Choose midi output device #: ")

	# Create streams
	inStream = Midi.Input(int(input_id))
	outStream = Midi.Output(int(output_id))

	#Main loop. Currently no way to terminate!!! besides killing the process
	while not done:
		if inStream.poll():
			data = inStream.read(1)
			if receivingSysEx: #Check if already receiving SysEx
				receivingSysEx = appendSysEx(data)
			else:
				if sysExCheck(data): #Check if start of a SysEx msg
					receivingSysEx = appendSysEx(data)
				else:
					print(data)

if __name__ == '__main__':
    main()
