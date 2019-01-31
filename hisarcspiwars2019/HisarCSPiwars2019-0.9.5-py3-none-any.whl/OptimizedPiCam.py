from picamera import PiCamera
from picamera.array import PiRGBArray
from threading import Thread

import cv2

class OptimizedPiCam:

    def __init__(self, resolution=(640, 480)):

        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.rawFrame = PiRGBArray(self.camera, size=self.camera.resolution)
        self.broadcast = self.camera.capture_continuous(self.rawFrame, format="bgr", use_video_port=True)

        self.currentFrame = None

    def startReadingData(self):

        Thread(target=self.updateData, args=()).start()
        return self

    def updateData(self):

        for f in self.broadcast:

            self.currentFrame = f.array
            self.rawFrame.truncate(0)

    def readData(self):

        return self.suAnkiKare

    def showFrame(self):
        Thread(target=self.updateShownFrame, args=()).start()

    def updateShownFrame(self):

        while True:
            cv2.imshow("frame", self.currentFrame)

            key = cv2.waitKey(1)

            if key == ord("q"):
                cv2.destroyAllWindows()
                break
