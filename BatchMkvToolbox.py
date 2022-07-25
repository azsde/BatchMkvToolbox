from mkvEngine.mkvEngine import mkvEngine
from ui.TrackCheckbox import TrackCheckbox
from ui.customLayout import FlowLayout

from functools import partial

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QFileDialog, QApplication


from PyQt6.QtCore import Qt

from ui.customLayout.FlowLayout import FlowLayout

import sys

from ui.ui import UI

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
            batchMkvToolbox.clear()

            # Update the UI
            MainWindow.tabWidget.setVisible(False)
            MainWindow.welcomeFrame.setVisible(True)
            MainWindow.welcomeLabel.setText("Scanning tracks")
            MainWindow.mkvParsingProgressbar.setVisible(True)

            # Start scanning for tracks
            mkv_engine.startScan(self.sourcePath)

    def openFolderDialog(self):
        self.sourcePath = QFileDialog.getExistingDirectory(None,"Select a folder")
        if self.sourcePath:
            print("Opening folder: ", self.sourcePath)

            # Reset the mkv engine
            mkv_engine.reset()

            # Update the UI
            MainWindow.tabWidget.setVisible(False)
            MainWindow.welcomeFrame.setVisible(True)
            MainWindow.welcomeLabel.setText("Scanning tracks")
            MainWindow.mkvParsingProgressbar.setVisible(True)

            # Start scanning for tracks
            mkv_engine.startScan(self.sourcePath)

    # onScanCompleted, populate UI
    def onScanCompleted(self):
        print("Scan completed")
        MainWindow.tabWidget.setVisible(True)
        MainWindow.welcomeFrame.setVisible(False)

        for audioLanguage in mkv_engine.available_audio_languages:
            cb = TrackCheckbox()
            cb.setText(audioLanguage)
            cb.setChecked(True)
            cb.setType("audio")
            # Important here, since we are connecting the signals in a loop but
            # need to pass the checkbox as a parameter, we use partial
            cb.stateChanged.connect(partial(self.doCheck, cb))
            MainWindow.audioTracksFlowLayout.addWidget(cb)

        for subsLanguage in mkv_engine.available_subs_languages:
            cb = TrackCheckbox()
            cb.setText(subsLanguage)
            cb.setChecked(True)
            cb.setType("subs")
            # Important here, since we are connecting the signals in a loop but
            # need to pass the checkbox as a parameter, we use partial
            cb.stateChanged.connect(partial(self.doCheck, cb))
            MainWindow.subsTracksFlowLayout.addWidget(cb)

    def doCheck(self, checkbox):
        if checkbox.isChecked():
            print("Checkbox " + checkbox.text() + "("+ checkbox.type +") is checked")
        else:
            print("Checkbox " + checkbox.text() + "("+ checkbox.type +") is unchecked")

    def clear(self):
        for i in reversed(range(MainWindow.audioTracksFlowLayout.count())):
            MainWindow.audioTracksFlowLayout.itemAt(i).widget().deleteLater()
        for i in reversed(range(MainWindow.subsTracksFlowLayout.count())):
            MainWindow.subsTracksFlowLayout.itemAt(i).widget().deleteLater()

# Method to simulate a MKV with lots of tracks
def debug():
    MainWindow.tabWidget.setVisible(True)
    MainWindow.welcomeFrame.setVisible(False)

    batchMkvToolbox.clear()

    for i in range (10):
        cb = TrackCheckbox()
        cb.setText("audioLanguage - " + str(i))
        cb.setChecked(True)
        cb.setType("audio")
        # Important here, since we are connecting the signals in a loop but
        # need to pass the checkbox as a parameter, we use partial
        #cb.stateChanged.connect(partial(self.doCheck, cb))
        MainWindow.audioTracksFlowLayout.addWidget(cb)
    for i in range (10):
        cb = TrackCheckbox()
        cb.setText("subsLanguage - " + str(i))
        cb.setChecked(True)
        cb.setType("subs")
        # Important here, since we are connecting the signals in a loop but
        # need to pass the checkbox as a parameter, we use partial
        #cb.stateChanged.connect(partial(self.doCheck, cb))
        MainWindow.subsTracksFlowLayout.addWidget(cb)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = UI()
    MainWindow.show()

    batchMkvToolbox = BatchMkvToolbox()

    MainWindow.tabWidget.setVisible(False)
    MainWindow.mkvParsingProgressbar.setVisible(False)

    MainWindow.actionOpen_file.triggered.connect(lambda: batchMkvToolbox.openFileNameDialog())
    MainWindow.actionOpen_folder.triggered.connect(lambda: batchMkvToolbox.openFolderDialog())
    MainWindow.actionOpen_folder.triggered.connect(lambda: batchMkvToolbox.closeCurrentSession())
    MainWindow.actionExit.triggered.connect(lambda: sys.exit(app.exec_()))

    mkv_engine = mkvEngine()
    mkv_engine.scanFinished.connect(batchMkvToolbox.onScanCompleted)

    sys.exit(app.exec())