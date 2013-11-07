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


        self.addFontDropdown()
        self.addSpacing()

        self.setMetadataManagers('main') 
        self.addSection("Details View Metadata", self.XnatMetadataManagers['main'])
        

        self.setDefaultSelectedMetadata('main',  self.MODULE.GLOBALS.DEFAULT_XNAT_METADATA)
        for key, manager in self.XnatMetadataManagers.iteritems():
            manager.setCustomEditVisible(False)
            manager.setItemType('checkbox')


        self.complete()



    def addFontDropdown(self, title = "Font Size:" ):
        """
        """
        super(XnatDetailsSettings, self).addFontDropdown(title)

        self.fontSizeTag = "DetailsFontSize"
        
        xnatHost = self.MODULE.XnatMetadataSettings.hostDropdown.currentText
        font = self.MODULE.XnatSettingsFile.getTagValues(xnatHost, self.fontSizeTag)


        if len(font) == 0:
            currSize = self.MODULE.GLOBALS.FONT_SIZE
            self.MODULE.XnatSettingsFile.setTagValues(xnatHost, {self.fontSizeTag: [str(currSize)]})
        else:
            currSize = font[0]
        
        def changeFontSize(size):
            try:
                self.MODULE.XnatNodeDetails.changeFontSize(int(size))
                self.MODULE.XnatSettingsFile.setTagValues(xnatHost, {self.fontSizeTag: [str(size)]})
            except Exception, e:
                print self.MODULE.utils.lf(), str(e)
                pass

        currDropdown = self.fontDropdowns[-1]
        currDropdown.connect('currentIndexChanged(const QString&)', changeFontSize)
        currDropdown.setCurrentIndex(currDropdown.findText(currSize))
