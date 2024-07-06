from PyQt5.QtCore import QObject, QThread, pyqtSignal, QLineF, QTimer
import DeviceManager
import Server
import VisionTool
import console
import Tracking
import MatrixTool
from PyQt5.QtCore import QMutex
import Pick
import Tracking

class Project(QObject):
    run_script_sig = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.scripts = []

        self.global_var = 0
        self.mutex = QMutex()
        self.important_port = None
        self.ui = None


    def get_cmd(self, cmd):
        if cmd =='run scripts':            
            
            
            # self.script1 = Pick1.Script(self)
            # self.scriptThread1 = QThread()
            # self.script1.moveToThread(self.scriptThread1)
            # self.scriptThread1.started.connect(self.script1.run)     
            # self.scriptThread1.start()

            # self.script2 = Pick2.Script(self)
            # self.scriptThread2 = QThread()
            # self.scriptThread2.moveToThread(self.scriptThread2)
            # self.scriptThread2.started.connect(self.script2.run)
            # self.scriptThread2.start()
            self.run_script_sig.emit()

    def set_script(self, script):
        self.scripts.append(script)

    def run(self):
        # Console
        self.cons = console.Command()
        self.consoleThread = QThread()
        self.cons.moveToThread(self.consoleThread)
        self.consoleThread.started.connect(self.cons.run)
        self.consoleThread.start()

        self.cons.inputSig.connect(self.get_cmd)
        
        # # Devices
        # self.device_manager = DeviceManager.DeviceManager()
        # self.device_managerThread = QThread()
        # self.device_manager.moveToThread(self.device_managerThread)
        # self.device_managerThread.started.connect(self.device_manager.create_pick_n_place_system)
        # self.device_managerThread.start()

        # self.device_manager.create_pick_n_place_system()
        # self.device_manager.cameras[0].set_encoder(self.device_manager.conveyor_station.sub_encoders[2])
        # self.device_manager.conveyor_station.set_encoder_invert('C3', True)
        # self.cons.inputSig.connect(self.device_manager.get_cmd)
        # print('2')
        # self.important_port = self.device_manager.conveyor_station.serial_device
        
        self.camera = DeviceManager.CameraDevice('basler', 0, 'connect', 500)
        self.camera.scaleWidth = 800
        self.cameraThread = QThread()
        self.camera.moveToThread(self.cameraThread)
        self.cameraThread.started.connect(self.camera.run)
        self.cameraThread.start()

        

        self.conveyor_station = DeviceManager.ConveyorStation(COM='COM19', is_open= False)
        self.conveyorThread = QThread()
        self.conveyor_station.moveToThread(self.conveyorThread)
        self.conveyorThread.started.connect(self.conveyor_station.init_in_other_thread)
        self.conveyorThread.start()
        
        # # Server
        self.server = Server.ImageServer('192.168.101.135', 8844)
        self.serverThread = QThread()
        self.server.moveToThread(self.serverThread)
        self.serverThread.started.connect(self.server.open)
        self.serverThread.start()
        # self.server.read_mess.connect(self.cons.forward)

        # #Detecting
        self.vision = VisionTool.VisionTool()
        
        self.visionThread = QThread()
        self.vision.moveToThread(self.visionThread)
        self.vision.load_settings()
        self.visionThread.start()
        self.camera.captured.connect(self.vision.detect)
        self.cons.inputSig.connect(self.vision.get_cmd)
        self.vision.detect_algorithm = 'external'
        self.vision.sending_image_type = 'calib'
        self.vision.detect_image_ready.connect(self.server.send_image)
        self.server.got_objects.connect(self.vision.get_objs_from_external)
        
        # Init Tracking        
        self.tracking1 = Tracking.TrackingManager(encoder = self.conveyor_station.sub_encoders[2])
        self.trackingThread1 = QThread()
        self.tracking1.moveToThread(self.trackingThread1)
        self.trackingThread1.start()
        self.vision.detected.connect(self.tracking1.add_new_objects)
        self.cons.inputSig.connect(self.tracking1.get_cmd)
        
        self.tracking1.set_clear_limit(1500)
        
        # self.tracking2 = Tracking.TrackingManager(encoder = self.device_manager.conveyor_station.sub_encoders[0])
        # self.trackingThread2 = QThread()
        # self.tracking2.moveToThread(self.trackingThread2)
        # self.trackingThread2.start()
        # self.cons.inputSig.connect(self.tracking2.get_cmd)

        self.tracking1.velocity_m = 100
        self.tracking1.cal_con_speed_offset_time(100)

        self.script1 = Pick.Pick1(None, self.tracking1)
        self.scriptThread1 = QThread()
        self.script1.moveToThread(self.scriptThread1)
        self.run_script_sig.connect(self.script1.run)
        self.script1.object_checked.connect(self.tracking1.get_objects)
        self.tracking1.objects_in_area.connect(self.script1.pick_action)  
        self.scriptThread1.start()

        

        self.script2 = Pick.Pick2(None, self.tracking1)
        self.scriptThread2 = QThread()
        self.scriptThread2.moveToThread(self.scriptThread2)
        self.run_script_sig.connect(self.script2.run)
        self.script2.object_checked.connect(self.tracking1.get_objects)
        self.tracking1.objects_in_area2.connect(self.script2.pick_action)
        self.scriptThread2.start()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.conveyor_station.sub_encoders[2].read_position)
        self.timer.start(50)
        
        self.camera.startedCapture.connect(self.tracking1.capture_moment)
        
        self.tracking1.display_obj_request.connect(self.ui.handle_received_text)
        