from signal import signal
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from time import sleep
from PyQt5.QtCore import QVariant, pyqtSignal
from PyQt5.QtCore import QObject, QSettings, QRect, QPointF, QPoint, QLineF
from Device import *
import time
import cv2
import traceback
from PyQt5.QtCore import QMutex, QSemaphore
from queue import Queue
import math
id_counter = 0

class TrackingObject(QObject):
    def __init__(self, x=100, y=100, w=10, l=10, a=0, start_pos=0, error=3):
        global id_counter
        super().__init__()
        self.start_x = x
        self.start_y = y
        self.cur_x = x
        self.cur_y = y

        self.width = w
        self.length = l
        # if w < l:
        #     self.width = w
        #     self.length = l
        # else:
        #     self.width = l
        #     self.length = w

        self.angle = a
        self.start_encoder_pos = start_pos
        self.cur_encoder_pos = start_pos
        self.error = error
        self.id = -1
        # id_counter += 1
        self.is_picked = False
        self.is_passed = False
        self.obj_type = 0

        

    def set_rect(self, rect):
        self.rect = rect
        box = np.int0(cv2.boxPoints(rect))

    def print(self, console = True):
        msg = 'id={} x={} y={} a={}'.format(self.obj_type, self.cur_x,
                self.cur_y, self.angle)
        if console == True:
            print(msg)
        else:
            return msg

    def pos_print(self, console = True):
        msg = 'id={} x={} y={}'.format(self.obj_type, self.cur_x, self.cur_y)
        if console == True:
            print(msg)
        else:
            return msg
        
    #def cal_iou

    def is_same(self, other_obj, _iou = 0.5, _distanceThreshold = 30):
        # thres = 0.5
        # if abs(self.cur_x - other_obj.cur_x) > self.length * self.error:
        #     return False

        # if abs(self.cur_y - other_obj.cur_y) > self.width * self.error:
        #     return False
        
        # return True

        # Check IoU
        iou = self.calculateIoU(other_obj)
        if iou >= _iou:
            return True

        # Check distance
        distance = self.distanceToPoint(other_obj)
        if distance <= _distanceThreshold:
            return True

        return False

    def calculateIoU(self, other_obj):
        # Calculate overlap area
        x_overlap = max(0.0, min(self.cur_x + self.width / 2, other_obj.cur_x + other_obj.width / 2) -
                             max(self.cur_x - self.width / 2, other_obj.cur_x - other_obj.width / 2))
        y_overlap = max(0.0, min(self.cur_y + self.length / 2, other_obj.cur_y + other_obj.length / 2) -
                             max(self.cur_y - self.length / 2, other_obj.cur_y - other_obj.length / 2))
        overlapArea = x_overlap * y_overlap

        # Calculate union area
        box1Area = self.width  * self.length
        box2Area = other_obj.width * other_obj.length
        unionArea = box1Area + box2Area - overlapArea

        # Calculate IoU
        iou = overlapArea / unionArea
        return iou
    
    def distanceToPoint(self, other_obj):
        return math.sqrt((self.cur_x - other_obj.cur_x) ** 2 + (self.cur_y - other_obj.cur_y) ** 2)

    
    def overlap_percentage(self, r1, r2, threshold):
        # Tính toán tọa độ các điểm của hai hình chữ nhật
        r1_x1 = r1[0] - r1[2] / 2 * math.cos(math.radians(r1[4])) + r1[3] / 2 * math.sin(math.radians(r1[4]))
        r1_y1 = r1[1] - r1[2] / 2 * math.sin(math.radians(r1[4])) - r1[3] / 2 * math.cos(math.radians(r1[4]))
        r1_x2 = r1[0] + r1[2] / 2 * math.cos(math.radians(r1[4])) + r1[3] / 2 * math.sin(math.radians(r1[4]))
        r1_y2 = r1[1] + r1[2] / 2 * math.sin(math.radians(r1[4])) - r1[3] / 2 * math.cos(math.radians(r1[4]))
        r1_x3 = r1[0] + r1[2] / 2 * math.cos(math.radians(r1[4])) - r1[3] / 2 * math.sin(math.radians(r1[4]))
        r1_y3 = r1[1] + r1[2] / 2 * math.sin(math.radians(r1[4])) + r1[3] / 2 * math.cos(math.radians(r1[4]))
        r1_x4 = r1[0] - r1[2] / 2 * math.cos(math.radians(r1[4])) - r1[3] / 2 * math.sin(math.radians(r1[4]))
        r1_y4 = r1[1] - r1[2] / 2 * math.sin(math.radians(r1[4])) + r1[3] / 2 * math.cos(math.radians(r1[4]))

        r2_x1 = r2[0] - r2[2] / 2 * math.cos(math.radians(r2[4])) + r2[3] / 2 * math.sin(math.radians(r2[4]))
        r2_y1 = r2[1] - r2[2] / 2 * math.sin(math.radians(r2[4])) - r2[3] / 2 * math.cos(math.radians(r2[4]))
        r2_x2 = r2[0] + r2[2] / 2 * math.cos(math.radians(r2[4])) + r2[3] / 2 * math.sin(math.radians(r2[4]))
        r2_y2 = r2[1] + r2[2] / 2 * math.sin(math.radians(r2[4])) - r2[3] / 2 * math.cos(math.radians(r2[4]))
        r2_x3 = r2[0] + r2[2] / 2 * math.cos(math.radians(r2[4])) - r2[3] / 2 * math.sin(math.radians(r2[4]))
        r2_y3 = r2[1] + r2[2] / 2 * math.sin(math.radians(r2[4])) + r2[3] / 2 * math.cos(math.radians(r2[4]))

        # Kiểm tra xem hai hình chữ nhật có giao nhau hay không
        if r1_x1 > r2_x2 or r1_x2 < r2_x1 or r1_y1 > r2_y2 or r1_y2 < r2_y1:
            return 0.0  # Không chồng lên nhau

        # Tính diện tích của phần giao nhau
        overlap_x1 = max(r1_x1, r2_x1)
        overlap_y1 = max(r1_y1, r2_y1)
        overlap_x2 = min(r1_x2, r2_x2)
        overlap_y2 = min(r1_y2, r2_y2)
        overlap_area = (overlap_x2 - overlap_x1) * (overlap_y2 - overlap_y1)

        # Tính tỷ lệ phần giao nhau so với diện tích tổng của hai hình chữ nhật
        total_area = r1[2] * r1[3] + r2[2] * r2[3] - overlap_area
        overlap_percentage = overlap_area / total_area

        # So sánh tỷ lệ phần giao nhau với ngưỡng độ chồng
        if overlap_percentage >= threshold:
            return overlap_percentage  # Hai hình chữ nhật chồng lên nhau
        else:
            return 0.0  # Không chồng lên nhau



