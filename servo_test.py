# ***************************************************
#   SERVO test for duty cycle range
#
#   ProtoStax Air Quality Monitor.
#   using Raspberry Pi A+, Micro Servo SG92R, RGB LED and ProtoStax Enclosure for Raspberry Pi
#   --> https://www.protostax.com/products/protostax-for-raspberry-pi-a
#   You can also use
#   --> https://www.protostax.com/products/protostax-for-raspberry-pi-b
#   --> https://www.protostax.com/products/protostax-for-raspberry-pi-zero
#
#   Use this program to test the range of movement from your micro servo
#   and set the appropriate MIN, MAX and CENTER duty cycles for your given
#   servo in the aqi_monitor.py program
#
#   At the way the servo is oriented on the ProtoStax Kit for Micro Servo,
#   the highest duty cycle will position the servo arm to the left and
#   reducing the duty cycle will cause a clockwise rotation to the max
#   value. So note that MAX_DUTY cycle will correspond to a ZERO reading
#   and MIN_DUTY cycle will correspond to a maximum reading (of around 250)
#   This inversion of logic is handled in the main aqi_monitor.py program - you just
#   need to plug in the values for MIN_DUTY and MAX_DUTY and CENTER_DUTY. 
#
#   Start off with the highest duty cycle where the servo moves without jittering.
#   Then place the gauge indicator and position it so that it is closest to zero reading (or less than zero).
#   Then adjust the duty cycle (by reducing the duty cycle so that you get a ZERO reading) - this will be your MAX_DUTY
#
#   Find out the MIN_DUTY cycle where the servo will safely get to the max
#   rotation. If the servo is grinding or whining, back off. This was
#   around 3 in my case. If I set it to 1, for example, the servo goes
#   crazy and goes into continuous rotation. Avoid this if you don't want to
#   risk damaging your servo! If I set it to 2, the needle started drifting - you
#   don't want this either!
#
#   If this happens, you will need to repeat the zeroing procedure above, and the
#   MIN_DUTY to where it doesn't jitter or drift. After that, proceed with the next step:
#
#   Adjust the duty cycle so that the gauge needle points to 150, the center value
#   Note this CENTER_DUTY cycle value. It was around 5.9 to 6.0 in my case. 
#
#   Written by Sridhar Rajagopal for ProtoStax.
#
#
#   BSD license. All text above must be included in any redistribution

import RPi.GPIO as GPIO
import time

# Configure the Pi to use pin names (i.e. BOARD) and allocate I/O
# We are utilizing the BOARD pin numbering, which means
# connect the servo to physical pin number 7 on your Raspberry Pi
# (Or change the SERVO_PIN below to correspond to the physical pin number you
# are using)
GPIO.setmode(GPIO.BOARD)
SERVO_PIN = 7

# Set SERVO_PIN for output
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Create PWM channel on the SERVO_PIN with a frequency of 50Hz
# Refer to your micro servo's datasheet for the frequency it uses
pwm_servo = GPIO.PWM(SERVO_PIN, 50)
pwm_servo.start(0)

try:
    print("Test different duty cycles to find out the: ")
    print("* MIN DUTY CYCLE (this will correspond to HIGHEST indicator reading, usually around 250), ")
    print("* MAX DUTY CYCLE (this will correpond to the 0 indicator")
    print("* CENTER DUTY CYCLE - find out which duty cycle gets you to a reading of 150")
    print("Note these values for use in the aqi_monitor.py program")
    
    while True:
        duty_cycle = float(input("Enter Duty Cycle (usually between 2 and 12 for SG92R, but the exact limits vary):"))
        pwm_servo.ChangeDutyCycle(duty_cycle)
        time.sleep(0.5)
            
except KeyboardInterrupt:
    print("CTRL-C: Terminating program.")
finally:
    print("Cleaning up GPIO...")
    pwm_servo.stop()
    GPIO.cleanup()
