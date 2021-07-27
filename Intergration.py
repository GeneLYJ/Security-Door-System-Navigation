# Import libraries
import Encryption
import numpy as np
import random
import tkinter as tk
from tkinter import messagebox
import sys
import os
import argparse
import cv2
import time
from threading import Thread
import importlib.util
from collections import Counter
import requests
from gpiozero import MotionSensor
from picamera import PiCamera
from signal import pause
from filestack import Client
import picamera
import datetime as dt
import RPi.GPIO as GPIO
import Adafruit_DHT
from time import sleep
from subprocess import call
import pickle
import ChangeParametersGUI

##################################################################################

# # Log in page
Encryption.main()
LogIn = Encryption.stop()
if LogIn == 0:
    sys.exit()
    
###################################################################################

# GUI for user preference
ChangeParametersGUI.main()
#User Defined Video Duration
z = ChangeParametersGUI.videoDuration
videoDuration = float(z)
#User Defined Detection Distance
z = ChangeParametersGUI.detectDistance
detectDistance = float(z)
#User Defined Humidity 
z = ChangeParametersGUI.userHumidity
userHumidity = float(z)
#User Defined Alert Interval (IN SECONDS)
z = ChangeParametersGUI.userInterval
userInterval = float(z)
#User Defined Alert for Humidity and Object Detected
message1 = ChangeParametersGUI.message1
#User Defined Alert for Humidity and No Object Detected
message2 = ChangeParametersGUI.message2
#User Defined Alert for Object Detected
message3 = ChangeParametersGUI.message3
message3_out = message3

###################################################################################

#Getting humidity and temperature GPIO ready
start_time = time.time()

#Initialise Distance Array
distArr = []
k=0

#initialise alert flag
alert=0

# Set sensor type : Options are DHT11,DHT22 or AM2302
sensor=Adafruit_DHT.AM2302
 
# Set AM2302 GPIO pin
gpio=13

#initialise sum of temperature and humidity
temperatureTotal=0;
humidityTotal=0;

# Set US sensor GPIO pins
PIN_TRIGGER=4
PIN_ECHO=11

model = pickle.load(open('CART_model.sav', 'rb'))

request = None

# initialise the system
print("Initialising system...")
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_TRIGGER,GPIO.OUT)
GPIO.setup(PIN_ECHO,GPIO.IN)    
GPIO.output(PIN_TRIGGER,GPIO.LOW)    
print("")
time.sleep(2)

# Set up camera constants
IM_WIDTH = 1280
IM_HEIGHT = 720


# Define outside box coordinates (top left and bottom right)
TL_outside = (int(IM_WIDTH*0.46),int(IM_HEIGHT*0.25))
BR_outside = (int(IM_WIDTH*0.8),int(IM_HEIGHT*.85))

pause = 0
pause_counter = 0
outside_counter = 0
detected_outside = False

#######################################################################################################################################

# Define VideoStream class to handle streaming of video from webcam in separate processing thread
# Source - Adrian Rosebrock, PyImageSearch: https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/
class VideoStream:
    """Camera object that controls video streaming from the Picamera"""
    def __init__(self,resolution=(320,240),framerate=24):
        # Initialize the PiCamera and the camera image stream
        self.stream = cv2.VideoCapture(0)
        ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret = self.stream.set(3,resolution[0])
        ret = self.stream.set(4,resolution[1])
            
        # Read first frame from the stream
        (self.grabbed, self.frame) = self.stream.read()

    # Variable to control when the camera is stopped
        self.stopped = False

    def start(self):
    # Start the thread that reads frames from the video stream
        Thread(target=self.update,args=()).start()
        return self

    def update(self):
        # Keep looping indefinitely until the thread is stopped
        while True:
            # If the camera is stopped, stop the thread
            if self.stopped:
                # Close camera resources
                self.stream.release()
                return

            # Otherwise, grab the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
    # Return the most recent frame
        return self.frame

    def stop(self):
    # Indicate that the camera and thread should be stopped
        self.stopped = True
        
######################################################################################################################################################

# Setting up TFLite model
# Define and parse input arguments
parser = argparse.ArgumentParser()

parser.add_argument('--graph', help='Name of the .tflite file, if different than detect.tflite',
                    default='detect.tflite')
parser.add_argument('--labels', help='Name of the labelmap file, if different than labelmap.txt',
                    default='labelmap.txt')
parser.add_argument('--threshold', help='Minimum confidence threshold for displaying detected objects',
                    default=0.5)
parser.add_argument('--resolution', help='Desired webcam resolution in WxH. If the webcam does not support the resolution entered, errors may occur.',
                    default='1280x720')
parser.add_argument('--edgetpu', help='Use Coral Edge TPU Accelerator to speed up detection',
                    action='store_true')

args = parser.parse_args()

