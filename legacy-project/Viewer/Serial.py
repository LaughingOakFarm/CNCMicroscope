import serial
import time
import cv2

arduino = serial.Serial('/dev/tty.usbserial-3340', 115200, timeout=2)
time.sleep(2)


def sendCommand(command, pram=0):
    arduino.write((command+":"+str(pram)+"\n").encode('utf-8'))
    while True:
        data = arduino.readline()[:-2]
        if data == "<Complete>".encode('utf-8'):
            return True


sendCommand('H')
# load the image, convert it to grayscale, and compute the
# focus measure of the image using the Variance of Laplacian
# method
image = cv2.imread(imagePath)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
fm = variance_of_laplacian(gray)
text = "Not Blurry"
# if the focus measure is less than the supplied threshold,
# then the image should be considered "blurry"
if fm < args["threshold"]:
    text = "Blurry"
# show the image
cv2.putText(image, "{}: {:.2f}".format(text, fm), (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
cv2.imshow("Image", image)
key = cv2.waitKey(0)
