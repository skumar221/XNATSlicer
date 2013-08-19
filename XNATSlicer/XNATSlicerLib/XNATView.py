from __main__ import vtk, ctk, qt, slicer

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



comment = """
  XNATView is the class that handles all of the UI interactions to the XNATCommunicator.

# TODO : 
"""



class XNATView(object):
    """ Descriptor
    """
    
    def __init__(self, parent=None, browser = None):
        """ Descriptor
        """
        self.parent = parent
        self.browser = browser
        self.sessionManager = XNATSessionManager(self.browser)
        
        self.setup()


        
        
    def loadProjects(self):
        """ Descriptor
        """
        pass


    
    
    def begin(self):
        """ Descriptor
        """
        if self.loadProjects():
            self.browser.XNATButtons.setEnabled(buttonKey='addProj', enabled=True) 
        else:
            qt.QMessageBox.warning( None, "Login error", "Invalid login credentials for '%s'."%(self.XNATCommunicator.server))


            
        
    def clear(self):
        """ Descriptor
        """
        self.viewWidget.clear()
