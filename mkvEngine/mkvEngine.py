from pymkv import MKVFile

from PyQt6.QtCore import (QCoreApplication, QObject, QRunnable, QThread,
                          QThreadPool, pyqtSignal)

import glob
import os
import time

from ui.TrackCheckbox import TrackCheckbox

class mkvEngine(QObject):

    scanFinished = pyqtSignal()

    class mkvEngineWorker(QObject):

        finished = pyqtSignal()

        def __init__(self, outer_instance, path):
            super().__init__()
            self.outer_instance = outer_instance
            self.path = path

        def startScanTracks(self):
            # If this is a folder, scan every file in it (not recursive for now)
            if os.path.isdir(self.path):
                os.chdir(self.path)
                for file in glob.glob("*.mkv"):
                 self.outer_instance.scanAvailableLanguages(file)
            elif os.path.isfile(self.path):
                self.outer_instance.scanAvailableLanguages(self.path)
            else:
                print("Not a file or folder")
                return
            count = 0
            self.finished.emit()

    def __init__(self):
        super().__init__()
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
        mkv = MKVFile(file_path)
        self.files_to_process.append(mkv)
        tracks = mkv.get_track()
        for track in tracks:
            if (track.track_type == "audio"):
                if track.language not in self.available_audio_languages:
                    self.available_audio_languages.append(track.language)
                if track.track_codec not in self.available_audio_codecs:
                    self.available_audio_codecs.append(track.track_codec)
            if (track.track_type == "subtitles"):
                if track.language not in self.available_subs_languages:
                    self.available_subs_languages.append(track.language)
                if track.track_codec not in self.available_subs_codecs:
                    self.available_subs_codecs.append(track.track_codec)
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
            tracks = mkv.get_track()
            for track in tracks:
                if (track.track_type == "audio"):
                    if track.language in self.audio_languages_to_remove or track.track_codec in self.audio_codecs_to_remove:
                        print("Audio track" + track.language +  "(" + track.track_id + ")" +"matches removal condition")
                        track_ids_to_remove.append(track.track_id)
                if (track.track_type == "subtitles"):
                    if track.language in self.subs_languages_to_remove or track.track_codec in self.subs_codecs_to_remove:
                        print("Subs track" + track.language +  "(" + track.track_id + ")" +"matches removal condition")
                        track_ids_to_remove.append(track.track_id)
            print("MkvFile : ", mkv.file_path)