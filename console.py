from PyQt5.QtCore import QObject, pyqtSignal

class Command(QObject):
    inputSig = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        print("Command Here:")
        while True:
            cmd = input()
            # print(cmd)
            self.inputSig.emit(cmd)

    def forward(self, cmd):
        print(cmd)
        self.inputSig.emit(cmd)