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

        # Create and assign the flow layouts
        # Audio tracks
        self.audioLanguagesFlowLayout = FlowLayout(self.audioLanguagesScrollAreaWidget, orientation=Qt.Orientation.Vertical)
        self.audioLanguagesFlowLayout.widthChanged.connect(self.audioLanguagesScrollAreaWidget.setMinimumWidth)
        self.audioLanguagesFlowLayout.setObjectName("audioLanguagesFlowLayout")
        # Audio codecs
        self.audioCodecsFlowLayout = FlowLayout(self.audioCodecsScrollAreaWidget, orientation=Qt.Orientation.Vertical)
        self.audioCodecsFlowLayout.widthChanged.connect(self.audioCodecsScrollAreaWidget.setMinimumWidth)
        self.audioCodecsFlowLayout.setObjectName("audioCodecsFlowLayout")
        # Subs tracks
        self.subsLanguagesFlowLayout = FlowLayout(self.subLanguagesScrollAreaWidget, orientation=Qt.Orientation.Vertical)
        self.subsLanguagesFlowLayout.widthChanged.connect(self.subLanguagesScrollAreaWidget.setMinimumWidth)
        self.subsLanguagesFlowLayout.setObjectName("subsLanguagesFlowLayout")
        # Subs codecs
        self.subsCodecsFlowLayout = FlowLayout(self.subsCodecsScrollAreaWidget, orientation=Qt.Orientation.Vertical)
        self.subsCodecsFlowLayout.widthChanged.connect(self.subsCodecsScrollAreaWidget.setMinimumWidth)
        self.subsCodecsFlowLayout.setObjectName("subsCodecsFlowLayout")

        # Add right click actions
        self.audioLanguagesScrollArea.addAction(self.actionSelect_all_audio_languages)
        self.audioLanguagesScrollArea.addAction(self.actionDeselect_all_audio_languages)

        self.subLanguagesScrollArea.addAction(self.actionSelect_all_subs_languages)
        self.subLanguagesScrollArea.addAction(self.actionDeselect_all_subs_languages)

        self.audioCodecsScrollArea.addAction(self.actionSelect_all_audio_codecs)
        self.audioCodecsScrollArea.addAction(self.actionDeselect_all_audio_codecs)

        self.subsCodecsScrollArea.addAction(self.actionSelect_all_subs_codecs)
        self.subsCodecsScrollArea.addAction(self.actionDeselect_all_subs_codecs)

        #self.processFilesPushButton.clicked.connect(lambda: self.tabWidget.setEnabled(False))

        self.resize(QtGui.QGuiApplication.primaryScreen().availableGeometry().size() * 0.65)
        self.center()

    def center(self):

        qr = self.frameGeometry()
        cp = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()

        qr.moveCenter(cp)
        self.move(qr.topLeft())