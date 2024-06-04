import cv2
import time
import numpy as np
from HandTrackingModule import handDetector
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Set the width and height of the webcam feed
wCam, hCam = 640, 480

# Open the webcam (camera index 0)
cap = cv2.VideoCapture(0)

# Set the width and height of the webcam feed
cap.set(3, wCam)
cap.set(4, hCam)

# Initialize the previous time variable for FPS calculation
pTime = 0

# Create an instance of the handDetector class with specified parameters
detector = handDetector(detectionCon=1)

# Get the audio output device (speakers) and its interface
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

# Get the volume range of the audio device
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

# Initialize variables for volume control
vol = 0
volBar = 400
volPer = 0

# Start an infinite loop to capture frames from the webcam
while True:
    # Read a frame from the webcam
    success, img = cap.read()

    # Find hands in the frame using the handDetector object
    img = detector.findHands(img)

    # Find the position of landmarks in the frame
    lmList = detector.findPosition(img, draw=False)

    # If hand landmarks are detected
    if len(lmList) != 0:
        # Calculate the coordinates of key landmarks
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        # Draw circles and lines to visualize hand landmarks
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        # Calculate the length between two landmarks (hand range)
        length = math.hypot(x2 - x1, y2 - y1)

        # Map the hand range to the volume range
        vol = np.interp(length, [50, 300], [minVol, maxVol])
        volBar = np.interp(length, [50, 300], [400, 150])
        volPer = np.interp(length, [50, 300], [0, 100])

        # Set the master volume level
        volume.SetMasterVolumeLevel(vol, None)

        # If hand range is less than 50, draw a green circle
        if length < 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

    # Draw volume bar and percentage text on the frame
    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    # Calculate and display FPS (frames per second)
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS:{int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    # Display the frame
    cv2.imshow("Img", img)
    cv2.waitKey(1)
