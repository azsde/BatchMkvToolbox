from fileinput import filename
from mkvEngine.mkvEngine import mkvEngine
from ui.mainwindow import Ui_MainWindow

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QListWidgetItem

import glob
import os
import sys
import threading


class QtBatchMkvToolbox:

    def __init__(self):
        self.sourcePath = ""

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
        for i in range(10):
            item = QListWidgetItem()
            item.setText("Dada")
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            ui.listWidget.addItem(item)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    batchMkvToolbox = QtBatchMkvToolbox()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    ui.tabWidget.setVisible(False)
    ui.mkvParsingProgressbar.setVisible(False)

    ui.actionOpen_file.triggered.connect(lambda: batchMkvToolbox.openFileNameDialog())
    ui.actionOpen_folder.triggered.connect(lambda: batchMkvToolbox.openFolderDialog())
    ui.actionExit.triggered.connect(lambda: sys.exit(app.exec_()))

    mkv_engine = mkvEngine()
    mkv_engine.scanFinished.connect(batchMkvToolbox.onScanCompleted)

    MainWindow.show()
    sys.exit(app.exec_())