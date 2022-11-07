import configparser

# Class to handle the settings
class batchMkvToolboxSettings():

    # Filename
    CONFIG_FILE = "config.cfg"
    # Expected configuration file version (to update when updating the settings)
    EXPECTED_CONFIG_FILE_VERSION = "1"

    # The section of the settings
    BATCH_MKV_TOOLBOX_CONFIG_SECTION = "BATCH_MKV_TOOLBOX"

    # Name of the setting holding the configuration version
    CONFIG_FILE_VERSION = "batch_mkv_toolbox_configfile_version"
    # Name of the setting holding the location of the mkvMerge binary
    MKV_MERGE_LOCATION_SETTING = "mkv_merge_location"
    # Name of the setting determining the strategy to adopt for input files
    INPUT_FILE_SETTING = "input_file_setting"
    # Name of the setting determining the strategy to adopt for output files
    OUTPUT_FILE_SETTING = "output_file_setting"
    # Name of the setting holding the location of the custom folder to store output files
    OUTPUT_FILE_CUSTOM_FOLDER_SETTING = "output_file_custom_folder_setting"
    # Name of the setting determining whether or not the folder structure should be preserved
    OUTPUT_FILE_PRESERVE_FOLDER_STRUCTURE_SETTING = "output_file_preserve_folder_structure_setting"

    # Setting value to leave the input file(s) in place after processing it
    INPUT_FILE_LEAVE_IN_PLACE = 0
    # Setting value to rename the input file(s) after processing it
    INPUT_FILE_RENAME = 1
    # Setting value to delete the input file(s) after processing it
    INPUT_FILE_DELETE = 2

    # Setting value to place the output file(s) alongside the original file(s)
    OUTPUT_FILE_IN_SAME_FOLDER_AS_ORIGINAL = 0
    # Setting value to place the output file(s) in a REMUX folder which itself is alongside the original file(s)
    OUTPUT_FILE_IN_REMUX_FOLDER = 1
    # Setting value to place the output file(s) in a custom folder
    OUTPUT_FILE_IN_CUSTOM_FOLDER = 2

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(batchMkvToolboxSettings.CONFIG_FILE)

        if self.config.has_section(batchMkvToolboxSettings.BATCH_MKV_TOOLBOX_CONFIG_SECTION):
            try:
                print("config found")
                print("Settings version: ", self.config[batchMkvToolboxSettings.BATCH_MKV_TOOLBOX_CONFIG_SECTION][batchMkvToolboxSettings.CONFIG_FILE_VERSION])
            except KeyError as e:
                print("Config was found but seems to be invalid : ", e)
                # TODO: warn the user that the config will be reset
                self.resetConfig()
        else:
            print("config not found")
            self.resetConfig()

    def resetConfig(self):
        print("Reset config")
        self.config.clear()
        self.config[batchMkvToolboxSettings.BATCH_MKV_TOOLBOX_CONFIG_SECTION] = {
            batchMkvToolboxSettings.CONFIG_FILE_VERSION : 1,
            batchMkvToolboxSettings.MKV_MERGE_LOCATION_SETTING : "", # Reset to empty value as it should be found automatically
            batchMkvToolboxSettings.INPUT_FILE_SETTING : batchMkvToolboxSettings.INPUT_FILE_LEAVE_IN_PLACE, # Reset to INPUT_FILE_LEAVE_IN_PLACE
            batchMkvToolboxSettings.OUTPUT_FILE_SETTING : batchMkvToolboxSettings.OUTPUT_FILE_IN_SAME_FOLDER_AS_ORIGINAL,
            batchMkvToolboxSettings.OUTPUT_FILE_CUSTOM_FOLDER_SETTING : "",
            batchMkvToolboxSettings.OUTPUT_FILE_PRESERVE_FOLDER_STRUCTURE_SETTING : False
        }

        with open(batchMkvToolboxSettings.CONFIG_FILE, 'w') as configfile:
            self.config.write(configfile)

    def getIntParam(self, key):
        return self.config.getint(batchMkvToolboxSettings.BATCH_MKV_TOOLBOX_CONFIG_SECTION, key)

    def getStrParam(self, key):
        return self.config.get(batchMkvToolboxSettings.BATCH_MKV_TOOLBOX_CONFIG_SECTION, key)

    def getBoolParam(self, key):
        return self.config.getboolean(batchMkvToolboxSettings.BATCH_MKV_TOOLBOX_CONFIG_SECTION, key)

    def setParam(self, key, value):
        self.config[batchMkvToolboxSettings.BATCH_MKV_TOOLBOX_CONFIG_SECTION][key] = str(value)
        with open(batchMkvToolboxSettings.CONFIG_FILE, 'w') as configfile:
            self.config.write(configfile)
