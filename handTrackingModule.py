import cv2 as cv
import mediapipe as mp
import time


class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionConfidence=0.5, trackingConfidence=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionConfidence = detectionConfidence
        self.trackingConfidence = trackingConfidence

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionConfidence,
            min_tracking_confidence=self.trackingConfidence
            )
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw = True):
        imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        #print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for handLandmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLandmarks, self.mpHands.HAND_CONNECTIONS)      
        return img
    
    def findPosition(self, img, handNo = 0, draw = True):
        
        self.lmList = []
        
        if self.results.multi_hand_landmarks:
            for handLandmarks in self.results.multi_hand_landmarks:              
                for id, lm in enumerate(handLandmarks.landmark):
                                #print(id, lm)
                                h, w, c = img.shape
                                cx, cy = int(lm.x*w), int(lm.y*h)
                                #print(id, cx, cy)
                                self.lmList.append([id, cx, cy])
                                if draw:
                                    if id ==0 or id ==4 or id == 8 or id == 12 or id == 16 or id == 20 :
                                        cv.circle(img, (cx,cy), 25, (255,0,255), -1)
        return self.lmList
    
    def fingersUp(self):
        if not hasattr(self, 'lmList') or len(self.lmList) < 21:
            return []  # Return empty list if landmarks are incomplete

        fingers = []
        tips = [8, 12, 16, 20]

        #thumb
        if self.lmList[4][1] < self.lmList[3][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        #fingers
        for tip in tips:
            if self.lmList[tip][2] < self.lmList[tip - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

def main():
    pTime = 0
    cTime = 0

    cap = cv.VideoCapture(0)
    detector = handDetector()

    while True:
        success, img = cap.read()
        img = cv.flip(img, 1)

        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        if len(lmList) != 0:    
            print(lmList[4]) # printing for index 0 ie palm 

        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime

        cv.putText(img, str(int(fps)), (10,70), cv.FONT_HERSHEY_COMPLEX, 1.0, (255,0,255), 3)

        cv.imshow('Image', img)
        cv.waitKey(1)



if __name__ == "__main__":
    main()








