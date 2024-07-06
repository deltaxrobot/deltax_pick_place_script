from PyQt5.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot

import numpy as np
from pypylon import pylon
import cv2
import time
import traceback
from Device import Encoder
import VariableManager

class CameraDevice(QObject):
    startedCapture = pyqtSignal()
    captured = pyqtSignal(np.ndarray)
    stateChanged = pyqtSignal(bool)

    def __init__(self, type = 'basler', id = '0', state = 'open', interval = 500):
        super().__init__()
        self.encoder = None
        self.capture_pos = 0
        self.type = 'basler'
        self.id = id
        self.state = state
        self.interval = interval
        self.time_mesure = 0 
        self.is_open = False

    def set_encoder(self, encoder):
        self.encoder = encoder
    
    def run(self):        
        self.scaleWidth = 800
        VariableManager.instance.set("camera_state", False)
        self.OpenIndustrialCamera()
        # self.ContinuesCapture()
        

    def OpenIndustrialCamera(self):
        try:
            self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

            self.camera.RegisterConfiguration(pylon.SoftwareTriggerConfiguration(), pylon.RegistrationMode_ReplaceAll,
                                pylon.Cleanup_Delete)

            self.camera.TriggerSelector = "FrameStart"
            #self.camera.ExposureTime.SetValue(25000)
            # Grabing Continusely (video) with minimal delay
            self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly) 
            self.converter = pylon.ImageFormatConverter()

            # converting to opencv bgr format
            self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
            self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
            self.camera.ExposureTime.SetValue(30000)
            self.state = 'opened'
            self.is_open = True

            self.stateChanged.emit(self.is_open)
        except Exception as e:
            self.state = 'error'
            print(e)


    def ContinuesCapture(self, isStart = True, interval = 500):
        if isStart == True:
            self.timer.setInterval(interval)
            self.timer.start()
        else:
            self.timer.stop()

    def Capture(self):
        try:
            if self.camera.IsGrabbing() and self.state == 'opened' and self.type == 'basler':
                if self.camera.WaitForFrameTriggerReady(500, pylon.TimeoutHandling_ThrowException):
                    self.camera.ExecuteSoftwareTrigger()
                    self.startedCapture.emit()
                
                grabResult = self.camera.RetrieveResult(500, pylon.TimeoutHandling_ThrowException)

                if grabResult.GrabSucceeded():
                    if self.encoder != None:
                        self.capture_pos = 0#self.encoder.read_position()

                    # Access the image data
                    self.image = self.converter.Convert(grabResult)
                    self.mat = self.image.GetArray()

                    self.scaleHeight = self.mat.shape[0] * self.scaleWidth/self.mat.shape[1]
                    dim = (int(self.scaleWidth), int(self.scaleHeight))
                    self.resizeMat = cv2.resize(self.mat, dim, interpolation = cv2.INTER_NEAREST)
            
                    self.captured.emit(self.resizeMat)

                    return self.resizeMat
                    # print(type(self.resizeMat))
                    # cv2.imshow("image", self.resizeMat)
                    # cv2.waitKey(1)
            elif self.camera.IsOpen() == False:
                self.state = 'error'
                self.is_open = False
                self.stateChanged.emit(self.is_open)
                return None
        except Exception as e:
            # In ra lỗi
            print(e)
            traceback.print_exc()

