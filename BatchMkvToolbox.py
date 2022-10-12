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
            cb.setType(TrackCheckbox.TYPE_AUDIO_LANGUAGE)
            # Important here, since we are connecting the signals in a loop but
            # need to pass the checkbox as a parameter, we use partial
            cb.stateChanged.connect(partial(self.onCheckboxStateChanged, cb))
            MainWindow.audioLanguagesFlowLayout.addWidget(cb)

        for audioCodecs in mkv_engine.available_audio_codecs:
            cb = TrackCheckbox()
            cb.setText(audioCodecs)
            cb.setChecked(True)
            cb.setType(TrackCheckbox.TYPE_AUDIO_CODEC)
            # Important here, since we are connecting the signals in a loop but
            # need to pass the checkbox as a parameter, we use partial
            cb.stateChanged.connect(partial(self.onCheckboxStateChanged, cb))
            MainWindow.audioCodecsFlowLayout.addWidget(cb)

        for subsLanguage in mkv_engine.available_subs_languages:
            cb = TrackCheckbox()
            cb.setText(subsLanguage)
            cb.setChecked(True)
            cb.setType(TrackCheckbox.TYPE_SUBS_LANGUAGE)
            # Important here, since we are connecting the signals in a loop but
            # need to pass the checkbox as a parameter, we use partial
            cb.stateChanged.connect(partial(self.onCheckboxStateChanged, cb))
            MainWindow.subsLanguagesFlowLayout.addWidget(cb)

        for subsCodec in mkv_engine.available_subs_codecs:
            cb = TrackCheckbox()
            cb.setText(subsCodec)
            cb.setChecked(True)
            cb.setType(TrackCheckbox.TYPE_SUBS_CODEC)
            # Important here, since we are connecting the signals in a loop but
            # need to pass the checkbox as a parameter, we use partial
            cb.stateChanged.connect(partial(self.onCheckboxStateChanged, cb))
            MainWindow.subsCodecsFlowLayout.addWidget(cb)

    def onCheckboxStateChanged(self, checkbox):
        if checkbox.isChecked():
            print("Checkbox " + checkbox.text() + "("+ checkbox.type +") is checked")
        else:
            print("Checkbox " + checkbox.text() + "("+ checkbox.type +") is unchecked")
        mkv_engine.updateTracksToRemove(checkbox)

    def massCheckUncheck(self, type, isChecked):
        match type:
            case TrackCheckbox.TYPE_AUDIO_LANGUAGE:
                targetFlowLayout = MainWindow.audioLanguagesFlowLayout
            case TrackCheckbox.TYPE_SUBS_LANGUAGE:
                targetFlowLayout = MainWindow.subsLanguagesFlowLayout
            case TrackCheckbox.TYPE_AUDIO_CODEC:
                targetFlowLayout = MainWindow.audioCodecsFlowLayout
            case TrackCheckbox.TYPE_SUBS_CODEC:
                targetFlowLayout = MainWindow.subsCodecsFlowLayout
        for i in range(targetFlowLayout.count()):
            targetFlowLayout.itemAt(i).widget().setChecked(isChecked)

    def clear(self):
        for i in reversed(range(MainWindow.audioLanguagesFlowLayout.count())):
            MainWindow.audioLanguagesFlowLayout.itemAt(i).widget().deleteLater()
        for i in reversed(range(MainWindow.subsLanguagesFlowLayout.count())):
            MainWindow.subsLanguagesFlowLayout.itemAt(i).widget().deleteLater()

