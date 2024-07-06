from PyQt5.QtCore import QEventLoop
from PyQt5.QtCore import QObject, QTimer, QThread, QLineF, QPointF, pyqtSlot, QMutex, pyqtSignal
from PyQt5.QtWidgets import QApplication
import sys

from time import sleep
# import PnPProject
import MatrixTool
import traceback
from ScriptTemplate import Script
import Device
import time

import VariableManager
from Tracking import TrackingObject
import math

class Pick1(Script):
    robotStateChanged = pyqtSignal(bool)
    numberObjectChanged = pyqtSignal(int)
    fiber1Changed = pyqtSignal(bool)

    received_position = pyqtSignal(list)
    pickedRequet = pyqtSignal(int)
    boxCounterRequest = pyqtSignal()

    stationStopRequest = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.limit1 = 1200
        self.limit2 = 1500
        self.id = 1

        self.mutex = QMutex()

    def init_action(self):
        if self.enable == False:
            return

        if self.id == 1:
            VariableManager.instance.set("robot1_state", False)
        elif self.id == 2:
            VariableManager.instance.set("robot2_state", False)
        

        self.robot = Device.Robot(self.com_port, 115200)
        self.robotStateChanged.emit(self.robot.connected)

        self.robot.received_input.connect(self.read_robot_input)
        self.robot.received_position.connect(self.got_position)

        self.variable_init()

        self.robot.send_gcode('G90')
        self.robot.send_gcode('M60 D0')
        self.robot.send_gcode('M08 I0 B1')
        self.robot.send_gcode('M08 I1 B0')
        self.robot.send_gcode('G28')
        self.robot.send_gcode('G01 F500 A10000 Z{}'.format(self.z_safe))
        self.robot.send_gcode('M5 D0')
        self.robot.send_gcode('M5 D1')

        self.pick_number = 0
        self.sensor_state = 0
        self.exit_loop = True

        VariableManager.instance.set("pick_number" + str(self.id), 0)
        VariableManager.instance.set("is_box" + str(self.id) + "_filled", True)

        self.fiber1 = False
        self.filled = bool(VariableManager.instance.get("is_box" + str(self.id) + "_filled", False))
        self.error_num = 0

        self.is_first_run = True
        self.first_counter = 0

        self.estop_press_last = False

        self.robot.send_gcode('M07 I0')

        # print(self.con_robot_matrix.map((500, 50)))
        # print(self.con_robot_matrix.map((600, 50)))
        # print(self.con_robot_matrix.map((600, -20)))
        # print(self.con_robot_matrix.map((500, -20)))
        VariableManager.instance.set("box_counter", 0)
        self.boxCounterRequest.emit()

    def read_robot_input(self, response):
        #print("response" + str(self.id), response)
        if response.strip() == "I0 V0":
            #VariableManager.instance.set("is_fiber" + str(self.id) + "_touch", False)
            self.fiber1Changed.emit(False)
            self.fiber1 = False
        elif response.strip() == "I0 V1":
            #VariableManager.instance.set("is_fiber" + str(self.id) + "_touch", True)
            self.fiber1Changed.emit(True)
            self.fiber1 = True
        elif response.strip() == "Delta:EStop Pressing!":
            self.robot._read_line_only()
            self.robot._read_line_only()
            self.estop_press_last = True
            self.stationStopRequest.emit()


    
    def got_position(self, position):
        #print("sc_robot_:", position)
        self.received_position.emit(position)

    def variable_init(self):
        if self.enable == False:
            return
        
        self.load_variable()
        #self.robot.set_sync_path(path='line', con_vel=100, con_angle=-self.conveyor_angle)
        self.robot.set_sync_path(path='line', con_vel=100, con_angle=self.conveyor_angle + 89.5)
        
    def setCalibState(self):
        if self.exit_loop == True:
            self.robot.send_gcode('G91')
            self.robot.send_gcode('M5 D0')

    def setRunState(self):
        self.robot.send_gcode('G90')
        self.robot.send_gcode('M5 D0')

        self.variable_init()

    def getPosition(self):
        self.robot.send_gcode('Position')

    def sendGcode(self, gcode):
        self.robot.send_gcode(gcode)

    def pick_action(self):
        last_time_count = time.time()
        pick_counter = 0
        if self.estop_press_last == True:
            self.robot.send_gcode('G90')
            self.robot.send_gcode('M60 D0')
            self.robot.send_gcode('M08 I0 B1')
            self.robot.send_gcode('M08 I1 B0')
            self.robot.send_gcode('G28')
            self.robot.send_gcode('G01 F500 A10000 Z{}'.format(self.z_safe))
            self.robot.send_gcode('M5 D0')
            self.robot.send_gcode('M5 D1')

            self.estop_press_last = False

        while self.exit_loop == False:
            try:
                # if bool(VariableManager.instance.get("is_running", False)) == False:
                #     self.exit_loop = True
                #     self.filled = True
                #     self.robot.send_gcode('G01 F500 A10000 Z{}'.format(self.z_safe))
                #     self.robot.send_gcode('M5 D0')
                #     self.robot.send_gcode('M5 D1')
                #     VariableManager.instance.set("is_box" + str(self.id) + "_filled", self.filled)
                #     VariableManager.instance.set("pick_number" + str(self.id), 0)
                #     continue  

                
                # if self.filled == True:
                #    self.loadNewPlacingBox1()
                #    continue

                ##
                #self.thread().msleep(8000)
                #self.filled = True
                #VariableManager.instance.set("is_box" + str(self.id) + "_filled", self.filled)

                #_box_counter = int(VariableManager.instance.get("box_counter", 0))
                #VariableManager.instance.set("box_counter", _box_counter + 1)


                _obj_para = []
                if self.id == 1:
                    _obj_para = self.tracking_manager.getObjectForPick1()
                else:
                    _obj_para = self.tracking_manager.getObjectForPick2()
                
                if len(_obj_para) > 4:
                    objs_cur_x = _obj_para[0]
                    objs_cur_y = _obj_para[1]
                    objs_angle = _obj_para[2]
                    exe_time = _obj_para[3]
                    path_vel = _obj_para[4]
                    objs_type = _obj_para[5]

                    #print("_obj_para",_obj_para)

                    self.robot.set_sync_path_vel(path_vel)
                    self.con_speed_offset_time = (path_vel * 10)/(300 * 300)  
                    obj_pos = self.con_robot_matrix.map((objs_cur_x, objs_cur_y))
                    #print("new_pos:",obj_pos)
                    angle = objs_angle - 90
                    if angle > 180:
                        angle = angle - 360
                    elif angle < -180:
                        angle = angle + 360

                    rad = 0
                    _x = obj_pos[1] - rad * math.sin(math.radians(angle))
                    _y = obj_pos[0] + rad * math.cos(math.radians(angle))

                    _time_delay = time.time() - exe_time

                    # F A S J moving parameter
                    self.robot.move(X=_x + self.offset_x, Y=_y + self.offset_y, Z=self.z_safe, W=angle, F=3000, A=42000, S=500, E=250, J=910000, sync=True, time_offset=(_time_delay + self.con_speed_offset_time))          
                    
                    self.robot.output(self.d_suction_cup, 0)
                    self.robot.move(Z=self.z_working, sync=True)
                    #self.robot.move(Z = -860, sync=True)
                    # air delay
                    self.robot.sleep(time_ms=130, sync=True)
                    self.robot.move(Z=self.place_z_working, sync=True)
                    #self.robot.move(Z=-770, sync=True)

                    # order, place_pos, is_filled = self.placing_matrix.next()
                    # self.robot.move(X = place_pos.x(), Y = place_pos.y(), Z=self.place_z_safe, W=0)
                    
                    # plastic bottle placement
                    if objs_type == 0:
                        self.robot.move(X = -250, Y = -190, Z=self.place_z_working)
                    elif objs_type == 1:
                        self.robot.move(X = -250, Y = 0, Z=self.place_z_working)
                    elif objs_type == 2:
                        self.robot.move(X = -250, Y = 190, Z=self.place_z_working)

                    #self.robot.move(Z=self.place_z_working, sync=False)
                    self.robot.output(self.d_suction_cup, 1)
                    self.robot.output(self.d_blow, 1)

                    self.robot.sleep(time_ms=40, sync=False)

                    self.robot.output(self.d_blow, 0)
                    self.robot.output(self.d_suction_cup, 0)
                    #self.robot.move(Z=self.place_z_safe, sync=False)

                    #self.pickedRequet.emit(order)
                    # VariableManager.instance.set("pick_number" + str(self.id), order)

                    # if is_filled == True:
                    #     self.filled = True
                    #     VariableManager.instance.set("is_box" + str(self.id) + "_filled", self.filled)

                    #     if self.id == 2:
                    #         _box_counter = int(VariableManager.instance.get("box_counter", 0))
                    #         VariableManager.instance.set("box_counter", _box_counter + 1)
                        
                    #self.thread().msleep(1)
                    pick_counter = pick_counter + 1
                    print(pick_counter)
                    
                else:
                    self.thread().msleep(1)

                if time.time() - last_time_count >= 60:
                    VariableManager.instance.set("box_counter", pick_counter)
                    last_time_count = time.time()
                    pick_counter = 0
                    self.boxCounterRequest.emit()
                
            except Exception as e:
                # In ra lỗi
                print(e)
                traceback.print_exc()

    def loadNewPlacingBox1(self):
        self.robot.send_gcode('M07 I0')
        self.read_robot_input(self.robot._read_line_only())

        if self.load_placing_box_step == 0:
            self.robot.send_gcode('M07 I0')
            self.robot.output(self.d_box_holder, 0)

            other_robot_id = 1
            if self.id == other_robot_id:
                other_robot_id = 2
            if bool(VariableManager.instance.get("is_box" + str(other_robot_id) + "_filled", False)) == True:
                self.conveyor_move_speed_request.emit(90)

            self.load_placing_box_step = 1

        elif self.load_placing_box_step == 1:
            if self.fiber1 == False:

                self.error_num = self.error_num + 1
                if self.error_num >= 12:
                    self.error_num = 0

                    self.load_placing_box_step = 2
                    #if self.id == 2:
                    #    print("step1")
                    self.thread().msleep(550)
                    self.robot.output(self.d_box_holder, 1) 
            else:
                self.error_num = 0
        elif self.load_placing_box_step == 2:
            if self.fiber1 == True:
                
                self.error_num = self.error_num + 1
                if self.error_num >= 12:
                    self.error_num = 0

                    self.load_placing_box_step = 0
                    #print(self.id, "load done....")

                    self.thread().msleep(700)

                    self.filled = False
                    VariableManager.instance.set("is_box" + str(self.id) + "_filled", False)

                    other_robot_id = 1
                    if self.id == other_robot_id:
                        other_robot_id = 2
                    if bool(VariableManager.instance.get("is_box" + str(other_robot_id) + "_filled", False)) == False:
                        self.conveyor_move_speed_request.emit(0)
                    

                    if self.id == 1 and self.first_counter < 4:
                        self.first_counter = self.first_counter + 1
                        self.conveyor_move_speed_request.emit(0)                        

                    self.read_robot_input(self.robot._read_line_only())    
            else:
                self.error_num = 0    
        

    def loadNewPlacingBox(self):
        #self.robot.send_gcode('M07 I0')
        self.read_robot_input(self.robot._read_line_only())

        if self.load_placing_box_step == 0:
            self.robot.send_gcode('M07 I0')
            self.robot.output(self.d_box_holder, 0)
            self.conveyor_move_speed_request.emit(90)
            self.load_placing_box_step = 1

            if self.is_first_run == True and self.id == 2:
                self.load_placing_box_step = 3
                self.is_first_run = False

        elif self.load_placing_box_step == 1:
            if self.fiber1 == False:

                self.error_num = self.error_num + 1
                if self.error_num >= 12:
                    self.error_num = 0

                    self.load_placing_box_step = 2
                    #if self.id == 2:
                    #    print("step1")
            else:
                self.error_num = 0
        elif self.load_placing_box_step == 2:
            if self.fiber1 == True:

                self.error_num = self.error_num + 1
                if self.error_num >= 12:
                    self.error_num = 0

                    self.load_placing_box_step = 3
                    #if self.id == 2:
                    #    print("step2")
            else:
                self.error_num = 0
        elif self.load_placing_box_step == 3:
            if self.fiber1 == False:

                self.error_num = self.error_num + 1
                if self.error_num >= 12:
                    self.error_num = 0

                    self.load_placing_box_step = 4
                    #if self.id == 2:
                    #    print("step3")
                    self.thread().msleep(15)#spg
                    self.robot.output(self.d_box_holder, 1) 
            
            else:
                self.error_num = 0
        elif self.load_placing_box_step == 4:
            if self.fiber1 == True:
                
                self.error_num = self.error_num + 1
                if self.error_num >= 12:
                    self.error_num = 0

                    self.load_placing_box_step = 0
                    other_robot_id = 1
                    if self.id == other_robot_id:
                        other_robot_id = 2
                    #print(self.id, "load done....")

                    self.thread().msleep(1000)
                    self.filled = False
                    VariableManager.instance.set("is_box" + str(self.id) + "_filled", False)

                    if bool(VariableManager.instance.get("is_box" + str(other_robot_id) + "_filled", False)) == False:
                        self.conveyor_move_speed_request.emit(0)
                      
                       

                    self.read_robot_input(self.robot._read_line_only())    
            else:
                self.error_num = 0

