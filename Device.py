from ast import Global
from signal import signal
import sys
import math

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import Qt, QEventLoop
from PyQt5.QtCore import QObject, QTimer, QThread, pyqtSignal, QRunnable, QThreadPool, pyqtSlot, QSettings, QRect, QRectF, QLineF, QPointF
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtCore import QMetaObject, QObject, Qt, QGenericArgument

from time import sleep
import numpy as np
from PyQt5.QtCore import QMutex, QMutexLocker, Q_ARG
import re
import VariableManager

from scurve_interpolator import *

class Device(QObject):
    responded = pyqtSignal(str)
    # stateChanged = pyqtSignal(bool)

    def __init__(self, COM='auto', baudrate=115200, default_cmd='', confirm_msg='Ok', is_open = True):
        super().__init__()
        self.COM = COM
        self.baudrate = baudrate
        self.default_cmd = default_cmd
        self.confirm_msg = confirm_msg
        self.active_receive_slot = True
        self.connected = False
        if is_open == True:
            self.init_in_other_thread()

    def init_in_other_thread(self):
        self.serial_device = QSerialPort()

        # Case 1: Auto connection
        if self.COM.lower() == 'auto' and self.default_cmd != '':
            for port_info in QSerialPortInfo.availablePorts():
                self.serial_device.setPortName(port_info.portName())
                self.serial_device.setBaudRate(self.baudrate)
                if self.serial_device.open(QtCore.QIODevice.ReadWrite):
                    self.serial_device.write((self.default_cmd + '\n').encode())
                    self.serial_device.waitForReadyRead(500)
                    response = self.serial_device.readLine().data().decode()
                    print(response)
                    if response.find(self.confirm_msg) > -1:
                        print(port_info.portName() + ' is connected \n')
                        self.serial_device.readyRead.connect(self.on_receive_feedback)
                        break
                    else:
                        self.serial_device.close()

        # Case 2: Manual connection
        if self.COM.lower() != 'auto':
            self.serial_device.setPortName(self.COM)
            self.serial_device.setBaudRate(self.baudrate)
            if self.serial_device.open(QtCore.QIODevice.ReadWrite):
                print(self.COM + ' is connected\n')
                self.serial_device.readyRead.connect(self.on_receive_feedback)
                # self.stateChanged.emit(True)
                self.connected = True
            else:
                print(self.COM + ' is not connected')
                # self.stateChanged.emit(False)
                self.connected = False

    def connect(self, port = 'COM1', baudrate = 115200):
        
        self.serial_device.setPortName(port)
        self.serial_device.setBaudRate(baudrate)
        
        if not self.serial_device.open(QtCore.QIODevice.ReadWrite):
            return False
        self.serial_device.readyRead.connect(self.on_receive_feedback)
        return True

    def delay_ms(self, msec):
        loop = QEventLoop()
        QTimer.singleShot(msec, loop.quit)
        loop.exec()

    def on_receive_feedback(self):
        if self.active_receive_slot == False:
            return
        
        if self.serial_device.canReadLine() == True:
            self.response_msg = self.serial_device.readLine().data().decode()
            self.responded.emit(self.response_msg)
            
            print(self.response_msg)

    def _read_line(self, timeout = 2000):
        start = time.time()
        while time.time() - start < timeout:
            # with QMutexLocker(self.mutex):
            self.serial_device.waitForReadyRead(1)
            if self.serial_device.canReadLine() == True:
                return self._read()
        return ""
    
    def _read_line_only(self, timeout = 2000):
        self.serial_device.waitForReadyRead(2)
        if self.serial_device.canReadLine() == True:
            return self.serial_device.readLine().data().decode()
            
        return ""
                

    def _read(self):    
        # with QMutexLocker(self.mutex):        
        self.response_msg = self.serial_device.readLine().data().decode()
        

        self.responded.emit(self.response_msg)
        
        return self.response_msg
    
    

