from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys

from XnatSettings import *



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
        hostDict = self.MODULE.settingsFile.getHostNameAddressDictionary()
        for name in hostDict:     
            self.hostDropdown.addItem(name)  
        labelLayout = qt.QHBoxLayout()
        labelLayout.addWidget(mLabel)
        labelLayout.addWidget(self.hostDropdown)
        labelLayout.addStretch()


        
        
        self.masterLayout.addLayout(labelLayout)
        self.masterLayout.addSpacing(15)
        self.metadataManager = self.makeMetadataManager(buttonOnClick = self.makeAddCustomMetadataModal)
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



        #--------------------
        # Define the custom metadata tags for storing into 
        # the settings file
        #--------------------
        self.customMetadataTags = {}
        for key in self.metaKeys:
            self.customMetadataTags[key] = 'customMetadataTags_' + key



        #--------------------
        # Make the metadata managers
        #--------------------
        self.customManagers = {}
        for key in self.metaKeys:
            self.customManagers[key] = self.makeCustomMetadataManager(key)
            self.customManagers[key]['widget'].setStyleSheet('width: 100%')
            self.buttonGrids[key].addWidget(self.customManagers[key]['widget'], self.buttonGrids[key].rowCount(), 0, 4, 3)
            

            

    def update(self):
        """
        """
        self.hostDropdown.setCurrentIndex(self.MODULE.XnatLoginMenu.hostDropdown.currentIndex)
        for key in self.customManagers:
            self.customManagers[key]['list'].clear() 
            self.customManagers[key]['line'].clear() 

            
            customMetadataItems = self.MODULE.settingsFile.getTagValues(self.hostDropdown.currentText, self.customMetadataTags[key])
            if customMetadataItems:
                customMetadataItems = customMetadataItems.split(',')
                self.customManagers[key]['list'].addItems(customMetadataItems)
        




    def addCustomMetadataTag(self):
        """
        """
        customTags = {}
        for key, value in self.customMetadataTags.iteritems():
            customTags[value] = []
            
        for key in self.customManagers:
            lineText = self.customManagers[key]['line'].text.strip('')
            if len(lineText) > 0:
                if not self.customMetadataTags[key] in customTags:
                    customTags[self.customMetadataTags[key]] = []
                customTags[self.customMetadataTags[key]].append(str(lineText))

            customMetadataItems = self.MODULE.settingsFile.getTagValues(self.hostDropdown.currentText, self.customMetadataTags[key])
            if customMetadataItems:
                customMetadataItems = customMetadataItems.split(',')
                customTags[self.customMetadataTags[key]] += customMetadataItems        

        self.MODULE.settingsFile.saveCustomPropertiesToHost(self.hostDropdown.currentText, customTags)
        self.update()
        

        
            
    def makeCustomMetadataManager(self, xnatHost):
        """
        """
        customMetaManager = {}
        
        customMetaManager['widget'] = qt.QWidget()
        customMetaManager['list'] = qt.QListWidget()

        customMetaManager['line'] = qt.QLineEdit()
        addButton = qt.QPushButton('Add')
        deleteButton = qt.QPushButton('Remove')

        mainLayout = qt.QVBoxLayout()
        lineLayout = qt.QHBoxLayout()

        lineLayout.addWidget(customMetaManager['line'])
        lineLayout.addWidget(addButton)
        lineLayout.addWidget(deleteButton)


        addButton.connect('clicked()', self.addCustomMetadataTag)

        mainLayout.addWidget(customMetaManager['list'])
        mainLayout.addLayout(lineLayout)

        customMetaManager['widget'].setLayout(mainLayout)

        return customMetaManager
        
        
        

    def saveCustomMetadata(self):
        """ Saves the custom metadata tags to the given host.
        """
        #--------------------
        # Remove existing.
        #--------------------
        #self.MODULE.settingsFile.saveCustomPropertiesToHost('CNDA', {self.customMetadataTags['projects'] : ['asdf','ab','cas','eer']})



        
    def makeAddCustomMetadataModal(self):
        """
        """
        self.addCustomMetadataModal = qt.QWidget()
        self.addCustomMetadataModal.setWindowModality(2)
        

        modalLayout = qt.QVBoxLayout()
        customRow = qt.QHBoxLayout()
        

        addMetadataLabel = qt.QLabel('Add Custom Metdata to ')
        addMetadataLabel.setFont(self.MODULE.GLOBALS.LABEL_FONT_BOLD)
        modalLayout.addWidget(addMetadataLabel)
        
        self.levelDropdown = qt.QComboBox()
        self.levelDropdown.setFont(self.MODULE.GLOBALS.LABEL_FONT)
        self.levelDropdown.toolTip = "Select XNAT Level"
        self.levelDropdown.addItems(self.metaKeys)

        self.lineEdit = qt.QLineEdit()


        
        
        
        customRow.addWidget(self.levelDropdown)
        customRow.addWidget(self.lineEdit)
        modalLayout.addLayout(customRow)

        
        self.addCustomMetadataModal.setLayout(modalLayout)
        
        self.addCustomMetadataModal.show()
