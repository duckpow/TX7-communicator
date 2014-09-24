#Test with full pygame module

#External modules
import pygame, sys
import pygame.midi as Midi

from yamahaX7 import TX7
from midiController import MidiController

def get_midi_devices():
	device_count = Midi.get_count()
	#get info on devices
	if device_count > 0:
		print("Midi-devices found:")
		for device in range(device_count):
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
	else:
		print("No Midi devices found \n exiting...")
		sys.exit(0) #No reason to carry on so exit

#Main program
def main():
	pygame.init()
	Midi.init()

	done = False

	get_midi_devices()
	#Prompt user for devices
	input_id = raw_input("Choose midi input device #: ")
	output_id = raw_input("Choose midi output device #: ")

	controller_id = raw_input("Choose midi controller: ")

	#Create handlers
	tx7 = TX7(int(input_id),int(output_id))
	keyboard = MidiController(int(controller_id))

	#Clock control.
	fps = 60
	clock = pygame.time.Clock()

	#Main loop
	while not done:
		#Handle keyboard
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				done = True
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					done = True

		if tx7.poll():
			data = tx7.read()
			if data != 0:
				print(data)
		elif keyboard.poll():
			data = keyboard.read_noteMsg()
			if data != None:
				print(data)
				tx7.write_noteOn(data[1],data[2])

		clock.tick(fps)

	#proper exit
	pygame.quit()
	sys.exit(0)

if __name__ == '__main__':
	main()