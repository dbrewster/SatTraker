import cv2
import threading
from typing import List
from abc import ABC, abstractmethod
import time
import imutils
import numpy as np

import Controller


class ImageOptions:
    cameraNum: int = 0
    flipHorizontal: bool = False
    flipVertical: bool = False
    rotate: int = 0
    captureRateInMS: int = 1.0/60.0
    exposure: float = -3


class Image:
    img = None
    captureTime = None
    timeSinceLastCapture = None


class ImageObserver(ABC):
    @abstractmethod
    def processingStarted(self) -> None:
        pass

    @abstractmethod
    def imageCaptured(self, img: Image) -> None:
        pass

    @abstractmethod
    def processingDone(self) -> None:
        pass


class ImageCapture:
    _observers: List[ImageObserver] = []

    def __init__(self, controller: Controller) -> None:
        super().__init__()
        self.cap = None
        self.controller = controller
        self.capturing = False
        self.currentExposure = 0
        self.currentGain = 0

    def startCaputure(self):
        self.capturing = True
        imagethread = threading.Thread(target=self.processImage)
        imagethread.start()

    def stopCapture(self):
        self.capturing = False

    def processImage(self):
        self.cap = cv2.VideoCapture(self.controller.get("camera"), cv2.CAP_DSHOW)
        cam = self.cap
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)
        print("CAP_PROP_FORMAT: " + str(cam.get(cv2.CAP_PROP_FORMAT)))
        print("CAP_PROP_MODE: " + str(cam.get(cv2.CAP_PROP_MODE)))
        print("CAP_PROP_FPS: " + str(cam.get(cv2.CAP_PROP_FPS)))
        print("CAP_PROP_CONTRAST: " + str(cam.get(cv2.CAP_PROP_CONTRAST)))
        print("CAP_PROP_GAIN: " + str(cam.get(cv2.CAP_PROP_GAIN)))
        print("CAP_PROP_FRAME_WIDTH: " + str(cam.get(cv2.CAP_PROP_FRAME_WIDTH)))
        print("CAP_PROP_FRAME_HEIGHT: " + str(int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))))
        print("CAP_PROP_POS_FRAMES: " + str(cam.get(cv2.CAP_PROP_POS_FRAMES)))
        print("CAP_PROP_EXPOSURE: " + str(cam.get(cv2.CAP_PROP_EXPOSURE)))
        
        for observer in self._observers:
            observer.processingStarted()

        lastCapture = 0
        while self.capturing:
            ret, img = self.cap.read()
            exposure = self.controller.get("exposure")
            if exposure != self.currentExposure:
                if exposure > 0:
                    str_val = str(pow(2, exposure))
                else:
                    str_val = "1/" + str(pow(2, -exposure))
                print("Setting to exposure " + str_val)
                self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
                self.cap.set(cv2.CAP_PROP_EXPOSURE, exposure)
                self.currentExposure = exposure

            gain = self.controller.get("gain")
            if gain != self.currentGain:
                print("Setting to gain " + str(gain))
                self.cap.set(cv2.CAP_PROP_GAIN, gain)
                self.currentGain = gain

            if ret:
                if self.controller.get("flipVertical") and self.controller.get("flipHorizontal"):
                    img = cv2.flip(img, 0)
                elif self.controller.get("flipHorizontal"):
                    img = cv2.flip(img, 1)
                elif self.controller.get("flipVertical"):
                    img = cv2.flip(img, -1)
                img = imutils.rotate(img, self.controller.get("rotate"))
                currentTime = time.time()
                timeSinceLastCapture = currentTime - lastCapture
                lastCapture = currentTime
                image = Image()
                image.img = img
                is_all_zero = np.all((img == 0))
                if not is_all_zero:
                    image.captureTime = currentTime
                    image.timeSinceLastCapture = timeSinceLastCapture
                    for observer in self._observers:
                        observer.imageCaptured(image)
            # delayTime = float(self.options.captureRateInMS) / 1000.0
            # time.sleep(delayTime)  # sleep 20 ms

        for observer in self._observers:
            observer.processingDone()
        self.cap.release()

    def addObserver(self, param):
        self._observers.append(param)
