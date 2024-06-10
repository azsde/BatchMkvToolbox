from mkvEngine.mkvEngine import mkvEngine
from settings.batchMkvToolboxSettings import batchMkvToolboxSettings
from ui.PrefDialog import PrefDialog
from ui.myWidgets import TrackCheckbox
from ui.customLayout import FlowLayout

from functools import partial

from PyQt6.QtWidgets import QFileDialog, QApplication, QMessageBox, QLabel
from pathlib import Path


from PyQt6.QtCore import Qt

from ui.customLayout.FlowLayout import FlowLayout
from ui.MkvFileWidget import MkvFileWidget

import os
import sys

from ui.MainWindow import MainWindow

class BatchMkvToolbox:

    def __init__(self):
        self.sourcePath = ""
        #self.audio_tracks_checkboxes = []
        #self.subs_tracks_checkboxes = []

        # Mapping between files and their progress bars
        self.files_progress_bars = {}

    def openFileNameDialog(self):
        self.sourcePath, _ = QFileDialog.getOpenFileName(None,"Select a file", "","Mkv files (*.mkv)")
        if self.sourcePath:
            print("Opening file: ", self.sourcePath)

            batchMkvToolbox.reset()

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

            batchMkvToolbox.reset()

            # Update the UI
            MainWindow.tabWidget.setVisible(False)
            MainWindow.welcomeFrame.setVisible(True)
            MainWindow.welcomeLabel.setText("Scanning tracks")
            MainWindow.mkvParsingProgressbar.setVisible(True)

            # Start scanning for tracks
            mkv_engine.startScan(self.sourcePath)

    def closeCurrentSession(self):
        self.reset()
        MainWindow.tabWidget.setVisible(False)
        MainWindow.welcomeFrame.setVisible(True)
        MainWindow.mkvParsingProgressbar.setVisible(False)
        MainWindow.welcomeLabel.setText("Open a file or folder to begin")

    def openPreferencesDialog(self):
        PrefDialog(settings).exec()

    # onScanCompleted, populate UI
    def onScanCompleted(self):
        print("Scan completed")
        MainWindow.tabWidget.setVisible(True)
        MainWindow.welcomeFrame.setVisible(False)

        for audioLanguage in mkv_engine.available_languages_and_codecs.audio_languages:
            cb = TrackCheckbox()
            cb.setText(audioLanguage)
            cb.setChecked(True)
            cb.setType(TrackCheckbox.TYPE_AUDIO_LANGUAGE)
            # Important here, since we are connecting the signals in a loop but
            # need to pass the checkbox as a parameter, we use partial
            cb.stateChanged.connect(partial(self.onTrackCheckboxStateChanged, cb))
            MainWindow.audioLanguagesFlowLayout.addWidget(cb)

        for audioCodecs in mkv_engine.available_languages_and_codecs.audio_codecs:
            cb = TrackCheckbox()
            cb.setText(audioCodecs)
            cb.setChecked(True)
            cb.setType(TrackCheckbox.TYPE_AUDIO_CODEC)
            # Important here, since we are connecting the signals in a loop but
            # need to pass the checkbox as a parameter, we use partial
            cb.stateChanged.connect(partial(self.onTrackCheckboxStateChanged, cb))
            MainWindow.audioCodecsFlowLayout.addWidget(cb)

        for subsLanguage in mkv_engine.available_languages_and_codecs.subs_languages:
            cb = TrackCheckbox()
            cb.setText(subsLanguage)
            cb.setChecked(True)
            cb.setType(TrackCheckbox.TYPE_SUBS_LANGUAGE)
            # Important here, since we are connecting the signals in a loop but
            # need to pass the checkbox as a parameter, we use partial
            cb.stateChanged.connect(partial(self.onTrackCheckboxStateChanged, cb))
            MainWindow.subsLanguagesFlowLayout.addWidget(cb)

        for subsCodec in mkv_engine.available_languages_and_codecs.subs_codecs:
            cb = TrackCheckbox()
            cb.setText(subsCodec)
            cb.setChecked(True)
            cb.setType(TrackCheckbox.TYPE_SUBS_CODEC)
            # Important here, since we are connecting the signals in a loop but
            # need to pass the checkbox as a parameter, we use partial
            cb.stateChanged.connect(partial(self.onTrackCheckboxStateChanged, cb))
            MainWindow.subsCodecsFlowLayout.addWidget(cb)

        filesToProcess = sorted(mkv_engine.files_to_process, key=lambda x: x.filepath)
        #for mkv in filesToProcess:
        #    label_width = QLabel(mkv.filepath).fontMetrics().boundingRect(mkv.filepath).width()
        #    max_label_width = (int)(max(max_label_width, label_width)*0.75)
        for mkv in filesToProcess:
            #MainWindow.filesToProcessVerticalLayout.addWidget(mkv.filepath)
            widget = MkvFileWidget(mkv.filepath)
            self.files_progress_bars[mkv] = widget
            MainWindow.filesToProcessVerticalLayout.addWidget(widget)

    def onTrackCheckboxStateChanged(self, checkbox):
        #if checkbox.isChecked():
        #    print("Checkbox " + checkbox.text() + "("+ checkbox.type +") is checked")
        #else:
        #    print("Checkbox " + checkbox.text() + "("+ checkbox.type +") is unchecked")
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

    def reset(self):
        # Reset the mkv engine
        mkv_engine.reset()

        # Clear the UI
        for i in reversed(range(MainWindow.audioLanguagesFlowLayout.count())):
            MainWindow.audioLanguagesFlowLayout.itemAt(i).widget().deleteLater()
        for i in reversed(range(MainWindow.subsLanguagesFlowLayout.count())):
            MainWindow.subsLanguagesFlowLayout.itemAt(i).widget().deleteLater()
        for i in reversed(range(MainWindow.audioCodecsFlowLayout.count())):
            MainWindow.audioCodecsFlowLayout.itemAt(i).widget().deleteLater()
        for i in reversed(range(MainWindow.subsCodecsFlowLayout.count())):
            MainWindow.subsCodecsFlowLayout.itemAt(i).widget().deleteLater()
        for i in reversed(range(MainWindow.filesToProcessVerticalLayout.count())):
            MainWindow.filesToProcessVerticalLayout.itemAt(i).widget().deleteLater()

        self.files_progress_bars.clear()

    def update_remux_progress(self, tuple):
        mkv = tuple[0]
        progress = tuple[1]

        widget = self.files_progress_bars[mkv]
        widget.update_progress(progress)
        #print(f"Todo : Update progress UI: {tuple[0].filepath} - {tuple[1]}%")

    def output_file_alread_exist_prompt(self, tuple):
        mkvFile = tuple[0]
        initial_output_file = tuple[1]
        outputPath = self.openExistingFileDialog(mkvFile, initial_output_file, settings.getIntParam(batchMkvToolboxSettings.OUTPUT_FILE_SETTING))
        if outputPath:
            mkv_engine.resolve_output_conflict(mkvFile, outputPath)
        print(f"Output path on conflict: {outputPath}")


    # When a file already exist at the output location, open a dialog to ask the user what do to.
    # Parameters:
    # - mkvFile : the mkvFile to be processed
    # - outputPath : the output path the output file is supposed to be placed at.
    def openExistingFileDialog(self, mkvFile, outputPath, outputFileSetting):
        print("openExistingFileDialog")
        dlg = QMessageBox()
        dlg.setWindowTitle("Output file already exists.")
        dlg.setText("The output file " + str(outputPath) + " already exists.\nWhat do you wish to do ?")
        renameBtn = dlg.addButton("Rename new file", QMessageBox.ButtonRole.YesRole)
        skipBtn = dlg.addButton("Skip file", QMessageBox.ButtonRole.YesRole)
        overwriteBtn = dlg.addButton("Overwrite existing file", QMessageBox.ButtonRole.YesRole)
        dlg.setIcon(QMessageBox.Icon.Warning)
        dlg.setDefaultButton(renameBtn)
        dlg.exec()
        # BUG WITH THE RENAME FEATURE, DOESN'T PLACE THE OUTPUT FILE IN THE CORRECT FOLDER
        if dlg.clickedButton() == renameBtn:
            tryNumber = 1
            while os.path.exists(outputPath):
                # Append "REMUX" only if the output file setting is set to batchMkvToolboxSettings.OUTPUT_FILE_IN_SAME_FOLDER_AS_ORIGINAL
                if (outputFileSetting == batchMkvToolboxSettings.OUTPUT_FILE_IN_SAME_FOLDER_AS_ORIGINAL):
                    filename = Path(mkvFile.filepath).stem + "-REMUX(" + str(tryNumber)+").mkv"
                else:
                    filename = Path(mkvFile.filepath).stem + "(" + str(tryNumber)+").mkv"
                outputPath = os.path.join(Path(outputPath).parent.absolute(), filename)
                tryNumber += 1
        elif dlg.clickedButton() == skipBtn:
            outputPath = ""
        elif dlg.clickedButton() == overwriteBtn:
            print("Warning: " + outputPath + " will be overwritten.")
        return outputPath

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
        cb.stateChanged.connect(partial(batchMkvToolbox.onTrackCheckboxStateChanged, cb))
        MainWindow.audioLanguagesFlowLayout.addWidget(cb)
    for i in range (10):
        cb = TrackCheckbox()
        cb.setText("subsLanguage - " + str(i))
        cb.setChecked(True)
        cb.setType(TrackCheckbox.TYPE_SUBS_LANGUAGE)
        # Important here, since we are connecting the signals in a loop but
        # need to pass the checkbox as a parameter, we use partial
        cb.stateChanged.connect(partial(batchMkvToolbox.onTrackCheckboxStateChanged, cb))
        MainWindow.subsLanguagesFlowLayout.addWidget(cb)
    for i in range (10):
        cb = TrackCheckbox()
        cb.setText("audioCodec - " + str(i))
        cb.setChecked(True)
        cb.setType(TrackCheckbox.TYPE_AUDIO_CODEC)
        # Important here, since we are connecting the signals in a loop but
        # need to pass the checkbox as a parameter, we use partial
        cb.stateChanged.connect(partial(batchMkvToolbox.onTrackCheckboxStateChanged, cb))
        MainWindow.audioCodecsFlowLayout.addWidget(cb)
    for i in range (10):
        cb = TrackCheckbox()
        cb.setText("subsCodec - " + str(i))
        cb.setChecked(True)
        cb.setType(TrackCheckbox.TYPE_SUBS_CODEC)
        # Important here, since we are connecting the signals in a loop but
        # need to pass the checkbox as a parameter, we use partial
        cb.stateChanged.connect(partial(batchMkvToolbox.onTrackCheckboxStateChanged, cb))
        MainWindow.subsCodecsFlowLayout.addWidget(cb)

