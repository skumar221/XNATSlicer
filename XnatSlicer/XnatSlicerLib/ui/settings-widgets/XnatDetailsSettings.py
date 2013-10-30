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

        
        self.setupMetadataManager()
        self.XnatMetadataManager.setItemType('checkbox')
        self.XnatMetadataManager.setCustomEditVisible(False)
    
        self.ON_METADATA_CHECKED_TAG = "DetailsInfo_" 
        self.XnatMetadataManager.setOnMetadataCheckedTag(self.ON_METADATA_CHECKED_TAG)
