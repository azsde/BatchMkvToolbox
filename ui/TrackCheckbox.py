from PyQt5.QtWidgets import QCheckBox

class TrackCheckbox(QCheckBox):
    def setType(self, type):
        self.type = type