from PyQt6.QtWidgets import QMainWindow, QTabWidget, QProgressBar
from PyQt6 import uic, QtGui

from PyQt6.QtCore import Qt

from ui.customLayout.FlowLayout import FlowLayout

class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()

        # Load the UI file
        uic.loadUi("ui/mainwindow.ui", self)

        # Initial hide
        self.tabWidget.setVisible(False)
        self.mkvParsingProgressbar.setVisible(False)

        # Create and assign the flow layout
        self.audioTracksFlowLayout = FlowLayout(self.audioTracksScrollAreaWidget, orientation=Qt.Orientation.Vertical)
        self.audioTracksFlowLayout.widthChanged.connect(self.audioTracksScrollAreaWidget.setMinimumWidth)
        self.audioTracksFlowLayout.setObjectName("audioTracksFlowLayout")
        self.subsTracksFlowLayout = FlowLayout(self.subTracksScrollAreaWidget, orientation=Qt.Orientation.Vertical)
        self.subsTracksFlowLayout.widthChanged.connect(self.subTracksScrollAreaWidget.setMinimumWidth)
        self.subsTracksFlowLayout.setObjectName("subsTracksFlowLayout")

        # Add right click actions
        self.audioTracksScrollArea.addAction(self.actionSelect_all_audio_tracks)
        self.audioTracksScrollArea.addAction(self.actionDeselect_all_audio_tracks)

        self.subTracksScrollArea.addAction(self.actionSelect_all_subs_tracks)
        self.subTracksScrollArea.addAction(self.actionDeselect_all_subs_tracks)

        self.pushButton.clicked.connect(lambda: self.tabWidget.setEnabled(False))

        self.resize(QtGui.QGuiApplication.primaryScreen().availableGeometry().size() * 0.65)
        self.center()

    def center(self):

        qr = self.frameGeometry()
        cp = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()

        qr.moveCenter(cp)
        self.move(qr.topLeft())