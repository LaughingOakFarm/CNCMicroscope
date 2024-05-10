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

outputFrame = None
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

arduino = serial.Serial('/dev/tty.usbserial-3320', 115200, timeout=2)
time.sleep(1.0)


@app.route('/')
def index():
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
    currentReport['Status'] = 'cancelled'
    sendCommand('H')
    return redirect('/')


@app.route('/feed')
def video_feed():
    return Response(
        streamFeed(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


def navigatorProcess():
    global currentReport, outputFrame, lock, captureNum

    # Setup
    currentReport['Status'] = 'running'
    currentReport['ReportPath'] = os.path.join(reportsPath, currentReport['ReportName'])
    try:
        os.mkdir(currentReport['ReportPath'])
    except OSError as error:
        print(error)

    try:
        os.mkdir(os.path.join(currentReport['ReportPath'], 'AutoCapturesRaw'))
    except OSError as error:
        print(error)

    try:
        os.mkdir(os.path.join(currentReport['ReportPath'], 'AutoCapturesCropped'))
    except OSError as error:
        print(error)

    # try:
    #     os.mkdir(os.path.join(currentReport['ReportPath'], 'ManualCaptures'))
    # except OSError as error:
    #     print(error)
    #
    # try:
    #     os.mkdir(os.path.join(currentReport['ReportPath'], 'AutoDetections'))
    # except OSError as error:
    #     print(error)

    with open(os.path.join(currentReport['ReportPath'], 'Report.json'), 'w') as fp:
        json.dump(currentReport, fp)

    sendCommand('H')
    sendCommand('A', int(currentReport['ZoomLevel']))

    bestZ = pickBestFocus()
    print("Best Focus: " + str(bestZ))
    # bestZ = 596

    sendCommand('H')
    sendCommand('Z', bestZ)

    # Loop
    isDone = False
    while currentReport['Status'] == 'running' and not isDone:
        isDone = sendNextCommand('N')
        time.sleep(.3)
        with lock:
            captureNum += 1
            if outputFrame is None:
                continue

            y = 50
            x = 150
            w = h = 500
            cropped = outputFrame[y:y+h, x:x+w]
            # cv2.imwrite(os.path.join(
            #     currentReport['ReportPath'],
            #     'AutoCapturesRaw'
            # ) + "/capture-%d.jpg" % captureNum, outputFrame)
            cv2.imwrite(os.path.join(
                currentReport['ReportPath'],
                'AutoCapturesCropped'
            ) + "/capture-%d.jpg" % captureNum, cropped)

    print("Report Complete")


def pickBestFocus():
    global outputFrame, lock

    sendCommand('X', 1125)
    sendCommand('Y', 400)

    highestValue = 0
    bestZValue = 0
    maxZ = 625
    currentZ = 550
    # downCount = 0

    while True:
        with lock:
            currentZ += 1
            if currentZ > maxZ:
                break

            sendCommand('Z', currentZ)

            gray = cv2.cvtColor(outputFrame, cv2.COLOR_BGR2GRAY)
            newBlurValue = cv2.Laplacian(gray, cv2.CV_64F).var()
            print("Z: " + str(currentZ) + " - " + str(newBlurValue))

            if newBlurValue > highestValue:
                bestZValue = currentZ
                highestValue = newBlurValue
                # downCount = 0
            # else:
            #     downCount += 1
            #
            # if downCount > 15:
            #     break

        time.sleep(.3)

    return bestZValue


def sendNextCommand(command, pram=0):
    arduino.write((command + ":" + str(pram) + "\n").encode('utf-8'))
    while True:
        data = arduino.readline()[:-2]
        print(data)
        if data == "<Complete>".encode('utf-8'):
            return False
        if data == "<Navigate Complete>".encode('utf-8'):
            return True


def sendCommand(command, pram=0):
    arduino.write((command + ":" + str(pram) + "\n").encode('utf-8'))
    while True:
        data = arduino.readline()[:-2]
        print(data)
        if data == "<Complete>".encode('utf-8'):
            return True


def parseNewFrames():
    global cam, outputFrame, lock, newFrame
    while True:
        r, frame = cam.read()
        with lock:
            # print("New Frame!")
            outputFrame = frame.copy()
            newFrame = True


def streamFeed():
    global outputFrame, lock, newFrame
    while True:
        with lock:
            if not newFrame:
                continue

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
    parserThread = threading.Thread(target=parseNewFrames)
    parserThread.daemon = True
    parserThread.start()

    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
        threaded=True,
        use_reloader=False
    )
