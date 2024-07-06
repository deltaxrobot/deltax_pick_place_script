from ast import Global
from signal import signal
import sys

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QObject, QTimer, QThread, pyqtSignal, QRunnable, QThreadPool, pyqtSlot, QSettings, QRect, QRectF, QLineF, QMutex
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtQml import QQmlApplicationEngine

from time import sleep
import numpy as np
import keyboard
from pypylon import pylon
import cv2
import os
import json
import PnPProject
import VisionTool
import Server
import Test
import Pick
import CameraDevice
import DeviceManager
import Tracking
import VariableManager
import ConveyorStation
import ui.user_gui.qmlgui

import glob, os, importlib

# main
if __name__ == "__main__":

    app = QApplication(sys.argv)

    VariableManager.instance.load("settings.ini")

    qmlui = ui.user_gui.qmlgui.QmlGui()

    prediction_result = "Orienty"
    
    #These are the names of the plastic bottle types that you have labeled in the imiu software
    prediction_result_type_list_str = ['Nhom', 'Nhua', 'Giay', 'Xop']
    #prediction_result = "Orienty"

    # camera
    camera = CameraDevice.CameraDevice()
    cameraThread = QThread()
    camera.moveToThread(cameraThread)
    cameraThread.started.connect(camera.run)
    camera.stateChanged.connect(qmlui.setCameraState)
    cameraThread.start()
    timer = QTimer()
    timer.timeout.connect(camera.Capture)
    timer.setInterval(800)
    timer.start()

    # aix server
    server = Server.ImageServer('127.0.0.1', 5555, prediction_result)
    server.obj_type_list = prediction_result_type_list_str
    serverThread = QThread()
    server.moveToThread(serverThread)
    serverThread.started.connect(server.open)    
    server.stateChanged.connect(qmlui.setServerState)
    serverThread.start()

    # conveyor 1
    port_name = "COM6"
    com_thread = ConveyorStation.ComPortReaderWriter(port_name)
    com_thread.con_name = "con1"
    com_thread.device_type = "new_xconveyor"
    com_thread.stateChanged.connect(qmlui.setConveyor1State)
    com_thread.speedChanged.connect(qmlui.setConveyor1SpeedText)
    com_thread.start()

    # conveyor 2
    port_name = "COM8"
    con2_thread = ConveyorStation.ComPortReaderWriter(port_name)
    con2_thread.con_name = "con2"
    con2_thread.device_type = "new_xencoder"
    con2_thread.stateChanged.connect(qmlui.setConveyor2State)
    con2_thread.speedChanged.connect(qmlui.setConveyor2SpeedText)
    con2_thread.start()

    # wrap and crop
    vision = VisionTool.VisionTool()        
    visionThread = QThread()
    vision.moveToThread(visionThread)    
    camera.captured.connect(vision.detect)
    vision.detect_algorithm = 'internal'
    vision.result_type = prediction_result
    #vision.detect_algorithm = 'internal'
    vision.sending_image_type = 'calib'
    vision.detect_image_ready.connect(server.send_image)
    server.got_objects.connect(vision.get_objs_from_external)
    vision.display_image_ready.connect(qmlui.setImageLabel)
    visionThread.start()

    # tracking
    tracking1 = Tracking.TrackingManager()
    trackingThread1 = QThread()
    tracking1.moveToThread(trackingThread1)
    
    tracking1.set_clear_limit(1100)
    tracking1.display_obj_request.connect(qmlui.setObjectLabel)
    tracking1.got_con_speed.connect(qmlui.setEncoderSpeedText)
    tracking1.got_con_position.connect(qmlui.setEncoderPositionText)
    tracking1.position_request.connect(com_thread.read_position, Qt.QueuedConnection)
    tracking1.is_encoder_reversed = False

    vision.detected.connect(tracking1.add_new_objects, Qt.QueuedConnection)
    camera.startedCapture.connect(tracking1.capture_moment)
    com_thread.got_position.connect(tracking1.update_conveyor_position, Qt.QueuedConnection)
    
    trackingThread1.start()

    # -------- Script --------
    
    script1 = Pick.Pick1()
    script1.com_port = "COM3"
    script1.id = 1
    script1.tracking_manager = tracking1
    script1Thread = QThread()
    script1.moveToThread(script1Thread)
    script1Thread.started.connect(script1.run)
    script1.robotStateChanged.connect(qmlui.setRobot1State)
    script1.fiber1Changed.connect(qmlui.setBox1FiberSensor)
    #script1.pickedRequet.connect(qmlui.setBox1NumberText)
    script1.boxCounterRequest.connect(qmlui.setBoxCounterText)
    script1.conveyor_move_speed_request.connect(con2_thread.moveSpeed)
    script1.conveyor_move_speed_time_request.connect(con2_thread.moveSpeedTime)
    script1.stationStopRequest.connect(qmlui.stationStopFromRobot)
    script1Thread.start()

    script2 = Pick.Pick1()
    script2.enable = False
    script2.com_port = "COM20"
    script2.id = 2
    script2.tracking_manager = tracking1
    script2Thread = QThread()
    script2.moveToThread(script2Thread)
    script2Thread.started.connect(script2.run)
    script2.robotStateChanged.connect(qmlui.setRobot2State)
    script2.fiber1Changed.connect(qmlui.setBox2FiberSensor)
    #script2.pickedRequet.connect(qmlui.setBox2NumberText)
    #script2.boxCounterRequest.connect(qmlui.setBoxCounterText)
    script2.conveyor_move_speed_request.connect(con2_thread.moveSpeed)
    script2.conveyor_move_speed_time_request.connect(con2_thread.moveSpeedTime)
    script2.stationStopRequest.connect(qmlui.stationStopFromRobot)
    script2Thread.start()


    qmlui.imageCalibRequest.connect(vision.getCalibImages)
    vision.calib_image1_ready.connect(qmlui.setCalibImg1)
    vision.calib_image2_ready.connect(qmlui.setCalibImg2)
    vision.calib_image3_ready.connect(qmlui.setCalibImg3)
    vision.calib_image4_ready.connect(qmlui.setCalibImg4)

    qmlui.robotCalibStateRequest.connect(script1.setCalibState)
    qmlui.robotCalibStateRequest.connect(script2.setCalibState)

    qmlui.robotRunStateRequest.connect(script1.setRunState)
    #qmlui.robotRunStateRequest.connect(script2.setRunState)

    qmlui.robot1PositionRequest.connect(script1.getPosition)
    qmlui.robot2PositionRequest.connect(script2.getPosition)

    script1.received_position.connect(qmlui.got_position_form_robot)
    script2.received_position.connect(qmlui.got_position_form_robot)

    qmlui.robot1controler.moveRequest.connect(script1.sendGcode)
    qmlui.robot2controler.moveRequest.connect(script2.sendGcode)

    qmlui.conveyor1controler.moveSpeedClicked.connect(com_thread.moveSpeed)
    qmlui.conveyor1controler.movePositionClicked.connect(com_thread.movePosition)

    qmlui.conveyor2controler.moveSpeedClicked.connect(con2_thread.moveSpeed)
    qmlui.conveyor2controler.movePositionClicked.connect(con2_thread.movePosition)

    qmlui.saveCalibRequest.connect(vision.calculateAndSaveCalibValue)
    qmlui.saveCalibRequest.connect(script1.variable_init)
    qmlui.saveCalibRequest.connect(script2.variable_init)
    qmlui.saveCalibRequest.connect(tracking1.loadRobotPickingZone)

    qmlui.saveProfileRequest.connect(script1.variable_init)
    qmlui.saveProfileRequest.connect(script2.variable_init)

    qmlui.conMoveSpeedRequest.connect(com_thread.moveSpeed)
    qmlui.con2MoveSpeedRequest.connect(con2_thread.moveSpeed)

    qmlui.started.connect(tracking1.start)
    qmlui.stopped.connect(tracking1.stop)

    qmlui.started.connect(script1.start)
    # qmlui.stopped.connect(script1.stop)

    qmlui.started.connect(script2.start)
    # qmlui.stopped.connect(script2.stop)

    app.exec_()