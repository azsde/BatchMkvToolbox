import orjson
import subprocess
import re

from pathlib import Path

from .mkvMergeJsonConstants import *

class mkvFile():
    """Class representing an MKV file.
    """

    def __init__(self, filepath, mkvMerge):
        """Init method of the mkvFile class

        Args:
            filepath (str): the filepath of the mkv file.
            mkvMerge (str): the path to the mkvMerge binary file.
        """
        self.filepath = filepath
        self.outputPath = None
        self.mkvMerge = mkvMerge
        self.rawData = self.getRawJsonData()
        self.jsonData = orjson.loads(self.rawData)
        self.audioTracksToRemove = []
        self.subtitlesTracksToRemove = []
        #TODO: Check if mkv file is valid and send a signal if it is not the case

    def getRawJsonData(self):
        """Get the raw json output result after calling mkvmerge -J [inputfile]

        Returns:
            str: the raw json string returned by mkvmerge -J
        """
        return subprocess.check_output([self.mkvMerge, '-J', self.filepath])

    def getTracksByType(self, type):
        """Returns a list of tracks of the specified type, see constants defined in mkvMergeJsonConstants.py

        Args:
            type (str): the string value of the type of track to be retrieved.

        Returns:
            :class: ~mkvFile.myMkvTrack []: the list of tracks matching the specified type.
        """
        tracks = []
        try:
            for jsonTrackData in self.jsonData[TRACKS_TAG]:
                if (jsonTrackData[TYPE_TAG] == type):
                    tracks.append(myMkvTrack(jsonTrackData))
        except KeyError as e:
            print("Cannot get track by type, ", e)

        return tracks

    def getTrackType(self, trackId):
        """Returns the type of a specified track.

        Args:
            trackId (int): the id of the track of which we want to retrieve the type of.

        Returns:
            str: the type of the track as string, will returned "Undefined" in case the information is not found.
        """
        if (self.isTrackIdValid(trackId)):
            for jsonTrackData in self.jsonData[TRACKS_TAG]:
                if (trackId == jsonTrackData[ID_TAG]):
                    return jsonTrackData[TYPE_TAG]
        return "Undefined"

    def isTrackIdValid(self, trackId):
        """Check whether or not a track is valid based on its ID.

        Args:
            trackId (int): the id of the track we want to check

        Returns:
            bool: true if the track id is valid, false otherwise.
        """
        for jsonTrackData in self.jsonData[TRACKS_TAG]:
            if (trackId == jsonTrackData[ID_TAG]):
                return True
        return False

    def removeTrack(self, trackId):
        """Remove a track from the mkvFile.

        Note that this will not have any effect until mux() is called.

        Args:
            trackId (int): the id of the track to remove.
        """
        if (self.isTrackIdValid(trackId)):
            if (self.getTrackType(trackId) == AUDIO_TYPE):
                print("Marking audio track " + str(trackId) + " for removal. ")
                self.audioTracksToRemove.append(trackId)
            elif (self.getTrackType(trackId) == SUBTITLES_TYPE):
                print("Marking subtitles track " + str(trackId) + " for removal. ")
                self.subtitlesTracksToRemove.append(trackId)
            else:
                print("Cannot remove track, unsupported track type : ", self.getTrackType(trackId))
        else:
            print("Cannot remove track, invalid track id: ", str(trackId))

    def prepareMkvMergeCmd(self, outputPath):
        """Prepare the mkvMerge command than will be ran to remux the mkvFile.

        Args:
            outputPath (str): The complete output path where to store the muxed mkv file.

        Returns:
            str[]: An array of string forming the full mkvmerge command.
        """
        mkvMergeAudioArg = ""
        mkvMergeSubtitlesArg = ""

        # MKV Merge command is weird in case of track removal here's the format:
        # mkvmerge -o /output/path -s !subId1,subId2...subIdx -a !audioId1, audioId2...audioIdX /path/to/inputfile
        mkvMergeCommand = [self.mkvMerge, '--ui-language', 'en','-o', outputPath]

        # Create parent folder if needed
        Path(Path(outputPath).parent.absolute()).mkdir(parents=True, exist_ok=True)

        if (self.audioTracksToRemove):
            print("Audio tracks to be removed : ", self.audioTracksToRemove)
            for index, trackId in enumerate(self.audioTracksToRemove):
                if index != len(self.audioTracksToRemove) - 1:
                    mkvMergeAudioArg += str(trackId)
                    mkvMergeAudioArg += ","
                else:
                    mkvMergeAudioArg += str(trackId)
            mkvMergeAudioArg = "!" + mkvMergeAudioArg
            mkvMergeCommand.append("-a")
            mkvMergeCommand.append(mkvMergeAudioArg)

        if (self.subtitlesTracksToRemove):
            print("Subtitles tracks to be removed : ", self.subtitlesTracksToRemove)

            for index, trackId in enumerate(self.subtitlesTracksToRemove):
                if index != len(self.subtitlesTracksToRemove) - 1:
                    mkvMergeSubtitlesArg += str(trackId)
                    mkvMergeSubtitlesArg += ","
                else:
                    mkvMergeSubtitlesArg += str(trackId)
            mkvMergeSubtitlesArg = "!" + mkvMergeSubtitlesArg
            mkvMergeCommand.append("-s")
            mkvMergeCommand.append(mkvMergeSubtitlesArg)

        mkvMergeCommand.append(self.filepath)
        return mkvMergeCommand

    def mux(self, outputPath, update_progress_bar_callback):
        """Muxes the file to the given output path, removing marked tracks in the process.
        Args:
            outputPath (str): The complete output path where to store the muxed mkv file.
        """
        if (not self.audioTracksToRemove and not self.subtitlesTracksToRemove):
            return

        mkvMergeCommand = self.prepareMkvMergeCmd(outputPath)
        print("MkvMerge cmd: ", mkvMergeCommand)

        # Call mkvMerge
        process = subprocess.Popen(mkvMergeCommand, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in iter(process.stdout.readline, ''):
            print(line.strip())  # For debugging purposes
            progress = self.extract_progress(line)
            if progress is not None:
                update_progress_bar_callback.emit((self, progress))
        process.stdout.close()
        muxing_status_code = process.wait()

        print(f"Process exited with status code: {muxing_status_code}")

        self.audioTracksToRemove.clear()
        self.subtitlesTracksToRemove.clear()

        return (self, muxing_status_code)

    def extract_progress(self, output):
        match = re.search(r'Progress:\s*(\d+)%', output)
        if match:
            return int(match.group(1))
        return None

class myMkvTrack():
    """Class representing a track from a mkvFile
    """

    def __init__(self, jsonTrackData):
        """Init

        Args:
            jsonTrackData (dict): the json data of the track
        """
        self.id = jsonTrackData[ID_TAG]
        if (TRACK_NAME_TAG in jsonTrackData[PROPERTIES_TAG]):
            self.name = jsonTrackData[PROPERTIES_TAG][TRACK_NAME_TAG]
        else:
            self.name = ""
        self.type = jsonTrackData[TYPE_TAG]
        self.language = jsonTrackData[PROPERTIES_TAG][LANGUAGE_TAG]
        self.codec =  jsonTrackData[CODEC_TAG]
        self.forced = jsonTrackData[PROPERTIES_TAG][FORCED_TRACK_TAG]

    def toString(self):
        outputString = "Track #" + str(self.id) + ":" + \
         ("\n") + "    Name : " + self.name + \
         ("\n") + "    Type : " + self.type + \
         ("\n") + "    Forced : " + str(self.forced) + \
         ("\n") + "    Language : " + self.language + \
         ("\n") + "    Codec : " + self.codec
        return outputString