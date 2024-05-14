from flask import Response
from flask import Flask
from flask import render_template
from flask import request, redirect
import threading
import time
import cv2
import serial
import os
import json
from multiprocessing import Process, Queue
import numpy as np

outputFrame = None
liveViewTread = False
newFrame = False
captureNum = 0
reportTemplate = {
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
currentReport = reportTemplate
reportsPath = "/Volumes/Projects/CNC Microscope/Reports/"

lock = threading.Lock()
app = Flask(__name__)

cam = cv2.VideoCapture(1)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
time.sleep(2)
cam.set(cv2.CAP_PROP_EXPOSURE, 100)

arduino = serial.Serial('/dev/tty.usbserial-3320', 115200, timeout=2)


@app.route('/')
def index():
    # noinspection PyUnresolvedReferences
    if not liveViewTread:
        navigatorThread = threading.Thread(target=processLiveView)
        navigatorThread.daemon = True
        navigatorThread.start()

    # noinspection PyUnresolvedReferences
    return render_template("index.html")


@app.route('/navigator', methods=['POST'])
def navigator():
    global currentReport

    currentReport.update(request.form.to_dict())

    navigatorThread = threading.Thread(target=navigatorProcess)
    navigatorThread.daemon = True
    navigatorThread.start()

    # noinspection PyUnresolvedReferences
    return render_template("active-navigator.html")


@app.route('/cancel', methods=['POST'])
def cancel():
    global captureNum, currentReport, reportTemplate

    currentReport = reportTemplate
    sendCommand('H')
    captureNum = 0
    return redirect('/')


@app.route('/feed')
def video_feed():
    return Response(
        streamFrames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


def processLiveView():
    global liveViewTread, outputFrame, newFrame, lock, currentReport

    liveViewTread = True
    while currentReport['Status'] == '':
        time.sleep(0.025)
        with lock:
            r, outputFrame = cam.read()
            newFrame = True

    print('Exit Process Live View')


def navigatorProcess():
    global currentReport, outputFrame, lock, captureNum, newFrame

    # Setup
    currentReport['Status'] = 'running'
    currentReport['ReportPath'] = os.path.join(
        reportsPath,
        currentReport['ReportName']
    )

    createDir()
    createDir('AutoCapturesRaw')
    createDir('AutoCapturesCropped')
    createDir('ManualCaptures')
    createDir('AutoDetections')

    with open(os.path.join(
            currentReport['ReportPath'],
            'Report.json'
    ), 'w') as fp:
        json.dump(currentReport, fp)

    sendCommand('H')
    sendCommand('A', int(currentReport['ZoomLevel']))

    bestZ = pickBestFocus()
    print('Best Focus: ' + str(bestZ))

    sendCommand('H', 3)
    sendCommand('Z', int(bestZ))

    taskQueue = Queue()
    p = Process(target=saveImages, args=(taskQueue,))
    p.start()

    # Loop
    isDone = False
    while currentReport['Status'] == 'running' and not isDone:
        isDone = sendNextCommand('N')
        time.sleep(.075)
        r, frame = cam.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        newBlurValue = cv2.Laplacian(gray, cv2.CV_64F).var()
        print("Focus Value: " + str(newBlurValue))

        with lock:
            captureNum += 1
            outputFrame = frame.copy()
            newFrame = True

            y = 50
            x = 150
            w = h = 500
            cropped = outputFrame[y:y + h, x:x + w]
            filePath = os.path.join(
                currentReport['ReportPath'],
                'AutoCapturesCropped'
            ) + ("/capture-%d.jpg" % captureNum)
            taskQueue.put((cropped, filePath))

    taskQueue.put((None, ''))
    p.join()
    print("Report Complete")


def saveImages(taskQueue):
    while True:
        image, path = taskQueue.get()
        if image is None:
            break

        # WHITE BALANCE FRAME
        # result = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        # avg_a = np.average(result[:, :, 1])
        # avg_b = np.average(result[:, :, 2])
        # result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
        # result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)
        # result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)

        cv2.imwrite(path, image)


def createDir(subPath=''):
    global currentReport

    path = currentReport['ReportPath']
    if subPath:
        path = os.path.join(currentReport['ReportPath'], subPath)

    try:
        os.mkdir(path)
    except OSError as error:
        print(error)


def pickBestFocus():
    points = [5]
    maxZ = 625
    currentZ = 575
    highestFocus = 0
    bestZValue = 0
    totalZ = 0
    totalFocus = 0

    for p in points:
        sendCommand('H', 3)
        sendCommand('I', p)
        while True:
            currentZ += 1
            if currentZ > maxZ:
                print('Point ' + str(p) + " Best Focus: " + str(highestFocus) + ' @ Z: ' + str(bestZValue))
                totalZ += bestZValue
                totalFocus += highestFocus
                currentZ = 575
                highestFocus = 0
                bestZValue = 0
                break

            sendCommand('Z', currentZ)
            time.sleep(0.05)

            r, frame = cam.read()

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            newFocus = cv2.Laplacian(gray, cv2.CV_64F).var()

            if newFocus > highestFocus:
                bestZValue = currentZ
                highestFocus = newFocus

    print('Mean Focus: ' + str(int(totalFocus / 5)))
    return int(totalZ / 5)


def sendNextCommand(command, pram=0):
    arduino.write((command + ":" + str(pram) + "\n").encode('utf-8'))
    while True:
        data = arduino.readline()[:-2]
        # print(data)
        if data == "<Complete>".encode('utf-8'):
            return False
        if data == "<Navigate Complete>".encode('utf-8'):
            return True


def sendCommand(command, pram=0):
    arduino.write((command + ":" + str(pram) + "\n").encode('utf-8'))
    while True:
        data = arduino.readline()[:-2]
        # print(data)
        if data == "<Complete>".encode('utf-8'):
            return True


# def parseNewFrames():
#     global cam, outputFrame, lock, newFrame
#     while True:
#         r, frame = cam.read()
#         with lock:
#             # print("New Frame!")
#             outputFrame = frame.copy()
#             newFrame = True


def streamFrames():
    global outputFrame, lock, newFrame
    while True:
        if not newFrame:
            continue

        with lock:
            if outputFrame is None:
                continue

            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            if not flag:
                continue

            # print("Sent New Frame to Browser")
            yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + bytearray(
                encodedImage) + b'\r\n'
            newFrame = False


if __name__ == '__main__':
    # parserThread = threading.Thread(target=parseNewFrames)
    # parserThread.daemon = True
    # parserThread.start()

    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
        threaded=True,
        use_reloader=False
    )
