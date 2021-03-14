# ***************************************************
#   LED test for color mixing
#
#   ProtoStax Air Quality Monitor.
#   using Raspberry Pi A+, Micro Servo SG92R, RGB LED and ProtoStax Enclosure for Raspberry Pi
#   --> https://www.protostax.com/products/protostax-for-raspberry-pi-a
#   You can also use
#   --> https://www.protostax.com/products/protostax-for-raspberry-pi-b
#   --> https://www.protostax.com/products/protostax-for-raspberry-pi-zero
#
#   Use this program to test the color mixing for the RGB LED
#
#   In the AQI monitor, we use the following colors:
#   green, yellow, orange, red, purple and maroon
#
#   Using this program, you can figure out the R,G,B values for the perfect
#   color of your choice, and plug those values in aqi_monitor.py
#   should you desire to change the default values there
#
#   Written by Sridhar Rajagopal for ProtoStax.
#
#
#   BSD license. All text above must be included in any redistribution


import RPi.GPIO as GPIO
import time 

# Configure the Pi to use pin names (i.e. BOARD) and allocate I/O
# We are utilizing the BOARD pin numbering, which means
# connect the RGB LED pins to physical pin numbers 11, 13 and 15 on your Raspberry Pi
# (Or change the RED_PIN, GREEN_PIN and BLUE_PIN values below to correspond to the physical pin number you
# are using)
GPIO.setmode(GPIO.BOARD) 

#closing the warnings when you are compiling the code
GPIO.setwarnings(False)

#defining the pins
RED_PIN = 11
GREEN_PIN = 13
BLUE_PIN = 15

#defining the pins as output
GPIO.setup(RED_PIN, GPIO.OUT) 
GPIO.setup(GREEN_PIN, GPIO.OUT)
GPIO.setup(BLUE_PIN, GPIO.OUT)

#choosing a frequency for pwm
Freq = 2000

#defining the pins that are going to be used with PWM
pwm_red = GPIO.PWM(RED_PIN, Freq)  
pwm_green = GPIO.PWM(GREEN_PIN, Freq)
pwm_blue = GPIO.PWM(BLUE_PIN, Freq)

def setRGBled(red, green, blue):
    pwm_red.ChangeDutyCycle(100.0 - (100.0*red)/255.0)
    pwm_green.ChangeDutyCycle(100.0 - (100.0*green)/255.0)
    pwm_blue.ChangeDutyCycle(100.0 - (100.0*blue)/255.0)

# We are using a Common Anode (CA) RGB LED, so the logic is reversed
# setting a pin HIGH turns OFF the pin, and seting it LOW turns it ON
# Starting with a duty cycle of 100 therefore turns OFF the corresponding
# color LED
pwm_red.start(100)
pwm_green.start(100)
pwm_blue.start(100)

try:
    #we are starting with the loop
    while True:
        values = input("Input comma seprated RGB numbers : ")
        setRGBled(values[0], values[1], values[2])
        time.sleep(0.5)
except KeyboardInterrupt: 
    print("CTRL-C: Terminating program.")
finally:
    print("Cleaning up GPIO...")    
    pwm_red.stop()
    pwm_green.stop()
    pwm_blue.stop()
    GPIO.cleanup()