class Robot(Device):
    gcode_done = pyqtSignal()
    received_position = pyqtSignal(list)
    received_input = pyqtSignal(str)
    def __init__(self, COM='None', baudrate=115200, is_open = True):
        self.port = super().__init__(COM=COM, baudrate=baudrate, default_cmd='IsDelta', confirm_msg='YesDelta', is_open=is_open)
        #print('robot init\n')
        self.responded.connect(self.get_gcode_response)
        self.scurve_tool = Scurve_Interpolator()

        self.X, self.Y, self.Z, self.W, self.U, self.V, self.F, self.A, self.S, self.E, self.J = 0, 0, 0, 0, 0, 0, 500, 8000, 30, 40, 255000

        self.done_msg = 'Ok'
        
        self.path_type = 'line'
        self.path_vel = 100
        self.path_angle = 0
        self.path_rad_angle = 0
        self.is_sync = False
        self.encoder = None
        self.last_gcode = ""

    def get_gcode_response(self, response = ""):
        #print("robot_fb:", response)
        if response.count(self.done_msg) > 0:
            self.gcode_done.emit()

        elif response.startswith("I") or response.startswith("D"):          
            self.received_input.emit(response)

        elif self.last_gcode.count('Position') > 0:
            if response.count(',') > 1:
                paras = response.split(',')
                for i in range(len(paras)):
                    if i == 0:
                        self.X = float(paras[i])
                    if i == 1:
                        self.Y = float(paras[i])
                    if i == 2:
                        self.Z = float(paras[i])
                    if i == 3:
                        self.W = float(paras[i])
                    if i == 4:
                        self.U = float(paras[i])
                    if i == 5:
                        self.V = float(paras[i])

                
                self.received_position.emit([self.X, self.Y, self.Z, self.W, self.U, self.V])

    def send_gcode(self, gcode = "G28", is_wait = True, time_out=10000):
        if is_wait == True:
            self.active_receive_slot = False

        if not gcode.endswith('\n'):
            gcode = gcode + '\n'

        if gcode.find('G04') < 0:
            # print(gcode)
            pass
        #print(gcode)
        if self.serial_device.isOpen():            
            self.serial_device.write(gcode.encode())
        else:
            print('Robot is not connected\n')
            self.thread().sleep(1)
            return

        self.last_gcode = gcode
        isMovingGcode = self.get_para(gcode)

        if is_wait == True:
            self.active_receive_slot = False
            # if isMovingGcode == True:
            #     self.__cal_move_time()
            #     time_out = self.scurve_tool.t_target * 1000 + 1000
                # print(self.scurve_tool.t_target)
            
            # self.serial_device.waitForReadyRead(int(time_out)) 
            response = self._read_line()

            self.active_receive_slot = True
            # print(response)
            return response

        return ''

    def get_para(self, gcode):
        paras = gcode.split()
        
        if paras[0].find('G01') < 0 and paras[0].find('G1') < 0:
            return False

        self.old_X, self.old_Y, self.old_Z = self.X, self.Y, self.Z

        for para in paras:
            if para[0] == 'X':
                self.X = float(para[1:])
            if para[0] == 'Y':
                self.Y = float(para[1:])
            if para[0] == 'Z':
                self.Z = float(para[1:])
            if para[0] == 'W':
                self.W = float(para[1:])
            if para[0] == 'U':
                self.U = float(para[1:])
            if para[0] == 'V':
                self.V = float(para[1:])
            if para[0] == 'F':
                self.F = float(para[1:])
            if para[0] == 'A':
                self.A = float(para[1:])
            if para[0] == 'S':
                self.S = float(para[1:])
            if para[0] == 'E':
                self.E = float(para[1:])
            if para[0] == 'J':
                self.J = float(para[1:])

        self.scurve_tool.max_acc = self.A
        self.scurve_tool.max_vel = self.F
        self.scurve_tool.max_jer = self.J
        self.scurve_tool.vel_start = self.S
        self.scurve_tool.vel_end = self.E

        return True

    def __cal_move_time(self):
        xy = math.sqrt(math.pow(self.X - self.old_X, 2) + math.pow(self.Y - self.old_Y, 2))
        xyz = math.sqrt(math.pow(xy, 2) + math.pow(self.Z - self.old_Z, 2))
        self.scurve_tool.p_target = xyz
        self.scurve_tool.start()    

    def input(self, pin):
        gcode = 'M07 I{0}'.format(pin)
        state = self.send_gcode(gcode)
        paras = state.split()
        for para in paras:
            if para[0] == 'V':
                return para[1:]

    def output(self, pin, state):
        if state != 0:
            gcode = 'M03 D{0}'.format(pin)
        else:
            gcode = 'M05 D{0}'.format(pin)

        return self.send_gcode(gcode)

    def sleep(self, time_ms=1000, sync=False):
        if sync == False:
            self.send_gcode('G04 P{}'.format(time_ms))
        else:
            if self.encoder == None:
                distance = self.path_vel * (float(time_ms) / 1000)
                # print('sleep distance: ' + str(distance))
                new_x = self.X + distance * math.cos(self.path_rad_angle)
                new_y = self.Y + distance * math.sin(self.path_rad_angle)
                old_F = self.F
                self.move(X = round(float(new_x)), Y = round(float(new_y)), F = abs(self.path_vel), sync=False)
                self.F = old_F
                self.scurve_tool.max_vel = self.F
            else:
                start = time.time()
                start_pos = self.encoder.read_position()
                while time.time() - start < time_ms:
                    cur_pos = self.encoder.read_position()
                    distance = cur_pos - start_pos
                    # print('sleep distance: ' + str(distance))
                    new_x = self.X + distance * math.cos(self.path_rad_angle)
                    new_y = self.Y + distance * math.sin(self.path_rad_angle)
                    old_F = self.F
                    start_pos = self.encoder.read_position()
                    self.move(X = new_x, Y = new_y, F = self.path_vel, sync=False)
                    
                self.F = old_F
                self.scurve_tool.max_vel = self.F

    def move(self, X=None, Y=None, Z=None, W=None, U=None, V=None, F=None, A=None, S=None, E=None, J=None, sync=False, time_offset=0):
        gcode = 'G01'

        self.old_X, self.old_Y, self.old_Z = self.X, self.Y, self.Z

        if X != None:
            self.X = X
            gcode = gcode + ' X' + str(X)
        if Y != None:
            self.Y = Y
            gcode = gcode + ' Y' + str(Y)
        if Z != None:
            self.Z = Z
            gcode = gcode + ' Z' + str(Z)
        if W != None:
            self.W = W
            gcode = gcode + ' W' + str(W)
        if U != None:
            self.U = U
            gcode = gcode + ' U' + str(U)
        if V != None:
            self.V = V
            gcode = gcode + ' V' + str(V)
        if F != None:
            self.F = F
            self.scurve_tool.max_vel = F
            gcode = gcode + ' F' + str(F)
        if A != None:
            self.A = A
            self.scurve_tool.max_acc = A
            gcode = gcode + ' A' + str(A)
        if S != None:
            self.S = S
            self.scurve_tool.vel_start = S
            gcode = gcode + ' S' + str(E)
        if E != None:
            self.E = E
            self.scurve_tool.vel_end = E
            gcode = gcode + ' E' + str(E)
        if J != None:
            self.J = J
            self.scurve_tool.max_jer = J
            gcode = gcode + ' J' + str(J)

        if sync == False:
            return self.send_gcode(gcode)
        else:
            new_x, new_y = self.scurve_tool.find_sync_point(self.old_X, self.old_Y, self.old_Z, self.X, self.Y, self.Z, self.path_vel, self.path_angle, time_offset)
            
            new_x = round(float(new_x), 2)
            new_y = round(float(new_y), 2)

            # return self.send_gcode('G01 X{0} Y{1} Z{2} W{3} U{4} V{5} F{6} A{7} S{8} E{9} J{10}'.format(new_x, new_y, self.Z, self.W, self.U, self.V, self.F, self.A, self.S, self.E, self.J))
            return self.send_gcode('G01 X{0} Y{1} Z{2} W{3} F{4} A{5} S{6} E{7} J{8} U{9}'.format(new_x, new_y, self.Z, self.W, self.F, self.A, self.S, self.E, self.J, self.U))

    def move_step(self, direction:str, step):
        direction = direction.lower()
        step = float(step)
        if direction == 'left':
            pos = 'X' + str(self.X - step)
        if direction == 'right':
            pos = 'X' + str(self.X + step)
        if direction == 'forward':
            pos = 'Y' + str(self.Y + step)
        if direction == 'backward':
            pos = 'Y' + str(self.Y - step)
        if direction == 'up':
            pos = 'Z' + str(self.Z + step)
        if direction == 'down':
            pos = 'Z' + str(self.Z - step)

        gcode = 'G01 ' + pos
        self.send_gcode(gcode)


    def move_point(self, p):
        self.move(X=p[0], Y=p[1], Z=p[2])

    def go_home(self):
        self.send_gcode('G28')
        self.send_gcode('Position')

    def set_sync_path(self, path='line', con_vel=100, con_angle=0, encoder= None):
        self.path_type = path
        self.path_vel = con_vel
        self.path_angle = con_angle
        self.path_rad_angle = math.radians(con_angle)
        self.is_sync = True
        self.encoder = encoder

    def set_sync_path_vel(self, con_vel=100):
        self.path_vel = con_vel

    def set_tracking(self, tracking):
        self.set_sync_path(tracking.path, tracking.v)

    def stop_sync(self):
        self.is_sync = False

