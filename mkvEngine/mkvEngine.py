import os
import traceback, sys
import time


from pathlib import Path
from PyQt6.QtCore import (QObject, QThread, QRunnable, pyqtSignal, pyqtSlot, QThreadPool)
from mkvEngine.mkvFile import mkvFile
from ui.myWidgets import TrackCheckbox



from mkvEngine.mkvMergeJsonConstants import *
from settings.batchMkvToolboxSettings import *


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(tuple)
    progress = pyqtSignal(tuple)

class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['remux_progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done

class mkvEngine(QObject):

    scanFinished = pyqtSignal()
    fileRemuxProgress = pyqtSignal(tuple)
    fileRemuxFinished = pyqtSignal(tuple)
    allFilesProcessed = pyqtSignal()
    outputFileAlreadyExist = pyqtSignal(tuple)

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

    class tracksCollection(QObject):
        def __init__(self, remove_forced_tracks=False):
            self.audio_languages = []
            self.subs_languages = []
            self.audio_codecs = []
            self.subs_codecs = []
            self.remove_forced_tracks = remove_forced_tracks

        def reset(self):
            self.audio_languages.clear()
            self.subs_languages.clear()
            self.audio_codecs.clear()
            self.subs_codecs.clear()
            self.remove_forced_tracks = False

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.mkvMergePath = settings.getStrParam(batchMkvToolboxSettings.MKV_MERGE_LOCATION_SETTING)
        # Base folder for folder processing
        self.baseFolder = ""
        # List of files to be processed
        self.files_to_process = []
        # List of all available audio languages
        self.available_languages_and_codecs = mkvEngine.tracksCollection()
        # List of tracks to be removed
        self.tracks_to_remove = mkvEngine.tracksCollection(settings.getBoolParam(batchMkvToolboxSettings.REMOVE_FORCED_TRACKS_SETTING))
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(4)

    def reset(self):
        self.files_to_process.clear()
        self.available_languages_and_codecs.reset()
        self.tracks_to_remove.reset()

    def startScan(self, path):
        # 1 - Create a QThread
        self.scannerThread = QThread()
        # 2 - Create a Worker
        self.trackScanWorker = mkvEngine.mkvEngineWorker(self, path)
        # 3 - Move the Worker to the QThread
        self.trackScanWorker.moveToThread(self.scannerThread)
        # 4 - Connect the signals
        self.scannerThread.started.connect(self.trackScanWorker.startScanTracks)
        self.scannerThread.finished.connect(self.scanFinished.emit)

        # Thread / worker proper "shutdown"
        self.trackScanWorker.finished.connect(self.scannerThread.quit)
        self.trackScanWorker.finished.connect(self.trackScanWorker.deleteLater)
        self.scannerThread.finished.connect(self.scannerThread.deleteLater)

        # 5 - Start the QThread
        self.scannerThread.start()

    def scanAvailableLanguages(self, file_path):
        print("Processing: " + file_path)
        mkv = mkvFile(file_path, self.mkvMergePath)

        self.files_to_process.append(mkv)
        for audioTrack in mkv.getTracksByType(AUDIO_TYPE):
            if audioTrack.language not in self.available_languages_and_codecs.audio_languages:
               self.available_languages_and_codecs.audio_languages.append(audioTrack.language)
            if audioTrack.codec not in self.available_languages_and_codecs.audio_codecs:
                self.available_languages_and_codecs.audio_codecs.append(audioTrack.codec)
        for subtitlesTrack in mkv.getTracksByType(SUBTITLES_TYPE):
            if subtitlesTrack.language not in self.available_languages_and_codecs.subs_languages:
                self.available_languages_and_codecs.subs_languages.append(subtitlesTrack.language)
            if subtitlesTrack.codec not in self.available_languages_and_codecs.subs_codecs:
                self.available_languages_and_codecs.subs_codecs.append(subtitlesTrack.codec)

        print("Available audio languages: " + str(self.available_languages_and_codecs.audio_languages))
        print("Available audio codecs: " + str(self.available_languages_and_codecs.audio_codecs))
        print("Available subtitles languages: " + str(self.available_languages_and_codecs.subs_languages))
        print("Available subs codecs: " + str(self.available_languages_and_codecs.subs_codecs))

    def updateTracksToRemove(self, trackCheckbox):
        match trackCheckbox.type:
            case TrackCheckbox.TYPE_AUDIO_LANGUAGE:
                if (trackCheckbox.isChecked()):
                    if (trackCheckbox.text() in self.tracks_to_remove.audio_languages):
                        self.tracks_to_remove.audio_languages.remove(trackCheckbox.text())
                else:
                    if (trackCheckbox.text() not in self.tracks_to_remove.audio_languages):
                        self.tracks_to_remove.audio_languages.append(trackCheckbox.text())
            case TrackCheckbox.TYPE_SUBS_LANGUAGE:
                if (trackCheckbox.isChecked()):
                    if (trackCheckbox.text() in self.tracks_to_remove.subs_languages):
                        self.tracks_to_remove.subs_languages.remove(trackCheckbox.text())
                else:
                    if (trackCheckbox.text() not in self.tracks_to_remove.subs_languages):
                        self.tracks_to_remove.subs_languages.append(trackCheckbox.text())
            case TrackCheckbox.TYPE_AUDIO_CODEC:
                if (trackCheckbox.isChecked()):
                    if (trackCheckbox.text() in self.tracks_to_remove.audio_codecs):
                        self.tracks_to_remove.audio_codecs.remove(trackCheckbox.text())
                else:
                    if (trackCheckbox.text() not in self.tracks_to_remove.audio_codecs):
                        self.tracks_to_remove.audio_codecs.append(trackCheckbox.text())
            case TrackCheckbox.TYPE_SUBS_CODEC:
                if (trackCheckbox.isChecked()):
                    if (trackCheckbox.text() in self.tracks_to_remove.subs_codecs):
                        self.tracks_to_remove.subs_codecs.remove(trackCheckbox.text())
                else:
                    if (trackCheckbox.text() not in self.tracks_to_remove.subs_codecs):
                        self.tracks_to_remove.subs_codecs.append(trackCheckbox.text())
        print("Tracks to be removed : ")
        print("---------------------")
        print("Audio languages : ", self.tracks_to_remove.audio_languages)
        print("Subs languages : ", self.tracks_to_remove.subs_languages)
        print("Audio codecs : ", self.tracks_to_remove.audio_codecs)
        print("Subs codecs : ", self.tracks_to_remove.subs_codecs)

    def setForcedTrackRemoval(self, remove_forced_tracks):
        print(f"setForcedTrackRemoval : {remove_forced_tracks}")
        self.tracks_to_remove.remove_forced_tracks = remove_forced_tracks

    def startTracksRemoval(self):
        for mkv in self.files_to_process:
            worker = Worker(self.perform_remux, mkv=mkv, remux_progress_callback=self.remux_progress_callback ) # Any other args, kwargs are passed to the run function
            worker.signals.result.connect(self.on_muxing_results)
            worker.signals.finished.connect(self.thread_complete)
            worker.signals.progress.connect(self.remux_progress_callback)
            self.threadpool.start(worker)

    def resolve_output_conflict(self, mkv, output_path):
        worker = Worker(self.perform_remux, mkv=mkv, forced_output_path=output_path, remux_progress_callback=self.remux_progress_callback ) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.on_muxing_results)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.remux_progress_callback)
        self.threadpool.start(worker)

    def perform_remux(self, mkv, remux_progress_callback, forced_output_path=""):
        print(f"Working on : {mkv.filepath}")

        track_ids_to_remove = []

        audioTracks = mkv.getTracksByType(AUDIO_TYPE)
        subtitlesTracks = mkv.getTracksByType(SUBTITLES_TYPE)

        for audioTrack in audioTracks:
            if audioTrack.language in self.tracks_to_remove.audio_languages:
                print(f"Audio track {audioTrack.language} ({audioTrack.id}) matches removal condition: language {audioTrack.language}")
                track_ids_to_remove.append(audioTrack.id)
            elif audioTrack.codec in self.tracks_to_remove.audio_codecs:
                print(f"Audio track {audioTrack.language} ({audioTrack.id}) matches removal condition: codec {audioTrack.codec}")
                track_ids_to_remove.append(audioTrack.id)

        for subtitlesTrack in subtitlesTracks:
            if subtitlesTrack.language in self.tracks_to_remove.subs_languages:
                print(f"Subs track {subtitlesTrack.language} ({subtitlesTrack.id}) matches removal condition: language {subtitlesTrack.language}")
                track_ids_to_remove.append(subtitlesTrack.id)
            elif subtitlesTrack.codec in self.tracks_to_remove.subs_codecs:
                print(f"Subs track {subtitlesTrack.language} ({subtitlesTrack.id}) matches removal condition: codec {subtitlesTrack.codec}")
                track_ids_to_remove.append(subtitlesTrack.id)
            elif self.tracks_to_remove.remove_forced_tracks and subtitlesTrack.forced:
                print(f"Subs track {subtitlesTrack.language} ({subtitlesTrack.id}) matches removal condition: forced track")
                track_ids_to_remove.append(subtitlesTrack.id)
#
#
        print("MkvFile : ", mkv.filepath)
        for track_id_to_remove in track_ids_to_remove:
            mkv.removeTrack(track_id_to_remove)

        if forced_output_path:
            outputPath = forced_output_path
        else:
            outputPath = self.getOutputPath(mkv)

        if (outputPath):
            return mkv.mux(outputPath, remux_progress_callback)
        else:
            print("Couldn't get output path, skipping for now.")
            return((None, None))

        #for n in range(0, 5):
        #    time.sleep(1)
        #    remux_progress_callback.emit((mkv, n))

    def on_muxing_results(self, result):
        print(f"Muxing ended with {result}")
        self.fileRemuxFinished.emit(result)

    def thread_complete(self):
        # Get the number of active threads
        if self.threadpool.activeThreadCount() == 0:
            self.allFilesProcessed.emit()


    def remux_progress_callback(self, tuple):
        self.fileRemuxProgress.emit(tuple)

    def getOutputPath(self, mkvFile):
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
            self.outputFileAlreadyExist.emit((mkvFile, outputPath))
            return None
            #outputPath = self.openExistingFileDialog(mkvFile, outputPath, outputFileSetting)
            #print("Final output path : ", str(outputPath))
        return outputPath

