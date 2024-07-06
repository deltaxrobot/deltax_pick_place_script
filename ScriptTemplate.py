from PyQt5.QtCore import QEventLoop
from PyQt5.QtCore import QObject, QTimer, QThread, pyqtSignal, pyqtSlot, QPointF, QLineF
from PyQt5.QtWidgets import QApplication
import sys

from time import sleep
# import PnPProject
import MatrixTool
import traceback
import VariableManager

class Script(QObject):
    check_object_request = pyqtSignal()
    robot_request = pyqtSignal(str)
    conveyor_move_request = pyqtSignal(str, float, float)
    conveyor_move_speed_request = pyqtSignal(float)
    conveyor_move_speed_time_request = pyqtSignal(float, int)
    delete_object_request = pyqtSignal(int)
    done_request = pyqtSignal()
    is_picking = False

    def __init__(self):
        super().__init__()
        self.exit_loop = False
        self.new_request = True
        self.limit1 = 0
        self.limit2 = 0
        self.id = 0
        self.enable = True      
        self.con_speed_offset_time = (100 * 10)/(300 * 300)  
        self.is_stop = False
        self.offset_x = 0
        self.offset_y = 0
        self.com_port = "COM19"
        
        self.tracking_manager = None
        self.d_box_holder = 5
        self.d_suction_cup = 1
        self.d_blow = 0

        self.point1_camera = QPointF(1185.78, 0)
        self.point2_camera = QPointF(1679.82, 0)
        self.point1_robot = QPointF(-238.5, -297.5)
        self.point2_robot = QPointF(264, -281)

        self.place_z_safe = -865
        self.place_z_working = -893
        self.z_safe = -865
        self.z_working = -903

        self.con_robot_matrix = MatrixTool.MappingMatrix()
        self.placing_matrix = MatrixTool.PositionMatrix()

        self.load_placing_box_step = 0

        self.point1_placing = QPointF(31, 98)
        self.point2_placing = QPointF(31, 179)
        self.point3_placing = QPointF(-53, 177)
        self.point4_placing = QPointF(-53, 97)
        self.row_placing = 3
        self.col_placing = 2

        self.conveyor_angle = 0

        self.box_filled_counter = 0

    def load_variable(self):
        VariableManager.instance.set("is_box1_filled", False)

        # toạ độ camera thành toạ độ robot
        self.point1_camera = QPointF(VariableManager.instance.get("point1_camera" + str(self.id), self.point1_camera))
        self.point2_camera = QPointF(VariableManager.instance.get("point2_camera" + str(self.id), self.point2_camera))

        self.point1_robot = QPointF(VariableManager.instance.get("point1_robot" + str(self.id), self.point1_robot))
        self.point2_robot = QPointF(VariableManager.instance.get("point2_robot" + str(self.id), self.point2_robot))

        print(self.id, self.point1_camera)
        print(self.id, self.point2_camera)

        print(self.id, self.point1_robot)
        print(self.id, self.point2_robot)

        print("---")

        _point_camera_offset = self.point1_camera.y()
        self.point1_camera.setY(0)
        self.point2_camera.setY(0)

        # _point1_robot_y = self.point1_robot.y() - _point_camera_offset
        # self.point1_robot.setY(_point1_robot_y)

        # _point2_robot_y = self.point2_robot.y() - _point_camera_offset
        # self.point2_robot.setY(_point2_robot_y)

        # self.con_robot_matrix.calculate_matrix(((self.point1_camera.x(), self.point1_camera.y()), (self.point2_camera.x(), self.point2_camera.y())),
        #                                         ((self.point1_robot.x(), self.point1_robot.y()), (self.point2_robot.x(), self.point2_robot.y())))


        _point1_robot_x = self.point1_robot.x() - _point_camera_offset
        self.point1_robot.setX(_point1_robot_x)

        _point2_robot_x = self.point2_robot.x() - _point_camera_offset
        self.point2_robot.setX(_point2_robot_x)

        self.con_robot_matrix.calculate_matrix(((self.point1_camera.x(), self.point1_camera.y()), (self.point2_camera.x(), self.point2_camera.y())),
                                                ((self.point1_robot.y(), self.point1_robot.x()), (self.point2_robot.y(), self.point2_robot.x())))

        new_point1 = QPointF(self.point1_robot.y(), self.point1_robot.x())
        new_point2 = QPointF(self.point2_robot.y(), self.point2_robot.x())
        angle = QLineF(new_point1, new_point2).angle()
        self.conveyor_angle = angle

        # z gắp và thả
        self.place_z_safe = float(VariableManager.instance.get("place_z_safe" + str(self.id), self.place_z_safe))
        self.place_z_working = float(VariableManager.instance.get("place_z_working" + str(self.id), self.place_z_working))
        self.z_safe = float(VariableManager.instance.get("z_safe" + str(self.id), self.z_safe))
        self.z_working = float(VariableManager.instance.get("z_working" + str(self.id), self.z_working))

        # offset robot với vật
        self.offset_x = float(VariableManager.instance.get("offset_x" + str(self.id), 0))
        self.offset_y = float(VariableManager.instance.get("offset_y" + str(self.id), 0))

        # vị trí xắp xếp
        self.point1_placing = QPointF(VariableManager.instance.get("point1_placing" + str(self.id), self.point1_placing))
        self.point2_placing = QPointF(VariableManager.instance.get("point2_placing" + str(self.id), self.point2_placing))
        self.point3_placing = QPointF(VariableManager.instance.get("point3_placing" + str(self.id), self.point3_placing))
        self.point4_placing = QPointF(VariableManager.instance.get("point4_placing" + str(self.id), self.point4_placing))

        self.row_placing = int(VariableManager.instance.get("row_placing" + str(self.id), self.row_placing))
        self.col_placing = int(VariableManager.instance.get("col_placing" + str(self.id), self.col_placing))

        self.placing_matrix.cal(self.point4_placing, self.point2_placing, self.point1_placing, self.point3_placing, self.row_placing, self.col_placing)

        if self.id == 1:
            self.minmaxPlace1 = int(VariableManager.instance.get("minmaxPlace1", 7))
            self.placing_matrix.setMax(self.minmaxPlace1)
        elif self.id == 2:
            self.minmaxPlace2 = int(VariableManager.instance.get("minmaxPlace2", 8))
            self.placing_matrix.setMin(self.minmaxPlace2)

    def change_offset(self, x, y):
        self.offset_x = x
        self.offset_y = y

        VariableManager.instance.set("offset_x" + str(self.id), self.offset_x)
        VariableManager.instance.set("offset_y" + str(self.id), self.offset_y)

    def exit(self):
        self.exit_loop = True

    def run(self):
        self.init_action()
        #self.pick_action()
        
    def delay_ms(self, msec):
        loop = QEventLoop()
        QTimer.singleShot(msec, loop.quit)
        loop.exec()

    def init_action(self):
        pass

    def pick_action(self):
        pass

    def pick(self):
        pass

    def stop(self):
        self.exit_loop = True

    def start(self):
        if self.enable == False:
            return
        if self.exit_loop == True:
            self.exit_loop = False
            self.pick_action()

    def loadNewPlacingBox(self):
        pass


