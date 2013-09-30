from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil
import csv


from XnatTimer import *
from XnatSessionManager import *




comment = """
  XnatView is the class that handles all of the UI interactions to the XnatCommunicator.

# TODO : 
"""



class XnatView(object):
    """ Descriptor
    """
    
    def __init__(self, parent=None, browser = None):
        """ Descriptor
        """
        self.parent = parent
        self.browser = browser
        self.sessionManager = XnatSessionManager(self.browser)
        
        self.setup()


        
        
    def loadProjects(self):
        """ Descriptor
        """
        pass


    
    
    def begin(self):
        """ Descriptor
        """
        projectsLoaded = self.loadProjects()
        if projectsLoaded:
            self.browser.XnatButtons.setEnabled(buttonKey='addProj', enabled=True) 
        else:
            qt.QMessageBox.warning( None, "Login error", "Invalid login credentials for '%s'."%(self.browser.XnatCommunicator.server))


            
        
    def clear(self):
        """ Descriptor
        """
        self.viewWidget.clear()
