import base64
import requests
import toupcam
import threading
from PIL import Image
import io

class CameraApp:
    def __init__(self, endpoint_url):
        self.hcam = None
        self.endpoint_url = endpoint_url

    def cameraCallback(self, nEvent, extra_context):
        if nEvent == toupcam.TOUPCAM_EVENT_IMAGE:
            self.handleImageEvent(nEvent)

    def handleImageEvent(self, nEvent):
        try:
            width, height = self.hcam.get_Size()
            bufsize = ((width * 24 + 31) // 32 * 4) * height
            buf = bytes(bufsize)
            self.hcam.PullImageV2(buf, 24, None)
            
            # Create an image from the buffer
            image = Image.frombytes('RGB', (width, height), buf)
            with io.BytesIO() as output:
                image.save(output, format="PNG")
                encoded_string = base64.b64encode(output.getvalue()).decode('utf-8')
                response = requests.post(self.endpoint_url, json={"image": encoded_string, "format": "png"})
            
            if response.status_code == 200:
                print("Image sent successfully")
            else:
                print(f"Failed to send image, status code: {response.status_code}")

        except toupcam.HRESULTException as ex:
            print("Pull image failed, hr=0x{:x}".format(ex.hr))

    def run(self):
        self.hcam = toupcam.Toupcam.Open(toupcam.Toupcam.EnumV2()[0].id)
        toupcam.Toupcam.put_eSize(self.hcam, 1) # 1792 x 1372, bufsize = 7375872
        if self.hcam:
            self.hcam.StartPullModeWithCallback(self.cameraCallback, self)
            threading.Event().wait()  # Keep the script running
        else:
            print("Failed to open camera")

if __name__ == '__main__':
    cam_app = CameraApp('http://localhost:8000/image')
    cam_app.run()
