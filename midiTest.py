# Midi experiments in python
# aka What the hell am I doing

#Something with my TX7

# Need a midi lib
import pygame.midi as Midi

from yamahaX7 import TX7


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

	#Create handler
	tx7 = TX7(int(input_id),int(output_id))

	#Main loop. Currently no way to terminate!!! besides killing the process
	while not done:
		if tx7.poll():
			data = tx7.read()
			if data != 0:
				print(data)

if __name__ == '__main__':
    main()
