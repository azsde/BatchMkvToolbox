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

    def closeCurrentSession(self):
        self.clear()
        MainWindow.tabWidget.setVisible(False)
        MainWindow.welcomeFrame.setVisible(True)
        MainWindow.mkvParsingProgressbar.setVisible(False)
        MainWindow.welcomeLabel.setText("Open a file or folder to begin")

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

    def massCheckUncheck(self, type, isChecked):
        for i in range(MainWindow.audioTracksFlowLayout.count()):
            if (type == "audio"):
                MainWindow.audioTracksFlowLayout.itemAt(i).widget().setChecked(isChecked)
            elif (type == "subs"):
                MainWindow.subsTracksFlowLayout.itemAt(i).widget().setChecked(isChecked)

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

# Method to connect all signals from the UI components
def connectUiSignals():
    # Open file/folder actions
    MainWindow.actionOpen_file.triggered.connect(lambda: batchMkvToolbox.openFileNameDialog())
    MainWindow.actionOpen_folder.triggered.connect(lambda: batchMkvToolbox.openFolderDialog())
    # Close currently opened file/folder
    MainWindow.actionClose_current_file_folder.triggered.connect(lambda: batchMkvToolbox.closeCurrentSession())
    # Exit
    MainWindow.actionExit.triggered.connect(lambda: sys.exit())

    # Right click actions to mass check/uncheck subs
    MainWindow.actionSelect_all_audio_tracks.triggered.connect(lambda: batchMkvToolbox.massCheckUncheck("audio", True))
    MainWindow.actionDeselect_all_audio_tracks.triggered.connect(lambda: batchMkvToolbox.massCheckUncheck("audio", False))
    MainWindow.actionSelect_all_subs_tracks.triggered.connect(lambda: batchMkvToolbox.massCheckUncheck("subs", True))
    MainWindow.actionDeselect_all_subs_tracks.triggered.connect(lambda: batchMkvToolbox.massCheckUncheck("subs", False))

if __name__ == "__main__":
    # Create app
    app = QApplication(sys.argv)
    # Create UI and show it
    MainWindow = UI()
    MainWindow.show()
    # Create BatchMkvToolBox instance
    batchMkvToolbox = BatchMkvToolbox()
    # Connect UI signals
    connectUiSignals()
    # Create MKV engine and connect it to the batch mkv toolbox
    mkv_engine = mkvEngine()
    mkv_engine.scanFinished.connect(batchMkvToolbox.onScanCompleted)
    debug()
    sys.exit(app.exec())