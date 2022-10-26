from PyQt6.QtWidgets import QCheckBox

class TrackCheckbox(QCheckBox):

    TYPE_AUDIO_LANGUAGE = "audioLanguage"
    TYPE_SUBS_LANGUAGE = "subsLanguage"
    TYPE_AUDIO_CODEC = "audioCodec"
    TYPE_SUBS_CODEC = "subsCodec"

    def setType(self, type):
        self.type = type