# Method to simulate a MKV with lots of tracks
def fakeContent():
    MainWindow.tabWidget.setVisible(True)
    MainWindow.welcomeFrame.setVisible(False)

    batchMkvToolbox.clear()

    for i in range (10):
        cb = TrackCheckbox()
        cb.setText("audioLanguage - " + str(i))
        cb.setChecked(True)
        cb.setType(TrackCheckbox.TYPE_AUDIO_LANGUAGE)
        # Important here, since we are connecting the signals in a loop but
        # need to pass the checkbox as a parameter, we use partial
        cb.stateChanged.connect(partial(batchMkvToolbox.onCheckboxStateChanged, cb))
        MainWindow.audioLanguagesFlowLayout.addWidget(cb)
    for i in range (10):
        cb = TrackCheckbox()
        cb.setText("subsLanguage - " + str(i))
        cb.setChecked(True)
        cb.setType(TrackCheckbox.TYPE_SUBS_LANGUAGE)
        # Important here, since we are connecting the signals in a loop but
        # need to pass the checkbox as a parameter, we use partial
        cb.stateChanged.connect(partial(batchMkvToolbox.onCheckboxStateChanged, cb))
        MainWindow.subsLanguagesFlowLayout.addWidget(cb)
    for i in range (10):
        cb = TrackCheckbox()
        cb.setText("audioCodec - " + str(i))
        cb.setChecked(True)
        cb.setType(TrackCheckbox.TYPE_AUDIO_CODEC)
        # Important here, since we are connecting the signals in a loop but
        # need to pass the checkbox as a parameter, we use partial
        cb.stateChanged.connect(partial(batchMkvToolbox.onCheckboxStateChanged, cb))
        MainWindow.audioCodecsFlowLayout.addWidget(cb)
    for i in range (10):
        cb = TrackCheckbox()
        cb.setText("subsCodec - " + str(i))
        cb.setChecked(True)
        cb.setType(TrackCheckbox.TYPE_SUBS_CODEC)
        # Important here, since we are connecting the signals in a loop but
        # need to pass the checkbox as a parameter, we use partial
        cb.stateChanged.connect(partial(batchMkvToolbox.onCheckboxStateChanged, cb))
        MainWindow.subsCodecsFlowLayout.addWidget(cb)

# Method to connect all signals from the UI components
def connectUiSignals():
    # Open file/folder actions
    MainWindow.actionOpen_file.triggered.connect(lambda: batchMkvToolbox.openFileNameDialog())
    MainWindow.actionOpen_folder.triggered.connect(lambda: batchMkvToolbox.openFolderDialog())
    # Close currently opened file/folder
    MainWindow.actionClose_current_file_folder.triggered.connect(lambda: batchMkvToolbox.closeCurrentSession())
    # Exit
    MainWindow.actionExit.triggered.connect(lambda: sys.exit())

    # Right click actions to mass check/uncheck
    MainWindow.actionSelect_all_audio_languages.triggered.connect(lambda: batchMkvToolbox.massCheckUncheck(TrackCheckbox.TYPE_AUDIO_LANGUAGE, True))
    MainWindow.actionDeselect_all_audio_languages.triggered.connect(lambda: batchMkvToolbox.massCheckUncheck(TrackCheckbox.TYPE_AUDIO_LANGUAGE, False))
    MainWindow.actionSelect_all_subs_languages.triggered.connect(lambda: batchMkvToolbox.massCheckUncheck(TrackCheckbox.TYPE_SUBS_LANGUAGE, True))
    MainWindow.actionDeselect_all_subs_languages.triggered.connect(lambda: batchMkvToolbox.massCheckUncheck(TrackCheckbox.TYPE_SUBS_LANGUAGE, False))
    MainWindow.actionSelect_all_audio_codecs.triggered.connect(lambda: batchMkvToolbox.massCheckUncheck(TrackCheckbox.TYPE_AUDIO_CODEC, True))
    MainWindow.actionDeselect_all_audio_codecs.triggered.connect(lambda: batchMkvToolbox.massCheckUncheck(TrackCheckbox.TYPE_AUDIO_CODEC, False))
    MainWindow.actionSelect_all_subs_codecs.triggered.connect(lambda: batchMkvToolbox.massCheckUncheck(TrackCheckbox.TYPE_SUBS_CODEC, True))
    MainWindow.actionDeselect_all_subs_codecs.triggered.connect(lambda: batchMkvToolbox.massCheckUncheck(TrackCheckbox.TYPE_SUBS_CODEC, False))

    # Process files
    MainWindow.processFilesPushButton.clicked.connect(lambda: print("dadada"))

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
    fakeContent()
    sys.exit(app.exec())