class TrackingManager(QObject):
    objects_updated = pyqtSignal(list, float)
    display_obj_request = pyqtSignal(str)
    object_at_sensor = pyqtSignal(int, int)
    position_request = pyqtSignal()

    got_con_speed = pyqtSignal(float)
    got_con_position = pyqtSignal(float)

    def __init__(self, con_angle=0):
        super().__init__()
        self.con_angle = con_angle
        self.con_rad_angle = math.radians(con_angle)

        self.tracking_objects = []
        self.id_counter = 0

        self.move_direction = 'X'
        self.conveyor_pos = 0
        self.velocity_m = 0

        self.mutex = QMutex()
        self.semaphore = QSemaphore(0)

        self.sensor_state = [0, 0, 0]

        self.captured_conveyor_pos = 1

        self.time_update_last = time.time()

        self.check_new_objects_request = False
        self.new_objects = None
        
        self.max_t = 0
        self.list_picked = []

        self.time_captured = time.time()
        self.time_captured_last = time.time()

        self.conveyor_pos_captured_last = 0
        self.conveyor_vel_last = 0
        self.conveyor_vel = 97

        self.cal_con_speed_offset_time(100)

        self.robot1_limit1 = 1200
        self.robot1_limit2 = 1500

        self.robot2_limit1 = 350
        self.robot2_limit2 = 500
        
        self.is_encoder_reversed = False
        self.is_started = False

        self.loadRobotPickingZone()

    def loadRobotPickingZone(self):
        _zone1 = QPointF(VariableManager.instance.get("pickingZone1", QPointF(600, 900)))
        _zone2 = QPointF(VariableManager.instance.get("pickingZone2", QPointF(1000, 1200)))

        self.robot1_limit1 = _zone1.x()
        self.robot1_limit2 = _zone1.y()

        print(_zone1)

        self.robot2_limit1 = _zone2.x()
        self.robot2_limit2 = _zone2.y()

    def start(self):
        self.is_started = True
    
    def stop(self):
        self.is_started = False

    def cal_con_speed_offset_time(self, speed):
        self.con_speed_offset_time = (speed * 10)/(300 * 300)

    def capture_moment(self):
        if self.captured_conveyor_pos == None:
            self.position_request.emit()
            return
        self.captured_conveyor_pos = None
        self.time_captured = time.time()
        self.position_request.emit()

    def process_sensor(self, id, value):
        if id >= 1 and id < 4:
            self.sensor_state[id - 1] = value
            self.object_at_sensor.emit(id - 1, value)
    
    def check_objects(self):
        # objs = self.tracking_objects[:]
        self.objects_updated.emit(self.tracking_objects, self.time_update_last)       


    def add_new_objects(self, objs):
        _objs = []
        for obj in objs:
            tracking_obj = TrackingObject(x=obj[0], y=obj[1], w=obj[2], l=obj[3], a=obj[4], start_pos=obj[5], error=obj[6])
            tracking_obj.obj_type = obj[7]
            _objs.append(tracking_obj)

        #or self.is_started == False
        if len(_objs) == 0:
            return
        
        if self.captured_conveyor_pos != None:
            for i in range(len(_objs)):
                _objs[i].start_encoder_pos = self.captured_conveyor_pos
        else:
            for i in range(len(_objs)):
                _objs[i].start_encoder_pos = None                

        self.check_new_objects_request = True
        # self.mutex.lock()
        self.new_objects = _objs
        # self.mutex.unlock()
        # self.position_request.emit()

    def add_start_encoder_pos_for_new_objs(self):
        # self.mutex.lock()
        if self.new_objects == None:
            # self.mutex.unlock()
            return
        
        for i in range(len(self.new_objects)):
            if self.new_objects[i].start_encoder_pos == None:
                self.new_objects[i].start_encoder_pos = self.captured_conveyor_pos
        # self.mutex.unlock()

    def check_update_new_objects(self):      
        if self.new_objects == None:
            return
        
        self.update_new_position_for_new_objects()

        #
        _new_tracking_objects = self.tracking_objects

        for display_obj in self.new_objects:
            
            if type(display_obj) != TrackingObject:
                print(type(display_obj))
                continue
            is_new = True
            for i in range(0, len(self.tracking_objects)):
                tracking_obj = self.tracking_objects[i]
                if display_obj.is_same(tracking_obj):
                    is_new = False
                    # cap nhat neu obj moi to hon cu
                    if display_obj.width > tracking_obj.width and display_obj.length > tracking_obj.length:
                        self.tracking_objects[i] = display_obj
                        #
                        _new_tracking_objects[i] = display_obj
                    break

            if is_new == True:
                #self.tracking_objects.append(display_obj)
                #
                _new_tracking_objects.append(display_obj)

        self.new_objects = None
        #
        self.tracking_objects = _new_tracking_objects

    def set_clear_limit(self, limit):
        self.clear_limit = limit

    def delete_object(self, id):
        self.mutex.lock()
        self.list_picked.append(id)
        self.mutex.unlock()        

    def clear_objects(self):
        self.tracking_objects.clear()
        self.id_counter = 0

    def update_conveyor_position(self, _encoder_pos):
        try:
            if self.is_encoder_reversed == True:
                _encoder_pos = 0 - _encoder_pos

            _delay_request = time.time() - self.time_captured
            _time_for_vel = self.time_captured - self.time_captured_last
            self.time_captured_last = self.time_captured

            _pos_for_vel = _encoder_pos - self.conveyor_pos_captured_last
            self.conveyor_pos_captured_last = _encoder_pos

            _con_vel = 100
            if abs(_time_for_vel) < 0.2:
                _con_vel = 0
            else:
                _con_vel = _pos_for_vel / _time_for_vel

            self.conveyor_pos = _encoder_pos + _con_vel * _delay_request

            self.mutex.lock()

            # tinh van toc on dinh
            self.conveyor_vel = (self.conveyor_vel_last + _con_vel) / 2
            self.got_con_speed.emit(self.conveyor_vel)

            if self.is_started == False:
                self.got_con_position.emit(self.conveyor_pos)

            self.conveyor_vel_last = _con_vel

            if self.captured_conveyor_pos == None:
                self.captured_conveyor_pos = self.conveyor_pos
                self.add_start_encoder_pos_for_new_objs()
            
            for i in range(0, len(self.tracking_objects)):
                self.tracking_objects[i].cur_encoder_pos = self.conveyor_pos
                distance = self.tracking_objects[i].cur_encoder_pos - self.tracking_objects[i].start_encoder_pos
                self.tracking_objects[i].cur_x = self.tracking_objects[i].start_x + distance * math.cos(self.con_rad_angle)
                self.tracking_objects[i].cur_y = self.tracking_objects[i].start_y + distance * math.sin(self.con_rad_angle)

            self.check_update_new_objects()

            self.time_update_last = time.time()

            display_msg = ''

            _new_tracking_objects = []
            for i in range(0, len(self.tracking_objects)):
                obj = self.tracking_objects[i]
                if obj.cur_x <= self.clear_limit:
                    display_msg += obj.print(console = False) + '\n'
                    _new_tracking_objects.append(self.tracking_objects[i])
                else:
                    pass
                    #print("DeleteObj: ", i)

            self.tracking_objects = _new_tracking_objects

            self.display_obj_request.emit(display_msg)
            self.mutex.unlock()
            
        except Exception as e:
            # In ra lỗi
            print(e)
            traceback.print_exc()

    def getObjectForPick1(self):
        self.mutex.lock()
        _pick_para = []

        if len(self.tracking_objects) == 0:
            self.mutex.unlock()
            return _pick_para

        _current_time = time.time()
        _distance = self.conveyor_vel * (_current_time - self.time_update_last)
        self.time_update_last = _current_time
        for i in range(0, len(self.tracking_objects)):
            self.tracking_objects[i].cur_x += _distance * math.cos(self.con_rad_angle)
            self.tracking_objects[i].cur_y += _distance * math.sin(self.con_rad_angle)

        for i in range(0, len(self.tracking_objects)):
            obj = self.tracking_objects[i]
            if obj.cur_x >= self.robot1_limit1 and obj.cur_x <= self.robot1_limit2 and obj.is_passed == False:
                # self.id_counter += 1
                # if self.id_counter % 2 == 0:                        
                #     self.tracking_objects[i].is_passed = True
                #     continue
                _pick_para = [round(obj.cur_x, 2), round(obj.cur_y, 2), round(obj.angle, 4), self.time_update_last, self.conveyor_vel, obj.obj_type]
                self.tracking_objects.pop(i)
                
                break

        self.mutex.unlock()
        return _pick_para

    def getObjectForPick2(self):
        self.mutex.lock()
        _pick_para = []

        if len(self.tracking_objects) == 0:
            self.mutex.unlock()
            return _pick_para

        _current_time = time.time()
        _distance = self.conveyor_vel * (_current_time - self.time_update_last)

        self.time_update_last = _current_time
        for i in range(0, len(self.tracking_objects)):
            self.tracking_objects[i].cur_x += _distance * math.cos(self.con_rad_angle)
            self.tracking_objects[i].cur_y += _distance * math.sin(self.con_rad_angle)

        for i in range(0, len(self.tracking_objects)):
            obj = self.tracking_objects[i]
            if obj.cur_x >= self.robot2_limit1 and obj.cur_x <= self.robot2_limit2:
                # self.id_counter += 1
                # if self.id_counter % 2 == 0:
                #     self.tracking_objects[i].is_passed = True
                #     continue
                _pick_para = [round(obj.cur_x, 2), round(obj.cur_y, 2), round(obj.angle, 4), self.time_update_last, self.conveyor_vel, obj.obj_type]
                self.tracking_objects.pop(i)
                break

        self.mutex.unlock()
        return _pick_para

    def update_new_position_for_new_objects(self):
        # print('4')
        for i in range(0, len(self.new_objects)):
            self.new_objects[i].cur_encoder_pos = self.conveyor_pos
            # print('{}: c={}, s={}'.format(i, self.new_objects[i].cur_encoder_pos, self.new_objects[i].start_encoder_pos))
            distance = self.new_objects[i].cur_encoder_pos - self.new_objects[i].start_encoder_pos
            self.new_objects[i].cur_x = self.new_objects[i].start_x + distance * math.cos(self.con_rad_angle)
            self.new_objects[i].cur_y = self.new_objects[i].start_y + distance * math.sin(self.con_rad_angle)
    

    def set_velocity_vector(self, p1, p2):
        self.velocity_vector = p2 - p1

    def get_cmd(self, cmd: str):
        try:
            paras = cmd.split()

            if paras[0] == 'o':
                self.update_conveyor_position()
                if paras[1] == 'clear':
                    self.clear_objects()
                elif paras[1] == 'all':
                    for obj in self.tracking_objects:
                        obj.print()
                else:
                    id = int(paras[1])
                    if id < len(self.tracking_objects):
                        self.tracking_objects[id].print()
            if paras[0] == 'add':
                x, y, w, l, a, start, error = 0, 0, 20, 40, 0, encoder1.read_position(), 1

                for i in range(1, len(paras)):
                    if i == 1:
                        x = float(paras[i])
                    if i == 2:
                        y = float(paras[i])
                    if i == 3:
                        w = float(paras[i])
                    if i == 4:
                        l = float(paras[i])
                    if i == 5:
                        a = float(paras[i])
                    if i == 6:
                        start = float(paras[i])
                    if i == 7:
                        error = float(paras[i])

                obj = TrackingObject(x, y, w, l, a, start, error)
                self.add_object(obj)
        except:
            traceback.print_exc()
            print('wrong cmd')


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Devices
    import DeviceManager

    device_manager = DeviceManager.instance
    device_manager.create_pick_n_place_system()
    encoder1: SubEncoder = device_manager.conveyor_station.sub_encoders[2]
    robot1: Robot = device_manager.robots[0]

    device_manager.conveyor_station.set_encoder_invert('C3', True)

    # Mapping Matrix
    import MatrixTool
    con_robot_matrix = MatrixTool.MappingMatrix()
    con_robot_matrix.calculate_matrix(
        ((0, 0), (0, 400)), ((-500, -200), (-100, -200)))

    # Init Tracking
    tracking = TrackingManager(encoder1)
    trackingThread = QThread()
    tracking.moveToThread(trackingThread)
    trackingThread.start()

    # Console
    import console

    cons = console.Command()
    consoleThread = QThread()
    cons.moveToThread(consoleThread)
    consoleThread.started.connect(cons.run)
    consoleThread.start()

    cons.inputSig.connect(tracking.get_cmd)
    cons.inputSig.connect(device_manager.get_cmd)

    # #
    device_manager.conveyor_station.move(name='C3', vel=100)
    real_con_speed = device_manager.conveyor_station.cal_real_velocity('C3')

    tracking_y = 160
    tracking_x = 160
    obj = TrackingObject(x=tracking_x, y=tracking_y, w=20,
                         l=20, a=45, start_pos=encoder1.read_position())

    tracking.add_object(obj)

    objs, exe_time = tracking.get_objects(limit1=0, limit2=500)
    if len(objs) > 0:
        obj: TrackingObject = objs[0]
        obj_pos = con_robot_matrix.map((obj.cur_x, obj.cur_y))

        con_speed_offset_time = (real_con_speed * 10)/(300 * 300)
        robot1.move(X=obj_pos[0] - 10, Y=obj_pos[1], Z=-900, F=3000, A=50000, S=1000,
                    E=100, J=500000, sync=True, time_offset=(exe_time + con_speed_offset_time))
        tracking.delete_object(obj)

    app.exec_()
