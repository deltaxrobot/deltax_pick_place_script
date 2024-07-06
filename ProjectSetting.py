from ast import Global
from signal import signal
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from time import sleep
from PyQt5.QtCore import QVariant
from PyQt5.QtCore import QObject, QSettings, QRect, QPointF, QPoint


class ProjectSetting(QObject):
    def __init__(self):
        super().__init__()

    def Load(self, fileName):
        self.settings = QSettings(fileName, QSettings.Format.IniFormat)

    def PerspectivePoints(self):
        polyPoints = self.settings.value('Project/Robot0/ObjectDetector/ImageViewer/Quadangle', type=QtGui.QPolygonF)
        points = []
        for p in polyPoints:
            # print(p)
            points.append((int(p.x()), int(p.y())))
        
        return points

    def CropRectangle(self):
        rect = self.settings.value('Project/Robot0/ObjectDetector/ImageViewer/Area', type=QRect)
        return rect

    def CalibPoints(self):
        realPoint1 = self.settings.value('Project/Robot0/ObjectDetector/UnderCamerabPoint1', type=QPointF)
        realPoint2 = self.settings.value('Project/Robot0/ObjectDetector/UnderCamerabPoint2', type=QPointF)
        print('real points')
        print(realPoint1)
        print(realPoint2)
        imagePoint1 = self.settings.value('Project/Robot0/ObjectDetector/ImageViewer/Point1', type=QPoint)
        imagePoint2 = self.settings.value('Project/Robot0/ObjectDetector/ImageViewer/Point2', type=QPoint)
        print('image points')
        print(imagePoint1)
        print(imagePoint2)
        print('---')
        realPos = [(realPoint1.x(), realPoint1.y()), (realPoint2.x(), realPoint2.y())]
        imagePos = [(imagePoint1.x(), 0 - imagePoint1.y()), (imagePoint2.x(), 0 - imagePoint2.y())]

        return imagePos, realPos
    
    def FilterParameter(self):
        algorithm = self.settings.value('Project/Robot0/ObjectDetector/Parameter/algorithm', type=int)
        blurValue = self.settings.value('Project/Robot0/ObjectDetector/Parameter/blurV', type=int)
        thresValue = self.settings.value('Project/Robot0/ObjectDetector/Parameter/thresV', type=int)
        hsvValue = self.settings.value('Project/Robot0/ObjectDetector/Parameter/hsvV', type=list)
        invert = self.settings.value('Project/Robot0/ObjectDetector/Parameter/invert', type=bool)

        if blurValue % 2 == 0:
            blurValue = blurValue - 1

        return algorithm, thresValue, hsvValue, blurValue, invert

    def FilterObject(self):
        w = self.settings.value('Project/Robot0/ObjectDetector/ObjectWidth', type=int)
        l = self.settings.value('Project/Robot0/ObjectDetector/ObjectLength', type=int)
        min_w = self.settings.value('Project/Robot0/ObjectDetector/ImageMinObjectWidth', type=int)
        max_w = self.settings.value('Project/Robot0/ObjectDetector/ImageMaxObjectWidth', type=int)
        min_l = self.settings.value('Project/Robot0/ObjectDetector/ImageMinObjectLength', type=int)
        max_l = self.settings.value('Project/Robot0/ObjectDetector/ImageMaxObjectLength', type=int)

        return 0, w, max_w, min_w, l, max_l, min_l

    def EncoderPort(self):
        com = self.settings.value('Project/Robot0/ExternalDevice/Encoder/ComPort', type=str)

        return com

    def EncoderBaudrate(self):
        baudrate = self.settings.value('Project/Robot0/ExternalDevice/Encoder/Baudrate', type=int) 

        return baudrate  

    def conveyor_calib_points(self):
        p1 = self.settings.value('Project/Robot0/ObjectDetector/ConveyorPoint1', type=QPointF)
        p2 = self.settings.value('Project/Robot0/ObjectDetector/ConveyorPoint2', type=QPointF)

        return (p1, p2)