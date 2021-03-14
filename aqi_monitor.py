# ***************************************************
#   ProtoStax Air Quality Monitor.
#   using Raspberry Pi A+, Micro Servo SG92R, RGB LED and ProtoStax Enclosure for Raspberry Pi
#   --> https://www.protostax.com/products/protostax-for-raspberry-pi-a
#   You can also use
#   --> https://www.protostax.com/products/protostax-for-raspberry-pi-b
#   --> https://www.protostax.com/products/protostax-for-raspberry-pi-zero
#
#   It queries the current air quality information from a Purple Air Monitor,
#   calculates the AQI from the data (using a 10 minute average), and then
#   displays the information using a micro-servo (SG92R) as a retro-gauge
#   along with the color displayed on an RGB LED.
#
#   Purple Air data is obtained from Purple Air (https://www.purpleair.com/)
#
#   Written by Sridhar Rajagopal for ProtoStax.
#
#
#   BSD license. All text above must be included in any redistribution

import RPi.GPIO as GPIO
import time
import requests
import json
import argparse
import signal

GPIO.setmode(GPIO.BOARD)
SERVO_PIN = 7
RED_PIN = 11
GREEN_PIN = 13
BLUE_PIN = 15

class AnalogGauge(object):
    def __init__(self):
        # The max and min values are obtained from testing the servo (see servo_test.py)
        # The values represent the duty cycles for the range of motion of the servo
        # and are dependent on the type of servo and its characteristics
        # The center duty cycle represents the duty cycle required to place the servo at
        # the center of the analog gauge (which is 150 AQI)
        self.MIN_DUTY = 3.0 # ADJUST THESE VALUES FOR YOUR SERVO
        self.MAX_DUTY = 10.9 # ADJUST THESE VALUES FOR YOUR SERVO
        self.CENTER_DUTY = 5.75 # ADJUST THESE VALUES FOR YOUR SERVO
        
        self.LOWEST_VALUE = 0 # Correspoding to MIN_DUTY
        self.CENTER_VALUE = 150
        self.A = 0.0
        self.B = 0.0
        self.servo_pin = SERVO_PIN
        GPIO.setup(self.servo_pin, GPIO.OUT)
        self.calibrate()
        # Create PWM channel on the servo pin with a frequency of 50Hz
        self.pwm_servo = GPIO.PWM(self.servo_pin, 50)
        # Let's start with servo turned off
        self.pwm_servo.start(0)
        

    # This method tries to solve for the linear equation
    # duty_cycle = A*aq_value + B
    # to figure out the values for constants A and B
    # LOWEST_VALUE corresponds to MAX_DUTY and CENTER_VALUE (150) corresponds to CENTER_DUTY
    # duty_cycle = A*aq_value + B
    def calibrate(self):
        self.B = self.MAX_DUTY
        self.A = (self.CENTER_DUTY - self.MAX_DUTY)/self.CENTER_VALUE


    # This method maps the AQI value calculated to the required duty cycle value
    # It uses the constants computed when calibrate is called
    # It will never exceed the lower and upper limits of the DUTY cycle
    def mapValueToDutyCycle(self, value):
        retVal = value*self.A + self.B 
        retVal =  self.MIN_DUTY if (retVal < self.MIN_DUTY) else self.MAX_DUTY if (retVal > self.MAX_DUTY) else retVal
        return retVal

    # This method moves the gauge to the appropriate value as specified by the aq parameter
    def setGaugeValue(self, aq):
        self.pwm_servo.ChangeDutyCycle(self.mapValueToDutyCycle(aq))
        time.sleep(1)
        self.pwm_servo.ChangeDutyCycle(0)

    # Final cleanup when exiting
    def cleanup(self):
        self.setGaugeValue(0)
        self.pwm_servo.stop()
        

