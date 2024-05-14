import threading
from flask import Response, request
from flask import Flask
from flask import render_template
from flask import redirect
import time
import cv2
from Digitizer import Digitizer
from MU1003 import MU1003
from Scope import Scope


app = Flask(__name__)
camera = MU1003()
scope = Scope()
digitizer = Digitizer(camera, scope)


@app.route('/')
def index():
    # noinspection PyUnresolvedReferences
    return render_template("index.html")


@app.route('/navigator', methods=['POST'])
def navigator():

    digitizerTread = threading.Thread(target=digitizer.run, args=(request.form.to_dict(),))
    digitizerTread.daemon = True
    digitizerTread.start()

    # noinspection PyUnresolvedReferences
    return render_template("active-navigator.html")


@app.route('/cancel', methods=['POST'])
def cancel():
    digitizer.stop()
    return redirect('/')


@app.route('/feed')
def video_feed():
    return Response(
        streamFrames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


def streamFrames():
    global camera

    lastFrame = 0

    while True:
        frameCount = camera.getFrameCount()
        if lastFrame == frameCount:
            continue

        currentFrame = camera.getCurrentFrame()
        if currentFrame is None:
            continue

        # if digitizer.activeReport and digitizer.showFrame is False:
        #     continue

        (flag, encodedImage) = cv2.imencode(".jpg", currentFrame)
        if not flag:
            continue

        yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + bytearray(
            encodedImage) + b'\r\n'

        lastFrame = frameCount
        time.sleep(0.001)

        if digitizer.activeReport:
            digitizer.showFrame = False


if __name__ == '__main__':
    camera.daemon = True
    camera.start()

    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
        threaded=True,
        use_reloader=False
    )
