from PyQt5.QtCore import QSettings, QCoreApplication, QObject, pyqtSignal, pyqtSlot, QMutex, QMutexLocker
from typing import Dict, Any


class VariableManager(QObject):
    mutex = QMutex()

    def __init__(self):
        super().__init__()

        self.settings = None

    def set(self, name: str, value: Any):
        # Lock the mutex before updating variable
        locker = QMutexLocker(VariableManager.mutex)
        if self.settings == None:
            return

        # Set variable in QSettings
        self.settings.setValue(name, value)

    def get(self, name: str, default_value=None):
        # Lock the mutex before accessing variable
        locker = QMutexLocker(VariableManager.mutex)

        if self.settings == None:
            return

        # Retrieve variable from QSettings
        if self.settings.contains(name):
            return self.settings.value(name)
        else:
            return default_value
        
    def load(self, file_path):
        self.settings = QSettings(file_path, QSettings.IniFormat)


instance = VariableManager()