class Encoder(Device):
    gotValue = pyqtSignal(float)

    def __init__(self, COM='auto', baudrate=115200):
        super().__init__(COM=COM, baudrate=baudrate, default_cmd='M316 0', confirm_msg='Ok')
        print('encoder init')
        self.current_position = 0
        self.responded.connect(self.to_position_value)

    def read_continuously(self, interval = 100):
        self.serial_device.write('M317 T{0}\n'.format(interval).encode())

    def stop_read_continuously(self):
        self.serial_device.write('M316 0\n'.encode())

    def read_position(self):
        t0 = time.time()
        self.serial_device.write('M317\n'.encode())
        self.serial_device.waitForBytesWritten()
        value = self.to_position_value(self._read_line())
        
        # print('read time: ' + str(time.time() - t0))
        return value

    def cal_velocity(self):
        last = self.read_position()
        start = time.time()
        
        self.thread().msleep(2000)
        now = self.read_position()
        self.velocity_m = (now - last) / (time.time() - start)
        return self.velocity_m

    def to_position_value(self, st):
        if st == '':
            return 0

        if st[0] != 'P':
            return 0

        st = st.replace('P', '').replace('\r', '').replace('\n', '')
        # print(st)

        self.current_position = float(st)

        self.is_requesting = False
        
        self.gotValue.emit(self.current_position)

        return self.current_position

