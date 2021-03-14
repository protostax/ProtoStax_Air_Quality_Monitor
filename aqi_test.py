# ***************************************************
#   AQI Test - Test out querying Purple Air for data
#
#   ProtoStax Air Quality Monitor.
#   using Raspberry Pi A+, Micro Servo SG92R, RGB LED and ProtoStax enclosure
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
#   Use this program to test out querying Purple Air data without worrying yet
#   about SERVO and RGB LEDs
#
#   The main program aqi_monitor.py queries the Purple Air data for the
#   Station ID specified, AND sets the SERVO and the RGB LED to the appropriate
#   AQI value and color respectively
#
#   Purple Air data is obtained from Purple Air (https://www.purpleair.com/)
#
#   Written by Sridhar Rajagopal for ProtoStax.
#
#
#   BSD license. All text above must be included in any redistribution

import requests
import json
import argparse
import signal


def calcAQ (Cp, Ih, Il, BPh, BPl):
    a = (Ih - Il)
    b = (BPh - BPl)
    c = (Cp - BPl)
    aq = ((a/b) * c + Il)
    return aq

url = 'https://www.purpleair.com/json?key=9GJLOOSARUKDKMXY&show='

# The main function
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--stationID", action="store", required=True, dest="stationID", help="Purple Air Station ID")

    args = parser.parse_args()
    stationID = args.stationID
    
    r = requests.get(url+stationID)
    j = json.loads(r.text)
    
    pm2 = 0.0
    for row in j["results"]:
        pm2 = float(row["PM2_5Value"])
        pm2 = pm2 + pm2

    pm2 = pm2 /2

    if (pm2 > 350.5):
        aq = calcAQ(pm2, 500, 401, 500, 350.5)
    elif (pm2 > 250.5):
        aq = calcAQ(pm2, 400, 301, 350.4, 250.5)
    elif (pm2 > 150.5):
        aq = calcAQ(pm2, 300, 201, 250.4, 150.5)
    elif (pm2 > 55.5):
        aq = calcAQ(pm2, 200, 151, 150.4, 55.5)
    elif (pm2 > 35.5):
        aq = calcAQ(pm2, 150, 101, 55.4, 35.5)
    elif (pm2 > 12.1):
        aq = calcAQ(pm2, 100, 51, 35.4, 12.1)
    elif (pm2 > 0):
        aq = calcAQ(pm2, 50, 0, 12, 0)

    print ("PM: " + str(pm2))
    print ("AQ: " + str(aq))

# gracefully exit without a big exception message if possible
def ctrl_c_handler(signal, frame):
    print('Goodbye!')
    exit(0)    

signal.signal(signal.SIGINT, ctrl_c_handler)


if __name__ == '__main__':
    main()