class AQI(object):

    def calcAQI (self, Cp, Ih, Il, BPh, BPl):
        a = (Ih - Il)
        b = (BPh - BPl)
        c = (Cp - BPl)
        aq = ((a/b) * c + Il)
        return aq

    def getAQIfromPM25 (self, pm2):
        aq = 0.0
        if (pm2 > 350.5):
            aq = self.calcAQI(pm2, 500, 401, 500, 350.5)
        elif (pm2 > 250.5):
            aq = self.calcAQI(pm2, 400, 301, 350.4, 250.5)
        elif (pm2 > 150.5):
            aq = self.calcAQI(pm2, 300, 201, 250.4, 150.5)
        elif (pm2 > 55.5):
            aq = self.calcAQI(pm2, 200, 151, 150.4, 55.5)
        elif (pm2 > 35.5):
            aq = self.calcAQI(pm2, 150, 101, 55.4, 35.5)
        elif (pm2 > 12.1):
            aq = self.calcAQI(pm2, 100, 51, 35.4, 12.1)
        elif (pm2 > 0):
            aq = self.calcAQI(pm2, 50, 0, 12, 0)
        return aq

    # Returns an RGB tuple for the given AQI
    # RGB values are standard 0 to 255
    def mapAQItoColor(self, aq):
        if (aq >= 301):
            # Maroon
            return (255, 0, 10)
        elif (aq >= 201):
            # Purple
            return (128, 0, 128)
        elif (aq >= 151):
            # Red
            return (255, 0, 0)
        elif (aq >= 101):
            # Orange
            return (255, 10, 0)
        elif (aq >= 51):
            # Yellow
            return (255, 50, 0)
        elif (aq >= 0):
            # Green
            return (0, 255, 0)


class RGBLED(object):
    def __init__(self):
        self.red_pin = RED_PIN
        self.green_pin = GREEN_PIN
        self.blue_pin = BLUE_PIN
        self.LED_FREQ = 2000
        #defining the pins as output
        GPIO.setup(self.red_pin, GPIO.OUT) 
        GPIO.setup(self.green_pin, GPIO.OUT)
        GPIO.setup(self.blue_pin, GPIO.OUT)
        #defining the pins that are going to be used with PWM
        self.pwm_red = GPIO.PWM(self.red_pin, self.LED_FREQ)  
        self.pwm_green = GPIO.PWM(self.green_pin, self.LED_FREQ)
        self.pwm_blue = GPIO.PWM(self.blue_pin, self.LED_FREQ)
        self.pwm_red.start(100)
        self.pwm_green.start(100)
        self.pwm_blue.start(100)


    def setRGBled(self, red, green, blue):
        self.pwm_red.ChangeDutyCycle(100.0 - (100.0*red)/255.0)
        self.pwm_green.ChangeDutyCycle(100.0 - (100.0*green)/255.0)   
        self.pwm_blue.ChangeDutyCycle(100.0 - (100.0*blue)/255.0)
    

# The main function
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--stationID", action="store", required=True, dest="stationID", help="Purple Air Station ID")

    args = parser.parse_args()
    stationID = args.stationID
    
    url = 'https://www.purpleair.com/json?show=' + str(stationID)

    # Create and initialize the Analog Gauge, RGB LED and AQI helper
    analogGauge = AnalogGauge()
    rgbLED = RGBLED()
    aqi = AQI()
    
    DATA_LIMIT = 10 # 10 minute history for data collected every minute
    DATA_INTERVAL = 60
    pmHistory = []

    try:        
        while True:
            print (url)
            r = requests.get(url)
            j = json.loads(r.text)
            print(j["results"])
            print (type(j["results"]))

            pm2 = 0.0
            numPM25vals = 0
            for row in j["results"]:
                # Some results don't have PM2_5Value - let's not choke!
                if "PM2_5Value" in row:
                    pm25 = float(row["PM2_5Value"])
                    pm2 = pm2 + pm25
                    numPM25vals = numPM25vals + 1 

            # We only want to calculate average IF we've actually read some
            # values! If there are no values, for example, let's not choke!
            if (numPM25vals > 0): 
                pm2 = pm2 / numPM25vals

            # We store 10 minutes worth of data and
            # compute our 10 minute average from that
            if len(pmHistory) > (DATA_LIMIT - 1):
                del pmHistory[0]
            pmHistory.append(pm2)
            avPM = sum(pmHistory) / len(pmHistory) 
            aq = aqi.getAQIfromPM25(avPM)

            print ("PM (current): " + str(pm2))
            print ("PM 10 minute average: (" + str(len(pmHistory)) + " minute history available) :" +  str(avPM))
            print ("AQ (10 minute average): " + str(aq)) 

            analogGauge.setGaugeValue(aq)
            (r, g, b) = aqi.mapAQItoColor(aq)
            rgbLED.setRGBled(r, g, b)
            
            # Well, the true data interval will be longer than 60 seconds because
            # of the other processing we do, but we don't have to worry, since
            # we are reliant on Purple Air updating its data as well
            # so the ballpark should be good enough
            time.sleep(DATA_INTERVAL)
            
    except KeyboardInterrupt:
        print("CTRL-C: Terminating program.")
    finally:
        print("Cleaning up GPIO...")
        analogGauge.cleanup()
        time.sleep(0.5)
        GPIO.cleanup()


if __name__ == '__main__':
    main()