# Method to connect all signals from the UI components
def connectUiSignals():
    # Open file/folder actions
    MainWindow.actionOpen_file.triggered.connect(lambda: batchMkvToolbox.openFileNameDialog())
    MainWindow.actionOpen_folder.triggered.connect(lambda: batchMkvToolbox.openFolderDialog())
    # Close currently opened file/folder
    MainWindow.actionClose_current_file_folder.triggered.connect(lambda: batchMkvToolbox.closeCurrentSession())

    MainWindow.actionPreferences.triggered.connect(lambda: batchMkvToolbox.openPreferencesDialog())

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

    MainWindow.remove_forced_subs_checkbox.stateChanged.connect(lambda state: mkv_engine.setForcedTrackRemoval(MainWindow.remove_forced_subs_checkbox.isChecked()))

    # Process files
    MainWindow.processFilesPushButton.clicked.connect(lambda: mkv_engine.startTracksRemoval())

if __name__ == "__main__":
    # Create app
    app = QApplication(sys.argv)
    # Create UI and show it
    MainWindow = MainWindow()
    MainWindow.show()

    settings = batchMkvToolboxSettings()

    # Init the remove forced subs checkbox
    MainWindow.remove_forced_subs_checkbox.setChecked(settings.getBoolParam(batchMkvToolboxSettings.REMOVE_FORCED_TRACKS_SETTING))

    # Create BatchMkvToolBox instance
    batchMkvToolbox = BatchMkvToolbox()
    # Connect UI signals
    connectUiSignals()
    # Create MKV engine and connect it to the batch mkv toolbox
    mkv_engine = mkvEngine(settings)
    mkv_engine.scanFinished.connect(batchMkvToolbox.onScanCompleted)
    mkv_engine.fileRemuxProgress.connect(batchMkvToolbox.update_remux_progress)
    mkv_engine.outputFileAlreadyExist.connect(batchMkvToolbox.output_file_alread_exist_prompt)
    #fakeContent()
    sys.exit(app.exec())
