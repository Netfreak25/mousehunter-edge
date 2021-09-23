# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import warnings
import datetime
import imutils
import json
import time
import cv2

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True,help="path to the JSON configuration file")
args = vars(ap.parse_args())

# filter warnings, load the configuration
warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = tuple(conf["resolution"])
camera.framerate = conf["fps"]
rawCapture = PiRGBArray(camera, size=tuple(conf["resolution"]))

# allow the camera to warmup, then initialize the average frame, last
# saved timestamp, and frame motion counter
print(str(datetime.datetime.now()) + " [INFO] warming up...")
time.sleep(conf["camera_warmup_time"])
avg = None
# only for debugging
#c_count = 0
#c_avg = 0

# capture frames from the camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image and initialize
    # the timestamp and occupied/unoccupied text
    frame = f.array
    rawCapture.truncate(0)
    timestamp = datetime.datetime.now()
    movement = False

    # resize the frame, convert it to grayscale, and blur it
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

	# if the average frame is None, initialize it
    if avg is None:
        print(str(timestamp) + " [INFO] starting background model...")
        avg = gray.copy().astype("float")
        rawCapture.truncate(0)
        continue

    # accumulate the weighted average between the current frame and
    # previous frames, then compute the difference between the current
    # frame and running average
    cv2.accumulateWeighted(gray, avg, 0.5)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
    
    # threshold the delta image, dilate the thresholded image to fill#
    # in holes, then find contours on thresholded image
    thresh = cv2.threshold(frameDelta, 1, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # loop over the contours
    for c in cnts:
        contours = cv2.contourArea(c)
        # only for debugging
        #if c_count >= conf["c_avg_count"]:
        #    print(str(timestamp) + " [INFO] Average contours on last " + str(conf["c_avg_count"]) + " images: " + str(c_avg / conf["c_avg_count"]))
        #    c_count = 0
        #    c_avg = 0
        #else:
        #    c_count += 1
        #    c_avg += int(contours)
        #print(str(timestamp) + " [DEBUG] c_count: " + str(c_count))
        # detect movement
        if contours >= conf["min_contours"]:
            print(str(timestamp) + " [INFO] Saving image...")
            # update the last uploaded timestamp and reset the motion counter
            path = "{base_path}/{ts}-{c}.jpg".format(base_path=conf["file_base_path"], ts=timestamp.strftime('%Y%m%d%H%M%S%f'), c=str(contours))
            # Check if image saving was successful
            if cv2.imwrite(path, frame):
                print(str(timestamp) + " [INFO] Image saved successful")
            else:
                print(str(timestamp) + " [ERROR] Image could not be saved")