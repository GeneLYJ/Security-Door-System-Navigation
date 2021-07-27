# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 04:50:28 2020

@author: Wong Zhi Wei
"""
#This is just a test. Adding comments only.


import requests 
from gpiozero import MotionSensor 
from picamera import PiCamera 
from signal import pause 
from filestack import Client

import RPi.GPIO as GPIO
import time
import requests
request = None


client = Client("AcTK79tFSTWWTIoVwLl6qz")

camera = PiCamera() 
camera.resolution = (1920, 1080) 

def send_alert(): 
       camera.capture("image.jpg") 
       new_filelink = client.upload(filepath="image.jpg") 
       print(new_filelink.url) 
       r = requests.post("https://maker.ifttt.com/trigger/trigger/with/key/dBmJLfhxmK7brYJM6dU7pp", json={"value1" : new_filelink.url}) 
       if r.status_code == 200: 
           print("Alert Sent") 
       else:
           print("Error") 

      
try:
    GPIO.setmode(GPIO.BOARD)
    PIN_TRIGGER=7
    PIN_ECHO=11
    GPIO.setup(PIN_TRIGGER,GPIO.OUT)
    GPIO.setup(PIN_ECHO,GPIO.IN)
    GPIO.output(PIN_TRIGGER,GPIO.LOW)
    print("Waiting for sensor to settle")
    time.sleep(2)
    print("Calculating distance")
    GPIO.output(PIN_TRIGGER,GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(PIN_TRIGGER,GPIO.LOW)
    while GPIO.input(PIN_ECHO)==0:
        pulse_start_time=time.time()
    while GPIO.input(PIN_ECHO)==1:
        pulse_end_time=time.time()
    pulse_duration = pulse_end_time - pulse_start_time
    distance1=round(pulse_duration*17150,2)
    print("Distance1:",distance1,"cm")
    print("Calculating distance")
    print("sending to thingspeak")
    RequestToThingspeak = 'https://api.thingspeak.com/update?api_key=E6SC8Y3E3P6GANIB&field1='
    RequestToThingspeak +=str(distance1)
    request=requests.get(RequestToThingspeak)
    print('this is the answer')
    print(request.text)
    time.sleep(15)       

finally:
    GPIO.cleanup()

           
if distance1 < 10:
    if distance1 > 0:
        print(distance1)
        client = Client("AcTK79tFSTWWTIoVwLl6qz") #filestack api key = abcdefghijk
        camera = PiCamera()
        camera.rotation = 180
        camera.resolution = (1920, 1080)
        camera.framerate = 15
        camera.capture('/home/pi/Desktop/image.jpg') #path to your image
        new_filelink = client.upload(filepath="/home/pi/Desktop/image.jpg") #path to you image
        print(new_filelink.url)
        r = requests.post("https://maker.ifttt.com/trigger/trigger/with/key/dBmJLfhxmK7brYJM6dU7pp", json={"value1" : new_filelink.url}) #one line # ifttt api key = hjklyuioi
        camera.close()  
                  
