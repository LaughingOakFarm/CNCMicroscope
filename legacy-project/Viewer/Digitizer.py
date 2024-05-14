import time
import os
import json
from multiprocessing import Process, Queue
from MU1003 import MU1003
import cv2


class Digitizer:
    def __init__(self, camera, scope):
        self.camera = camera  # type: MU1003
        self.scope = scope
        self.captureNum = 0
        self.stopReport = False
        self.activeReport = False
        self.showFrame = False
        self.reportTemplate = {
            'Status': '',
            'ReportName': '',
            'NavigationMode': '',
            'ZoomLevel': '',
            'FocusSystem': '',
            'DetectionModel': '',
            'SlideEdgeModel': '',
            'NavigationSpeed': '',
            'ReportPath': ''
        }
        self.currentReport = self.reportTemplate
        self.reportsPath = "/Volumes/Projects/CNC Microscope/Reports/"

    def run(self, reportData):
        self.captureNum = 0
        self.currentReport = self.reportTemplate
        self.stopReport = False
        self.currentReport.update(reportData)

        # Setup
        self.currentReport['Status'] = 'running'
        self.currentReport['ReportPath'] = os.path.join(
            self.reportsPath,
            self.currentReport['ReportName']
        )

        self.createDir()
        self.createDir('AutoCapturesRaw')
        self.createDir('AutoCapturesCropped')
        self.createDir('ManualCaptures')
        self.createDir('AutoDetections')

        with open(os.path.join(
                self.currentReport['ReportPath'],
                'Report.json'
        ), 'w') as fp:
            json.dump(self.currentReport, fp)

        self.scope.sendCommand('H')
        self.scope.sendCommand('A', int(self.currentReport['ZoomLevel']))
        self.pickBestFocus()

        taskQueue = Queue()
        p = Process(target=saveImages, args=(taskQueue,))
        p.start()

        # Loop
        isDone = False
        self.activeReport = True
        while self.currentReport['Status'] == 'running' and not isDone:
            if self.stopReport:
                break

            isDone = self.scope.sendNextCommand('N')
            time.sleep(.1)
            frame = self.camera.getCurrentFrame()
            self.showFrame = True
            if frame is None:
                # The camera is updating the current frame
                continue

            # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # newBlurValue = cv2.Laplacian(gray, cv2.CV_64F).var()
            # print("Focus Value: " + str(newBlurValue))

            self.captureNum += 1

            y = 100
            x = 100
            w = 1592
            h = 1172
            cropped = frame[y:y + h, x:x + w]
            filePath = os.path.join(
                self.currentReport['ReportPath'],
                'AutoCapturesCropped'
            ) + ("/capture-%d.jpg" % self.captureNum)
            taskQueue.put((cropped, filePath))

        taskQueue.put((None, ''))
        p.join()
        self.activeReport = False
        print("Report Complete")

    def createDir(self, subPath=''):
        path = self.currentReport['ReportPath']
        if subPath:
            path = os.path.join(self.currentReport['ReportPath'], subPath)

        try:
            os.mkdir(path)
        except OSError as error:
            print(error)

    def pickBestFocus(self):
        points = [1, 3, 5, 7, 9]
        for p in points:
            self.scope.sendCommand('I', p)
            time.sleep(5)
            self.scope.sendCommand('H')

    def stop(self):
        self.stopReport = True
        self.activeReport = False

def saveImages(taskQueue):
    while True:
        image, path = taskQueue.get()
        if image is None:
            break

        cv2.imwrite(path, image)
