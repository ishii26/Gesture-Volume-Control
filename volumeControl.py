import cv2 as cv
import mediapipe as mp
import time
import numpy as np
import handTrackingModule as htm
import math
import os

# xxxxxxxxxxx DO NOT WORK ON MAC OS xxxxxxxxxxx

#from pycaw.pycaw import AudioUtilities
#from ctypes import cast, POINTER
#from comtypes import CLSCTX_ALL


wCam, hCam = 1280,720

cap = cv.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
cTime = 0

detector = htm.handDetector(detectionConfidence=0.8)

# Volume range
minVol = 0    # 0%
maxVol = 100  # 100%
minLen = 50   # min hand distance
maxLen = 300  # max hand distance
vol_percent = 80
vol_percent_bar = 0
def set_volume(vol_percent):
    vol = int(np.clip(vol_percent, 0, 100))
    os.system(f"osascript -e 'set volume output volume {vol}'")

#pycaw -- does not work on mac

#device = AudioUtilities.GetSpeakers()
#volume = device.EndpointVolume
#print(f"Audio output: {device.FriendlyName}")
#print(f"- Muted: {bool(volume.GetMute())}")
#print(f"- Volume level: {volume.GetMasterVolumeLevel()} dB")
#print(f"- Volume range: {volume.GetVolumeRange()[0]} dB - {volume.GetVolumeRange()[1]} dB")
#volume.SetMasterVolumeLevel(-20.0, None)

while True:
    success, img = cap.read()
    img = cv.flip(img, 1)

    detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    fingers = detector.fingersUp()

    #play msuic
    if fingers == [1, 0, 0, 0, 0]:
        os.system("osascript -e 'tell application \"Music\" to play'")
        cv.putText(img, 'Play', (100,150), cv.FONT_HERSHEY_SIMPLEX, 2, (255,0,255), 3)
        print("Play")
    
    #pause music
    elif fingers == [0, 1, 1, 1, 0]:
        os.system("osascript -e 'tell application \"Music\" to pause'")
        cv.putText(img, 'Pause', (100,150), cv.FONT_HERSHEY_SIMPLEX, 2, (255,0,255), 3)
        print("Pause")

    if len(lmList) != 0:
        #print(lmList[4], lmList[8])

        # coordinates of centre of thumb and index finger
        x1,y1 = lmList[4][1], lmList[4][2]
        x2,y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2 #centre of line between thumb and index finger

        cv.circle(img, (x1,y1),15,(255,0,0), -1) #circle for thumb
        cv.circle(img, (x2,y2),15,(255,0,0), -1) #circle for index finger

        cv.line(img, (x1,y1), (x2,y2), (255,0,0), 3) #line between thumb and index finger
        cv.circle(img, (cx,cy),15,(255,0,0), -1) #circle for centre of line

        lenLine = math.hypot(x2-x1, y2-y1) #length of the line
        #print(lenLine)

        vol_percent = np.interp(lenLine, [minLen, maxLen], [minVol, maxVol])
        vol_percent_bar = np.interp(lenLine, [50, 300], [400, 150])
        set_volume(vol_percent)
        print(vol_percent)

        if lenLine < minLen:
            cv.circle(img, (cx,cy),15,(0,255,0), -1)

    cv.rectangle(img, (50,150), (85,400), (255,0,0), 3)
    cv.rectangle(img, (50,int(vol_percent_bar)), (85,400), (255,0,0), -1)
    cv.putText(img,f'Volume: {int(vol_percent)}%', (40,450), cv.FONT_HERSHEY_COMPLEX, 1.0, (255,0,0), 3)

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv.putText(img, str(int(fps)), (40,50), cv.FONT_HERSHEY_COMPLEX, 1.0, (255,0,0), 3)

    cv.imshow("Image", img)

    cv.waitKey(1)