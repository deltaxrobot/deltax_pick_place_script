import cv2
import numpy as np
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QHBoxLayout, QVBoxLayout, QSlider, QPushButton
from PyQt5.QtCore import QSettings

class ThresholdAdjuster(QMainWindow):
    saved = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self.h_min = 0
        self.h_max = 255
        self.s_min = 0
        self.s_max = 255
        self.v_min = 0
        self.v_max = 255
        self.blur = 0

        self.init_widgets()

    def init_widgets(self):
        # Create the sliders
        self.h_min_slider = QSlider(QtCore.Qt.Horizontal)
        self.h_max_slider = QSlider(QtCore.Qt.Horizontal)
        self.s_min_slider = QSlider(QtCore.Qt.Horizontal)
        self.s_max_slider = QSlider(QtCore.Qt.Horizontal)
        self.v_min_slider = QSlider(QtCore.Qt.Horizontal)
        self.v_max_slider = QSlider(QtCore.Qt.Horizontal)
        self.blur_slider = QSlider(QtCore.Qt.Horizontal)

        self.save_button = QPushButton()
        self.save_button.clicked.connect(self.save)
        self.save_button.setText("Save")

        # Set the range and default values for the sliders
        self.h_min_slider.setRange(0, 255)
        self.h_max_slider.setRange(0, 255)
        self.s_min_slider.setRange(0, 255)
        self.s_max_slider.setRange(0, 255)
        self.v_min_slider.setRange(0, 255)
        self.v_max_slider.setRange(0, 255)
        self.blur_slider.setRange(0, 50)
            
        # Connect the sliders to the update function
        self.h_min_slider.sliderReleased.connect(self.update_image)
        self.h_max_slider.sliderReleased.connect(self.update_image)
        self.s_min_slider.sliderReleased.connect(self.update_image)
        self.s_max_slider.sliderReleased.connect(self.update_image)
        self.v_min_slider.sliderReleased.connect(self.update_image)
        self.v_max_slider.sliderReleased.connect(self.update_image)
        self.blur_slider.sliderReleased.connect(self.update_image)

        # Create a label to display the image
        self.image_label = QLabel()
        
        # Create the layout
        layout = QVBoxLayout()
        h_layout1 = QHBoxLayout()
        h_layout2 = QHBoxLayout()
        h_layout3 = QHBoxLayout()

        # Add the sliders and labels to the layout
        h_layout1.addWidget(QLabel("Hue Min"))
        h_layout1.addWidget(self.h_min_slider)
        h_layout1.addWidget(QLabel("Hue Max"))
        h_layout1.addWidget(self.h_max_slider)

        h_layout2.addWidget(QLabel("Saturation Min"))
        h_layout2.addWidget(self.s_min_slider)
        h_layout2.addWidget(QLabel("Saturation Max"))
        h_layout2.addWidget(self.s_max_slider)

        h_layout3.addWidget(QLabel("Value Min"))
        h_layout3.addWidget(self.v_min_slider)
        h_layout3.addWidget(QLabel("Value Max"))
        h_layout3.addWidget(self.v_max_slider)

        layout.addWidget(self.image_label)
        layout.addLayout(h_layout1)
        layout.addLayout(h_layout2)
        layout.addLayout(h_layout3)
        layout.addWidget(self.blur_slider)

        layout.addWidget(self.save_button)

        # Set the layout for the main window
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setWindowTitle("Threshold Adjuster")


    def open(self, image):
        # Load the image
        if type(image) == str:            
            self.image = cv2.imread(image)
        else:
            self.image = image.copy()
        
        self.gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)

        qimage = QtGui.QImage(self.gray_image, self.gray_image.shape[1], self.gray_image.shape[0], self.gray_image.strides[0], QtGui.QImage.Format_Grayscale8)
        self.image_label.setPixmap(QtGui.QPixmap.fromImage(qimage))

        self.load_setting()

        self.h_min_slider.setValue(self.h_min)
        self.h_max_slider.setValue(self.h_max)
        self.s_min_slider.setValue(self.s_min)
        self.s_max_slider.setValue(self.s_max)
        self.v_min_slider.setValue(self.v_min)
        self.v_max_slider.setValue(self.v_max)
        self.blur_slider.setValue(self.blur)

        self.update_image()

        self.show()

    def load_setting(self):
        settings = QSettings('settings.ini', QSettings.IniFormat)
        self.h_min = settings.value('h_min', self.h_min, type=int)
        self.h_max = settings.value('h_max', self.h_max, type=int)
        self.s_min = settings.value('s_min', self.s_min, type=int)
        self.s_max = settings.value('s_max', self.s_max, type=int)
        self.v_min = settings.value('v_min', self.v_min, type=int)
        self.v_max = settings.value('v_max', self.v_max, type=int)
        self.blur = settings.value('blur', self.blur, type=int)

    def save_setting(self):
        settings = QSettings('settings.ini', QSettings.IniFormat)
        settings.setValue('h_min', self.h_min)
        settings.setValue('h_max', self.h_max)
        settings.setValue('s_min', self.s_min)
        settings.setValue('s_max', self.s_max)
        settings.setValue('v_min', self.v_min)
        settings.setValue('v_max', self.v_max)
        settings.setValue('blur', self.blur)

    def update_image(self):
        # Get the current threshold values from the sliders
        self.h_min = self.h_min_slider.value()
        self.h_max = self.h_max_slider.value()
        self.s_min = self.s_min_slider.value()
        self.s_max = self.s_max_slider.value()
        self.v_min = self.v_min_slider.value()
        self.v_max = self.v_max_slider.value()
        self.blur = self.blur_slider.value()
        self.blur = (self.blur//2) * 2 + 1

        print("h_min: {0}, h_max: {1},, s_min: {2},, s_max: {3},, v_min: {4}, h_max: {5}".format(self.h_min, self.h_max, self.s_min, self.s_max, self.v_min, self.v_max))

        # Apply the threshold to the image
        lower_threshold = np.array([self.h_min, self.s_min, self.v_min])
        upper_threshold = np.array([self.h_max, self.s_max, self.v_max])
        thresholded_image = cv2.inRange(self.gray_image, lower_threshold, upper_threshold)

        thresholded_image = cv2.medianBlur(thresholded_image, self.blur)
        
        # Update the image label with the thresholded image
        self.image_label.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(thresholded_image, thresholded_image.shape[1], thresholded_image.shape[0], thresholded_image.strides[0], QtGui.QImage.Format_Grayscale8)))
    
    def save(self):
        paras = dict()
        paras['hsv'] =[self.h_min, self.h_max, self.s_min, self.s_max, self.v_min, self.v_max]
        paras['blur'] = self.blur
        self.saved.emit(paras)
        print("Save: h_min: {0}, h_max: {1},, s_min: {2},, s_max: {3},, v_min: {4}, h_max: {5}".format(self.h_min, self.h_max, self.s_min, self.s_max, self.v_min, self.v_max))

        self.save_setting()

    def closeEvent(self, event):
        # Xử lý sự kiện tắt cửa sổ tại đây
        result = QtWidgets.QMessageBox.question(self, "Confirm Exit", "Are you sure you want to exit?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if result == QtWidgets.QMessageBox.Yes:
            if __name__ == '__main__':
                return
            else:
                self.hide()
        
        event.ignore()

if __name__ == '__main__':
    app = QApplication([])
    viewer = ThresholdAdjuster()
    viewer.open(r"C:\Users\Surface LaptopStudio\Desktop\FakeMushroom-Resize\0.jpg")
    app.exec_()
