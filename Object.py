from signal import signal
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from time import sleep
from PyQt5.QtCore import QVariant
from PyQt5.QtCore import QObject, QSettings, QRect, QPointF, QPoint, QLineF
import time

class Object(QObject):
    def __init__(self):
        super().__init__()
        self.pos = dict()

    def set_info(self, parent, id, x, y, w, h, a):
        self.pos[parent] = { "id": id, "x": x, "y": y, "w":w, "h":h, "a":a}



    