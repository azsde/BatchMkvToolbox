import os

from pathlib import Path
from PyQt6.QtCore import (QObject, QThread, pyqtSignal)
from mkvEngine.mkvFile import mkvFile
from ui.myWidgets import TrackCheckbox

from PyQt6.QtWidgets import QMessageBox

from mkvEngine.mkvMergeJsonConstants import *
from settings.batchMkvToolboxSettings import *

class mkvEngine(QObject):

    scanFinished = pyqtSignal()

    class mkvEngineWorker(QObject):

        finished = pyqtSignal()

        def __init__(self, outer_instance, path):
            super().__init__()
            self.outer_instance = outer_instance
            self.path = path

        def startScanTracks(self):
            # If this is a folder, scan recursively every file in it
            if os.path.isdir(self.path):
                self.outer_instance.baseFolder = Path(self.path)
                for file in list(Path(self.path).rglob("*.[mM][kK][vV]")):
                    print("Found file: ", str(file.resolve()))
                    self.outer_instance.scanAvailableLanguages(str(file.resolve()))
                #TODO: Reorder alphabetically

            elif os.path.isfile(self.path):
                self.outer_instance.scanAvailableLanguages(self.path)
            else:
                print("Not a file or folder")
                return
            self.finished.emit()

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.mkvMergePath = settings.getStrParam(batchMkvToolboxSettings.MKV_MERGE_LOCATION_SETTING)
        # Base folder for folder processing
        self.baseFolder = ""
        # List of files to be processed
        self.files_to_process = []
        # List of all available audio languages
        self.available_audio_languages = []
        # List of all available subs language
        self.available_subs_languages = []
        # List of all available audio codecs
        self.available_audio_codecs = []
        # List of all available subs codecs
        self.available_subs_codecs = []
        # List of tracks to be removed
        self.audio_languages_to_remove = []
        self.subs_languages_to_remove = []
        self.audio_codecs_to_remove = []
        self.subs_codecs_to_remove = []

    def reset(self):
        self.files_to_process.clear()
        self.available_audio_languages.clear()
        self.available_subs_languages.clear()
        self.available_audio_codecs.clear()
        self.available_subs_codecs.clear()
        self.audio_languages_to_remove.clear()
        self.subs_languages_to_remove.clear()
        self.audio_codecs_to_remove.clear()
        self.subs_codecs_to_remove.clear()

    def startScan(self, path):
        # 1 - Create a QThread
        self.objThread = QThread()
        # 2 - Create a Worker
        self.obj = mkvEngine.mkvEngineWorker(self, path)
        # 3 - Move the Worker to the QThread
        self.obj.moveToThread(self.objThread)
        # 4 - Connect the signals
        self.obj.finished.connect(self.objThread.quit)
        #self.objThread.started.connect(lambda: self.obj.startScanTracks(path))
        self.objThread.started.connect(self.obj.startScanTracks)
        self.objThread.finished.connect(self.scanFinished.emit)
        # 5 - Start the QThread
        self.objThread.start()

    def scanAvailableLanguages(self, file_path):
        print("Processing: " + file_path)
        mkv = mkvFile(file_path, self.mkvMergePath)

        self.files_to_process.append(mkv)
        for audioTrack in mkv.getTracksByType(AUDIO_TYPE):
            if audioTrack.language not in self.available_audio_languages:
                self.available_audio_languages.append(audioTrack.language)
            if audioTrack.codec not in self.available_audio_codecs:
                self.available_audio_codecs.append(audioTrack.codec)
        for subtitlesTrack in mkv.getTracksByType(SUBTITLES_TYPE):
            if subtitlesTrack.language not in self.available_subs_languages:
                self.available_subs_languages.append(subtitlesTrack.language)
            if subtitlesTrack.codec not in self.available_subs_codecs:
                self.available_subs_codecs.append(subtitlesTrack.codec)

        print("Available audio languages: " + str(self.available_audio_languages))
        print("Available audio codecs: " + str(self.available_audio_codecs))
        print("Available subtitles languages: " + str(self.available_subs_languages))
        print("Available subs codecs: " + str(self.available_subs_codecs))

    def updateTracksToRemove(self, trackCheckbox):
        match trackCheckbox.type:
            case TrackCheckbox.TYPE_AUDIO_LANGUAGE:
                if (trackCheckbox.isChecked()):
                    if (trackCheckbox.text() in self.audio_languages_to_remove):
                        self.audio_languages_to_remove.remove(trackCheckbox.text())
                else:
                    if (trackCheckbox.text() not in self.audio_languages_to_remove):
                        self.audio_languages_to_remove.append(trackCheckbox.text())
            case TrackCheckbox.TYPE_SUBS_LANGUAGE:
                if (trackCheckbox.isChecked()):
                    if (trackCheckbox.text() in self.subs_languages_to_remove):
                        self.subs_languages_to_remove.remove(trackCheckbox.text())
                else:
                    if (trackCheckbox.text() not in self.subs_languages_to_remove):
                        self.subs_languages_to_remove.append(trackCheckbox.text())
            case TrackCheckbox.TYPE_AUDIO_CODEC:
                if (trackCheckbox.isChecked()):
                    if (trackCheckbox.text() in self.audio_codecs_to_remove):
                        self.audio_codecs_to_remove.remove(trackCheckbox.text())
                else:
                    if (trackCheckbox.text() not in self.audio_codecs_to_remove):
                        self.audio_codecs_to_remove.append(trackCheckbox.text())
            case TrackCheckbox.TYPE_SUBS_CODEC:
                if (trackCheckbox.isChecked()):
                    if (trackCheckbox.text() in self.subs_codecs_to_remove):
                        self.subs_codecs_to_remove.remove(trackCheckbox.text())
                else:
                    if (trackCheckbox.text() not in self.subs_codecs_to_remove):
                        self.subs_codecs_to_remove.append(trackCheckbox.text())
        print("Tracks to be removed : ")
        print("---------------------")
        print("Audio languages : ", self.audio_languages_to_remove)
        print("Subs languages : ", self.subs_languages_to_remove)
        print("Audio codecs : ", self.audio_codecs_to_remove)
        print("Subs codecs : ", self.subs_codecs_to_remove)

    # TODO: move this to a dedicated thread
    def startTracksRemoval(self):
        for mkv in self.files_to_process:
            track_ids_to_remove = []

            audioTracks = mkv.getTracksByType(AUDIO_TYPE)
            subtitlesTracks = mkv.getTracksByType(SUBTITLES_TYPE)

            for audioTrack in audioTracks:
                if audioTrack.language in self.audio_languages_to_remove or audioTrack.codec in self.audio_codecs_to_remove:
                    print("Audio track" + audioTrack.language +  "(" + str(audioTrack.id) + ")" +"matches removal condition")
                    track_ids_to_remove.append(audioTrack.id)

            for subtitlesTrack in subtitlesTracks:
                if subtitlesTrack.language in self.subs_languages_to_remove or subtitlesTrack.codec in self.subs_codecs_to_remove:
                    print("Subs track" + subtitlesTrack.language +  "(" + str(subtitlesTrack.id) + ")" +"matches removal condition")
                    track_ids_to_remove.append(subtitlesTrack.id)

            print("MkvFile : ", mkv.filepath)
            for track_id_to_remove in track_ids_to_remove:
                mkv.removeTrack(track_id_to_remove)
            outputPath = self.getOutputPath(mkv)
            if (outputPath):
                mkv.mux(outputPath)
            print("Done")

    def getOutputPath(self, mkvFile):
        print("==========================")
        outputPath = ""
        outputFileSetting = self.settings.getIntParam(batchMkvToolboxSettings.OUTPUT_FILE_SETTING)
        match outputFileSetting:
            case batchMkvToolboxSettings.OUTPUT_FILE_IN_SAME_FOLDER_AS_ORIGINAL:
                parentFolder = Path(mkvFile.filepath).parent.absolute()
                filename = Path(mkvFile.filepath).stem + "-REMUX.mkv"
                outputPath = os.path.join(parentFolder, filename)
                print("The output file should be placed along side the original file: ", str(outputPath))
            case batchMkvToolboxSettings.OUTPUT_FILE_IN_REMUX_FOLDER:
                parentFolder = Path(mkvFile.filepath).parent.absolute()
                remuxFolder = os.path.join(parentFolder, "REMUX")
                filename = Path(mkvFile.filepath).name
                outputPath = os.path.join(remuxFolder, filename)
                print("The output file should be placed in REMUX folder along side the original file: ", str(outputPath))
            case batchMkvToolboxSettings.OUTPUT_FILE_IN_CUSTOM_FOLDER:
                customFolder = self.settings.getStrParam(batchMkvToolboxSettings.OUTPUT_FILE_CUSTOM_FOLDER_SETTING)
                folderStructurePreserveEnabled = self.settings.getBoolParam(batchMkvToolboxSettings.OUTPUT_FILE_PRESERVE_FOLDER_STRUCTURE_SETTING)
                filename = Path(mkvFile.filepath).name
                # For folder structure preservation, it should work only when opening a folder and use this folder as a base:
                # Example: C:\Users\Azsde\TvShows folder is openeded, every mkv file under this folder and subfolders will be scanned
                # So for a file located at C:\Users\Azsde\TvShows\MyTvShow\Season1\S01E01.mkv, structure preservation will mean that we should
                # isolate 'MyTvShow\Season1\' and append it to our custom folder so that the output path will be:
                # [CUSTOM_FOLDER]\MyTvShow\Season1\S01E01.mkv
                if (self.baseFolder and folderStructurePreserveEnabled):
                    intialMkvParentFolder = str(Path(mkvFile.filepath).parent.absolute())
                    newMkvParentFolder = intialMkvParentFolder.replace(str(self.baseFolder), customFolder)
                    outputPath = os.path.join(newMkvParentFolder, filename)
                else:
                    outputPath = os.path.join(customFolder, filename)
                print("The output file should be placed here: ", str(outputPath))
            case _:
                print("Insupported setting.")

        if os.path.exists(outputPath):
            print("Output file already exists, prompting the user...")
            outputPath = self.openExistingFileDialog(mkvFile, outputPath, outputFileSetting)
            print("Final output path : ", str(outputPath))
        print("==========================")
        return outputPath

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