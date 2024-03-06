# I am Mohammad Omar, this module is builded to interface with the Driver MDD10A, to control two DC motors.
# the original code designed by Ingmar Stapel ,www.raspberry-pi-car.com to control two motors with a L298N H-Bridge
# The pins configuration for Model B Revision 1.0 

import sys, tty, termios, os
import MDD10A as HBridge
#from picamera import PiCamera
import time
import glob

speedleft = 0
speedright = 0
obstacle_capture_count = 0
waypoint_capture_count = 0

obstacle_images = glob.glob("/home/koi/Desktop/obstacle/obstacle*.jpg")
waypoint_images = glob.glob("/home/koi/Desktop/waypoint/waypoint*.jpg")

# Instructions for when the user has an interface
print("w/s: direction")
print("a/d: steering")
print("q: stops the motors")
print("p: print motor speed (L/R)")
print("x: exit")
print("o: take obstacle picture")
print("p: take waypoint picture")

#camera = PiCamera()
#camera.resolution = (640, 480)
#camera.rotation = 180
time.sleep(2)

# The catch method can determine which key has been pressed
# by the user on the keyboard.
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# Infinite loop
# The loop will not end until the user presses the
# exit key 'X' or the program crashes... #

def printscreen():
	# Print the motor speed just for interest
	os.system('clear')
	print("w/s: direction")
	print("a/d: steering")
	print("q: stops the motors")
	print("x: exit")
	print("e: take picture")
	print("========== Speed Control ==========")
	print("left motor: " + str(speedleft))
	print("right motor: " + str(speedright))
	print("========== Image Capture ==========")
	print("o: obstacle taken: " + str(obstacle_capture_count))
	print("o: obstacle total: " + str(len(obstacle_images)))
	print("p: waypoint taken: " + str(waypoint_capture_count))
	print("p: waypoint total: " + str(len(waypoint_images)))

while True:
    # Keyboard character retrieval method. This method will save
    # the pressed key into the variable char
	char = getch()

	if(char == "o"):
	
		# synchronize after a turning the motor speed
			
		# if speedleft > speedright:
			# speedleft = speedright
		
		# if speedright > speedleft:
			# speedright = speedleft
				
		# accelerate the RaPi car
		obstacle_images = glob.glob("/home/koi/Desktop/obstacle/obstacle*.jpg")
		obstacle_number = len(obstacle_images) + 1
		camera.capture("/home/koi/Desktop/obstacle/obstacle{}.jpg".format(obstacle_number))
		obstacle_capture_count += 1
		obstacle_images = glob.glob("/home/koi/Desktop/obstacle/obstacle*.jpg")
		printscreen()
		
	if(char == "p"):
	
		# synchronize after a turning the motor speed
			
		# if speedleft > speedright:
			# speedleft = speedright
		
		# if speedright > speedleft:
			# speedright = speedleft
				
		# accelerate the RaPi car
		waypoint_images = glob.glob("/home/koi/Desktop/waypoint/waypoint*.jpg")
		waypoint_number = len(waypoint_images) + 1
		camera.capture("/home/koi/Desktop/waypoint/waypoint{}.jpg".format(waypoint_number))
		waypoint_capture_count += 1
		waypoint_images = glob.glob("/home/koi/Desktop/waypoint/waypoint*.jpg")
		printscreen()
	
	# The car will drive forward when the "w" key is pressed
	if(char == "w"):
	
		# synchronize after a turning the motor speed
			
		# if speedleft > speedright:
			# speedleft = speedright
		
		# if speedright > speedleft:
			# speedright = speedleft
				
		# accelerate the RaPi car
		speedleft = speedleft + 0.1
		speedright = speedright + 0.1

		if speedleft > 1:
			speedleft = 1
		if speedright > 1:
			speedright = 1
		
		HBridge.setMotorLeft(speedleft)
		HBridge.setMotorRight(speedright)
		printscreen()

    # The car will reverse when the "s" key is pressed
	if(char == "s"):
	
		# synchronize after a turning the motor speed
			
		# if speedleft > speedright:
			# speedleft = speedright
			
		# if speedright > speedleft:
			# speedright = speedleft
			
		# slow down the RaPi car
		speedleft = speedleft - 0.1
		speedright = speedright - 0.1

		if speedleft < -1:
			speedleft = -1
		if speedright < -1:
			speedright = -1
		
		HBridge.setMotorLeft(speedleft)
		HBridge.setMotorRight(speedright)
		printscreen()

    # Stop the motors
	if(char == "q"):
		speedleft = 0
		speedright = 0
		HBridge.setMotorLeft(speedleft)
		HBridge.setMotorRight(speedright)
		printscreen()

    # The "d" key will toggle the steering right
	if(char == "d"):		
		#if speedright > speedleft:
		#speedright = speedright - 0.1
		speedleft = speedleft + 0.1
		
		#if speedright < -1:
		#	speedright = -1
		
		if speedleft > 1:
			speedleft = 1
		
		HBridge.setMotorLeft(speedleft)
		HBridge.setMotorRight(speedright)
		printscreen()
		
    # The "a" key will toggle the steering left
	if(char == "a"):
		#if speedleft > speedright:
		#speedleft = speedleft - 0.1
		speedright = speedright + 0.1
			
		#if speedleft < -1:
		#	speedleft = -1
		
		if speedright > 1:
			speedright = 1
		
		HBridge.setMotorLeft(speedleft)
		HBridge.setMotorRight(speedright)
		printscreen()
		
	# The "x" key will break the loop and exit the program
	if(char == "x"):
		HBridge.setMotorLeft(0)
		HBridge.setMotorRight(0)
		HBridge.exit()
		print("Program Ended")
		break
	
    # The keyboard character variable char has to be set blank. We need
	# to set it blank to save the next key pressed by the user
	char = ""
# End
