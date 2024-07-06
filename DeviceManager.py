from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import Qt, QEventLoop
from PyQt5.QtCore import QObject, QTimer, QThread, pyqtSignal, QRunnable, QThreadPool, pyqtSlot, QSettings, QRect, QRectF
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtQml import QQmlApplicationEngine

from time import sleep
import numpy as np

from VisionTool import *
from CameraDevice import *
from ProjectSetting import *
from VariableManager import *
from Device import *
from Tracking import *
from StationController import *
from MatrixTool import *
import traceback

class DeviceManager(QObject):
    def __init__(self):
        super().__init__()
        self.cameras = []
        self.robots = []
        self.robot_threads = []

    def load_available_devices(self):
        for port_info in QSerialPortInfo.availablePorts():
            print(port_info.portName())

    def print(self):
        pass

    def create_robot(self, para = None):
        if para == None:
            robot = Robot(COM='auto', baudrate=115200)
            # robotThread = QThread()
            # robot.moveToThread(robotThread)    
            # robotThread.start()
            self.robots.append(robot)
            # self.robot_threads.append(robotThread)

    def create_encoder(self):
        print('create encoder')

    def create_conveyor(self, type='x'):
        print('create conveyor ' + type)

        if type == 'station':
            self.conveyor_station = ConveyorStation(COM='auto', is_open= False)
            self.conveyorThread = QThread()
            self.conveyor_station.moveToThread(self.conveyorThread)
            self.conveyorThread.started.connect(self.conveyor_station.init_in_other_thread)
            self.conveyorThread.start()

    def create_camera(self, para = None):
        try:
            if para != None:
                camera_type = para['type']
                camera_id = para['id']
                camera_state = para['state']
                interval = para['interval']
                width = para['width']
            else:
                camera_type = 'basler'
                camera_id = len(self.cameras)
                camera_state = 'connect'
                interval = 500
                width = 800
            
            camera = CameraDevice(camera_type, camera_id, camera_state, interval)
            camera.scaleWidth = width
            self.cameras.append(camera)

            cameraThread = QThread(self)
            camera.moveToThread(cameraThread)
            cameraThread.started.connect(camera.run)
            cameraThread.start()

            # print('Opened camera')

        except Exception as e:
            # In ra lỗi
            print(e)
            traceback.print_exc()

    def create_pick_n_place_system(self):
        print("Creating p&p system")
        # self.create_robot()
        # self.create_robot()
        self.create_camera()
        self.create_conveyor('station')

    def get_info(self):
        for i, robot in enumerate(self.robots):
            robot:Robot
            print('robot {}: {}'.format(i, robot.port))

    def get_cmd(self, cmd: str):
        # print(cmd)
        # robot gcode
        paras = cmd.split()
        if len(paras) == 0:
            return

        try:
            if paras[0].find('info') > -1:
                self.get_info()

            if paras[0].find('robot') > -1:
                gcode = cmd[len(paras[0]) + 1:]
                id = int(paras[0][5:])
                robot:Robot = self.robots[id]
                robot.send_gcode(gcode)

            if paras[0].find('move') > -1:
                if paras[1].find('C') > -1:
                    if len(paras) == 4:
                        self.conveyor_station.move(paras[1], pos=float(paras[2]),vel=float(paras[3]))
                    else:
                        self.conveyor_station.move(paras[1], vel=float(paras[2]))
                if paras[1].find('robot') > -1:
                    pos = cmd[5 + len(paras[1]) + 1:]
                    id = int(paras[1][5:])
                    robot:Robot = self.robots[id]
                    if pos.find('home') > -1:
                        robot.go_home()
                    else:
                        dir = paras[2]
                        step = paras[3]
                        robot.move_step(dir, step)

            if paras[0].find('read') > -1:
                if paras[1].find('C') > -1:
                    # C3 -> 2
                    id = int(paras[1][1:]) - 1
                    print(self.conveyor_station.sub_encoders[id].read_position())

            if paras[0].find('eval') > -1:
                code = cmd[len(paras[0]) + 1:]
                eval(code)

        except:
            traceback.print_exc()
            print('wrong cmd')

instance = DeviceManager()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    device_manager = DeviceManager()
    device_manager.load_available_devices()
    device_manager.print()
    
    # device_manager.robots[0].send_gcode("G28")
    # device_manager.robots[0].send_gcode("Position")
    # device_manager.robots[0].send_gcode("G01 Z-830")
    # device_manager.robots[0].send_gcode("G01 X-200 F1000")

    # device_manager.robots[1].send_gcode("G28")
    # device_manager.robots[1].send_gcode("Position")
    # device_manager.robots[1].send_gcode("G01 Z-670")

    # instance.conveyor_station.set_encoder_invert('C3', True)
    # print(instance.conveyor_station.sub_encoders[2].read_position())
    # instance.conveyor_station.move(name='C3', pos = 100)
    # print(instance.conveyor_station.sub_encoders[2].read_position())
    # instance.conveyor_station.move(name='C3', pos = -100)

    # # # #Detecting
    # from VisionTool import *    
    # vision = VisionTool()
    # visionThread = QThread()
    # vision.moveToThread(visionThread)
    # visionThread.start()

    # instance.cameras[0].captured.connect(vision.open_calib_tool)

    # instance.create_pick_n_place_system()

    instance.create_conveyor('station')
    
    instance.conveyor_station.set_encoder_invert('C3', True)
    

    # Console

    import console

    cons = console.Command()
    consoleThread = QThread()
    cons.moveToThread(consoleThread)
    consoleThread.started.connect(cons.run)
    consoleThread.start()

    cons.inputSig.connect(instance.get_cmd)

    # Server

    import Server
    server = Server.SocketCommand('192.168.101.135', 8844)
    server.read_mess.connect(instance.get_cmd)

    app.exec_()