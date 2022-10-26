from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QFileDialog, QMessageBox

from os import path

from settings.batchMkvToolboxSettings import batchMkvToolboxSettings

import sys

# Dialog displayed to change the different settings
class PrefDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)

        self.settings = settings
        # Load the UI file
        uic.loadUi("ui/settings.ui", self)

        # Populate the settings from the saved one
        self.populateSettings()

        # Connect all radio buttons toggled signals
        self.leaveOriginalFileRadioButton.toggled.connect(lambda: self.onRadioButtonEnabled(self.leaveOriginalFileRadioButton))
        self.renameOriginalFileRadioButton.toggled.connect(lambda: self.onRadioButtonEnabled(self.renameOriginalFileRadioButton))
        self.deleteOriginalFileRadioButton.toggled.connect(lambda: self.onRadioButtonEnabled(self.deleteOriginalFileRadioButton))
        self.outputFileSameFolderRadioButton.toggled.connect(lambda: self.onRadioButtonEnabled(self.outputFileSameFolderRadioButton))
        self.outputFileRemuxFolderRadioButton.toggled.connect(lambda: self.onRadioButtonEnabled(self.outputFileRemuxFolderRadioButton))
        self.outputFileCustomFolderRadioButton.toggled.connect(lambda: self.onRadioButtonEnabled(self.outputFileCustomFolderRadioButton))

        # Connect signals for mkvMerge location
        self.browseMkvMergeButton.clicked.connect(lambda: self.browseForMkvMerge())

        # Connect signals for custom folder location
        self.browseCustomOutputFolderPushButton.clicked.connect(lambda: self.browseForCustomOutputFolder())

        # Connect signal for preserve folder structure checkbox
        self.preserveFolderStructureCheckBox.clicked.connect(lambda: self.onPreserveFolderStructureClicked())

        # Connect dialog OK / Cancel buttons
        self.accepted.connect(lambda: self.applyChanges())
        self.rejected.connect(lambda: self.pendingChanges.clear())

        # Align everything to the top of the layout
        self.settingsVerticalLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # List of changes to apply
        self.pendingChanges = {}

    # Open a file browser to navigate to the folder containing mkvmerge binary
    # (Usually under the MkvToolNix installation folder)
    def browseForMkvMerge(self):
        mkvMergeFolder = QFileDialog.getExistingDirectory(None,"Select a folder", self.mkvMergeLocationLineEdit.text())
        self.verifyMkvMergePath(mkvMergeFolder)

    # Verify the validity of the mkvmerge path
    def verifyMkvMergePath(self, mkvMergeFolder):
        if mkvMergeFolder:
            print("Searching mkvmerge in path: ", mkvMergeFolder)
            if sys.platform.startswith("win"):
                mkvMergePath = mkvMergeFolder + "/mkvmerge.exe"
            elif sys.platform.startswith("linux"):
                mkvMergePath = mkvMergeFolder + "/mkvmerge"
            if (path.exists(mkvMergePath)):
                print("MkvMerge found")
                self.mkvMergeLocationLineEdit.setText(mkvMergeFolder)
                self.pendingChanges[batchMkvToolboxSettings.MKV_MERGE_LOCATION_SETTING] = mkvMergeFolder
            else:
                print("MkvMerge not found")
                self.mkvMergeLocationLineEdit.clear()
                QMessageBox.critical(self, "Error", "mkvmerge was not found at the specified path.",
                    buttons=QMessageBox.StandardButton.Ok,
                    defaultButton=QMessageBox.StandardButton.Ok)

     # Open a file browser to navigate to the folder that will hold the output files
    def browseForCustomOutputFolder(self):
        print("browseForCustomOutputFolder")
        outputFolder = QFileDialog.getExistingDirectory(None,"Select a folder", self.customOutputFolderlineEdit.text())
        if outputFolder:
            self.customOutputFolderlineEdit.setText(outputFolder)
            self.pendingChanges[batchMkvToolboxSettings.OUTPUT_FILE_CUSTOM_FOLDER_SETTING] = outputFolder

    # Callback for all radio buttons related to files operation
    # In the settings.ui, dynamic properties were defined:
    #     - SETTING_KEY : the key of the setting associated to the radio button
    #     - SETTING_VALUE: the value of the setting associated to the radio button
    def onRadioButtonEnabled(self, radioBtn):
        if (radioBtn.isChecked()):
            self.pendingChanges[radioBtn.property("SETTING_KEY")] = radioBtn.property("SETTING_VALUE")

            # Specific case to enable custom output folder fields
            if (radioBtn.property("SETTING_KEY") == batchMkvToolboxSettings.OUTPUT_FILE_SETTING):
                if (radioBtn.property("SETTING_VALUE") == batchMkvToolboxSettings.OUTPUT_FILE_IN_CUSTOM_FOLDER):
                    self.customOutputFolderlineEdit.setEnabled(True)
                    self.browseCustomOutputFolderPushButton.setEnabled(True)
                    self.preserveFolderStructureCheckBox.setEnabled(True)
                else:
                    self.customOutputFolderlineEdit.setEnabled(False)
                    self.browseCustomOutputFolderPushButton.setEnabled(False)
                    self.preserveFolderStructureCheckBox.setEnabled(False)

    # Callback when the "preserve folder structure" checkbox has been clicked
    def onPreserveFolderStructureClicked(self):
        self.pendingChanges[batchMkvToolboxSettings.OUTPUT_FILE_PRESERVE_FOLDER_STRUCTURE_SETTING] = self.preserveFolderStructureCheckBox.isChecked()

    # Apply all pending changes
    def applyChanges(self):
        for key, value in self.pendingChanges.items():
            print("Updating setting " + key + " to " + str(value))
            self.settings.setParam(key, value)
        self.pendingChanges.clear()

    # Populate the settings with the saved values
    def populateSettings(self):
        # MkvMerge location
        self.mkvMergeLocationLineEdit.setText(self.settings.getStrParam(batchMkvToolboxSettings.MKV_MERGE_LOCATION_SETTING))

        # Input file strategy
        inputFileSettingValue = self.settings.getIntParam(batchMkvToolboxSettings.INPUT_FILE_SETTING)
        match inputFileSettingValue:
            case batchMkvToolboxSettings.INPUT_FILE_LEAVE_IN_PLACE:
                self.leaveOriginalFileRadioButton.setChecked(True)
            case batchMkvToolboxSettings.INPUT_FILE_RENAME:
                self.renameOriginalFileRadioButton.setChecked(True)
            case batchMkvToolboxSettings.INPUT_FILE_DELETE:
                self.deleteOriginalFileRadioButton.setChecked(True)
            case _:
                #TODO: throw an error
                pass

        # Output file strategy
        outputFileSettingValue = self.settings.getIntParam(batchMkvToolboxSettings.OUTPUT_FILE_SETTING)
        match outputFileSettingValue:
            case batchMkvToolboxSettings.OUTPUT_FILE_IN_SAME_FOLDER_AS_ORIGINAL:
                self.outputFileSameFolderRadioButton.setChecked(True)
            case batchMkvToolboxSettings.OUTPUT_FILE_IN_REMUX_FOLDER:
                self.outputFileRemuxFolderRadioButton.setChecked(True)
                self.preserveFolderStructureCheckBox.setEnabled(True)
            case batchMkvToolboxSettings.OUTPUT_FILE_IN_CUSTOM_FOLDER:
                self.outputFileCustomFolderRadioButton.setChecked(True)
                self.customOutputFolderlineEdit.setEnabled(True)
                self.browseCustomOutputFolderPushButton.setEnabled(True)
                self.preserveFolderStructureCheckBox.setEnabled(True)
            case _:
                #TODO: throw an error
                pass
        self.customOutputFolderlineEdit.setText(self.settings.getStrParam(batchMkvToolboxSettings.OUTPUT_FILE_CUSTOM_FOLDER_SETTING))
        self.preserveFolderStructureCheckBox.setChecked(self.settings.getBoolParam(batchMkvToolboxSettings.OUTPUT_FILE_PRESERVE_FOLDER_STRUCTURE_SETTING))
