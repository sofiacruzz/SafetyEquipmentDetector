import cv2
import torch
from .tracker import *
import numpy as np

model = torch.hub.load(".\yolov5", 'custom', path = '.\model.pt', source='local')
model.conf = 0.45



class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, image = self.video.read()
        detect = model(image)
        ret, jpeg = cv2.imencode('.jpg', np.squeeze(detect.render()))
        return jpeg.tobytes()


def gen(camera):

#    tracker = Tracker()
    while True:
#        frame = camera.detect()
        frame = camera.get_frame()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

#    while True:
#        frame = camera.get_frame()
#        yield (b'--frame\r\n'
#               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
