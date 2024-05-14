import threading
import time

import cv2

import toupcam
import numpy as np


class MU1003 (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.camera = None
        self.buffer = None
        self.width = 0
        self.height = 0
        self.updatingFrame = False
        self.currentFrame = None
        self.frameCount = 0
        self.fps = 0

    @staticmethod
    def cameraCallback(nEvent, ctx):
        if nEvent == toupcam.TOUPCAM_EVENT_IMAGE:
            ctx.CameraCallback()

    def CameraCallback(self):
        try:
            self.updatingFrame = True
            self.camera.PullImageV2(self.buffer, 24, None)
            self.currentFrame = np.ndarray(
                shape=(self.height, self.width, 3),
                buffer=self.buffer,
                dtype=np.uint8
            )
            self.currentFrame = cv2.cvtColor(self.currentFrame, cv2.COLOR_BGR2RGB)

            # gray = cv2.cvtColor(self.currentFrame, cv2.COLOR_BGR2GRAY)
            # y = 300
            # x = 400
            # w = 992
            # h = 772
            # gray = gray[y:y + h, x:x + w]
            # newBlurValue = cv2.Laplacian(gray, cv2.CV_64F).var()
            # print("Focus Value: " + str(newBlurValue))

            self.updatingFrame = False
            self.frameCount += 1
            self.fps += 1

        except toupcam.HRESULTException:
            print('pull image failed')

    def getCurrentFrame(self):
        if self.updatingFrame is True:
            return None

        return self.currentFrame

    def run(self):
        a = toupcam.Toupcam.EnumV2()
        if len(a) > 0:
            print('Connecting Camera')
            self.camera = toupcam.Toupcam.Open(a[0].id)

            # toupcam.Toupcam.put_eSize(self.camera, 1)  # 1792 x 1372, buffer size = 7375872
            # toupcam.Toupcam.put_AutoExpoEnable(self.camera, 100)
            # toupcam.Toupcam.put_TempTint(self.camera, 6325, 886)
            # toupcam.Toupcam.put_Hue(self.camera, 0)

            if self.camera:
                try:
                    self.width, self.height = self.camera.get_Size()
                    bufferSize = ((self.width * 24 + 31) // 32 * 4) * self.height
                    self.buffer = bytes(bufferSize)
                    if self.buffer:
                        try:
                            self.camera.StartPullModeWithCallback(self.cameraCallback, self)
                        except toupcam.HRESULTException:
                            print('failed to start camera')
                    while True:
                        # x = range(-180, 180)
                        # for n in x:
                        #     print(n)
                        #     toupcam.Toupcam.put_Hue(self.camera, n)
                        time.sleep(1)
                        # print('FPS: '+str(self.fps))
                        self.fps = 0

                finally:
                    self.camera.Close()
                    self.camera = None
                    self.buffer = None
            else:
                print('failed to open camera')
        else:
            print('no camera found')

    def getFrameCount(self):
        return self.frameCount
