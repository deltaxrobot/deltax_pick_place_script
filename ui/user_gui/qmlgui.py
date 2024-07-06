# This Python file uses the following encoding: utf-8
from PyQt5 import QtCore
from PyQt5.QtQml import QQmlApplicationEngine
from pathlib import Path
from PyQt5.QtCore import pyqtSignal, QObject, QSettings, QPointF, QVariant
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtQuick import QQuickImageProvider
import cv2
import time
import sys
import numpy as np
sys.path.append("...")
import VariableManager

class CVImageProvider(QQuickImageProvider):
    def __init__(self):
        super().__init__(QQuickImageProvider.Pixmap)

    def requestPixmap(self, id, size):
        img = cv2.cvtColor(self.current_detect_img , cv2.COLOR_BGR2RGB)

        # cv2.imshow('req', img)

        h, w, c = img.shape
        bytes_per_line = c * w
        qimg = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)

#        p = qimg.scaled(400, 300, Qt.KeepAspectRatio)

        return QPixmap.fromImage(qimg), qimg.size()

    def setNewImage(self, frame):
        self.current_detect_img = frame


class QmlGui(QtCore.QObject):
    started = pyqtSignal()
    stopped = pyqtSignal()
    imageCalibRequest = pyqtSignal()

    robotCalibStateRequest = pyqtSignal()
    robotRunStateRequest = pyqtSignal()

    robot1PositionRequest = pyqtSignal()
    robot2PositionRequest = pyqtSignal()

    robot1MoveRequest = pyqtSignal(str)
    robot2MoveRequest = pyqtSignal(str)

    saveCalibRequest = pyqtSignal()
    saveProfileRequest = pyqtSignal()

    conMoveSpeedRequest = pyqtSignal(float)
    con2MoveSpeedRequest = pyqtSignal(float)

    def __init__(self):
        super().__init__()

        self.engine = QQmlApplicationEngine()

        masterPass = str(VariableManager.instance.get("masterPass", "123456"))
        self.engine.rootContext().setContextProperty("masterPass", masterPass)
        #print(masterPass)

        self.image_provider = CVImageProvider()

        self.image_provider1 = CVImageProvider()
        self.image_provider2 = CVImageProvider()
        self.image_provider3 = CVImageProvider()
        self.image_provider4 = CVImageProvider()

        qml_file = Path(__file__).resolve().parent / "main.qml"
        self.engine.load(str(qml_file))

        self.engine.addImageProvider('src_detect_image', self.image_provider)
        self.engine.addImageProvider('src_calib_image1', self.image_provider1)
        self.engine.addImageProvider('src_calib_image2', self.image_provider2)
        self.engine.addImageProvider('src_calib_image3', self.image_provider3)
        self.engine.addImageProvider('src_calib_image4', self.image_provider4)

        self.loadQmlChild()
        self.measure = time.time()

        self.waiting_read_point_index = 0
        self.box_counter = 0
        self.is_calibing = False

        self.list_profiles = []

        VariableManager.instance.set("is_running", False)
        
        self.is_update_image = False

    def loadQmlChild(self):
        child_quick_item = self.engine.rootObjects()

        # station state
        self.robot1State = child_quick_item[0].findChild(QObject, 'robot1State')
        self.robot2State = child_quick_item[0].findChild(QObject, 'robot2State')
        self.cameraState = child_quick_item[0].findChild(QObject, 'cameraState')
        self.conveyor1State = child_quick_item[0].findChild(QObject, 'conveyor1State')
        self.conveyor2State = child_quick_item[0].findChild(QObject, 'conveyor2State')
        self.serverState = child_quick_item[0].findChild(QObject, 'serverState')

        self.box1FiberSensor = child_quick_item[0].findChild(QObject, 'box1FiberSensor')
        self.box1NumberText = child_quick_item[0].findChild(QObject, 'box1NumberText')
        self.box2FiberSensor = child_quick_item[0].findChild(QObject, 'box2FiberSensor')
        self.box2NumberText = child_quick_item[0].findChild(QObject, 'box2NumberText')

        self.conveyor1SpeedText = child_quick_item[0].findChild(QObject, 'conveyor1SpeedText')
        self.conveyor2SpeedText = child_quick_item[0].findChild(QObject, 'conveyor2SpeedText')
        self.encoderSpeedText = child_quick_item[0].findChild(QObject, 'encoderSpeedText')

        self.imageLabel = child_quick_item[0].findChild(QObject, 'imageLabel')
        self.objectLabel = child_quick_item[0].findChild(QObject, 'objectLabel')

        self.boxCounter = child_quick_item[0].findChild(QObject, 'boxCounter')

        self.currentPointLog = child_quick_item[0].findChild(QObject, 'currentPointLog')
        self.currentEncoderLog = child_quick_item[0].findChild(QObject, 'currentEncoderLog')
        self.currentEncoderPositon = 0

        # calib element
        self.calibBtn = child_quick_item[0].findChild(QObject, 'settingBtn')
        self.startBtn = child_quick_item[0].findChild(QObject, 'startBtn')
        self.homePannelBtn = child_quick_item[0].findChild(QObject, 'homePannelBtn')

        self.timeForFrameText = child_quick_item[0].findChild(QObject, 'timeForFrameText')

        self.wrap_rect_p1 = child_quick_item[0].findChild(QObject, 'rec_p_1')
        self.wrap_rect_p2 = child_quick_item[0].findChild(QObject, 'rec_p_2')
        self.wrap_rect_p3 = child_quick_item[0].findChild(QObject, 'rec_p_3')
        self.wrap_rect_p4 = child_quick_item[0].findChild(QObject, 'rec_p_4')
        self.calibImage1 = child_quick_item[0].findChild(QObject, 'calibImage1')

        self.crop_rect_p1 = child_quick_item[0].findChild(QObject, 'crop_p_1')
        self.crop_rect_p2 = child_quick_item[0].findChild(QObject, 'crop_p_2')
        self.calibImage2 = child_quick_item[0].findChild(QObject, 'calibImage2')

        self.line_p1 = child_quick_item[0].findChild(QObject, 'line_p_1')
        self.line_p2 = child_quick_item[0].findChild(QObject, 'line_p_2')
        self.distance2Point = child_quick_item[0].findChild(QObject, 'distance2Point')
        self.calibImage3 = child_quick_item[0].findChild(QObject, 'calibImage3')

        self.real_point = child_quick_item[0].findChild(QObject, 'real_point')
        self.calibImage4 = child_quick_item[0].findChild(QObject, 'calibImage4')
        self.real_point_encoder_pos = 0
        self.read_point_cal = QPointF(0, 0)

        self.calib_point_r1_1 = child_quick_item[0].findChild(QObject, 'setPoint11Btn')
        self.calib_point_r1_1_encoder_pos = 0
        self.calib_point_r1_2 = child_quick_item[0].findChild(QObject, 'setPoint12Btn')
        self.calib_point_r1_2_encoder_pos = 0

        self.calib_point_r2_1 = child_quick_item[0].findChild(QObject, 'setPoint21Btn')
        self.calib_point_r2_1_encoder_pos = 0
        self.calib_point_r2_2 = child_quick_item[0].findChild(QObject, 'setPoint22Btn')
        self.calib_point_r2_2_encoder_pos = 0

        self.reloadCalibImageBtn = child_quick_item[0].findChild(QObject, 'reloadImageBtn')
        self.saveCalibBtn = child_quick_item[0].findChild(QObject, 'saveCalibBtn')

        self.pickingZone1 = child_quick_item[0].findChild(QObject, 'pickingZone1')
        self.pickingZone2 = child_quick_item[0].findChild(QObject, 'pickingZone2')

        self.placing1P1 = child_quick_item[0].findChild(QObject, 'placing1P1')
        self.placing1P2 = child_quick_item[0].findChild(QObject, 'placing1P2')
        self.placing1P3 = child_quick_item[0].findChild(QObject, 'placing1P3')
        self.placing1P4 = child_quick_item[0].findChild(QObject, 'placing1P4')
        self.placing1Row = child_quick_item[0].findChild(QObject, 'placing1Row')
        self.placing1Col = child_quick_item[0].findChild(QObject, 'placing1Col')

        self.placing1Offset = child_quick_item[0].findChild(QObject, 'placing1Offset')
        self.minmaxPlace1 = child_quick_item[0].findChild(QObject, 'minmaxPlace1')

        self.placing2P1 = child_quick_item[0].findChild(QObject, 'placing2P1')
        self.placing2P2 = child_quick_item[0].findChild(QObject, 'placing2P2')
        self.placing2P3 = child_quick_item[0].findChild(QObject, 'placing2P3')
        self.placing2P4 = child_quick_item[0].findChild(QObject, 'placing2P4')
        self.placing2Row = child_quick_item[0].findChild(QObject, 'placing2Row')
        self.placing2Col = child_quick_item[0].findChild(QObject, 'placing2Col')

        self.placing2Offset = child_quick_item[0].findChild(QObject, 'placing2Offset')
        self.minmaxPlace2 = child_quick_item[0].findChild(QObject, 'minmaxPlace2')

        self.robot1ZPick = child_quick_item[0].findChild(QObject, 'robot1ZPick')
        self.robot1ZMove = child_quick_item[0].findChild(QObject, 'robot1ZMove')
        self.robot1ZPlace = child_quick_item[0].findChild(QObject, 'robot1ZPlace')

        self.robot2ZPick = child_quick_item[0].findChild(QObject, 'robot2ZPick')
        self.robot2ZMove = child_quick_item[0].findChild(QObject, 'robot2ZMove')
        self.robot2ZPlace = child_quick_item[0].findChild(QObject, 'robot2ZPlace')

        self.robot1controler = child_quick_item[0].findChild(QObject, 'robot1controler')
        self.robot2controler = child_quick_item[0].findChild(QObject, 'robot2controler')
        self.conveyor1controler = child_quick_item[0].findChild(QObject, 'conveyor1controler')
        self.conveyor2controler = child_quick_item[0].findChild(QObject, 'conveyor2controler')

        self.placeProfiles = child_quick_item[0].findChild(QObject, 'placeProfiles')
        self.newProfileInput = child_quick_item[0].findChild(QObject, 'newProfileInput')
        self.newProfileButton = child_quick_item[0].findChild(QObject, 'newProfileButton')
        self.loadProfile = child_quick_item[0].findChild(QObject, 'loadProfile')
        self.deleteProfile = child_quick_item[0].findChild(QObject, 'deleteProfile')

        self.activeProfileText = child_quick_item[0].findChild(QObject, 'activeProfileText')
        self.placeProfilesMain = child_quick_item[0].findChild(QObject, 'placeProfilesMain')
        self.selectProfile = child_quick_item[0].findChild(QObject, 'selectProfile')

        # connect signal btn
        self.selectProfile.clicked.connect(self.selectProfileBtnClicked)


        self.newProfileButton.clicked.connect(self.newProfileBtnClicked)
        self.loadProfile.clicked.connect(self.loadProfileBtnClicked)
        self.deleteProfile.clicked.connect(self.deleteProfileBtnClicked)


        self.calibBtn.clicked.connect(self.calibBtnClicked)
        self.homePannelBtn.clicked.connect(self.homePannelBtnClicked)

        self.startBtn.clicked.connect(self.startBtnClicked)
        self.reloadCalibImageBtn.clicked.connect(self.reloadCalibImageBtnClicked)

        self.calib_point_r1_1.clicked.connect(self.calib_point_r1_1_clicked)
        self.calib_point_r1_2.clicked.connect(self.calib_point_r1_2_clicked)

        self.calib_point_r2_1.clicked.connect(self.calib_point_r2_1_clicked)
        self.calib_point_r2_2.clicked.connect(self.calib_point_r2_2_clicked)

        self.saveCalibBtn.clicked.connect(self.saveCalibBtnClicked)

        self.real_point.mouseReleased.connect(self.realPointMouseReleased)

        self.setBox1NumberText(0)
        self.setBox2NumberText(0)

        self.box_counter = int(VariableManager.instance.get("box_counter", 0))
        self.boxCounter.setProperty('text', str(self.box_counter))

        self.setConveyor1SpeedText(0)
        self.setConveyor2SpeedText(0)
        self.setEncoderSpeedText(0)

        self.loadDataForMain()

    def realPointMouseReleased(self):
        self.real_point_encoder_pos = self.currentEncoderPositon

        settings = QSettings('settings.ini', QSettings.IniFormat)
        settings.beginGroup('VisionTool0')
        _MappingMatrix = settings.value('mapping_matrix', 0, type=np.ndarray)
        settings.endGroup()

        pos =  np.dot(_MappingMatrix, [[self.real_point.property('x') + 15], [self.real_point.property('y') + 15], [1]])
        self.read_point_cal = QPointF(pos[0][0], pos[1][0])

        _point_text = str(round(pos[0][0], 3)) + "; " + str(round(pos[1][0], 3))
        self.currentPointLog.setProperty("text", _point_text)

    def calibBtnClicked(self):
        self.loadCalibValue()
        self.is_calibing = True
        self.robotCalibStateRequest.emit()

    def homePannelBtnClicked(self):
        self.is_calibing = False
        self.robotRunStateRequest.emit()

    def startBtnClicked(self):
        if self.startBtn.property("text") == "Start":
            _robot1_state = bool(VariableManager.instance.get("robot1_state", False))
            _robot2_state = bool(VariableManager.instance.get("robot2_state", False))
            _camera_state = bool(VariableManager.instance.get("camera_state", False))
            _server_state = bool(VariableManager.instance.get("server_state", False))
            _conveyor1_state = bool(VariableManager.instance.get("conveyor1_state", False))
            _conveyor2_state = bool(VariableManager.instance.get("conveyor2_state", False))

            #test
            self.startBtn.setProperty("text", "Stop")
            VariableManager.instance.set("is_running", True)
            self.started.emit()
            # set the conveyor speed
            self.conMoveSpeedRequest.emit(170)

            if _robot1_state == True and _robot2_state == True and _camera_state == True and _server_state == True and _conveyor1_state == True and _conveyor2_state == True:
                self.startBtn.setProperty("text", "Stop")
                VariableManager.instance.set("is_running", True)
                self.started.emit()
                self.conMoveSpeedRequest.emit(170)
        else:
            self.startBtn.setProperty("text", "Start")
            VariableManager.instance.set("is_running", False)
            self.stopped.emit()
            self.conMoveSpeedRequest.emit(0)
            self.con2MoveSpeedRequest.emit(0)

    def stationStopFromRobot(self):
        self.startBtn.setProperty("text", "Start")
        VariableManager.instance.set("is_running", False)
        self.stopped.emit()
        self.conMoveSpeedRequest.emit(0)
        self.con2MoveSpeedRequest.emit(0)

    def reloadCalibImageBtnClicked(self):
        self.calibImage1.setProperty('source', "")
        self.calibImage2.setProperty('source', "")
        self.calibImage3.setProperty('source', "")
        self.calibImage4.setProperty('source', "")

        self.get_wrap_crop_point_in_qml()

        self.imageCalibRequest.emit()

    def get_wrap_crop_point_in_qml(self):
        _wrap_rect_p1 = QPointF(self.wrap_rect_p1.property('x') + 15, self.wrap_rect_p1.property('y') + 15)
        _wrap_rect_p2 = QPointF(self.wrap_rect_p2.property('x') + 15, self.wrap_rect_p2.property('y') + 15)
        _wrap_rect_p3 = QPointF(self.wrap_rect_p3.property('x') + 15, self.wrap_rect_p3.property('y') + 15)
        _wrap_rect_p4 = QPointF(self.wrap_rect_p4.property('x') + 15, self.wrap_rect_p4.property('y') + 15)

        _crop_rect_p1 = QPointF(self.crop_rect_p1.property('x') + 15, self.crop_rect_p1.property('y') + 15)
        _crop_rect_p2 = QPointF(self.crop_rect_p2.property('x') + 15, self.crop_rect_p2.property('y') + 15)


        settings = QSettings('settings.ini', QSettings.IniFormat)
        settings.beginGroup('VisionTool0')
        settings.setValue('wrap_rect_p1', _wrap_rect_p1)
        settings.setValue('wrap_rect_p2', _wrap_rect_p2)
        settings.setValue('wrap_rect_p3', _wrap_rect_p3)
        settings.setValue('wrap_rect_p4', _wrap_rect_p4)
        settings.setValue('crop_rect_p1', _crop_rect_p1)
        settings.setValue('crop_rect_p2', _crop_rect_p2)
        settings.endGroup()

        #print("qml:")
        #print(_crop_rect_p1)
        #print(_crop_rect_p2)

    def loadDataForMain(self):
        self.currentProfile = str(VariableManager.instance.get("currentProfile", str("")))
        self.list_profiles = VariableManager.instance.get("list_profiles", [])

        self.placeProfilesMain.setProperty("model", self.list_profiles)

        self.activeProfileText.setProperty("text", "ActiveProfile: " + self.currentProfile)
        if self.currentProfile != "":
            _currentIndex = self.list_profiles.index(self.currentProfile)
            if _currentIndex > -1:
                self.placeProfilesMain.setProperty("currentIndex", _currentIndex)

    def selectProfileBtnClicked(self):
        if self.placeProfilesMain.property("currentText") != "":
            self.currentProfile = self.placeProfilesMain.property("currentText")

            VariableManager.instance.set("currentProfile", self.currentProfile)

            self.loadProfileInSetting(self.currentProfile)

            VariableManager.instance.set("pickingZone1", self.getPointFromString(self.pickingZone1.property("text")))
            VariableManager.instance.set("pickingZone2", self.getPointFromString(self.pickingZone2.property("text")))

            VariableManager.instance.set("point1_placing1", self.getPointFromString(self.placing1P1.property("text")))
            VariableManager.instance.set("point2_placing1", self.getPointFromString(self.placing1P2.property("text")))
            VariableManager.instance.set("point3_placing1", self.getPointFromString(self.placing1P3.property("text")))
            VariableManager.instance.set("point4_placing1", self.getPointFromString(self.placing1P4.property("text")))

            VariableManager.instance.set("row_placing1", int(self.placing1Row.property("text")))
            VariableManager.instance.set("col_placing1", int(self.placing1Col.property("text")))

            VariableManager.instance.set("point1_placing2", self.getPointFromString(self.placing2P1.property("text")))
            VariableManager.instance.set("point2_placing2", self.getPointFromString(self.placing2P2.property("text")))
            VariableManager.instance.set("point3_placing2", self.getPointFromString(self.placing2P3.property("text")))
            VariableManager.instance.set("point4_placing2", self.getPointFromString(self.placing2P4.property("text")))

            VariableManager.instance.set("row_placing2", int(self.placing2Row.property("text")))
            VariableManager.instance.set("col_placing2", int(self.placing2Col.property("text")))

            _offset_robot1 = self.getPointFromString(self.placing1Offset.property("text"))
            VariableManager.instance.set("offset_x1", _offset_robot1.x())
            VariableManager.instance.set("offset_y1", _offset_robot1.y())

            VariableManager.instance.set("minmaxPlace1", int(self.minmaxPlace1.property("text")))

            _offset_robot2 = self.getPointFromString(self.placing2Offset.property("text"))
            VariableManager.instance.set("offset_x2", _offset_robot2.x())
            VariableManager.instance.set("offset_y2", _offset_robot2.y())

            VariableManager.instance.set("minmaxPlace2", int(self.minmaxPlace2.property("text")))

            VariableManager.instance.set("z_working1", float(self.robot1ZPick.property("text")))
            VariableManager.instance.set("z_safe1", float(self.robot1ZMove.property("text")))
            VariableManager.instance.set("place_z_safe1", float(self.robot1ZMove.property("text")))
            VariableManager.instance.set("place_z_working1", float(self.robot1ZPlace.property("text")))

            VariableManager.instance.set("z_working2", float(self.robot2ZPick.property("text")))
            VariableManager.instance.set("z_safe2", float(self.robot2ZMove.property("text")))
            VariableManager.instance.set("place_z_safe2", float(self.robot2ZMove.property("text")))
            VariableManager.instance.set("place_z_working2", float(self.robot2ZPlace.property("text")))


            self.loadDataForMain()
            self.saveProfileRequest.emit()


    def newProfileBtnClicked(self):
        if self.newProfileInput.property("text") != "":
            self.currentProfile = self.newProfileInput.property("text")

            self.list_profiles.append(self.newProfileInput.property("text"))

            self.placeProfiles.setProperty("model", self.list_profiles)

            _currentIndex = self.list_profiles.index(self.currentProfile)
            if _currentIndex > -1:
                self.placeProfiles.setProperty("currentIndex", _currentIndex)

                self.saveProfileInSetting(self.currentProfile)

    def loadProfileBtnClicked(self):
        if self.placeProfiles.property("currentText") != "":
            self.currentProfile = self.placeProfiles.property("currentText")
            self.loadProfileInSetting(self.currentProfile)

    def deleteProfileBtnClicked(self):
        if self.placeProfiles.property("currentText") != "":
            _currentIndex = self.list_profiles.index(self.placeProfiles.property("currentText"))
            if _currentIndex > -1:
                self.list_profiles.remove(self.placeProfiles.property("currentText"))

            self.placeProfiles.setProperty("model", self.list_profiles)
            self.placeProfiles.setProperty("currentIndex", 0)

            self.loadProfileInSetting(self.list_profiles[0])
            self.currentProfile = self.list_profiles[0]


    def deleteProfileInSetting(self, profile_name):
        settings = QSettings('settings.ini', QSettings.IniFormat)
        settings.beginGroup(profile_name)
        settings.remove("")
        settings.endGroup()

    def saveProfileInSetting(self, profile_name):
        settings = QSettings('settings.ini', QSettings.IniFormat)
        settings.beginGroup(profile_name)

        settings.setValue("pickingZone1", self.getPointFromString(self.pickingZone1.property("text")))
        settings.setValue("pickingZone2", self.getPointFromString(self.pickingZone2.property("text")))

        settings.setValue("point1_placing1", self.getPointFromString(self.placing1P1.property("text")))
        settings.setValue("point2_placing1", self.getPointFromString(self.placing1P2.property("text")))
        settings.setValue("point3_placing1", self.getPointFromString(self.placing1P3.property("text")))
        settings.setValue("point4_placing1", self.getPointFromString(self.placing1P4.property("text")))

        settings.setValue("row_placing1", int(self.placing1Row.property("text")))
        settings.setValue("col_placing1", int(self.placing1Col.property("text")))

        settings.setValue("point1_placing2", self.getPointFromString(self.placing2P1.property("text")))
        settings.setValue("point2_placing2", self.getPointFromString(self.placing2P2.property("text")))
        settings.setValue("point3_placing2", self.getPointFromString(self.placing2P3.property("text")))
        settings.setValue("point4_placing2", self.getPointFromString(self.placing2P4.property("text")))

        settings.setValue("row_placing2", int(self.placing2Row.property("text")))
        settings.setValue("col_placing2", int(self.placing2Col.property("text")))

        _offset_robot1 = self.getPointFromString(self.placing1Offset.property("text"))
        settings.setValue("offset_x1", _offset_robot1.x())
        settings.setValue("offset_y1", _offset_robot1.y())

        settings.setValue("minmaxPlace1", int(self.minmaxPlace1.property("text")))

        _offset_robot2 = self.getPointFromString(self.placing2Offset.property("text"))
        settings.setValue("offset_x2", _offset_robot2.x())
        settings.setValue("offset_y2", _offset_robot2.y())

        settings.setValue("minmaxPlace2", int(self.minmaxPlace2.property("text")))

        settings.setValue("z_working1", float(self.robot1ZPick.property("text")))
        settings.setValue("z_safe1", float(self.robot1ZMove.property("text")))
        settings.setValue("place_z_safe1", float(self.robot1ZMove.property("text")))
        settings.setValue("place_z_working1", float(self.robot1ZPlace.property("text")))

        settings.setValue("z_working2", float(self.robot2ZPick.property("text")))
        settings.setValue("z_safe2", float(self.robot2ZMove.property("text")))
        settings.setValue("place_z_safe2", float(self.robot2ZMove.property("text")))
        settings.setValue("place_z_working2", float(self.robot2ZPlace.property("text")))

        settings.endGroup()

    def loadProfileInSetting(self, profile_name):
        settings = QSettings('settings.ini', QSettings.IniFormat)
        settings.beginGroup(profile_name)

        self.placing1P1.setProperty("text", self.getStrFromPoint(QPointF(settings.value('point1_placing1', QPointF(100, 200), type=QPointF))))
        self.placing1P2.setProperty("text", self.getStrFromPoint(QPointF(settings.value('point2_placing1', QPointF(100, 200), type=QPointF))))
        self.placing1P3.setProperty("text", self.getStrFromPoint(QPointF(settings.value('point3_placing1', QPointF(100, 200), type=QPointF))))
        self.placing1P4.setProperty("text", self.getStrFromPoint(QPointF(settings.value('point4_placing1', QPointF(100, 200), type=QPointF))))


        self.placing1Row.setProperty("text", str(int(settings.value('row_placing1', 2, type=int))))
        self.placing1Col.setProperty("text", str(int(settings.value('col_placing1', 3, type=int))))

        _offset_robot1 = QPointF()
        _offset_robot1.setX(float(settings.value('offset_x1', 0, type=float)))
        _offset_robot1.setY(float(settings.value('offset_y1', 0, type=float)))
        self.placing1Offset.setProperty("text", self.getStrFromPoint(_offset_robot1))

        self.minmaxPlace1.setProperty("text", str(int(settings.value('minmaxPlace1', 7, type=int))))

        self.placing2P1.setProperty("text", self.getStrFromPoint(QPointF(settings.value('point1_placing2', QPointF(100, 200), type=QPointF))))
        self.placing2P2.setProperty("text", self.getStrFromPoint(QPointF(settings.value('point2_placing2', QPointF(100, 200), type=QPointF))))
        self.placing2P3.setProperty("text", self.getStrFromPoint(QPointF(settings.value('point3_placing2', QPointF(100, 200), type=QPointF))))
        self.placing2P4.setProperty("text", self.getStrFromPoint(QPointF(settings.value('point4_placing2', QPointF(100, 200), type=QPointF))))

        self.placing2Row.setProperty("text", str(int(settings.value('row_placing2', 2, type=int))))
        self.placing2Col.setProperty("text", str(int(settings.value('col_placing2', 3, type=int))))

        _offset_robot2 = QPointF()
        _offset_robot2.x = float(settings.value('offset_x2', 0, type=float))
        _offset_robot2.y = float(settings.value('offset_y2', 0, type=float))
        self.placing2Offset.setProperty("text", self.getStrFromPoint(_offset_robot2))

        self.minmaxPlace2.setProperty("text", str(int(settings.value('minmaxPlace2', 8, type=int))))


        self.pickingZone1.setProperty("text", self.getStrFromPoint(QPointF(settings.value('pickingZone1', QPointF(600, 900), type=QPointF))))
        self.pickingZone2.setProperty("text", self.getStrFromPoint(QPointF(settings.value('pickingZone2', QPointF(1000, 1200), type=QPointF))))


        self.robot1ZPick.setProperty("text", str(float(settings.value('z_working1', -840, type=float))))
        self.robot1ZMove.setProperty("text", str(float(settings.value('z_safe1', -800, type=float))))
        self.robot1ZPlace.setProperty("text", str(float(settings.value('place_z_working1', -840, type=float))))

        self.robot2ZPick.setProperty("text", str(float(settings.value('z_working2', -840, type=float))))
        self.robot2ZMove.setProperty("text", str(float(settings.value('z_safe2', -800, type=float))))
        self.robot2ZPlace.setProperty("text", str(float(settings.value('place_z_working2', -840, type=float))))
        #print("loading............")

        settings.endGroup()

    def saveCalibBtnClicked(self):
        #print("saving.....")
        _wrap_rect_p1 = QPointF(self.wrap_rect_p1.property('x') + 15, self.wrap_rect_p1.property('y') + 15)
        _wrap_rect_p2 = QPointF(self.wrap_rect_p2.property('x') + 15, self.wrap_rect_p2.property('y') + 15)
        _wrap_rect_p3 = QPointF(self.wrap_rect_p3.property('x') + 15, self.wrap_rect_p3.property('y') + 15)
        _wrap_rect_p4 = QPointF(self.wrap_rect_p4.property('x') + 15, self.wrap_rect_p4.property('y') + 15)

        _crop_rect_p1 = QPointF(self.crop_rect_p1.property('x') + 15, self.crop_rect_p1.property('y') + 15)
        _crop_rect_p2 = QPointF(self.crop_rect_p2.property('x') + 15, self.crop_rect_p2.property('y') + 15)

        _line_p1 = QPointF(self.line_p1.property('x') + 15, self.line_p1.property('y') + 15)
        _line_p2 = QPointF(self.line_p2.property('x') + 15, self.line_p2.property('y') + 15)
        _distance2Point = float(self.distance2Point.property("text"))

        settings = QSettings('settings.ini', QSettings.IniFormat)
        settings.beginGroup('VisionTool0')
        settings.setValue('wrap_rect_p1', _wrap_rect_p1)
        settings.setValue('wrap_rect_p2', _wrap_rect_p2)
        settings.setValue('wrap_rect_p3', _wrap_rect_p3)
        settings.setValue('wrap_rect_p4', _wrap_rect_p4)
        settings.setValue('crop_rect_p1', _crop_rect_p1)
        settings.setValue('crop_rect_p2', _crop_rect_p2)
        settings.setValue('line_p1', _line_p1)
        settings.setValue('line_p2', _line_p2)
        settings.setValue('distance2Point', _distance2Point)
        settings.endGroup()

        if self.calib_point_r1_1_encoder_pos != 0 and self.calib_point_r1_2_encoder_pos != 0 and self.calib_point_r1_1_encoder_pos != self.calib_point_r1_2_encoder_pos:
            VariableManager.instance.set("point1_robot1", self.r1_point1)
            VariableManager.instance.set("point2_robot1", self.r1_point2)

            _point1_camera = QPointF(self.read_point_cal.x() + (self.calib_point_r1_1_encoder_pos - self.real_point_encoder_pos), self.read_point_cal.y())
            VariableManager.instance.set("point1_camera1", _point1_camera)
            _point2_camera = QPointF(self.read_point_cal.x() + (self.calib_point_r1_2_encoder_pos - self.real_point_encoder_pos), self.read_point_cal.y())
            VariableManager.instance.set("point2_camera1", _point2_camera)

        if self.calib_point_r2_1_encoder_pos != 0 and self.calib_point_r2_2_encoder_pos != 0 and self.calib_point_r2_1_encoder_pos != self.calib_point_r2_2_encoder_pos:
            VariableManager.instance.set("point1_robot2", self.r2_point1)
            VariableManager.instance.set("point2_robot2", self.r2_point2)

            _point1_camera = QPointF(self.read_point_cal.x() + (self.calib_point_r2_1_encoder_pos - self.real_point_encoder_pos), self.read_point_cal.y())
            VariableManager.instance.set("point1_camera2", _point1_camera)
            _point2_camera = QPointF(self.read_point_cal.x() + (self.calib_point_r2_2_encoder_pos - self.real_point_encoder_pos), self.read_point_cal.y())
            VariableManager.instance.set("point2_camera2", _point2_camera)

        
        VariableManager.instance.set("pickingZone1", self.getPointFromString(self.pickingZone1.property("text")))
        VariableManager.instance.set("pickingZone2", self.getPointFromString(self.pickingZone2.property("text")))

        VariableManager.instance.set("point1_placing1", self.getPointFromString(self.placing1P1.property("text")))
        VariableManager.instance.set("point2_placing1", self.getPointFromString(self.placing1P2.property("text")))
        VariableManager.instance.set("point3_placing1", self.getPointFromString(self.placing1P3.property("text")))
        VariableManager.instance.set("point4_placing1", self.getPointFromString(self.placing1P4.property("text")))

        VariableManager.instance.set("row_placing1", int(self.placing1Row.property("text")))
        VariableManager.instance.set("col_placing1", int(self.placing1Col.property("text")))

        VariableManager.instance.set("point1_placing2", self.getPointFromString(self.placing2P1.property("text")))
        VariableManager.instance.set("point2_placing2", self.getPointFromString(self.placing2P2.property("text")))
        VariableManager.instance.set("point3_placing2", self.getPointFromString(self.placing2P3.property("text")))
        VariableManager.instance.set("point4_placing2", self.getPointFromString(self.placing2P4.property("text")))

        VariableManager.instance.set("row_placing2", int(self.placing2Row.property("text")))
        VariableManager.instance.set("col_placing2", int(self.placing2Col.property("text")))

        _offset_robot1 = self.getPointFromString(self.placing1Offset.property("text"))
        VariableManager.instance.set("offset_x1", _offset_robot1.x())
        VariableManager.instance.set("offset_y1", _offset_robot1.y())

        VariableManager.instance.set("minmaxPlace1", int(self.minmaxPlace1.property("text")))

        _offset_robot2 = self.getPointFromString(self.placing2Offset.property("text"))
        VariableManager.instance.set("offset_x2", _offset_robot2.x())
        VariableManager.instance.set("offset_y2", _offset_robot2.y())

        VariableManager.instance.set("minmaxPlace2", int(self.minmaxPlace2.property("text")))

        VariableManager.instance.set("z_working1", float(self.robot1ZPick.property("text")))
        VariableManager.instance.set("z_safe1", float(self.robot1ZMove.property("text")))
        VariableManager.instance.set("place_z_safe1", float(self.robot1ZMove.property("text")))
        VariableManager.instance.set("place_z_working1", float(self.robot1ZPlace.property("text")))

        VariableManager.instance.set("z_working2", float(self.robot2ZPick.property("text")))
        VariableManager.instance.set("z_safe2", float(self.robot2ZMove.property("text")))
        VariableManager.instance.set("place_z_safe2", float(self.robot2ZMove.property("text")))
        VariableManager.instance.set("place_z_working2", float(self.robot2ZPlace.property("text")))

        self.saveProfileInSetting(self.currentProfile)

        VariableManager.instance.set("currentProfile", self.currentProfile)
        VariableManager.instance.set("list_profiles", QVariant(self.list_profiles))
        
        self.saveCalibRequest.emit()
        self.loadDataForMain()

    def loadCalibValue(self):

        settings = QSettings('settings.ini', QSettings.IniFormat)
        settings.beginGroup('VisionTool0')
        _wrap_rect_p1 = QPointF(settings.value('wrap_rect_p1', QPointF(300, 100), type=QPointF))
        _wrap_rect_p2 = QPointF(settings.value('wrap_rect_p2', QPointF(600, 100), type=QPointF))
        _wrap_rect_p3 = QPointF(settings.value('wrap_rect_p3', QPointF(600, 400), type=QPointF))
        _wrap_rect_p4 = QPointF(settings.value('wrap_rect_p4', QPointF(300, 400), type=QPointF))

        _crop_rect_p1 = QPointF(settings.value('crop_rect_p1', QPointF(300, 100), type=QPointF))
        _crop_rect_p2 = QPointF(settings.value('crop_rect_p2', QPointF(600, 400), type=QPointF))

        _line_p1 = QPointF(settings.value('line_p1', QPointF(300, 100), type=QPointF))
        _line_p2 = QPointF(settings.value('line_p2', QPointF(600, 100), type=QPointF))

        _distance2Point = float(settings.value('distance2Point', 200.0, type=float))
        settings.endGroup()

        self.wrap_rect_p1.setProperty("x", _wrap_rect_p1.x() - 15)
        self.wrap_rect_p1.setProperty("y", _wrap_rect_p1.y() - 15)
        self.wrap_rect_p2.setProperty("x", _wrap_rect_p2.x() - 15)
        self.wrap_rect_p2.setProperty("y", _wrap_rect_p2.y() - 15)
        self.wrap_rect_p3.setProperty("x", _wrap_rect_p3.x() - 15)
        self.wrap_rect_p3.setProperty("y", _wrap_rect_p3.y() - 15)
        self.wrap_rect_p4.setProperty("x", _wrap_rect_p4.x() - 15)
        self.wrap_rect_p4.setProperty("y", _wrap_rect_p4.y() - 15)

        self.crop_rect_p1.setProperty("x", _crop_rect_p1.x() - 15)
        self.crop_rect_p1.setProperty("y", _crop_rect_p1.y() - 15)
        self.crop_rect_p2.setProperty("x", _crop_rect_p2.x() - 15)
        self.crop_rect_p2.setProperty("y", _crop_rect_p2.y() - 15)

        self.line_p1.setProperty("x", _line_p1.x() - 15)
        self.line_p1.setProperty("y", _line_p1.y() - 15)
        self.line_p2.setProperty("x", _line_p2.x() - 15)
        self.line_p2.setProperty("y", _line_p2.y() - 15)
        self.distance2Point.setProperty("text", str(_distance2Point))

        self.r1_point1 = QPointF(VariableManager.instance.get("point1_robot1", QPointF(-100, 0)))
        self.r1_point2 = QPointF(VariableManager.instance.get("point2_robot1", QPointF(100, 0)))

        self.r2_point1 = QPointF(VariableManager.instance.get("point1_robot2", QPointF(-100, 0)))
        self.r2_point2 = QPointF(VariableManager.instance.get("point2_robot2", QPointF(100, 0)))

        self.placing1P1.setProperty("text", self.getStrFromPoint(QPointF(VariableManager.instance.get("point1_placing1", QPointF(100, 200)))))
        self.placing1P2.setProperty("text", self.getStrFromPoint(QPointF(VariableManager.instance.get("point2_placing1", QPointF(100, 270)))))
        self.placing1P3.setProperty("text", self.getStrFromPoint(QPointF(VariableManager.instance.get("point3_placing1", QPointF(-100, 270)))))
        self.placing1P4.setProperty("text", self.getStrFromPoint(QPointF(VariableManager.instance.get("point4_placing1", QPointF(-100, 200)))))

        
        self.placing1Row.setProperty("text", str(int(VariableManager.instance.get("row_placing1", 2))))
        self.placing1Col.setProperty("text", str(int(VariableManager.instance.get("col_placing1", 3))))

        _offset_robot1 = QPointF()
        _offset_robot1.setX(float(VariableManager.instance.get("offset_x1", 0)))
        _offset_robot1.setY(float(VariableManager.instance.get("offset_y1", 0)))
        self.placing1Offset.setProperty("text", self.getStrFromPoint(_offset_robot1))

        self.minmaxPlace1.setProperty("text", str(int(VariableManager.instance.get("minmaxPlace1", 7))))

        self.placing2P1.setProperty("text", self.getStrFromPoint(QPointF(VariableManager.instance.get("point1_placing2", QPointF(100, 200)))))
        self.placing2P2.setProperty("text", self.getStrFromPoint(QPointF(VariableManager.instance.get("point2_placing2", QPointF(100, 270)))))
        self.placing2P3.setProperty("text", self.getStrFromPoint(QPointF(VariableManager.instance.get("point3_placing2", QPointF(-100, 270)))))
        self.placing2P4.setProperty("text", self.getStrFromPoint(QPointF(VariableManager.instance.get("point4_placing2", QPointF(-100, 200)))))

        self.placing2Row.setProperty("text", str(int(VariableManager.instance.get("row_placing2", 2))))
        self.placing2Col.setProperty("text", str(int(VariableManager.instance.get("col_placing2", 3))))

        _offset_robot2 = QPointF()
        _offset_robot2.x = float(VariableManager.instance.get("offset_x2", 0))
        _offset_robot2.y = float(VariableManager.instance.get("offset_y2", 0))
        self.placing2Offset.setProperty("text", self.getStrFromPoint(_offset_robot2))

        self.minmaxPlace2.setProperty("text", str(int(VariableManager.instance.get("minmaxPlace2", 8))))

        self.pickingZone1.setProperty("text", self.getStrFromPoint(QPointF(VariableManager.instance.get("pickingZone1", QPointF(600, 900)))))
        self.pickingZone2.setProperty("text", self.getStrFromPoint(QPointF(VariableManager.instance.get("pickingZone2", QPointF(1000, 1200)))))


        self.robot1ZPick.setProperty("text", str(float(VariableManager.instance.get("z_working1", -840))))
        self.robot1ZMove.setProperty("text", str(float(VariableManager.instance.get("z_safe1", -800))))
        self.robot1ZPlace.setProperty("text", str(float(VariableManager.instance.get("place_z_working1", -840))))

        self.robot2ZPick.setProperty("text", str(float(VariableManager.instance.get("z_working2", -840))))
        self.robot2ZMove.setProperty("text", str(float(VariableManager.instance.get("z_safe2", -800))))
        self.robot2ZPlace.setProperty("text", str(float(VariableManager.instance.get("place_z_working2", -840))))
        #print("loading............")

        self.currentProfile = str(VariableManager.instance.get("currentProfile", str("")))
        self.list_profiles = VariableManager.instance.get("list_profiles", [])

        self.placeProfiles.setProperty("model", self.list_profiles)
        if self.currentProfile != "":
            _currentIndex = self.list_profiles.index(self.currentProfile)
            if _currentIndex > -1:
                self.placeProfiles.setProperty("currentIndex", _currentIndex)


    def getPointFromString(self, string_point):
        paras = string_point.split(',')
        return QPointF(float(paras[0]), float(paras[1]))
    
    def getStrFromPoint(self, point):
        point = QPointF(point)
        new_str = str(point.x()) + "," + str(point.y())
        return new_str

    def calib_point_r1_1_clicked(self):
        self.waiting_read_point_index = 1
        self.robot1PositionRequest.emit()
        self.calib_point_r1_1_encoder_pos = self.currentEncoderPositon

    def calib_point_r1_2_clicked(self):
        self.waiting_read_point_index = 2
        self.robot1PositionRequest.emit()
        self.calib_point_r1_2_encoder_pos = self.currentEncoderPositon

    def calib_point_r2_1_clicked(self):
        self.waiting_read_point_index = 3
        self.robot2PositionRequest.emit()
        self.calib_point_r2_1_encoder_pos = self.currentEncoderPositon

    def calib_point_r2_2_clicked(self):
        self.waiting_read_point_index = 4
        self.robot2PositionRequest.emit()
        self.calib_point_r2_2_encoder_pos = self.currentEncoderPositon

    def got_position_form_robot(self, point):
        
        if self.waiting_read_point_index == 1:
            self.r1_point1 = QPointF(point[0], point[1])
            print("robot1_read:", point)
        elif self.waiting_read_point_index == 2:
            self.r1_point2 = QPointF(point[0], point[1])
            print("robot2_read:", point)
        elif self.waiting_read_point_index == 3:
            self.r2_point1 = QPointF(point[0], point[1])
        elif self.waiting_read_point_index == 4:
            self.r2_point2 = QPointF(point[0], point[1])

        _point_text = str(round(point[0], 3)) + "; " + str(round(point[1], 3))
        self.currentPointLog.setProperty("text", _point_text)

    def setRobot1State(self, state):
        new_color = "#12b326"
        if state == False:
            new_color = "#6c1414"
        self.robot1State.setProperty('color', new_color)
        VariableManager.instance.set("robot1_state", state)

    def setRobot2State(self, state):
        new_color = "#12b326"
        if state == False:
            new_color = "#6c1414"
        self.robot2State.setProperty('color', new_color)
        VariableManager.instance.set("robot2_state", state)

    def setCameraState(self, state):
        new_color = "#12b326"
        if state == False:
            new_color = "#6c1414"
        self.cameraState.setProperty('color', new_color)
        VariableManager.instance.set("camera_state", state)

    def setServerState(self, state):
        new_color = "#12b326"
        if state == False:
            new_color = "#6c1414"
        self.serverState.setProperty('color', new_color)
        VariableManager.instance.set("server_state", state)

    def setConveyor1State(self, state):
        new_color = "#12b326"
        if state == False:
            new_color = "#6c1414"
        self.conveyor1State.setProperty('color', new_color)
        VariableManager.instance.set("conveyor1_state", state)

    def setConveyor2State(self, state):
        new_color = "#12b326"
        if state == False:
            new_color = "#6c1414"
        self.conveyor2State.setProperty('color', new_color)
        VariableManager.instance.set("conveyor2_state", state)

    def setBox1FiberSensor(self, state):
        new_color = "#cb372a"
        if state == False:
            new_color = "#636363"
        self.box1FiberSensor.setProperty('color', new_color)

    def setBox2FiberSensor(self, state):
        new_color = "#cb372a"
        if state == False:
            new_color = "#636363"
        self.box2FiberSensor.setProperty('color', new_color)

    def setBox1NumberText(self, number):
        self.box1NumberText.setProperty('text', str(number))

    def setBox2NumberText(self, number):
        self.box2NumberText.setProperty('text', str(number))

    def setBoxCounterText(self):
        self.box_counter = int(VariableManager.instance.get("box_counter", 0))
        self.boxCounter.setProperty('text', str(self.box_counter))

    def setConveyor1SpeedText(self, number):
        new_str_speed = 'Conveyor 1 Speed: ' + str(number) + ' mm/s'
        self.conveyor1SpeedText.setProperty('text', new_str_speed)

    def setConveyor2SpeedText(self, number):
        new_str_speed = 'Conveyor 2 Speed: ' + str(number) + ' mm/s'
        self.conveyor2SpeedText.setProperty('text', new_str_speed)

    def setEncoderSpeedText(self, number):
        new_str_speed = 'Encoder Speed: ' + str(number) + ' mm/s'
        self.encoderSpeedText.setProperty('text', new_str_speed)
        #print(new_str_speed)

    def setEncoderPositionText(self, number):
        new_str_speed = 'Encoder: ' + str(number) + ' mm'
        self.currentEncoderPositon = number
        self.currentEncoderLog.setProperty('text', new_str_speed)

        #print(new_str_speed)

    def setObjectLabel(self, number):
        self.objectLabel.setProperty('text', number)

    def setImageLabel(self, frame):
        if self.is_calibing == True:
            return
        
        #self.imageLabel.setProperty('source', "")
        self.image_provider.setNewImage(frame)

        self.timeForFrameText.setProperty('text', str(round(time.time() - self.measure, 6)) + 's')
        self.measure = time.time()
        
        if self.is_update_image == True:
            self.imageLabel.setProperty('source', "image://src_detect_image/1detect1")
            self.is_update_image == False
        else:
            self.imageLabel.setProperty('source', "image://src_detect_image/0detect0")
            self.is_update_image == True
        # _box1_number = int(VariableManager.instance.get("pick_number1", 0))
        # self.setBox1NumberText(_box1_number)
        # _box2_number = int(VariableManager.instance.get("pick_number2", 0))
        # self.setBox2NumberText(_box2_number)

        # self.box_counter = int(VariableManager.instance.get("box_counter", 0))
        # self.boxCounter.setProperty('text', str(self.box_counter))


    def setCalibImg1(self, frame):
        self.image_provider1.setNewImage(frame)

        self.calibImage1.setProperty('source', "image://src_calib_image1/calib_img2")

    def setCalibImg2(self, frame):
        self.image_provider2.setNewImage(frame)
        
        self.calibImage2.setProperty('source', "image://src_calib_image2/calib_img2")

    def setCalibImg3(self, frame):
        self.image_provider3.setNewImage(frame)

        self.calibImage3.setProperty('source', "image://src_calib_image3/calib_img2")

    def setCalibImg4(self, frame):
        self.image_provider4.setNewImage(frame)

        self.calibImage4.setProperty('source', "image://src_calib_image4/calib_img2")

    