MODEL_NAME = 'Sample_TFLite_model'
GRAPH_NAME = args.graph
LABELMAP_NAME = args.labels
min_conf_threshold = float(args.threshold)
resW, resH = args.resolution.split('x')
imW, imH = int(resW), int(resH)
use_TPU = args.edgetpu

# Import TensorFlow libraries
# If tflite_runtime is installed, import interpreter from tflite_runtime, else import from regular tensorflow
# If using Coral Edge TPU, import the load_delegate library
pkg = importlib.util.find_spec('tflite_runtime')
if pkg:
    from tflite_runtime.interpreter import Interpreter
    if use_TPU:
        from tflite_runtime.interpreter import load_delegate
else:
    from tensorflow.lite.python.interpreter import Interpreter
    if use_TPU:
        from tensorflow.lite.python.interpreter import load_delegate

# If using Edge TPU, assign filename for Edge TPU model
if use_TPU:
    # If user has specified the name of the .tflite file, use that name, otherwise use default 'edgetpu.tflite'
    if (GRAPH_NAME == 'detect.tflite'):
        GRAPH_NAME = 'edgetpu.tflite'       

# Get path to current working directory
CWD_PATH = os.getcwd()

# Path to .tflite file, which contains the model that is used for object detection
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,GRAPH_NAME)

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH,MODEL_NAME,LABELMAP_NAME)

