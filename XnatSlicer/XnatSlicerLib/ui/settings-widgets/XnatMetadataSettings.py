from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys

from XnatSettings import *
from XnatMetadataManager import *



comment = """
XnatMetadataSettings 

TODO:
"""



        
class XnatMetadataSettings(XnatSettings):
    """ Embedded within the settings popup.  Manages hosts.
    """

  
    def __init__(self, title, MODULE):
        """ Init function.
        """
        
        #--------------------
        # Call parent init
        #--------------------
        super(XnatMetadataSettings, self).__init__(title, MODULE)


        
        #--------------------
        # Add Metadata Label and Manager.
        #--------------------
        mLabel = qt.QLabel('<b>Metadata for</b>')
        self.hostDropdown = qt.QComboBox()
        self.hostDropdown.setFixedHeight(20)


        
        #--------------------
        # Get the dictionary from settings and the key to 
        # the dropdown widget.
        #--------------------
        hostDict = self.MODULE.XnatSettingsFile.getHostNameAddressDictionary()
        for name in hostDict:     
            self.hostDropdown.addItem(name)  
        labelLayout = qt.QHBoxLayout()
        labelLayout.addWidget(mLabel)
        labelLayout.addWidget(self.hostDropdown)
        labelLayout.addStretch()


        
        
        self.masterLayout.addLayout(labelLayout)
        self.masterLayout.addSpacing(15)


        #--------------------
        # Hide metadata manager buttons
        #--------------------

        #self.setupMetadataManager()
        #self.XnatMetadataManager.setEditButtonsVisible(False)
        self.setMetadataManagers('main')
        self.masterLayout.addWidget(self.XnatMetadataManagers['main'])
        self.XnatMetadataManagers['main'].setEditButtonsVisible(False)

        self.masterLayout.addWidget(self.XnatMetadataManagers['main'])


        for key, manager in self.XnatMetadataManagers.iteritems():
            manager.setItemType('label')

        self.complete()


            

            


        








     
