import random
from PyQt5.QtCore import Qt, QLineF
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QMainWindow

class MyRectItem(QGraphicsRectItem):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.setRect(x, y, width, height)
        self.setFlag(QGraphicsRectItem.ItemIsMovable)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.scene().updateLines()

class MyLine(QLineF):
    def __init__(self, p1, p2):
        super().__init__(p1, p2)

    def update(self, rect):
        self.setP1(rect.topLeft())
        self.setP2(rect.bottomRight())

class MyScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.items = []
        self.lines = []
        self.initScene()
        self.updateLines()

    def initScene(self):
        for i in range(4):
            x = random.randint(0, 250)
            y = random.randint(0, 250)
            width = random.randint(50, 100)
            height = random.randint(50, 100)
            rect = MyRectItem(x, y, width, height)
            self.items.append(rect)
            self.addItem(rect)

    def updateLines(self):
        for line in self.lines:
            self.removeItem(line)
        self.lines.clear()

        pen = QPen(Qt.black)
        pen.setWidth(2)

        for i in range(4):
            line = MyLine(self.items[i].rect().topLeft(), self.items[(i+1)%4].rect().topLeft())
            line = self.addLine(line, pen)
            self.lines.append(line)

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.view = QGraphicsView(self)
        self.setCentralWidget(self.view)
        self.scene = MyScene()
        self.view.setScene(self.scene)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
