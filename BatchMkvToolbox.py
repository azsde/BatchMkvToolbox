from fileinput import filename
from mkvEngine.mkvEngine import mkvEngine
from ui.TrackCheckbox import TrackCheckbox
from ui.mainwindow import Ui_MainWindow
from ui.customLayout import FlowLayout

from functools import partial


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QListWidgetItem, QScrollArea, QLabel, QCheckBox, QHBoxLayout


from PyQt5.QtCore import QPoint, QRect, QSize, Qt

from ui.customLayout.FlowLayout import FlowLayout

import glob
import os
import sys
import threading


class BatchMkvToolbox:

    def __init__(self):
        self.sourcePath = ""
        #self.audio_tracks_checkboxes = []
        #self.subs_tracks_checkboxes = []

    def openFileNameDialog(self):
        self.sourcePath, _ = QFileDialog.getOpenFileName(None,"Select a file", "","Mkv files (*.mkv)")
        if self.sourcePath:
            print("Opening file: ", self.sourcePath)
            
            # Reset the mkv engine
            mkv_engine.reset()
            
            # Update the UI
            ui.tabWidget.setVisible(False)
            ui.welcomeFrame.setVisible(True)
            ui.welcomeLabel.setText("Scanning tracks")
            ui.mkvParsingProgressbar.setVisible(True)

            # Start scanning for tracks
            mkv_engine.startScan(self.sourcePath)

    def openFolderDialog(self):
        self.sourcePath = QFileDialog.getExistingDirectory(None,"Select a folder")
        if self.sourcePath:
            print("Opening folder: ", self.sourcePath)

            # Reset the mkv engine
            mkv_engine.reset()

            # Update the UI
            ui.tabWidget.setVisible(False)
            ui.welcomeFrame.setVisible(True)
            ui.welcomeLabel.setText("Scanning tracks")
            ui.mkvParsingProgressbar.setVisible(True)

            # Start scanning for tracks
            mkv_engine.startScan(self.sourcePath)

    # onScanCompleted, populate UI
    def onScanCompleted(self):
        print("Scan completed")
        ui.tabWidget.setVisible(True)
        ui.welcomeFrame.setVisible(False)

        for i in range(2):
            for audioLanguage in mkv_engine.available_audio_languages:
                cb = TrackCheckbox()
                cb.setText(audioLanguage + " - " + str(i))
                cb.setChecked(True)
                cb.setType("audio")
                cb.setFixedWidth(100)
                # Important here, since we are connecting the signals in a loop but
                # need to pass the checkbox as a parameter, we use partial
                cb.stateChanged.connect(partial(self.doCheck, cb))
                self.audioTracksFlowLayout.addWidget(cb)

        for i in range(2):
            for subsLanguage in mkv_engine.available_subs_languages:
                cb = TrackCheckbox()
                cb.setText(subsLanguage)
                cb.setChecked(True)
                cb.setType("subs")
                cb.setFixedWidth(100)
                # Important here, since we are connecting the signals in a loop but
                # need to pass the checkbox as a parameter, we use partial
                cb.stateChanged.connect(partial(self.doCheck, cb))
                self.subsTracksFlowLayout.addWidget(cb)

    def doCheck(self, checkbox):
        if checkbox.isChecked():
            print("Checkbox " + checkbox.text() + "("+ checkbox.type +") is checked")
        else:
            print("Checkbox " + checkbox.text() + "("+ checkbox.type +") is unchecked")

    def initCustomUi(self):

        self.audioTracksFlowLayout = FlowLayout(ui.audioTracksScrollAreaWidget, orientation=Qt.Vertical)
        self.audioTracksFlowLayout.widthChanged.connect(ui.audioTracksScrollAreaWidget.setMinimumWidth)
        self.audioTracksFlowLayout.setObjectName("audioTracksFlowLayout")

        self.subsTracksFlowLayout = FlowLayout(ui.subTracksScrollAreaWidget, orientation=Qt.Vertical)
        self.subsTracksFlowLayout.widthChanged.connect(ui.subTracksScrollAreaWidget.setMinimumWidth)
        self.subsTracksFlowLayout.setObjectName("subsTracksFlowLayout")

    def debug(self):
        ui.tabWidget.setVisible(True)
        ui.welcomeFrame.setVisible(False)
        
        for i in range (10):
            cb = TrackCheckbox()
            cb.setText("audioLanguage - " + str(i))
            cb.setChecked(True)
            cb.setType("audio")
            # Important here, since we are connecting the signals in a loop but
            # need to pass the checkbox as a parameter, we use partial
            cb.stateChanged.connect(partial(self.doCheck, cb))
            self.audioTracksFlowLayout.addWidget(cb)
        for i in range (17):
            cb = TrackCheckbox()
            cb.setText("subsLanguage - " + str(i))
            cb.setChecked(True)
            cb.setType("subs")
            # Important here, since we are connecting the signals in a loop but
            # need to pass the checkbox as a parameter, we use partial
            cb.stateChanged.connect(partial(self.doCheck, cb))
            self.subsTracksFlowLayout.addWidget(cb)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    batchMkvToolbox = BatchMkvToolbox()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.tabWidget.setVisible(False)
    ui.mkvParsingProgressbar.setVisible(False)

    ui.actionOpen_file.triggered.connect(lambda: batchMkvToolbox.openFileNameDialog())
    ui.actionOpen_folder.triggered.connect(lambda: batchMkvToolbox.openFolderDialog())
    ui.actionExit.triggered.connect(lambda: sys.exit(app.exec_()))

    batchMkvToolbox.initCustomUi()

    #ui.testFlowLayout.setAlignment(QtCore.Qt.AlignTop)
    #ui.subsTracksListVBoxLayout.setAlignment(QtCore.Qt.AlignTop)

    mkv_engine = mkvEngine()
    mkv_engine.scanFinished.connect(batchMkvToolbox.onScanCompleted)

    ui.pushButton.clicked.connect(lambda: ui.tabWidget.setEnabled(False))

    batchMkvToolbox.debug()

    MainWindow.show()
    sys.exit(app.exec_())