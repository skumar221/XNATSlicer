from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys

from XnatSettings import *
from XnatMetadataManager import *



comment = """
XnatTreeViewSettings

TODO:
"""




#--------------------
# Define the info metadata tags for storing into 
# the settings file
#--------------------
infoMetadataTags = {'projects': '', 'subjects' : '', 'experiments' : '', 'scans' :'', 'files' : '', 'slicer': ''}
for key in infoMetadataTags:
    infoMetadataTags[key] = 'infoMetadataTags_' + key


    
        
class XnatTreeViewSettings(XnatSettings):
    """ Embedded within the settings popup.  Manages hosts.
    """
  
    def __init__(self, title, MODULE):
        """ Init function.
        """
        
        #--------------------
        # Call parent init
        #--------------------
        super(XnatTreeViewSettings, self).__init__(title, MODULE)

            
        
        #--------------------
        # Sort Buttons
        #--------------------
        
        #
        # Add section Label
        #
        bLabel = qt.QLabel('<b>Filter Projects By:</b>')
        self.masterLayout.addWidget(bLabel)
        self.masterLayout.addSpacing(8)
        
        #
        # Create buttons
        #
        self.buttons = {}
        self.buttons['sort'] = {}
        self.buttons['sort'] = {'accessed': self.MODULE.utils.generateButton(iconOrLabel = 'Last Accessed', 
                                                                               toolTip = "Sort projects, prioritizing those accessed by current user.", 
                                                                               font = self.MODULE.GLOBALS.LABEL_FONT,
                                                                               size = qt.QSize(90, 20), 
                                                                               enabled = True)}

        #
        # Add buttons to master layout.
        #
        self.sortButtonLayout = qt.QHBoxLayout()
        for key, value in self.buttons['sort'].iteritems():
            self.sortButtonLayout.addWidget(value)
        self.sortButtonLayout.addStretch()
        self.masterLayout.addLayout(self.sortButtonLayout)


        
        
        self.addSpacing()
        self.addSpacing()

                   
        
        #--------------------
        # Add Metadata Label and Manager.
        #--------------------
        mLabel = qt.QLabel('<b>Info. Column Metadata</b>')
        self.masterLayout.addWidget(mLabel)
        self.masterLayout.addSpacing(15)


        self.setupMetadataManager()
        self.XnatMetadataManager.setItemType('checkbox')




        
        #
        # For saving in the settings file a metadata checkbox is tracked
        #
        self.ON_METADATA_CHECKED_TAG = "TreeViewInfo_" 
        print "TREE SETTNS"
        self.XnatMetadataManager.setOnMetadataCheckedTag(self.ON_METADATA_CHECKED_TAG)
        #self.masterLayout.addWidget(self.XnatMetadataManager)



        
        
      
    def setButtonDown(self, category = None, name = None, isDown = True, callSignals = True):
          """ Programmatically sets a button down based on
              the arguments.  The user has the option to allow for
              the 'clicked()' signals to be called or not.  
              This is used primarily for default programmatic 
              manipulation of the buttons, such as loadProjects() in 
              XNATTreeView, where default filters are applied, but
              the signals of clicking are not desired, but 
              self.currentlyToggledFilterButton is still tracked.
          """
          if isDown and category == 'sort':
              self.buttons[category][name].setChecked(True)
              self.currentlyToggledFilterButton = self.buttons['sort'][name]



              
    def saveInfoMetadata(self):
        """ Saves the info metadata tags to the given host.
        """
        #--------------------
        # Remove existing.
        #--------------------
        self.MODULE.settingsFile.saveCustomPropertiesToHost('CNDA', {infoMetadataTags['projects'] : ['asdf','ab','cas','eer']})


            
