import serial
import time
import cv2
import numpy as np
from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

# arduino = serial.Serial('/dev/tty.usbserial-3340', 115200, timeout=2)
# time.sleep(2)


def grayout(gray, x, y, w, h):
    sub_img = gray[y:y+h, x:x+w]
    white_rect = np.ones(sub_img.shape, dtype=np.uint8) * 0
    res = cv2.addWeighted(sub_img, 0.75, white_rect, 0.25, 1.0)
    gray[y:y+h, x:x+w] = res
    return gray


# def send_command(command, pram=0):
#     arduino.write((command+":"+str(pram)+"\n").encode('utf-8'))
#     while True:
#         data = arduino.readline()[:-2]
#         if data == "<Complete>".encode('utf-8'):
#             return True


while cap.isOpened():
    ret, frame = cap.read()

    # if video finished or no Video Input
    if not ret:
        break

    gray = frame
    cv2.rectangle(gray, (150, 50), (650, 550), (255, 255, 255))

    gray = grayout(gray, 0, 0, 150, 600)
    gray = grayout(gray, 150, 0, 500, 50)
    gray = grayout(gray, 650, 0, 800, 600)
    gray = grayout(gray, 150, 550, 500, 600)

    cv2.imshow('Microscope Navigator', gray)

    # press 'Q' if you want to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
