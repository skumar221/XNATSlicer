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

    
    def __init__(self, parent=None, browser = None):
        self.parent = parent
         

        self.browser = browser

        self.viewWidget = None
        
        self.statusView = textStatusBar(overwriteMode = True, size = 7)
        self.sessionManager = XNATSessionManager(self.browser)
        self.setup()

        
    def loadProjects(self):
        pass


    
    def begin(self):
        if self.loadProjects():
            self.browser.XNATButtons.setEnabled(buttonKey='addProj', enabled=True) 
        else:
            qt.QMessageBox.warning( None, "Login error", "Invalid login credentials for '%s'."%(self.XNATCommunicator.server))

        
    