# Load the label map
with open(PATH_TO_LABELS, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

# Have to do a weird fix for label map if using the COCO "starter model" from
# https://www.tensorflow.org/lite/models/object_detection/overview
# First label is '???', which has to be removed.
if labels[0] == '???':
    del(labels[0])

# Load the Tensorflow Lite model.
# If using Edge TPU, use special load_delegate argument
if use_TPU:
    interpreter = Interpreter(model_path=PATH_TO_CKPT,
                              experimental_delegates=[load_delegate('libedgetpu.so.1.0')])
    print(PATH_TO_CKPT)
else:
    interpreter = Interpreter(model_path=PATH_TO_CKPT)

interpreter.allocate_tensors()

# Get model details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

floating_model = (input_details[0]['dtype'] == np.float32)

input_mean = 127.5
input_std = 127.5

# Initialize frame rate calculation
frame_rate_calc = 1
freq = cv2.getTickFrequency()

# Initialize video stream
videostream = VideoStream(resolution=(imW,imH),framerate=24).start()
time.sleep(1)

############################################################################################

# main loop
while True:

    ############################################################################################
    
    # Object detection
    #Getting the font type
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Grab frame from video stream
    frame1 = videostream.read()

    # Acquire frame and resize to expected shape [1xHxWx3]
    frame = frame1.copy()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_resized = cv2.resize(frame_rgb, (width, height))
    input_data = np.expand_dims(frame_resized, axis=0)

    # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
    if floating_model:
        input_data = (np.float32(input_data) - input_mean) / input_std

    # Perform the actual detection by running the model with the image as input
    interpreter.set_tensor(input_details[0]['index'],input_data)
    interpreter.invoke()

    # Retrieve detection results
    boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
    classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
    scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects
    #num = interpreter.get_tensor(output_details[3]['index'])[0]  # Total number of detected objects (inaccurate and not needed)
    
    # Draw boxes defining "outside" locations.
    cv2.rectangle(frame,TL_outside,BR_outside,(255,20,20),3)
    cv2.putText(frame,"Outside box",(TL_outside[0]+10,TL_outside[1]-10),font,1,(255,20,255),3,cv2.LINE_AA)
    
    ##############################################################################################
    
    # set alert flag based on user defined alert interval
    current_time = time.time()
    elapse = current_time - start_time
        
    if elapse > userInterval and alert==0:
        alert=1
    
    ##############################################################################################
    
    # Reading distance
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
    US_timestamp = pulse_end_time
    time.sleep(1)
    
    #############################################################################################
    
    # Reading humidity and temperature
    # Use read_retry method. This will retry up to 15 times to
    # get a sensor reading (waiting 2 seconds between each retry).
    humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio)
            
    # Reading the DHT11 is very sensitive to timings and occasionally
    # the Pi might fail to get a valid reading. So check if readings are valid.
    if humidity is not None and temperature is not None:
        print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
    else:
        print('Failed to get reading. Try again!')
        
    #############################################################################################
    
    # Calculate number of object inside the pre defined box
    obj_arr = []
    # Loop over all detections and draw detection box if confidence is above minimum threshold
    for i in range(len(scores)):
        if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):
            if ((int(classes[i]) == 0) and (pause == 0)):
                
                x = int(((boxes[i][1]+boxes[i][3])/2)*IM_WIDTH)
                y = int(((boxes[i][0]+boxes[i][2])/2)*IM_HEIGHT)
        
                # Draw a circle at center of object
                cv2.circle(frame,(x,y), 5, (75,13,180), -1)
                
                ymin = int(max(1,(boxes[i][0] * imH)))
                xmin = int(max(1,(boxes[i][1] * imW)))
                ymax = int(min(imH,(boxes[i][2] * imH)))
                xmax = int(min(imW,(boxes[i][3] * imW)))

                # Draw label
                object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
                obj_arr.append(object_name)
                label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
                label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
                occurence = Counter(obj_arr)
                no_p = occurence["person"]
                
                
                # If object is in outside box, increment outside counter variable
                if ((x > TL_outside[0]) and (x < BR_outside[0]) and (y > TL_outside[1]) and (y < BR_outside[1]) and no_p >=1):

                    detected_outside = True
                    cv2.destroyAllWindows()
                    videostream.stop()
                    time.sleep(2)
                    pause = 1

    ################################################################################################################# 
    
    # if object is detected    
    if pause == 1:
            
        if distance > 0:
            print("Object detected!")
            client = Client("AcTK79tFSTWWTIoVwLl6qz") #filestack api key = abcdefghijk
            
            with picamera.PiCamera() as camera:
                camera.resolution=(320,240)
                camera.framerate=24
                camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                camera.start_recording('file.h264')
                camera.wait_recording(videoDuration)
                camera.stop_recording()
                
            timeRecorded = time.time()
            
            # Convert the h264 format to the mp4 format.
            #time.sleep(60)
            command = "ffmpeg -y -loglevel warning -probesize 100M -framerate 24 -i file.h264 -c copy output.mp4" 
            call([command], shell=True)
            
            new_filelink = client.upload(filepath="output.mp4") #PATH TO VIDEO
            print(new_filelink.url)
            #time.sleep(60)                
            r = requests.post("https://maker.ifttt.com/trigger/Video/with/key/XM7V88afj69n4Hl_bu2uB", json={"value1":new_filelink.url}) #one line # ifttt api key = hjklyuioi
            camera.close()
           
            RequestToThingspeak = 'https://api.thingspeak.com/update?api_key=T0KGS2IH69SN4X7X&field1='
            RequestToThingspeak += str(distance)
            request = requests.get(RequestToThingspeak)
            print(request.text)
                          
            # OBJECT DETECTED AND HIGH HUMIDITY ONLY SENDS THIS ALERT EVERY HOUR
            if humidity > userHumidity and alert == 1:
                r = requests.post("https://maker.ifttt.com/trigger/Humidity/with/key/XM7V88afj69n4Hl_bu2uB", json={"value1" : round(temperature,1),"value2" : round(humidity,1),"value3":message1})
                #RESET ALERT FLAG AND START TIME
                alert=0
                start_time=time.time()
            # OBJECT DETECT
            elif humidity < userHumidity and alert ==1 :
                r = requests.post("https://maker.ifttt.com/trigger/Humidity/with/key/XM7V88afj69n4Hl_bu2uB", json={"value1" : round(temperature,1),"value2" : round(humidity,1),"value3":message3_out})
                #RESET ALERT FLAG AND START TIME
                alert=0
                start_time=time.time()
            
            pause = 0
            pause_counter = 0
            detected_outside = False
            videostream = VideoStream(resolution=(imW,imH),framerate=24).start()
            time.sleep(1)
    
    ################################################################################################################
           
    #NO OBJECT DETECTED AND HIGH HUMIDITY ONLY SENDS THIS ALERT EVERY HOUR
    if humidity > userHumidity and distance > detectDistance and alert == 1 :
        r = requests.post("https://maker.ifttt.com/trigger/Humidity/with/key/XM7V88afj69n4Hl_bu2uB", json={"value1" : round(temperature,1),"value2" : round(humidity,1), "value3":message2})
        #RESET ALERT FLAG AND START TIME
        alert =0;
        start_time=time.time()
    
    ##################################################################################################################
    
    # Classify movement type using pretrained KNN model
    k+=1
    if k<3:
        distArr.append(distance)
    else:
        distArr.pop(0)
        distArr.append(distance)
        distDiff=[[(distArr[0]-distArr[1])/(US_timestamp-US_timestamp_prev)]]
        new_output=model.predict(distDiff)
        message3_out=message3 + ', ' + new_output[0]
    US_timestamp_prev = US_timestamp
    
    ###################################################################################################################
    
    #Draw counter info       
    cv2.putText(frame,'Detection counter: ' + str(outside_counter),(10,100),font,0.5,(255,255,0),1,cv2.LINE_AA)
    cv2.putText(frame,'Pause counter: ' + str(pause_counter),(10,150),font,0.5,(255,255,0),1,cv2.LINE_AA)          

    # All the results have been drawn on the frame, so it's time to display it.
    cv2.imshow('Object detector', frame)

    # Press 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        break  