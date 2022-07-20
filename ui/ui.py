from PyQt5.QtWidgets import QMainWindow, QTabWidget, QProgressBar
from PyQt5 import uic

class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()

        # Load the UI file
        uic.loadUi("ui/mainwindow.ui", self)