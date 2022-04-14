from pymkv import MKVFile

from PyQt5.QtCore import (QCoreApplication, QObject, QRunnable, QThread,
                          QThreadPool, pyqtSignal)

import glob
import os
import time


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
        self.available_audio_languages = []
        self.available_subs_languages = []
        self.audio_languages_to_keep = []
        self.subs_languages_to_keep = []

    def reset(self):
        self.available_audio_languages.clear()
        self.available_subs_languages.clear()
        self.audio_languages_to_keep.clear()
        self.subs_languages_to_keep.clear()

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
        tracks = mkv.get_track()
        for track in tracks:
            if (track.track_type == "audio"):
                if track.language not in self.available_audio_languages:
                    self.available_audio_languages.append(track.language)
            if (track.track_type == "subtitles"):
                if track.language not in self.available_subs_languages:
                    self.available_subs_languages.append(track.language)
        print("Available audio languages: " + str(self.available_audio_languages))
        print("Available subtitles languages: " + str(self.available_subs_languages))