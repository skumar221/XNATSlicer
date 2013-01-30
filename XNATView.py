from __main__ import vtk, ctk, qt, slicer
import datetime, time


import os
import sys
import shutil
import csv

from XNATFileInfo import *
from XNATUtils import *
from XNATInstallWizard import *
from XNATScenePackager import *
from XNATTimer import *
from XNATSettings import *
from XNATSessionManager import *
from XNATAddProjEditor import *

from XNATUtils import textStatusBar

#########################################################
#
# 
comment = """
  XNATView is the class that handles all of the UI interactions to the XNATCommunicator.

# TODO : 
"""
#
#########################################################

class XNATView(object):
    def __init__(self, parent=None, settings = None, browser = None):
        self.parent = parent
        self.utils = XNATUtils()   
        self.settings = settings
        self.browser = browser
        self.XNATCommunicator = None
        
        self.viewWidget = None
        
        self.loadButton = qt.QPushButton()
        self.loadButton.setFont(self.utils.labelFont)
        self.loadButton.setToolTip("Load file, image folder or scene from XNAT to Slicer.")
        self.loadButton.setIcon(qt.QIcon(os.path.join(self.utils.iconPath, 'load.jpg')) )
        self.loadButton.setFixedSize(self.utils.buttonSizeMed)
        self.loadButton.connect('clicked()', self.loadButtonClicked)
        self.loadButton.setEnabled(False)
        
        self.saveButton = qt.QPushButton()
        self.saveButton.setIcon(qt.QIcon(os.path.join(self.utils.iconPath, 'save.jpg')) )
        self.saveButton.setToolTip("Upload current scene to XNAT.")
        self.saveButton.setFont(self.utils.labelFont)
        self.saveButton.setFixedSize(self.utils.buttonSizeMed)
        self.saveButton.connect('clicked()', self.saveButtonClicked)
        self.saveButton.setEnabled(False) 
 
        self.deleteButton = qt.QPushButton()
        self.deleteButton.setIcon(qt.QIcon(os.path.join(self.utils.iconPath, 'delete.jpg')) )
        self.deleteButton.setToolTip("Delete XNAT File.")
        self.deleteButton.setFont(self.utils.labelFont)
        self.deleteButton.setFixedSize(self.utils.buttonSizeSmall)
        self.deleteButton.connect('clicked()', self.deleteButtonClicked)
        self.deleteButton.setEnabled(False) 
        
        self.addProjButton = qt.QPushButton()
        self.addProjButton.setIcon(qt.QIcon(os.path.join(self.utils.iconPath, 'addproj.jpg')) )
        self.addProjButton.setToolTip("Add Project, Subject, or Experiment to XNAT.")
        self.addProjButton.setFont(self.utils.labelFont)
        self.addProjButton.setFixedSize(self.utils.buttonSizeSmall)
        self.addProjButton.connect('clicked()', self.addProjClicked)
        self.addProjButton.setEnabled(False) 
        
        self.statusView = textStatusBar(overwriteMode = True, size = 7)
        
        self.sessionManager = XNATSessionManager(self.browser)
        
        self.addProjEditor = None
        
        if not self.parent == None:
            self.setup()
    
    def setup(self):
        pass
    
    def begin(self, XNATCommunicator):               
        self.XNATCommunicator = XNATCommunicator
        if not self.XNATCommunicator:
            raise ValueError, "No XNATCommunicator set for the current XNATView!"

    def setEnabled(self):
        pass
    
    def loadButtonClicked(self):
        pass   
    
    def saveButtonClicked(self):
        pass
    
    def navigateTo(self):
        pass

    def addProjClicked(self):
        self.addProjEditor = XNATAddProjEditor(self, self.browser, self.XNATCommunicator)
        self.addProjEditor.show()


        
    