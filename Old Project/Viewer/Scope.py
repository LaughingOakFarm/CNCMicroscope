import serial


class Scope:
    def __init__(self):
        self.arduino = serial.Serial('/dev/tty.usbserial-3320', 115200, timeout=2)

    def sendNextCommand(self, command, pram=0):
        self.arduino.write((command + ":" + str(pram) + "\n").encode('utf-8'))
        while True:
            data = self.arduino.readline()[:-2]
            if data == "<Complete>".encode('utf-8'):
                return False
            if data == "<Navigate Complete>".encode('utf-8'):
                return True

    def sendCommand(self, command, pram=0):
        self.arduino.write((command + ":" + str(pram) + "\n").encode('utf-8'))
        while True:
            data = self.arduino.readline()[:-2]
            # print(data)
            if data == "<Complete>".encode('utf-8'):
                return True
