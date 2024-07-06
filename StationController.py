from signal import signal
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from time import sleep
from PyQt5.QtCore import QVariant
from PyQt5.QtCore import QObject, QSettings, QRect, QPointF, QPoint, QLineF

class StationController(QObject):

    def __init__(self):
        super().__init__()
        self.devices = []
        self.robots = []

    def add_device(self, type, device):
        if type.lower() == 'Robot'.lower():
            self.robots.append(device)

        self.devices.append(device)
