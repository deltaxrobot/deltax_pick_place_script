from PyQt5.QtCore import QThread, pyqtSignal, QObject, QTimer
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
import sys
import VariableManager


class ComPortReaderWriter(QObject):
     got_position = pyqtSignal(float)
     stateChanged = pyqtSignal(bool)
     fiber1Changed = pyqtSignal(bool)
     fiber2Changed = pyqtSignal(bool)
     speedChanged = pyqtSignal(float)

     def __init__(self, port_name):
          super().__init__()
          self.port_name = port_name
          self.serial_port = None
          self.message_to_send = ""
          self.response = 0
          self.buffer = ""
          self.con_name = "con1"

          self.device_type = "old_xconveyor"

          self.timerStop = QTimer()

     def start(self):
          self.thread = QThread()
          self.moveToThread(self.thread)
          self.thread.started.connect(self.run)
          self.thread.start()

     def run(self):
          if self.con_name == "con1":
               VariableManager.instance.set("conveyor1_state", False)
          else:
               VariableManager.instance.set("conveyor2_state", False)

          self.serial_port = QSerialPort(self.port_name)
          self.serial_port.setBaudRate(QSerialPort.Baud115200)          
          self.serial_port.readyRead.connect(self.handle_ready_read)
          
          if not self.serial_port.open(QSerialPort.ReadWrite):
               print("Fail to open" + str(self.port_name) + "\n")
               self.stateChanged.emit(False)
               return
          else:
               print("Open " + str(self.port_name) + "\n")
               self.stateChanged.emit(True)

          self.timerStop.setSingleShot(True)
          self.timerStop.timeout.connect(self.moveSpeedStop)

          self.setupConveyorEncoder()
     
     def setupConveyorEncoder(self):
          if self.device_type == "old_xconveyor" or self.device_type == "old_xencoder":
               if self.device_type == "old_xconveyor":
                    self.send_message("M310 1")
               
               return
          
          self.send_message("M310 2")
          self.send_message("M315 S31.32")
          if self.con_name == "con1":
               self.send_message("M315 R1")
          else:
               self.send_message("M315 R0")
          self.send_message("M315 A250")
          self.send_message("M313 80")

          self.send_message("M316 0")
          self.send_message("M318 S10.17")
          self.send_message("M318 C2")

     def setupConveyorInput(self):
          

          self.send_message("M310 2")
          self.send_message("M315 S18.63")
          self.send_message("M315 A200")

          self.send_message("M316 2")

     def moveSpeed(self, speed):
          if self.device_type == "old_xconveyor" or self.device_type == "old_xencoder":
               self.send_message("M311 " + str(speed))
               return
          
          self.send_message("M310 2")
          self.send_message("M311 " + str(speed))
          self.speedChanged.emit(float(speed))
          self.timerStop.stop()

     def moveSpeedTime(self, speed, time):
          self.send_message("M310 2")
          self.send_message("M311 " + str(speed))
          self.speedChanged.emit(float(speed))

          self.timerStop.start(int(time))

     def moveSpeedStop(self):
          if self.device_type == "old_xconveyor" or self.device_type == "old_xencoder":
               self.send_message("M311 0")
               return

          self.send_message("M310 2")
          self.send_message("M311 0")
          self.speedChanged.emit(0)

     def movePosition(self, position):
          if self.device_type == "old_xconveyor" or self.device_type == "old_xencoder":
               #self.send_message("M313 100")
               self.send_message("M312 " + str(position))
               print("M312 " + str(position))
               return

          self.send_message("M310 1")
          self.send_message("M313 100")
          self.send_message("M312 " + str(position))

     def handle_ready_read(self):
          data = self.serial_port.readAll().data().decode()
          self.buffer += data
          if '\n' in self.buffer:
               lines = self.buffer.split('\n')
               for line in lines[:-1]:
                    self.process_line(line)
               self.buffer = lines[-1]

     def process_line(self, line):
          # print(line)
          if line.startswith("P"):
               try:
                    self.response = float(line.strip().split(":")[1])
                    self.got_position.emit(self.response)
               except:
                    pass
          elif line.startswith("I"):          
               if line.strip() == "I0 V0":
                    VariableManager.instance.set("is_fiber1_touch", False)
                    self.fiber1Changed.emit(False)
               elif line.strip() == "I0 V1":
                    VariableManager.instance.set("is_fiber1_touch", True)
                    self.fiber1Changed.emit(True)
               elif line.strip() == "I1 V0":
                    VariableManager.instance.set("is_fiber2_touch", False)
                    self.fiber2Changed.emit(False)
               elif line.strip() == "I1 V1":
                    VariableManager.instance.set("is_fiber2_touch", True)
                    self.fiber2Changed.emit(True)

     def write(self, data):
          if self.serial_port.isOpen():
               self.serial_port.write(data.encode())

     def send_message(self, message):
          # print(message)
          self.message_to_send = message
          if not self.message_to_send.rstrip().endswith('\n'):
               self.message_to_send = '\n'.join([self.message_to_send, ''])
          self.write(self.message_to_send)

     def read_position(self):
          self.send_message("M317")

     def read_encoder_position(self):
          self.send_message("M317")

     def move_speed(self, vel=100):
          pos = 0
          if pos == None or pos == 0:
               cmd = 'M310 2\n'           
               self.send_message(cmd)

               cmd = 'M311 {0}\n'.format(vel)
               self.send_message(cmd)

               self.speedChanged.emit(vel)
          else:
               cmd = 'M310 1\n'
               self.send_message(cmd)

               cmd = 'M313 {0}\n'.format(vel)
               self.send_message(cmd)

               cmd = 'M312 {0}\n'.format(pos)
               self.send_message(cmd)

               self.speedChanged.emit(0.0)

     def move(self, name='C1', pos=0, vel=100):
          if pos == None or pos == 0:
               cmd = 'M400 {0}=1\n'.format(name)               
               self.send_message(cmd)

               cmd = 'M401 {0}={1}\n'.format(name, vel)
               self.send_message(cmd)
          else:
               cmd = 'M400 {0}=0\n'.format(name)
               self.send_message(cmd)

               cmd = 'M402 {0}={1}\n'.format(name, vel)
               self.send_message(cmd)

               cmd = 'M403 {0}={1}\n'.format(name, pos)
               self.send_message(cmd)

class Test(QObject):
     move_request = pyqtSignal(str)
     def __init__(self):
          super().__init__()

     def get_position(self, pos):
          print(pos)

     def get_state(self, state):
         print(state)

     def get_response(self,res):
         print(res)

if __name__ == "__main__":
     app = QApplication(sys.argv)

     test = Test()

     port_name = "COM9"
     com_thread = ComPortReaderWriter(port_name)
     com_thread.got_position.connect(test.get_position)
     com_thread.start()

     # com_thread.send_message("M401 C1=100")
     # Console

     import console

     cons = console.Command()
     consoleThread = QThread()
     cons.moveToThread(consoleThread)
     consoleThread.started.connect(cons.run)
     cons.inputSig.connect(com_thread.send_message)
     consoleThread.start()

     app.exec_()