class VirtualEncoder(QObject):
    def __init__(self):
        super().__init__()
        self.start(0)

    def start(self, vel):
        self.velocity = vel
        self.last_time = time.time()
        # self.last_position = 0
        self.current_position = 0

    def change_velocity(self, vel):
        self.read_position()
        self.velocity = vel

    def stop(self):
        self.velocity = 0

    def read_position(self):
        self.current_time = time.time()
        distance = self.velocity * (self.current_time - self.last_time)
        self.last_time = time.time()
        self.current_position = round(self.current_position + distance, 3)
        return self.current_position

class SubEncoder():
    def __init__(self, conveyor_hub, name):
        self.conveyor_hub = conveyor_hub
        self.name = name
        self.value = 0

    def read_position(self, is_wait=False):
        self.conveyor_hub.set_current_encoder(self.name)
        self.value = self.conveyor_hub.read_position(is_wait=True)
        return self.value

class ConveyorStation(Device):
    '''
        Sensor:
            Auto Read Input: 
                Gcode:      M443 I1 I2 I3
                Response:   I1:0
                            I2:0
                            I3:0
            Turn Off Auto Read Input:
                Gcode:      M444 I1 I2 I3
            Read Input:
                Gcode:      M442 I1 I2 I3
                Response:   I1:0
                            I2:0
                            I3:0
        Encoder:
            Absolute Mode:
                Gcode:      M420 C1 C2 C3
            Auto Read:
                Gcode:      M421 C1:300 C3:500
            Read Value:
                Gcode:      M422 C1 C2 C3
            Reset Value:
                Gcode:      M423 C1 C2 C3

        Conveyor:
            Position Mode:
                Gcode:      M400 C1:0 C2:0 C3:0
            Speed in Position Mode:
                Gcode:      M402 C1:100 C2:200 C3:300
            Move to Position:
                Gcode:      M403 C1:1000 C3:500
            Speed Mode:
                Gcode:      M400 C1:1 C2:1 C3:1
            Speed in Speed Mode:
                Gcode:      M401 C1:50 C3:-200

        Config:
            Step/mm:
                M460 C1:38.81
            Pulse/Rev:
                M461 C1:5.12 C3:5.12
                

    '''


    sensor_state_changed = pyqtSignal(str, int)
    encoder_position_changed = pyqtSignal(str, float)
    selected_encoder_position_changed = pyqtSignal(float)
    move_request = pyqtSignal(str, float, float)

    def __init__(self, COM='None', baudrate=115200, is_open = True):
        super().__init__(COM=COM, baudrate=baudrate, default_cmd='M421 C1=0 C2=0 C3=0', confirm_msg='Ok', is_open=is_open)
        print('conveyor init')

        self.responded.connect(self.process_response)

        self.sub_encoders = []
        self.sub_encoders.append(SubEncoder(self, 'C1'))
        self.sub_encoders.append(SubEncoder(self, 'C2'))
        self.sub_encoders.append(SubEncoder(self, 'C3'))

        self.is_invert = {'C1':False, 'C2':False, 'C3':False}

        self.is_thread_busy = False

        self.exit_loop = False

        self.current_position = {'C1':0, 'C2':0, 'C3':0}
        self.current_sensor = {'I1':0, 'I2':0, 'I3':0}

        self.current_encoder = 'C3'

        self.set_encoder_invert('C3', True)
        self.move_request.connect(self.move)

    def run(self):
        self.init_in_other_thread()
        # print('vel', self.cal_real_velocity('C3'))
        # self.move('C3', vel=100)
        # self.move('C1', vel=100)

        self.active_receive_slot = False

        self.send('M420 C1=1 C2=1 C3=1\n')
        self._read_line()
        self.send('M443 I1 I2 I3\n')
        self._read_line()
        self.send('M421 C3=0\n')
        self._read_line()
        self.active_receive_slot = True

        # while True:
        #     self.sub_encoders[2].read_position()

    def process_response(self, response):
        # print('Step: 3 - ', response)
        lines = response.split('\n')

        for line in lines:           
            if line == '':
                continue

            # Encoder response
            if line[0] == 'P':
                ls = line.split('P')

                for l in ls:
                    if l == '':
                        continue

                    l = 'P' + l
                    value = l[3:]
                    name = l[0:2]
                    id = int(l[1])
                    
                    value = float(value)

                    if (self.is_invert['C{}'.format(id)] == True):
                        value = 0 - value

                    self.current_position[name] = value
                    # print('conveyor value {}: {}'.format(name, value))
                    self.encoder_position_changed.emit(name, value)                    
                    VariableManager.instance.set(name, value)
                    if name[1] == self.current_encoder[1]:
                        # print('Step: 4')
                        self.selected_encoder_position_changed.emit(value)
            
            # Sensor response
            if line[0] == 'I':
                value = int(line[3:])
                name = line[0:2]
                id = int(line[1])

                # if self.current_sensor[name] == 0 and value == 1:
                #     self.move_request.emit('C1', 0, 0)
                #     pass
                    
                self.current_sensor[name] = value
                # print('encoder value {}: {}'.format(name, value))
                self.sensor_state_changed.emit(name, value)
                VariableManager.instance.set(name, value)
                return value
        
        
    def send(self, msg):
        
        if self.serial_device == None or self.serial_device.isOpen() == False:
            print('Not open')
            return
        
        if not msg.endswith('\n'):
            msg = msg + '\n'
        
        self.serial_device.write(msg.encode())
        self.serial_device.waitForBytesWritten()
        
    def move(self, name='C1', pos=0, vel=100):
        if self.serial_device.isOpen() == False:
            return
        
        self.active_receive_slot = False
        
                    
        if pos == None or pos == 0:
            cmd = 'M400 {0}=1\n'.format(name)
            
            self.send(cmd)
            self._read_line()

            cmd = 'M401 {0}={1}\n'.format(name, vel)
            self.send(cmd)
            self._read_line()
        else:
            cmd = 'M400 {0}=0\n'.format(name)
            self.send(cmd)
            self._read_line()

            cmd = 'M402 {0}={1}\n'.format(name, vel)
            self.send(cmd)
            self._read_line()

            cmd = 'M403 {0}={1}\n'.format(name, pos)
            self.send(cmd)
            self._read_line(pos/vel * 1000 + 2000)

        self.active_receive_slot = True

    def set_current_encoder(self, name):
        self.current_encoder = name

    def to_position_value(self, st:str):
        if st == '':
            return 0
        
        st = st.replace('\r', '').replace('\n', '')

        if st[0] == 'P':
            value = st[3:]            
            name = st[0:2]
            id = int(st[1])
            # if bool(re.match(r'^-?\d+(?:\.\d+)?$', value)):
            self.current_position[name] = float(value)
            # print('conveyor value: ', self.current_position[name])
            self.encoder_position_changed.emit(name, self.current_position[name])                    
            VariableManager.instance.set(name, value)

            self.current_position[name]
            
        return 0       
    
    def to_sensor_value(self, st:str):
        if st == '':
            return 0
        
        st = st.replace('\r', '').replace('\n', '')

        # print('sensor response: ', st)

        # Sensor state

        if st[0] == 'I':
            value = int(st[3:])
            name = st[0:2]
            id = int(st[1])
            self.current_position[name] = value
            self.sensor_state_changed.emit(name, value)
            VariableManager.instance.set(name, value)
            # print('sensor value: ', value)
            return value

    def set_encoder_invert(self, name='all', is_inv=True):
        if name == 'all':
            self.is_invert = {'C1':is_inv, 'C2':is_inv, 'C3':is_inv}
        else:
            self.is_invert[name] = is_inv

    def read_position(self, is_wait=False):
        if is_wait == False:
            self.active_receive_slot = True

        cmd = 'M422 {0}\n'.format(self.current_encoder)
        
        self.send(cmd)

        #-----------
        
        if is_wait == False:
            return
        
        self.active_receive_slot = False

        value = self.to_position_value(self._read_line())

        self.active_receive_slot = True
        
        if (self.is_invert[self.current_encoder] == True):
            value = 0 - value

        self.pos_value = value

        return value
    
    def read_sensor(self, is_wait=False):
        cmd = 'M442 I1 I2 I3'
        # print('sensor:', cmd)
        self.send(cmd)
        
        if is_wait == False:
            return

        self.active_receive_slot = False
        value = self.to_sensor_value(self._read_line())
        self.active_receive_slot = True
    
        return value

    def cal_real_velocity(self, name = 'C1'):
        id = int(name[1:]) - 1
        last = self.sub_encoders[id].read_position(is_wait=True)
        print('last ', last)
        if last == 0:            
            return 0
        
        # print(last)
        # print('last: ' + str(last))
        start = time.time()
        
        self.delay_ms(1000)
        now = self.sub_encoders[id].read_position(is_wait=True)
        print('now ', last)
        if now == 0:
            return 0
        # print('now: ' + str(last))
        self.velocity_m = (now - last) / (time.time() - start)
        return self.velocity_m

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # robot = Robot('COM25', is_open=True)
    # angle = QLineF(QPointF(-74.49, -202.99), QPointF(125.51, -209.49)).angle()
    # robot.set_sync_path(path='line', con_vel=100, con_angle=0)
    # # robot.send_gcode('G28')
    # robot.send_gcode('G01 X-350 Y-70')
    # # robot.send_gcode('G01 Z-905')
    # robot.sleep(time_ms=5000, sync=True)

    # robot = Robot('COM28', is_open=True)
    # angle = QLineF(QPointF(-74.49, -202.99), QPointF(125.51, -209.49)).angle()
    # robot.set_sync_path(path='line', con_vel=100, con_angle=-angle)
    # robot.send_gcode('G28')
    # robot.send_gcode('G01 Z-665')
    # robot.send_gcode('G01 X-250 Y-20')
    
    # robot.sleep(time_ms=3000, sync=True)

    # vir_encoder = VirtualEncoder()

    # con_station = ConveyorStation(COM='auto')
    # con_station.set_encoder_invert('C3', True)

    # vir_encoder.start(100)
    # print('vir ', vir_encoder.read_position())
    # print(con_station.sub_encoders[2].read_position())
    # con_station.move(name='C3', pos = 500)
    # print(con_station.sub_encoders[2].read_position())
    # print('vir ', vir_encoder.read_position())

    # vir_encoder.change_velocity(-100)
    # con_station.move(name='C3', pos = -500)
    # print(con_station.sub_encoders[2].read_position())
    # print('vir ', vir_encoder.read_position())

    # ---------- Conveyor ----------
    conveyor_station = ConveyorStation(COM='COM11', is_open= False)
    conveyorThread = QThread()    
    conveyor_station.moveToThread(conveyorThread)
    conveyorThread.started.connect(conveyor_station.run)
    conveyorThread.start()

    # arg1 = QGenericArgument("str", 'C1')
    # arg2 = QGenericArgument("float", 0)
    # arg3 = QGenericArgument("float", 100)
    # QMetaObject.invokeMethod(conveyorThread, "move", Qt.QueuedConnection, arg1, arg2, arg3)

    timer2 = QTimer()
    timer2.timeout.connect(conveyor_station.read_sensor, Qt.QueuedConnection)
    timer2.start(1000)

    app.exec_()
    

    