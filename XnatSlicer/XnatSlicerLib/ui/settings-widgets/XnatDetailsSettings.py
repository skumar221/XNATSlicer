from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys

from XnatSettings import *
from XnatMetadataManager import *



comment = """
XnatDetailsSettings 

TODO:
"""



#--------------------
# Define the visible metadata tags for storing into 
# the settings file
#--------------------
visibleMetadataTags = {'projects': '', 'subjects' : '', 'experiments' : '', 'scans' :'', 'files' : '', 'slicer': ''}
for key in visibleMetadataTags:
    visibleMetadataTags[key] = 'visibleMetadataTags_' + key



    
class XnatDetailsSettings(XnatSettings):
    """ Embedded within the settings popup.  Manages hosts.
    """

  
    def __init__(self, title, MODULE):
        """ Init function.
        """
        
        #--------------------
        # Call parent init
        #--------------------
        super(XnatDetailsSettings, self).__init__(title, MODULE)


        
        #--------------------
        # Add Metadata Label and Manager.
        #--------------------
        mLabel = qt.QLabel('<b>Details Display Data:</b>')
        self.masterLayout.addWidget(mLabel)
        self.masterLayout.addSpacing(15)

        
        self.setMetadataManagers('main')
        self.masterLayout.addWidget(self.XnatMetadataManagers['main'])
        self.setDefaultSelectedMetadata('main',  self.MODULE.GLOBALS.DEFAULT_XNAT_METADATA)
        

        for key, manager in self.XnatMetadataManagers.iteritems():
            manager.setCustomEditVisible(False)
            manager.setItemType('checkbox')

        self.complete()
