from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys

from XnatSettings import *



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
        self.metadataManager = self.makeMetadataManager(asLabels = False)
        self.masterLayout.addWidget(self.metadataManager)

        

        #--------------------
        # Add to frame.
        #--------------------
        self.masterLayout.addStretch()
        self.frame.setLayout(self.masterLayout)
        if self.collapsibles:
            for key in self.collapsibles:
                self.collapsibles[key].show() 
                self.collapsibles[key].setChecked(False) 
        self.setWidget(self.frame)

        

        
    def saveVisibileMetadata(self):
        """ Saves the custom metadata tags to the given host.
        """
        #--------------------
        # Remove existing.
        #--------------------
        self.MODULE.settingsFile.saveCustomPropertiesToHost('CNDA', {visibleMetadataTags['projects'] : ['asdf','ab','cas','eer']})
