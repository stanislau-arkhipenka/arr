import cv2
import urllib.request
import numpy as np
import threading
import logging

logger = logging.getLogger(__name__)

class VideoStream:

    def __init__(self, addr: str): # 'http://192.168.0.6:9999/stream'
        self.addr = addr
        self.enabled = False
        self._frame = b''


    def _receive_video(self):
        stream = urllib.request.urlopen(self.addr)
        bin_data = b''
        timeout = 1
        while self.enabled:
            bin_data += stream.read(1024)
            a = bin_data.find(b'\xff\xd8')
            b = bin_data.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = bin_data[a:b+2]
                bin_data = bin_data[b+2:]
                img_data = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                self._frame = cv2.imencode('.ppm', img_data)[1].tobytes()

    def enable(self):
        if self.enabled:
            logger.warning("Unable to enable video stream. Already enabled")
        else:
            self.video_thread = threading.Thread(target=self._receive_video)
            self.video_thread.start()
            self.enabled = True  

    def disable(self):
        if not self.enabled:
            logger.warning("Unable to disable video stream. Already disabled")
        else:
            self.enabled = False
            self.video_thread.join() # TODO what if it hangs? 
        
    def get_frame(self):
        return self._frame
        
