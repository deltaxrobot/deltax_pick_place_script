import sys,time
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QScrollBar,QSplitter,QTableWidgetItem,QTableWidget,QComboBox,QVBoxLayout,QGridLayout,QDialog,QWidget, QPushButton, QApplication, QMainWindow,QAction,QMessageBox,QLabel,QTextEdit,QProgressBar,QLineEdit
from PyQt5.QtCore import QCoreApplication, QObject, pyqtSignal, QByteArray
from PyQt5.QtNetwork import QTcpServer, QTcpSocket, QHostAddress

import socket
from threading import Thread
from socketserver import ThreadingMixIn
import numpy as np
import struct
import Tracking
import Device
import VariableManager

class SocketCommand(QObject):
    read_mess = pyqtSignal(str)
    stateChanged = pyqtSignal(bool)

    def __init__(self, host = None, port = None):
        super().__init__()
        self.host = host
        self.port = port
        self.time_mesure = time.time()
        self.input_data = QByteArray()

    def open(self):
        VariableManager.instance.set("server_state", False)
        self.server_socket = QTcpServer()
        
        ret = self.server_socket.listen(QHostAddress(self.host), self.port)
        self.server_socket.newConnection.connect(self.handle_new_connection)
        self.clients = []

        if ret == True:
            print("Listening {0}:{1}".format(self.host, self.port))
        else:
            print("Fail to open server\n")

    def handle_new_connection(self):
        client = self.server_socket.nextPendingConnection()
        client.readyRead.connect(self.handle_client_data)
        self.clients.append(client)
        # print(client)

    def handle_client_data(self):
        client = self.sender()
        if type(client) == QTcpSocket:

            time_sleep = 0
            while not client.canReadLine():
                self.thread().msleep(5)
                time_sleep += 1
                if time_sleep == 50:
                    break

            self.input_data += client.readAll()

            if self.input_data == "ExternalScript\n":
                self.send_msg_to_clients("deltax".encode())
                self.input_data.clear()
                self.stateChanged.emit(True)
                return

            # print (self.input_data.indexOf('\n'))

            if self.input_data.indexOf('\n') > 6:
                # print ("emit sig")
                self.read_mess.emit(self.input_data.data().decode())
                self.input_data.clear()

    def send_msg_to_clients(self, data):
        size = -1
        for client in self.clients:
            size = client.write(data)
            client.flush()
        return size

class ImageServer(SocketCommand):
    got_objects = pyqtSignal(list)

    send_yesdelta_s = pyqtSignal()

    def __init__(self, host = None, port = None, result_type = "Orienty"):
        super().__init__(host, port)
        self.result_type = result_type
        self.read_mess.connect(self.process_object_infos)
        self.obj_type_list = []

    def process_object_infos(self, data):
        
        infos = []

        if self.result_type == "Segment":
            data = data.split('\n')
            data = data[len(data) - 2]

        prefix = "#Object = "
        if data[0:len(prefix)] == prefix:
            data = data[len(prefix):]
            #data = 0,200,400,100,50,125;
            obj_infos = data.split('; ')

            for obj_info in obj_infos:                
                paras = obj_info.split(', ')
                if len(paras) < 6:
                    continue
                try:
                    obj_type = paras[0]

                    for index in range(0, len(self.obj_type_list)):
                        if obj_type == self.obj_type_list[index]:
                            obj_type = index
                            break

                    paras = list(map(float, paras[1:]))
                    paras = list(map(int, paras))

                    info = []
                    info.append(obj_type)  #(id)
                    if self.result_type == "Segment":
                        for index in range(0, len(paras), 2):
                            if index + 1 < len(paras):
                                info.append((paras[index], (paras[index + 1]))) #(x, y)
                    else:
                        info.append((paras[0], (paras[1]))) #(x, y)
                        info.append((paras[2], (paras[3]))) #(w, h)
                        info.append(paras[4])  #(a)

                    infos.append(info)

                except:
                    return
        else:
            return

        self.got_objects.emit(infos)

    def send_yesdelta(self):
        self.send_msg_to_clients("deltax".encode())
        pass

    def send_image(self, input:np.ndarray):
        def __getSed(colByte,sedNum):
            if 1024 < colByte - sedNum:
                return 1024
            return colByte - sedNum

        height, width, channels = input.shape
        widthBytes = width.to_bytes(4, 'big')[::-1]
        heightBytes = height.to_bytes(4, 'big')[::-1]
        channelsBytes = channels.to_bytes(4, 'big')[::-1]
        shapeBytes = widthBytes + heightBytes + channelsBytes
        self.send_msg_to_clients(shapeBytes)
        # print(shapeBytes)
        #send image data
        SIZE_OF_BYTE = 1
        colByte = width*channels * SIZE_OF_BYTE
        for i in range(0,height,1):
            data = input[i].tobytes()
            sedNum = 0
            while (sedNum < colByte):
                sed = __getSed(colByte,sedNum)
                buf = data[sedNum:sedNum+sed]
                sendSize = self.send_msg_to_clients(buf)
                # print(buf)
                if (sendSize == -1):
                    break
                sedNum += sendSize
