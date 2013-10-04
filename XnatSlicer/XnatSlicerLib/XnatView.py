from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil
import csv

from XnatTimer import *
from XnatSessionManager import *



comment = """
XnatView is the class that handles all of the UI interactions 
to the XnatCommunicator.  It is meant to serve as a parent
class to various XnatView schemes such as XnatTreeView.

TODO:  Consider sending more functions from XnatTreeView
       here. 
"""



class XnatView(object):

    def __init__(self, parent = None, browser = None):
        """ Sets parent and browser parameters.
        """
        self.parent = parent
        self.browser = browser
        self.sessionManager = XnatSessionManager(self.browser)
        self.setup()


        
        
    def loadProjects(self):
        """ To be inherited by child class.
        """
        pass


    
    
    def begin(self):
        """ Begins the communication process with.  Shows
            an error modal if it fails.
        """
        projectsLoaded = self.loadProjects()
        if projectsLoaded:
            self.browser.XnatButtons.setEnabled(buttonKey='addProj', enabled=True) 
        else:
            qt.QMessageBox.warning( None, "Login error", "Invalid login credentials for '%s'."%(self.browser.XnatCommunicator.server))


            
        
    def clear(self):
        """ As stated.
        """
        self.viewWidget.clear()
