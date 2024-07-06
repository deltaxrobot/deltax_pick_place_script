from PyQt5.QtCore import QEventLoop
from PyQt5.QtCore import QObject, QTimer, QThread, QLineF, QPointF
from PyQt5.QtWidgets import QApplication
import sys

from time import sleep
import MatrixTool
import traceback
from ScriptTemplate import Script
import Device

class Script1(QObject):
    def __init__(self):
        super().__init__()

    def run(self):
        self.robot = Device.Robot('COM25', 115200)
        self.z_safe = -905
        self.z_working = -924 

        self.robot.send_gcode('G28')
        self.robot.send_gcode('G01 Z{}'.format(self.z_safe))
        while True:
            self.robot.send_gcode('G01 Z{}'.format(self.z_safe + 20))
            self.robot.send_gcode('G01 Z{}'.format(self.z_safe))

class Script2(QObject):
    def __init__(self):
        super().__init__()

    def run(self):
        self.robot = Device.Robot('COM28', 115200)
        self.z_safe = -665
        self.z_working = -685
        self.u_pick = -4

        self.robot.send_gcode('G28')
        self.robot.send_gcode('G01 Z{} U{}'.format(self.z_safe, self.u_pick))
        while True:
            self.robot.send_gcode('G01 Z{}'.format(self.z_safe + 20))
            self.robot.send_gcode('G01 Z{}'.format(self.z_safe))