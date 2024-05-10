import toupcam
import cv2
from PyQt5.QtGui import QPixmap, QImage
import numpy as np
import time


class App:
    def __init__(self):
        self.hcam = None
        self.buf = None
        self.total = 0
        self.width = 0
        self.height = 0

# the vast majority of callbacks come from toupcam.dll/so/dylib internal threads
    @staticmethod
    def cameraCallback(nEvent, ctx):
        if nEvent == toupcam.TOUPCAM_EVENT_IMAGE:
            ctx.CameraCallback(nEvent)

    def CameraCallback(self, nEvent):
        if nEvent == toupcam.TOUPCAM_EVENT_IMAGE:
            try:
                self.hcam.PullImageV2(self.buf, 24, None)

                arr = np.ndarray(shape=(self.height, self.width, 3),
                                 buffer=self.buf,
                                 dtype=np.uint8)

                cv2.imwrite('test-' + str(self.total) + '.jpg', arr)

                self.total += 1
                print('pull image ok, total = {}'.format(self.total))
            except toupcam.HRESULTException:
                print('pull image failed')
        else:
            print('event callback: {}'.format(nEvent))

    def run(self):
        a = toupcam.Toupcam.EnumV2()
        if len(a) > 0:
            print('{}: flag = {:#x}, preview = {}, still = {}'.format(a[0].displayname, a[0].model.flag, a[0].model.preview, a[0].model.still))
            for r in a[0].model.res:
                print('\t = [{} x {}]'.format(r.width, r.height))
            self.hcam = toupcam.Toupcam.Open(a[0].id)

            toupcam.Toupcam.put_eSize(self.hcam, 0) # 1792 x 1372, bufsize = 7375872
            # toupcam.Toupcam.put_AutoExpoEnable(self.hcam, 100)
            toupcam.Toupcam.put_TempTint(self.hcam, 6325, 886)

            if self.hcam:
                try:
                    self.width, self.height = self.hcam.get_Size()
                    bufsize = ((self.width * 24 + 31) // 32 * 4) * self.height
                    print('image size: {} x {}, bufsize = {}'.format(self.width, self.height, bufsize))
                    self.buf = bytes(bufsize)
                    if self.buf:
                        try:
                            self.hcam.StartPullModeWithCallback(self.cameraCallback, self)
                        except toupcam.HRESULTException:
                            print('failed to start camera')
                    input('press ENTER to exit')
                finally:
                    self.hcam.Close()
                    self.hcam = None # type: toupcam.Toupcam
                    self.buf = None
            else:
                print('failed to open camera')
        else:
            print('no camera found')


if __name__ == '__main__':
    app = App()
    app.run()
