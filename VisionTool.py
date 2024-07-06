from ast import Global
from signal import signal
import sys
import math

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QObject, QTimer, QThread, pyqtSignal, QRunnable, QThreadPool, pyqtSlot, QSettings, QRect, QRectF
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtQml import QQmlApplicationEngine

from time import sleep
import numpy as np
import keyboard
from pypylon import pylon
import cv2
from Tracking import *
from Device import Encoder
import MushroomAngle
from tool.threshold import *
import os
import pickle
import traceback
from ultralytics import YOLO

current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path) + "/"

class VisionTool(QObject):
    detected = pyqtSignal(list)
    detect_image_ready = pyqtSignal(np.ndarray)
    display_image_ready = pyqtSignal(np.ndarray)
    opened_tool = pyqtSignal(np.ndarray)#, int, int, int, int, int, int, int)

    calib_image1_ready = pyqtSignal(np.ndarray)
    calib_image2_ready = pyqtSignal(np.ndarray)
    calib_image3_ready = pyqtSignal(np.ndarray)
    calib_image4_ready = pyqtSignal(np.ndarray)
    

    def __init__(self):
        super().__init__()
        self.warpPoints = [(50, 50),(50, 150),(150, 150),(150, 50)]
        self.cropRect = QRect(0, 0, 400, 400)

        self.SetColorFilter(type='hsv')

        self.o_w = [10, 10, 10, 10, 10]
        self.o_l = [12, 12, 12, 12, 12]
        self.o_max_w = [15, 15, 15, 15, 15]
        self.o_min_w = [5, 5, 5, 5, 5]
        self.o_max_l = [18, 18, 18, 18, 18]
        self.o_min_l = [6, 6, 6, 6, 6]

        al_list = ['build-in', 'external']
        self.detect_algorithm = al_list[0]
        self.result_type = "Segment"

        img_type = ['origin', 'calib','color filter']
        self.sending_image_type = img_type[1]

        self.color_type = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (200, 255, 0), (255, 200, 0)]

        self.mainwindow = None
        self.filter_tool_open = False
        self.is_warp = False
        self.is_crop = False
        self.is_mapping = False
        self.id = 0
        self.name = 'visiontool0'

        self.ratio = 1.0
        self.PerspectiveMatrix = None
        self.origin_image = None
        self.detecting_image = None
        self.result_img = None
        self.crop_img = None
        self.warp_img = None
        self.MappingMatrix = None

        # yolo model
        self.model_yolo = YOLO('adawaste-v2.1.pt')
        #self.model_yolo.conf = 0.8

        self.load_settings()

        self.time_mesure = time.time()

    def save_settings(self):
        settings = QSettings('settings.ini', QSettings.IniFormat)
        settings.beginGroup('VisionTool' + str(self.id))
        settings.setValue('ratio', self.ratio)
        settings.setValue('perspective_matrix', self.PerspectiveMatrix)
        settings.setValue('is_warp', self.is_warp)
        settings.setValue('crop_rect', self.cropRect)
        settings.setValue('is_crop', self.is_crop)
        settings.setValue('mapping_matrix', self.MappingMatrix)
        
        # settings.setValue('v_min', self.v_min)
        # settings.setValue('v_max', self.v_max)
        # settings.setValue('blur', self.blur)
        settings.endGroup()

        self.save_filter()

    def save_filter(self):
        settings = QSettings('settings.ini', QSettings.IniFormat)
        settings.beginGroup('VisionTool' + str(self.id))
        settings.setValue('hsv', self.HSVValues)
        settings.setValue('blur', self.Blur)
        settings.beginGroup('object')
        settings.setValue('max_w', self.o_max_w)
        settings.setValue('min_w', self.o_min_w)
        settings.setValue('max_l', self.o_max_l)
        settings.setValue('min_l', self.o_min_l)
        settings.endGroup()
        settings.endGroup()

    def load_settings(self):
        settings = QSettings('settings.ini', QSettings.IniFormat)
        settings.beginGroup('VisionTool' + str(self.id))
        self.ratio = settings.value('ratio', self.ratio, type=float)
        self.PerspectiveMatrix = settings.value('perspective_matrix', self.PerspectiveMatrix, type=np.ndarray)
        self.is_warp = settings.value('is_warp', self.is_warp, type=bool)
        self.cropRect = settings.value('crop_rect', self.cropRect, type=QRect)
        self.is_crop = settings.value('is_crop', self.is_crop, type=bool)
        self.MappingMatrix = settings.value('mapping_matrix', self.MappingMatrix, type=np.ndarray)
        
        settings.endGroup()

        self.load_filter()

    def load_filter(self):
        settings = QSettings('settings.ini', QSettings.IniFormat)
        settings.beginGroup('VisionTool' + str(self.id))
        self.HSVValues = settings.value('hsv', self.HSVValues, type=list)
        self.HSVValues = list(map(int, self.HSVValues))
        self.Blur = settings.value('blur', self.Blur, type=int)

        settings.beginGroup('object')
        self.o_max_w = settings.value('max_w', self.o_max_w, type=list)
        self.o_min_w = settings.value('min_w', self.o_min_w, type=list)
        self.o_max_l = settings.value('max_l', self.o_max_l, type=list)
        self.o_min_l = settings.value('min_l', self.o_min_l, type=list)
        settings.endGroup()

        self.o_max_w = list(map(int, self.o_max_w))
        self.o_min_w = list(map(int, self.o_min_w))
        self.o_max_l = list(map(int, self.o_max_l))
        self.o_min_l = list(map(int, self.o_min_l))

        settings.endGroup()

        print(self.HSVValues)

    #def save

    def getCalibImages(self):
        self.calib_image1_ready.emit(self.origin_image.copy())

        settings = QSettings('settings.ini', QSettings.IniFormat)
        settings.beginGroup('VisionTool' + str(self.id))
        _wrap_rect_p1 = QPointF(settings.value('wrap_rect_p1', QPointF(300, 100), type=QPointF)).toPoint()
        _wrap_rect_p2 = QPointF(settings.value('wrap_rect_p2', QPointF(600, 100), type=QPointF)).toPoint()
        _wrap_rect_p3 = QPointF(settings.value('wrap_rect_p3', QPointF(600, 400), type=QPointF)).toPoint()
        _wrap_rect_p4 = QPointF(settings.value('wrap_rect_p4', QPointF(300, 400), type=QPointF)).toPoint()
        _crop_rect_p1 = QPointF(settings.value('crop_rect_p1', QPointF(300, 100), type=QPointF)).toPoint()
        _crop_rect_p2 = QPointF(settings.value('crop_rect_p2', QPointF(600, 400), type=QPointF)).toPoint()
        settings.endGroup()

        list_point_wrap = [(_wrap_rect_p1.x(), _wrap_rect_p1.y()),(_wrap_rect_p2.x(), _wrap_rect_p2.y()),(_wrap_rect_p3.x(), _wrap_rect_p3.y()),(_wrap_rect_p4.x(), _wrap_rect_p4.y())]
        self.CalculateCalibPerspectiveMatrix(list_point_wrap)

        _wrap_image = self.TransformPerspectiveForCalib(self.origin_image.copy())
        self.calib_image2_ready.emit(_wrap_image)


        print("py:")
        print(_crop_rect_p1)
        print(_crop_rect_p2)
        self.cropRect_Calib = QRect(_crop_rect_p1, _crop_rect_p2)
        _crop_image = self.Crop_For_Calib(_wrap_image.copy())

        self.thread().msleep(1)
        self.calib_image3_ready.emit(_crop_image)
        self.thread().msleep(1)
        self.calib_image4_ready.emit(_crop_image)

    def calculateAndSaveCalibValue(self):
        settings = QSettings('settings.ini', QSettings.IniFormat)
        settings.beginGroup('VisionTool0')
        _wrap_rect_p1 = QPointF(settings.value('wrap_rect_p1', QPointF(300, 100), type=QPointF)).toPoint()
        _wrap_rect_p2 = QPointF(settings.value('wrap_rect_p2', QPointF(600, 100), type=QPointF)).toPoint()
        _wrap_rect_p3 = QPointF(settings.value('wrap_rect_p3', QPointF(600, 400), type=QPointF)).toPoint()
        _wrap_rect_p4 = QPointF(settings.value('wrap_rect_p4', QPointF(300, 400), type=QPointF)).toPoint()

        _crop_rect_p1 = QPointF(settings.value('crop_rect_p1', QPointF(300, 100), type=QPointF)).toPoint()
        _crop_rect_p2 = QPointF(settings.value('crop_rect_p2', QPointF(600, 400), type=QPointF)).toPoint()

        _line_p1 = QPointF(settings.value('line_p1', QPointF(300, 100), type=QPointF)).toPoint()
        _line_p2 = QPointF(settings.value('line_p2', QPointF(600, 100), type=QPointF)).toPoint()

        _distance2Point = float(settings.value('distance2Point', 200.0, type=float))
        settings.endGroup()

        list_point_wrap = [(_wrap_rect_p1.x(), _wrap_rect_p1.y()),(_wrap_rect_p2.x(), _wrap_rect_p2.y()),(_wrap_rect_p3.x(), _wrap_rect_p3.y()),(_wrap_rect_p4.x(), _wrap_rect_p4.y())]
        self.CalculatePerspectiveMatrix(list_point_wrap)

        self.cropRect = QRect(_crop_rect_p1, _crop_rect_p2)
        self.is_crop = True

        self.SetMappingPoints(((_line_p1.x(), _line_p1.y()), (_line_p2.x(), _line_p2.y())), ((0, 0), (_distance2Point, 0)))
    
        self.save_settings()

    def set_encoder(self, encoder=None):
        self.encoder = encoder

    def set_object_filter(self, id, w, max_w, min_w, h, max_l, min_l):
        self.o_w[id] = w
        self.o_l[id] = h
        self.o_max_w[id] = max_w
        self.o_min_w[id] = min_w
        self.o_max_l[id] = max_l
        self.o_min_l[id] = min_l

    def check_obj(self, rect):
        pos, size, angle = rect
        l, w = size

        if l < w:
            l = rect[1][1]
            w = rect[1][0]

        for i in range(2):
            if w >= self.o_min_w[i] and w <= self.o_max_w[i]:
                if l >= self.o_min_l[i] and l <= self.o_max_l[i]:
                    return i
                         
        return -1

    def capture_moment(self):
        print("capture")

    def detect(self, image, capture_pos = 0):
        # print('run time', time.time() - self.time_mesure)
        # self.time_mesure = time.time()
        try:
            
            self.capture_pos = capture_pos
            self.detecting_image = image.copy()
            self.origin_image = image.copy()
            #
            # cv2.imshow('origin', image)
            if self.is_warp == True:
                self.detecting_image = self.TransformPerspective(self.detecting_image)
                self.warp_img = self.detecting_image.copy()
                # cv2.imshow("trans", transMat)

            if self.is_crop == True:
                self.detecting_image = self.Crop(self.detecting_image)
                self.crop_img = self.detecting_image.copy()
                # cv2.imshow("crop", self.cropMat)              

            # self.SetColorFilter(thres=170, blur=15, inverse=True)
            # self.run_color_filter()

            if self.detect_algorithm == "external":
                if self.sending_image_type == 'calib':
                    self.detect_image_ready.emit(self.detecting_image)
                elif self.sending_image_type == 'color filter':
                    self.run_color_filter()
                    self.detect_image_ready.emit(self.filter_image)
                elif self.sending_image_type == 'origin':
                    self.detect_image_ready.emit(self.image)
                    
            else:    
                #self.run_color_filter()            
                #self.run_buildin_algorithm(self.detecting_image)
                #self.model_yolo
                self.get_objects(self.detecting_image)
            # cv2.waitKey(1)
        except Exception as e:
            # In ra lỗi
            print(e)
            traceback.print_exc()

    def get_objects(self, image):
        # Run YOLOv8 inference on the frame
        results = self.model_yolo(image, conf=0.65, iou=0.65)

        resultString = "#Objects = "

        img_height, img_width, _ = image.shape

        infos = []
        # View results
        for r in results:
            #print("detect_r:", r.masks)
            for box in r.boxes.xywhn:
                #print("detect_box:", r.boxes)
                id = int(r.boxes.cls[0])
                x = int(box[0] * img_width)
                y = int(box[1] * img_height)
                w = int(box[2] * img_width)
                h = int(box[3] * img_height)
                angle = 90

                top_obj = y - h / 2
                bot_obj = y + h / 2

                if top_obj < 2:
                    continue
                if bot_obj > img_height - 2:
                    continue

                info = []
                info.append(id)  #(id)
                info.append((x, y)) #(x, y)
                info.append((w, h)) #(w, h)
                info.append(angle)  #(a)
                infos.append(info)

                resultString += str(id) + ', ' + str(x) + ', ' + str(y)  + ', ' + str(w) + ', ' + str(h) + ', ' + str(angle)  + ";"
        
        
        self.get_objs_from_external(infos)

        # Visualize the results on the frame
        #annotated_frame = results[0].plot()

        # Display the annotated frame
        #cv2.imshow("YOLOv8 Inference", annotated_frame)

       # return resultString

    def open_filter_tool(self, img):
        if self.filter_tool_open == False:
            self.filter_tool_open == True
            self.opened_tool.emit(img)#, self.HSVValues[0], self.HSVValues[1], self.HSVValues[2], self.HSVValues[3], self.HSVValues[4], self.HSVValues[5], self.Blur)
        

    def get_color_filter_parameters(self, paras):
        self.HSVValues = paras['hsv'].copy()
        self.Blur = paras['blur']

        print(self.HSVValues)
        print(self.Blur)

    def run_color_filter(self):
        if self.FilterType == 'threshold':
            self.grayImage = cv2.cvtColor(self.detecting_image, cv2.COLOR_RGB2HSV)

            ret, self.binaryImage = cv2.threshold(self.grayImage, self.ThresholdValue, 255, cv2.THRESH_BINARY)

        else:
            self.grayImage = cv2.cvtColor(self.detecting_image, cv2.COLOR_BGR2HSV)
            low = (self.HSVValues[0], self.HSVValues[2], self.HSVValues[4])
            high = (self.HSVValues[1], self.HSVValues[3], self.HSVValues[5])
            self.binaryImage = cv2.inRange(self.grayImage, low, high)

        # print(self.Inverse)
        # cv2.imshow('Binary Image', self.binaryImage)
        # if self.Inverse == True:                
        #     self.binaryImage = cv2.bitwise_not(self.binaryImage)
        self.binaryImage = cv2.medianBlur(self.binaryImage, self.Blur)
        #cv2.imshow('Binary Image', self.binaryImage)
        self.filter_image = self.binaryImage

    def run_buildin_algorithm(self, img):
        self.result_img = img.copy()        

        contours, hierarchy = cv2.findContours(image=self.filter_image, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
        # contours, hierarchy = cv2.findContours(self.filter_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(image=self.result_img, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
        # cv2.imshow('Binary Image', self.result_img)

        objs = []

        # self.thread().msleep(200)
        
        for i in range(0, len(contours)):
            rotated_rect = cv2.minAreaRect(contours[i])
            # print(rotated_rect)
            b_x, b_y, b_w, b_h = cv2.boundingRect(contours[i])

            #---------- mushroom detecting -----------

            is_mushroom = False
            if is_mushroom == True:
                roi = self.filter_image[b_y:b_y + b_h, b_x:b_x + b_w]

                scaled = cv2.resize(roi, (16, 16), interpolation=cv2.INTER_AREA)
                predict = MushroomAngle.detect(scaled)
                angle = MushroomAngle.GetAngle(predict)
                rect_l = list(rotated_rect)
                rect_l[2] = angle
                rotated_rect = tuple(rect_l)
            #-------------------------------------------


            # bound x y w height
            # image row col

            # print(rect)

            if b_y <= 0 or (b_y + b_h) >= img.shape[0] - 2 or b_x <= 0 or (b_x + b_w) >= img.shape[1] - 2:
                continue

            id = self.check_obj(rotated_rect)

            if id == -1:
                continue

            imgPos, imgSize, angle = rotated_rect

            # realPos =  np.dot(self.MappingMatrix, [[], [], [1]])
            realPos = self.Mapping(imgPos[0], imgPos[1])

            center_x = round(realPos[0], 2)
            center_y = round(realPos[1], 2)
            width = round(imgSize[0] * self.ratio)
            height = round(imgSize[1] * self.ratio)

            rotated_rect = list(rotated_rect) 

            if imgSize[0] < imgSize[1]:
                rotated_rect[1] = (imgSize[1], imgSize[0])

                angle = int(angle) + 90
                
            else:
                angle = int(angle)
            
            rotated_rect[2] = angle

            if rotated_rect[1][0] < 10 or rotated_rect[1][0] > 400:
                continue

            # print(rect[1])

            # if is_mushroom == False:
                # print(angle)
                # if width > height:                    
                #     angle = rect[2] + 90
                    # print(angle)

            obj = TrackingObject(x=center_x, y=center_y, w=width, l=height, a=angle, start_pos=self.capture_pos, error=0.4)
            
            objs.append(obj)
            
            # obj.print()

            box = np.int0(cv2.boxPoints(rotated_rect))
            # obj.set_rect(rect)
            # draw oriented box of object
            self.result_img = cv2.drawContours(self.result_img, [box], 0, (36,255,12), 3)

            # display angle of object
            # self.detecting_image = cv2.putText(self.detecting_image, str(angle), (int(rect[0][0]), int(rect[0][1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            
        
        #print('---------------')
        if len(objs) > 0:
            self.detected.emit(objs)
            # print("detacj",len(objs))
        # cv2.imshow('detecting', self.result_img)
        self.display_image_ready.emit(self.result_img)

        cv2.waitKey(1)

    def find_display_angle(self, x):
        if x >= 0 and x <= 90:
            y = 90 - x
        elif x > 90 and x <= 180:
            y = 90 - x
        elif x < 0 and x >= -90:
            y = 90 - x
        elif x < -90 and x >= -180:
            y = -270 - x
        else:
            y = None
        return y

    def get_objs_from_external(self, objs):
        self.tracking_objs = []
        self.filter_objs = []
        
        for obj in objs:
            self.filter_objs.append(obj)

            width = 0
            length = 0
            angle = 0

            if self.result_type == "Segment":
                c_box = np.int0(obj[2:])
                rotated_rect = cv2.minAreaRect(c_box)
                b_x, b_y, b_w, b_h = cv2.boundingRect(c_box)

                if b_y <= 0 or (b_y + b_h) >= self.detecting_image.shape[0] - 2 or b_x <= 0 or (b_x + b_w) >= self.detecting_image.shape[1] - 2:
                    continue
                is_box = self.check_obj(rotated_rect)
                # if is_box == -1:
                #     continue

                imgPos, imgSize, angle = rotated_rect

                width = round(imgSize[0] * self.ratio)
                length = round(imgSize[1] * self.ratio)

                #rotated_rect = list(rotated_rect) 

                if imgSize[0] < imgSize[1]:
                    #rotated_rect[1] = (imgSize[1], imgSize[0])
                    angle = int(angle) + 90
                else:
                    angle = int(angle)

            else:
                width = round(obj[2][0] * self.ratio)
                length = round(obj[2][1] * self.ratio)
                angle = obj[3]

            realPos = self.Mapping(obj[1][0], obj[1][1])
            center_x = realPos[0]
            center_y = realPos[1]
            
            #print(width)
            #print(length)
            
            if width < 20:
                continue
            if length < 30:
                continue

            _tracking_obj = [center_x, center_y, width, length, angle, 0, 0.4, obj[0]]
            #print(_tracking_obj)
            self.tracking_objs.append(_tracking_obj)

        if len(self.tracking_objs) > 0:
            self.detected.emit(self.tracking_objs)
            
        if self.result_type == "Segment":
             self.draw_seg_objs(self.filter_objs)
        else:
            self.draw_rotated_objs(self.filter_objs)

    def draw_seg_objs(self, objs):        
        draw = self.detecting_image.copy()
        for obj in objs:
            box = obj[2:]

            cv2.circle(draw,(int(obj[1][0]), int(obj[1][1])),5,self.color_type[obj[0]],5)

            box = np.int0(box)
            draw = cv2.drawContours(draw, [box], 0, self.color_type[obj[0]], 2)
        
        cv2.imshow('result', draw)
        # print("draw image", len(objs))
        self.display_image_ready.emit(draw)

    def draw_rotated_objs(self, objs):     
        draw = self.detecting_image.copy()
        for obj in objs:

            box = obj[1:]

            angle = math.radians(box[2])

            cv2.putText(draw, str(box[2]), (box[0][0],box[0][1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,255), 2, cv2.LINE_AA)

            box[2] = self.find_display_angle(box[2])

            length = box[1][0] * 0.6            

            end_x = int(length * math.cos(angle)) + box[0][0]
            end_y = - int(length * math.sin(angle)) + box[0][1]
            
            end = (end_x, end_y)
            start = box[0]

            # Draw the arrow on the image
            cv2.arrowedLine(draw, start, end, (0, 255, 0), 2)
            
            box = np.int0(cv2.boxPoints(box))
            draw = cv2.drawContours(draw, [box], 0, self.color_type[obj[0]], 2)
        
        cv2.imshow('result', draw)
        self.display_image_ready.emit(draw)
        # cv2.waitKey(10)


    # def display_detected_objects(self, mat, objs):

    #     for obj in objs:
    #         self.detecting_image = cv2.drawContours(self.cropMat, [obj], 0, (36,255,12), 3)
    #         self.detecting_image = cv2.putText(self.detecting_image, str(obj.angle), (int(rect[0][0]), int(rect[0][1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            
    #     cv2.imshow('detecting', mat)

    #     cv2.waitKey(1)

    @pyqtSlot(str)
    def testSlot(smg):
        print(smg)

    def CalculatePerspectiveMatrix(self, points=[(50, 50),(50, 150),(150, 150),(150, 50)]):
        print(points)
        self.is_warp = True
        centerX = (points[0][0] + points[1][0] + points[2][0] + points[3][0]) / 4
        centerY = (points[0][1] + points[1][1] + points[2][1] + points[3][1]) / 4

        maxLength = np.sqrt(((points[0][0] - points[3][0]) ** 2 + (points[0][1] - points[3][1]) ** 2))

        for i in range(0, 3):
            line = np.sqrt(((points[i + 1][0] - points[i][0]) ** 2 + (points[i + 1][1] - points[i][1]) ** 2))

            if line > maxLength:
                maxLength = line

        halfLen = maxLength / 2

        input_pts = np.float32(points)
        output_pts = np.float32([[centerX - halfLen, centerY - halfLen],[centerX - halfLen,centerY + halfLen],[centerX + halfLen,centerY + halfLen],[centerX + halfLen,centerY - halfLen]])
        
        # Compute the perspective transform M
        self.PerspectiveMatrix = cv2.getPerspectiveTransform(input_pts,output_pts)

    def CalculateCalibPerspectiveMatrix(self, points=[(50, 50),(50, 150),(150, 150),(150, 50)]):
        print(points)
        self.is_warp = True
        centerX = (points[0][0] + points[1][0] + points[2][0] + points[3][0]) / 4
        centerY = (points[0][1] + points[1][1] + points[2][1] + points[3][1]) / 4

        maxLength = np.sqrt(((points[0][0] - points[3][0]) ** 2 + (points[0][1] - points[3][1]) ** 2))

        for i in range(0, 3):
            line = np.sqrt(((points[i + 1][0] - points[i][0]) ** 2 + (points[i + 1][1] - points[i][1]) ** 2))

            if line > maxLength:
                maxLength = line

        halfLen = maxLength / 2

        input_pts = np.float32(points)
        output_pts = np.float32([[centerX - halfLen, centerY - halfLen],[centerX - halfLen,centerY + halfLen],[centerX + halfLen,centerY + halfLen],[centerX + halfLen,centerY - halfLen]])
        
        # Compute the perspective transform M
        self.PerspectiveMatrix_Calib = cv2.getPerspectiveTransform(input_pts,output_pts)

    def TransformPerspective(self, img):
        # Apply the perspective transformation to the image
        out = cv2.warpPerspective(img, self.PerspectiveMatrix, (img.shape[1], img.shape[0]), flags=cv2.INTER_NEAREST)

        return out
    
    def TransformPerspectiveForCalib(self, img):
        # Apply the perspective transformation to the image
        out = cv2.warpPerspective(img, self.PerspectiveMatrix_Calib, (img.shape[1], img.shape[0]), flags=cv2.INTER_NEAREST)

        return out

    def SetCropParameter(self, rect):
        self.cropRect = rect
        self.is_crop = True

    def Crop(self, img):
        start_row = self.cropRect.topLeft().y()
        end_row = self.cropRect.bottomRight().y()
        start_col = self.cropRect.topLeft().x()
        end_col = self.cropRect.bottomRight().x()

        cropped = img[start_row:end_row, start_col:end_col]

        return cropped
    
    def Crop_For_Calib(self, img):
        start_row = self.cropRect_Calib.topLeft().y()
        end_row = self.cropRect_Calib.bottomRight().y()
        start_col = self.cropRect_Calib.topLeft().x()
        end_col = self.cropRect_Calib.bottomRight().x()

        cropped = img[start_row:end_row, start_col:end_col]

        return cropped


    def SetMappingPoints(self, imagePos, realPos):
        x1 = imagePos[0][0]
        y1 = imagePos[0][1]
        x2 = imagePos[1][0]
        y2 = imagePos[1][1]

        if x1 == 0 and y1 == 0 and x2 == 0 and y2 == 0:
            return

        xx1 = realPos[0][0]
        yy1 = realPos[0][1]
        xx2 = realPos[1][0]
        yy2 = realPos[1][1]

        if xx1 == 0 and yy1 == 0 and xx2 == 0 and yy2 == 0:
            return

        a1 = x2 - x1
        b1 = y2 - y1
        a2 = xx2 -xx1
        b2 = yy2 - yy1

        n1n2 = a1 * a2 + b1 * b2
        _n1 = math.sqrt(math.pow(a1, 2) + math.pow(b1, 2))
        _n2 = math.sqrt(math.pow(a2, 2) + math.pow(b2, 2))
        self.ratio = _n2/_n1

        _n1_n2_ = _n1 * _n2

        cosTheta = n1n2 / _n1_n2_
        #print("test1:",a1 * b2 - b1 * a2)
        #print("test2:",a1 * a2 + b1 * b2)

        tanTheta = 0
        if a1 * a2 + b1 * b2 == 0:
            if a1 * b2 - b1 * a2 >= 0:
                tanTheta = 90
            else:
                tanTheta = -90
        else:

            tanTheta = (a1 * b2 - b1 * a2) / (a1 * a2 + b1 * b2)
        theta = math.acos(cosTheta)

        if cosTheta < 0:    
            if tanTheta > 0:        
                theta = 0 - theta
            
        else:    
            if tanTheta < 0:        
                theta = 0 - theta

        angle = 0 - theta * (180 / math.pi)

        self.rotateMatrix = np.array([[math.cos(theta), -math.sin(theta), 0], [math.sin(theta), math.cos(theta), 0], [0, 0, 1]])
        self.scaleMatrix = np.array([[self.ratio, 0, 0], [0, self.ratio, 0], [0, 0, 1]])

        srMatrix = self.scaleMatrix @ self.rotateMatrix

        #x' = m11 * x + m21 * y + dx   --> dx = x' - (m11 * x + m21 * y)
        #y' = m12 * x + m22 * y + dy   --> dy = y' - (m12 * x + m22 * y)

        xRealCalibPoint = xx1
        yRealCalibPoint = yy1
        
        x = x1
        y = y1

        dx = xRealCalibPoint - (srMatrix[0][0] * x + srMatrix[0][1] * y)
        dy = yRealCalibPoint - (srMatrix[1][0] * x + srMatrix[1][1] * y)

        self.MappingMatrix = np.array([[srMatrix[0][0], srMatrix[0][1], dx], [srMatrix[1][0], srMatrix[1][1], dy], [0, 0, 1]])

        t1 = time.time_ns()

        mp1 = np.dot(self.MappingMatrix, [[x1], [y1], [1]])
        mp2 = np.dot(self.MappingMatrix, [[x2], [y2], [1]])

        print(mp1)
        print(mp2)

    def Mapping(self, x, y):
        pos =  np.dot(self.MappingMatrix, [[x], [y], [1]])
        return (pos[0][0], pos[1][0])


    def SetColorFilter(self, type = 'threshold', thres = 150, hsv = (0, 255, 0, 255, 0, 255), blur = 3, inverse = False):
        
        self.FilterType = type
        self.ThresholdValue = thres
        self.HSVValues = []
        for i in range(len(hsv)):
            self.HSVValues.append(int(hsv[i]))
        self.Blur = blur
        self.Inverse = inverse

    def open_calib_tool(self):
        self.click_points = []
        self.zoom = 1
        def on_mouse_click(event, x, y, flags, params):

            if event == cv2.EVENT_LBUTTONUP:                
                cv2.circle(self.calib_img, (x, y), 2, (0, 0, 255), 2)
                cv2.imshow("calib tool", self.calib_img)

                x, y = int(x / self.zoom), int(y / self.zoom)
                print("Point clicked: ({}, {})".format(x, y))
                if self.is_mapping == True:
                    mp = np.dot(self.MappingMatrix, [[x], [y], [1]])
                    print("Real point: ({}, {})".format(mp[0], mp[1]))
                self.click_points.append((x, y))

            elif event == cv2.EVENT_RBUTTONUP:
                self.click_points.clear()
                self.calib_img = cv2.resize(self.detecting_image, (self.detecting_image.shape[1] * self.zoom, self.detecting_image.shape[0] * self.zoom))
            
                cv2.imshow("calib tool", self.calib_img)

        # Set the mouse callback function for the window
        
        self.calib_img = self.detecting_image.copy()
        cv2.imshow('calib tool', self.calib_img)
        cv2.setMouseCallback("calib tool", on_mouse_click)
        # cv2.waitKey(0)

    def get_cmd(self, cmd: str):
        if cmd == 'calib':
            self.real_X = 200
            self.open_calib_tool()

        paras = cmd.split()

        if cmd == 'update calib':
            self.calib_img = self.detecting_image.copy()
            self.calib_img = cv2.resize(self.calib_img, (self.detecting_image.shape[1] * self.zoom, self.detecting_image.shape[0] * self.zoom))
            cv2.imshow('calib tool', self.calib_img)

        if cmd == 'zoomin':
            self.zoom = self.zoom * 2
            self.calib_img = cv2.resize(self.calib_img, (self.detecting_image.shape[1] * self.zoom, self.detecting_image.shape[0] * self.zoom))
            cv2.imshow('calib tool', self.calib_img)

        if cmd == 'get origin':
            self.is_warp = False
            self.is_crop = False
            self.calib_img = self.detecting_image.copy()
            cv2.imshow('calib tool', self.calib_img)

        if cmd == 'get warp':
            if len(self.click_points) == 4:
                self.CalculatePerspectiveMatrix(self.click_points)

        if cmd == 'get crop':
            if len(self.click_points) == 2:
                p1 = QPoint(self.click_points[0][0], self.click_points[0][1])
                p2 = QPoint(self.click_points[1][0], self.click_points[1][1])
                self.SetCropParameter(QRect(p1, p2))

        if cmd == 'get mapping':
            if len(self.click_points) == 2:
                self.SetMappingPoints((self.click_points[0], self.click_points[1]), ((0, 0), (self.real_X, 0)))
        
        if cmd == 'get min object size':
            if len(self.click_points) == 2:
                self.o_min_w[0] = abs(self.click_points[0][0] - self.click_points[1][0])
                self.o_min_l[0] = abs(self.click_points[0][1] - self.click_points[1][1])
                if self.o_min_w[0] > self.o_min_l[0]:
                    self.o_min_w[0], self.o_min_l[0] = self.o_min_l[0], self.o_min_w[0]

        if cmd == 'get max object size':
            if len(self.click_points) == 2:
                self.o_max_w[0] = abs(self.click_points[0][0] - self.click_points[1][0])
                self.o_max_l[0] = abs(self.click_points[0][1] - self.click_points[1][1])
                if self.o_max_w[0] > self.o_max_l[0]:
                    self.o_max_w[0], self.o_max_l[0] = self.o_max_l[0], self.o_max_w[0]


        if cmd == 'show warp':
            self.calib_img = cv2.resize(self.warp_img, (self.detecting_image.shape[1] * self.zoom, self.detecting_image.shape[0] * self.zoom))
            cv2.imshow('calib tool', self.calib_img)
        
        if cmd == 'show crop':
            self.calib_img = cv2.resize(self.crop_img, (self.detecting_image.shape[1] * self.zoom, self.detecting_image.shape[0] * self.zoom))
            cv2.imshow('calib tool', self.calib_img)

        if cmd == 'mapping':
            self.is_mapping = True

        if cmd == 'save setting':
            self.save_settings()

        if cmd == 'load setting':
            self.load_settings()

        if cmd == 'open filter tool':
            self.open_filter_tool(self.detecting_image)

        if cmd == 'save filter setting':
            self.save_filter()

        if cmd == 'load filter setting':
            self.load_filter()

        if paras[0].find('eval') > -1:
            code = cmd[len(paras[0]) + 1:]
            eval(code)

        if paras[0].find('realx') > -1:
            value = cmd[len(paras[0]) + 1:]
            self.real_X = float(value)
            print(self.real_X)

# TESTING

if __name__ == "__main__":
    from CameraDevice import *

    app = QApplication(sys.argv)

    # Server
    # from Server import *
    # server = ImageServer("192.168.101.135", 8844)

    # #Camera
    camera = CameraDevice()
    camera.scaleWidth = 800
    cameraThread = QThread()
    camera.moveToThread(cameraThread)
    cameraThread.started.connect(camera.run)
    cameraThread.start()

    timer = QTimer()
    timer.timeout.connect(camera.Capture)
    timer.setInterval(600)
    timer.start()

    # #Detecting
    vision = VisionTool()
    vision.load_settings()
    visionThread = QThread()
    vision.moveToThread(visionThread)
    visionThread.start()
    camera.captured.connect(vision.detect)
    # vision.detect_image_ready.connect(server.send_image)
    # vision.detect_image_ready.connect(vision.open_calib_tool)

    # Console
    import console

    cons = console.Command()
    consoleThread = QThread()
    cons.moveToThread(consoleThread)
    consoleThread.started.connect(cons.run)
    consoleThread.start()

    cons.inputSig.connect(vision.get_cmd)

    # camera.run()
    # vision.open_calib_tool(camera.Capture())

    # server.got_objects.connect(vision.draw_rotated_objs)

    # # Devices
    import DeviceManager
    device_manager = DeviceManager.DeviceManager()
    device_manager.create_conveyor('station')
    
    device_manager.conveyor_station.set_encoder_invert('C3', True)
    cons.inputSig.connect(device_manager.get_cmd)


    thresTool = ThresholdAdjuster()
    vision.opened_tool.connect(thresTool.open)
    thresTool.saved.connect(vision.get_color_filter_parameters)

    app.exec_()
