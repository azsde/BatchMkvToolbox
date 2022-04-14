#!/usr/bin/env python3

import glob
from mimetypes import init
from operator import le, truediv
import os
import sys
import threading

from tkinter import *
from tkinter import filedialog
from tkinter import ttk

from tkinter.scrolledtext import ScrolledText
from turtle import width

from pymkv import MKVFile
from pymkv import MKVTrack

from Toto import ChecklistBox

global available_audio_languages
global available_subs_languages

global audio_languages_to_keep
global subs_languages_to_keep

available_audio_languages = []
available_subs_languages = []
audio_languages_to_keep = []
subs_languages_to_keep = []

# Reset detected languages
def clear_languages():
    available_audio_languages.clear()
    available_subs_languages.clear()
    audio_languages_to_keep.clear()
    subs_languages_to_keep.clear()

# Define the source folder in which we are going to look for the MKVs
def set_source_folder():
    clear_languages()
    global source_folder
    source_folder = filedialog.askdirectory()
    if(source_folder):
        display_loading_bar()    
        t = threading.Thread(target=scan_available_languages)
        t.start()

# Define the source file
def set_source_file():
    clear_languages()
    global source_file 
    source_file = filedialog.askopenfilename(filetypes=[("Mkv files", ".mkv")])
    if(source_file):
        display_loading_bar()
        t = threading.Thread(target=scan_available_languages)
        t.start()

# Scan for every available languages
def scan_available_languages():
    try:
        source_folder
    except NameError:
        try:
            source_file
        except NameError:
            print("No source file or folder selected")
            return
        else:
            scanFileLanguages(source_file)
    else:
        os.chdir(source_folder)
        for file in glob.glob("*.mkv"):
            scanFileLanguages(file)
    populate_ui()
            

def scanFileLanguages(file):
    print("Processing: " + file)
    mkv = MKVFile(file)
    tracks = mkv.get_track()
    for track in tracks:
        if (track.track_type == "audio"):
            if track.language not in available_audio_languages:
                available_audio_languages.append(track.language)
        if (track.track_type == "subtitles"):
            if track.language not in available_subs_languages:
                available_subs_languages.append(track.language)
    print("Available audio languages: " + str(available_audio_languages))
    print("Available subtitles languages: " + str(available_subs_languages))

    #if (len(audio_language_to_remove) > 0 and track.track_type == "audio" and track.language in audio_language_to_remove):
                #    print("Removing audio track: " + track.language)
                #    #mkv.remove_track(track.track_number)
                #if (track.language in audio_language_to_remove):
                #    print("Track #", track.track_id, " - Name : ", track.track_name, " (", track.track_type, "), Language: ", track.language)
                ##if track.track_type == "subtitles":
                ##    print()
                ##    remove_track = True
    
def display_loading_bar():
    # Remove the label to inviting to open a file/folder
    openFileOrFolderLabel.grid_forget()

    # Attach the loading frame to the grid
    loadingFrame.grid(row=0, column=0, sticky='NESW')

    scanningLabel=Label(loadingFrame, text="Scanning available tracks...")
    progressBar = ttk.Progressbar(loadingFrame, orient='horizontal', mode='indeterminate')
    
    scanningLabel.grid(row=0, column=1, rowspan=1, columnspan=3, sticky="sew")
    progressBar.grid(row=1, column=1, rowspan=1, columnspan=3, sticky="new")

    progressBar.start()

def populate_ui():

    # Hide the loading items
    loadingFrame.grid_forget()

    # Tabs widget
    global notebook
    notebook = ttk.Notebook(mainWindow)
    notebook.grid(row=0, column=0, sticky='NESW')

    # Frames
    tracksRemoverFrame = Frame(notebook, background="orange", padx=5, pady=5)
    miscUtilsFrame = Frame(notebook, background="red", padx=5, pady=5)
    notebook.add(tracksRemoverFrame, text="Tracks removal")
    notebook.add(miscUtilsFrame, text="Misc.")

    rows = 0
    while rows < 50:
        tracksRemoverFrame.rowconfigure(rows, weight=1)
        tracksRemoverFrame.columnconfigure(rows, weight=1)
        rows += 1

    avalaibleAudioTracksLabel=Label(tracksRemoverFrame, text="Audio tracks: ")
    avalaibleAudioTracksLabel.grid(row=0, column=0, sticky="w")

    choices = ("Author", "John", "Mohan", "James", "Ankur", "Robert","Author", "John", "Mohan", "James", "Ankur", "Robert","Author", "John", "Mohan", "James", "Ankur", "Robert")
    checklist = ChecklistBox.ChecklistBox(tracksRemoverFrame, choices, bd=1, relief="sunken", background="white")
    checklist.grid(row=0, column=1, rowspan=1, sticky="w")


def init_ui():
    global mainWindow
    mainWindow = Tk()

    # Main Windows property
    mainWindow.title("MKV Batch Remover")
    mainWindow.geometry('800x600')
    mainWindow.columnconfigure(0, weight=1)
    mainWindow.rowconfigure(0, weight=1)

    # Menu Bar
    menubar = Menu(mainWindow)
    menu1 = Menu(menubar, tearoff=0)
    menu1.add_command(label="Select file", command=lambda: set_source_file())
    menu1.add_command(label="Select folder", command=lambda: set_source_folder())
    menu1.add_command(label="Close")
    menu1.add_separator()
    menu1.add_command(label="Quit", command=mainWindow.quit)
    menubar.add_cascade(label="File", menu=menu1)
    mainWindow.config(menu=menubar)

    global openFileOrFolderLabel
    openFileOrFolderLabel=Label(mainWindow, text="Select source file or folder")
    openFileOrFolderLabel.grid(row=0, column=0, sticky='NESW')

    global loadingFrame
    loadingFrame = Frame(mainWindow, background="green", padx=5, pady=5)

    # I didn't find a simpler way to align widgets into the frame...
    loadingFrame.rowconfigure(0, weight=1)
    loadingFrame.rowconfigure(1, weight=1)
    loadingFrame.columnconfigure(0, weight=1)
    loadingFrame.columnconfigure(1, weight=1)
    loadingFrame.columnconfigure(2, weight=1)
    loadingFrame.columnconfigure(3, weight=1)
    loadingFrame.columnconfigure(4, weight=1)   

    # Set the initial size as the min size so that UI won't be sized down
    mainWindow.update()
    mainWindow.minsize(mainWindow.winfo_width(), mainWindow.winfo_height())

    mainWindow.mainloop()

init_ui()



#try:
#    folder=sys.argv[1]
#except:
#    print('Please pass directory_name')
#    exit()
#
#audio_language_to_remove = input("Which audio language do you which to remove ? (ex: eng, spa, etc...) : ").split(",")
#print(audio_language_to_remove)
#
#subtitles_language_to_remove = input("Which subtitles language do you which to remove ? (ex: eng, spa, etc...) : ").split(",")
#print(subtitles_language_to_remove)
#
#
#
#
#os.chdir(folder)
#for file in glob.glob("*.mkv"):
#    print("Processing: " + file)
#    mkv = MKVFile(file)
#    tracks = mkv.get_track()
#    for track in tracks:
#        if (len(audio_language_to_remove) > 0 and track.track_type == "audio" and track.language in audio_language_to_remove):
#            print("Removing audio track: " + track.language)
#            #mkv.remove_track(track.track_number)
#
#        if (track.language in audio_language_to_remove):
#            print("Track #", track.track_id, " - Name : ", track.track_name, " (", track.track_type, "), Language: ", track.language)
#        #if track.track_type == "subtitles":
#        #    print()
#        #    remove_track = True