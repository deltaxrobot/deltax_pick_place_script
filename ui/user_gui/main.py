# This Python file uses the following encoding: utf-8
import sys

from PyQt5.QtGui import QGuiApplication
from qmlgui import QmlGui

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    loadqml = QmlGui()
    sys.exit(app.exec_())
