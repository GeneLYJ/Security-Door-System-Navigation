import requests
from gpiozero import MotionSensor
from picamera import PiCamera
from signal import pause
from filestack import Client
import picamera
import datetime as dt
import time
import numpy as np
import os
import sys

import RPi.GPIO as GPIO

import requests 
import Adafruit_DHT
request = None

from time import sleep
from subprocess import call

start_time = time.time()
#duration = 15*60

#User Defined Video Duration 
videoDuration = 60
#User Defined Detection Distance
detectDistance = 10
#User Defined Humidity 
userHumidity = 1
#User Defined Alert Interval (IN SECONDS)
userInterval = 60
#User Defined Alert for Humidity and Object Detected
message1="Person Outside and It is Raining"
#User Defined Alert for Humidity and No Object Detected
message2="Keep the Laundry"
#FIlestack API Key
#filestackAPI='AwBeerjbKTbOK12cs9Yj1z'

#initialise alert flag
alert=0

# Set sensor type : Options are DHT11,DHT22 or AM2302
sensor=Adafruit_DHT.AM2302
 
# Set GPIO sensor connected to
gpio=18

#initialise sum of temperature and humidity
temperatureTotal=0;
humidityTotal=0;

# Set US sensor GPIO pins
PIN_TRIGGER=7
PIN_ECHO=11

# initialise the system
print("Initialising system...")
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN_TRIGGER,GPIO.OUT)
GPIO.setup(PIN_ECHO,GPIO.IN)    
GPIO.output(PIN_TRIGGER,GPIO.LOW)    
print("Waiting for sensor to settle")
print("")
time.sleep(2)

try:
    while True:
        current_time = time.time()
        elapse = current_time - start_time
        
        if elapse > userInterval and alert==0:
            alert=1
    
        print("Calculating distance")
        GPIO.output(PIN_TRIGGER,GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(PIN_TRIGGER,GPIO.LOW)
        while GPIO.input(PIN_ECHO)==0:
            pulse_start_time=time.time()
        while GPIO.input(PIN_ECHO)==1:
            pulse_end_time=time.time()
        pulse_duration = pulse_end_time - pulse_start_time
        distance=round(pulse_duration*17150,2)
        print("Distance:",distance,"cm")
        #time.sleep(1)    
    
        # Use read_retry method. This will retry up to 15 times to
        # get a sensor reading (waiting 2 seconds between each retry).
        humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio)
            
        # Reading the DHT11 is very sensitive to timings and occasionally
        # the Pi might fail to get a valid reading. So check if readings are valid.
        if humidity is not None and temperature is not None:
            print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
        else:
            print('Failed to get reading. Try again!')
            
        if distance < detectDistance:
            if distance > 0:
                
                print(distance)
                client = Client("AwBeerjbKTbOK12cs9Yj1z") #filestack api key = abcdefghijk

                with picamera.PiCamera() as camera:
                    camera.resolution=(1280,720)
                    camera.framerate=30
                    camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    camera.start_recording('file.h264')
                    camera.wait_recording(videoDuration)
                    camera.stop_recording()
                    
                timeRecorded = time.time()
                
                # Convert the h264 format to the mp4 format.
                #time.sleep(60)
                command = "ffmpeg -y -loglevel warning -probesize 100M -framerate 30 -i file.h264 -c copy output.mp4" 
                call([command], shell=True)
                #time.sleep(60)
                new_filelink = client.upload(filepath="output.mp4") #PATH TO VIDEO
                print(new_filelink.url)
                r = requests.post("https://maker.ifttt.com/trigger/trigger/with/key/bDpx-YBk17ppwAvvRfCDm5", json={"value1":new_filelink.url}) #one line # ifttt api key = hjklyuioi
                camera.close()
               
                RequestToThingspeak = 'https://api.thingspeak.com/update?api_key=Z7QW2IMYL30IEGMU&field1='
                RequestToThingspeak += str(distance)
                request = requests.get(RequestToThingspeak)
                print(request.text)
                
                # OBJECT DETECTED AND HIGH HUMIDITY ONLY SENDS THIS ALERT EVERY HOUR
                if humidity > userHumidity and alert == 1:
                    r = requests.post("https://maker.ifttt.com/trigger/ObjectDetectedHumidityHigh/with/key/bDpx-YBk17ppwAvvRfCDm5", json={"value1" : round(temperature,1),"value2" : round(humidity,1),"value3":message1})
                    #RESET ALERT FLAG AND START TIME
                    alert=0
                    start_time=time.time()
                    
        #NO OBJECT DETECTED AND HIGH HUMIDITY ONLY SENDS THIS ALERT EVERY HOUR
        elif humidity > userHumidity and distance > detectDistance and alert == 1 :
            r = requests.post("https://maker.ifttt.com/trigger/ObjectDetectedHumidityHigh/with/key/bDpx-YBk17ppwAvvRfCDm5", json={"value1" : round(temperature,1),"value2" : round(humidity,1), "value3":message2})
            #RESET ALERT FLAG AND START TIME
            alert =0;
            start_time=time.time()
    
        print("")
finally:
    GPIO.cleanup()

