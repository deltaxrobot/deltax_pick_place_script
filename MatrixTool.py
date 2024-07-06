from signal import signal
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from time import sleep
from PyQt5.QtCore import QVariant
from PyQt5.QtCore import QObject, QSettings, QRect, QPointF, QPoint, QLineF
import math
import numpy as np
from scipy.spatial import transform

class PositionMatrix(QObject):
    def __init__(self):
        super().__init__()

    def next(self):
        i = self.id
        is_filled = False
        pos = self.dots[i // self.col][i % self.col]
        self.id = self.id + 1
        if self.id > self.max_id:
            self.id = self.min_id
            is_filled = True
        return i, pos, is_filled

    def cal(self, p1, p2, p3, p4, col, row):
        #print(p1)
        #print(p2)
        #print(p3)
        #print(p4)
        lines = []
        self.dots = []
        line1 = QLineF(p1, p2)
        line2 = QLineF(p2, p3)
        line3 = QLineF(p4, p3)
        line4 = QLineF(p1, p4)

        col1_dots = self.find_dots(line4, row)
        col2_dots = self.find_dots(line2, row)

        for i in range(row):
            l = QLineF(col1_dots[i], col2_dots[i])
            self.dots.append(self.find_dots(l, col))

        self.id = 0
        self.col = col
        self.row = row

        self.min_id = 0
        self.max_id = self.col * self.row - 1

    def setMin(self, min):
        self.min_id = min
        self.id = self.min_id

    def setMax(self, max):
        self.max_id = max

    def find_dots(self, line, num):
        dots = []
        dots.append(line.p1())

        leng = line.length()/(num - 1)

        for i in range(1, num):
            line.setLength(leng * i)
            dots.append(line.p2())

        return dots

class MappingMatrix(QObject):
    def __init__(self):
        super().__init__()

    # def calculate_matrix(self, p1, p2, mp1, mp2):
    #     x1 = p1[0]
    #     y1 = p1[1]
    #     x2 = p2[0]
    #     y2 = p2[1]

    #     if x1 == 0 and y1 == 0 and x2 == 0 and y2 == 0:
    #         return

    #     xx1 = mp1[0]
    #     yy1 = mp1[1]
    #     xx2 = mp2[0]
    #     yy2 = mp2[1]

    #     if xx1 == 0 and yy1 == 0 and xx2 == 0 and yy2 == 0:
    #         return

    #     a1 = x2 - x1
    #     b1 = y2 - y1
    #     a2 = xx2 - xx1
    #     b2 = yy2 - yy1

    #     n1n2 = a1 * a2 + b1 * b2
    #     _n1 = math.sqrt(math.pow(a1, 2) + math.pow(b1, 2))
    #     _n2 = math.sqrt(math.pow(a2, 2) + math.pow(b2, 2))
    #     ratio = _n2/_n1

    #     _n1_n2_ = _n1 * _n2

    #     cosTheta = n1n2 / _n1_n2_
    #     tanTheta = (a1 * b2 - b1 * a2) / (a1 * a2 + b1 * b2)
    #     theta = math.acos(cosTheta)

    #     if cosTheta < 0:    
    #         if tanTheta > 0:        
    #             theta = 0 - theta
            
    #     else:    
    #         if tanTheta < 0:        
    #             theta = 0 - theta

    #     angle = 0 - theta * (180 / math.pi)

    #     rotateMatrix = np.array([[math.cos(theta), -math.sin(theta), 0], [math.sin(theta), math.cos(theta), 0], [0, 0, 1]])
    #     scaleMatrix = np.array([[ratio, 0, 0], [0, ratio, 0], [0, 0, 1]])

    #     srMatrix = scaleMatrix @ rotateMatrix

    #     #x' = m11 * x + m21 * y + dx   --> dx = x' - (m11 * x + m21 * y)
    #     #y' = m12 * x + m22 * y + dy   --> dy = y' - (m12 * x + m22 * y)

    #     dx = mp1[0] - (srMatrix[0][0] * p1[0] + srMatrix[0][1] * p1[1])
    #     dy = mp1[1] - (srMatrix[1][0] * p1[0] + srMatrix[1][1] * p1[1])

    #     self.matrix = np.array([[srMatrix[0][0], srMatrix[0][1], dx], [srMatrix[1][0], srMatrix[1][1], dy], [0, 0, 1]])

    def calculate_matrix(self, begin_points, end_point):
        x1 = begin_points[0][0]
        y1 = begin_points[0][1]
        x2 = begin_points[1][0]
        y2 = begin_points[1][1]

        xx1 = end_point[0][0]
        yy1 = end_point[0][1]
        xx2 = end_point[1][0]
        yy2 = end_point[1][1]

        end_matrix = np.array([[xx1],
                            [yy1],
                            [xx2],
                            [yy2]])

        transform_matrix = np.array([[x1, -y1, 1, 0],
                                    [y1, x1, 0, 1],
                                    [x2, -y2, 1, 0],
                                    [y2, x2, 0, 1]])

        #print(np.linalg.inv(transform_matrix))

        value_matrix = np.linalg.inv(transform_matrix) @ end_matrix

        #print(value_matrix)

        _A = value_matrix[0][0]
        _B = value_matrix[1][0]
        _X = value_matrix[2][0]
        _Y = value_matrix[3][0]

        self.matrix = np.array([[_A, -_B, _X],
                    [_B, _A, _Y],
                    [0, 0, 1]])

        return self.matrix

    def calculate_affine_matrix(self, p1, p2, p3, mp1, mp2, mp3):        

        src = np.array([[0, 0], [0, 1], [1, 0]])
        dst = np.array([[1, 2], [2, 3], [3, 2]])

        self.affine_matrix = transform.AffineTransform()

    def calculate_matrix3D(self, src_points, dest_points):
        A = np.array([src_points[0], src_points[1], src_points[2], [1, 1, 1]])
        B = np.array([dest_points[0], dest_points[1], dest_points[2], [1, 1, 1]])
        self.matrix3D, residuals, rank, s = np.linalg.lstsq(A, B, rcond=None)

    def map3D(self, p):
        return np.around(np.dot(point, self.matrix3D)[:3], decimals=2)        

    # def map(self, p):
    #     self.in_x = p[0]
    #     self.in_y = p[1]

    #     mapPoint = np.dot(self.matrix, [[p[0]], [p[1]], [1]])

    #     self.out_x = mapPoint[0]
    #     self.out_y = mapPoint[1]

    #     return [self.out_x, self.out_y]

    def map(self, p):
        mp = self.matrix @ np.array([[p[0]], [p[1]], [1]])
        return mp[0][0], mp[1][0]


def find_angle(p1, p2):
    line = QLineF(p1, p2)
    return line.angle()

if __name__ == "__main__":
    cam_con_mapping = MappingMatrix()
    cam_con_mapping.calculate_matrix(((302, 72), (92, 72)), ((-486, -225), (-485, -108)))
    print(cam_con_mapping.map((302, 72)))
    print(cam_con_mapping.map((92, 72)))

    
    points1 = np.array([[302,72,0], [92,72,0], [0,0,0]])
    points2 = np.array([[-486,-225,0], [-485,-108,0], [0,0,0]])

    point = np.array([92,72,0])
    cam_con_mapping.calculate_matrix3D(points1, points2)    
    print(cam_con_mapping.map3D(point))