class Pick2(Script):
    robotStateChanged = pyqtSignal(bool)
    def __init__(self):
        super().__init__()
        self.limit1 = 350
        self.limit2 = 500
        self.id = 2

        self.mutex = QMutex()

    def init_action(self):

        self.robot = Device.Robot('COM7', 115200)
        self.robotStateChanged.emit(self.robot.connected)
        
        angle = QLineF(QPointF(-126.49, -247.49), QPointF(154.51, -248.99)).angle()
        # self.robot.set_sync_path(path='line', con_vel=96.732, con_angle=-angle)
        self.robot.set_sync_path(path='line', con_vel=97, con_angle=-angle)

        self.con_robot_matrix = MatrixTool.MappingMatrix()
        self.con_robot_matrix.calculate_matrix(((396.17, 0), (672.98, 0)), ((-126.49, -247.49), (154.51, -248.99)))

        self.placing_matrix = MatrixTool.PositionMatrix()
        self.placing_matrix.cal(QPointF(0, 65), QPointF(0, 115), QPointF(-100, 115), QPointF(-100, 65), 3, 5)     

        
        self.place_z_safe = -645
        self.place_z_working = -697 - 4
        self.z_safe = -645
        self.z_working = -679
        self.u_pick = 0

        self.offset_x = float(VariableManager.instance.get("offset_x2", 0))
        self.offset_y = float(VariableManager.instance.get("offset_y2", 0))

        # #R = 51.32
        # #XA = 10
        # #YA = 10

        # G01 X[#XA - #R * #sin(0)] Y[#YA + #R * #cos(0)] Z-680 W0 U-5

        # G01 X[#XA - #R * #sin(130)] Y[#YA + #R * #cos(130)] Z-680 W130 U-5
        self.robot.send_gcode('M60 D1')
        
        self.robot.send_gcode('M61 D1 A50000 F2500')

        self.robot.send_gcode('M212 F600 A16000 J1500000')
        
        self.robot.send_gcode('G28')

        self.robot.send_gcode('G01 X0 Y50 Z{} U{}'.format(self.z_safe, self.u_pick))

        self.pick_number = 0

        VariableManager.instance.set("pick_number2", self.pick_number)
        VariableManager.instance.set("is_box2_filled", False)

    def variable_init(self):
        self.load_variable()
        self.robot.set_sync_path(path='line', con_vel=100, con_angle=-self.conveyor_angle)

    def pick_action(self):
        #while self.exit_loop == False:
            try:
                #self.is_box2_filled = bool(VariableManager.instance.get("is_box2_filled", False))
                
                _obj_para = self.tracking_manager.getObjectForPick2()
                _obj_para = []

                if len(_obj_para) > 4:
                    objs_cur_x = _obj_para[0]
                    objs_cur_y = _obj_para[1]
                    objs_angle = _obj_para[2]
                    exe_time = _obj_para[3]
                    path_vel = _obj_para[4]

                    self.robot.set_sync_path_vel(path_vel)
                    obj_pos = self.con_robot_matrix.map((objs_cur_x, 0 - objs_cur_y))
                    angle = objs_angle
                    # if angle > 180:
                    #     angle = angle - 360
                    # elif angle < -180:
                    #     angle = angle + 360

                    rad = 51.32
                    _x = obj_pos[0] - rad * math.sin(math.radians(angle))
                    _y = obj_pos[1] + rad * math.cos(math.radians(angle))

                    # print("self.offset_x:", self.offset_x)
                    # print("self.offset_y:", self.offset_y)

                    _time_delay = time.time() - exe_time
                    self.robot.move(X=_x + self.offset_x, Y=_y + self.offset_y, Z=self.z_safe, W = angle, U=self.u_pick, F=1500, A=18000, S=100, E=100, J=350000, sync=True, time_offset=(_time_delay + self.con_speed_offset_time))        
                    
                    self.robot.output(4, 1)
                    self.robot.move(Z=self.z_working, sync=True)
                    self.robot.sleep(time_ms=250, sync=True)
                    self.robot.move(Z=self.z_safe, sync=True)

                    #order, place_pos = self.placing_matrix.next()

                    #self.robot.move(X = 0, Y = 43, Z=self.place_z_safe, W =90, U=-90)
                    self.robot.move(X = 0, Y = 62, Z=self.place_z_safe, W =90, U=-90)
                    #self.robot.sleep(time_ms=100, sync=False)
                    self.robot.move(Z=self.place_z_working, F=1000, A=5000, S=0, E=0, sync=False)
                    self.robot.set_sync_path_vel(80)
                    self.robot.output(4, 0)
                    self.robot.sleep(time_ms=100, sync=True)
                    self.robot.move(Y= 50, F=1500, A=18000, S=100, E=100, J=350000, sync=False)
                    # self.robot.sleep(time_ms=100, sync=False)
                    self.robot.move(Y= 10,F=1300, Z=self.place_z_safe, U=-60, sync=False)
                                        
                    #self.robot.move(Z=self.place_z_safe, U=self.u_pick, sync=False)
                    self.pick_number += 1

                    VariableManager.instance.set("pick_number2", self.pick_number)

                    if self.pick_number % 15 == 0:
                        print('box2 is filled')
                        VariableManager.instance.set("is_box2_filled", True)
        
                else:
                    #self.robot.sleep(time_ms=100, sync=False)
                    self.thread().msleep(20)

            except Exception as e:
                # In ra lỗi
                print(e)
                traceback.print_exc()


    def place_action(self):
        pass

    def loadNewPlacingBox(self):
        if self.load_placing_box_step == 0:
            self.robot.output(self.d_box_holder, 0)
            self.conveyor_move_speed_request.emit(100)
            self.load_placing_box_step += 1

        elif self.load_placing_box_step == 1 or self.load_placing_box_step == 3:
            is_fiber1_touch = bool(VariableManager.instance.get("is_fiber2_touch", False))
            if is_fiber1_touch == 0:
                self.load_placing_box_step += 1
        elif self.load_placing_box_step == 2:
            is_fiber1_touch = bool(VariableManager.instance.get("is_fiber2_touch", False))
            if is_fiber1_touch == 1:
                self.load_placing_box_step += 1    
        elif self.load_placing_box_step == 4:
            is_fiber1_touch = bool(VariableManager.instance.get("is_fiber2_touch", False))
            if is_fiber1_touch == 1:
                self.load_placing_box_step = 0
                self.robot.output(self.d_box_holder, 1)    
                VariableManager.instance.set("is_box2_filled", False)

                if bool(VariableManager.instance.get("is_box1_filled", False)) == False:
                    self.conveyor_move_speed_request.emit(0)
                   

    def pick(self):
        if self.is_picking == True:
                return
        self.is_picking = True
        self.robot.send_gcode('G01 Z{}'.format(self.z_safe))
        self.robot.send_gcode('G01 Z{}'.format(self.z_safe - 10))
        self.is_picking = False
        return
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    script = Script()
    scriptThread = QThread()
    script.moveToThread(scriptThread)
    scriptThread.started.connect(script.run)     
    scriptThread.start()