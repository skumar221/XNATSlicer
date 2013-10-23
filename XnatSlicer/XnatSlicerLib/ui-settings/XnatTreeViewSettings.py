from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys

from XnatSettings import *



comment = """
XnatTreeViewSettings

TODO:
"""


        
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
        self.buttons = {}
        self.buttons['sort'] = {}
        self.buttons['sort'] = {'accessed': self.MODULE.utils.generateButton(iconOrLabel = 'Accessed', 
                                                                               toolTip = "Sort projects, prioritizing those accessed by current user.", 
                                                                               font = self.MODULE.GLOBALS.LABEL_FONT,
                                                                               size = qt.QSize(50, 20), 
                                                                               enabled = True)}
        
        

        #--------------------
        # Gather checkboxes into groups by XNAT level.
        #--------------------
        metaKeys = ['projects', 'subjects', 'experiments', 'scans', 'slicer', 'files']
        checkBoxes = {}
        for key in metaKeys:
            if key != 'LABELS':
                metadataTags = self.MODULE.XnatIo.relevantMetadataDict[key]
                checkBoxes[key] = []                
                for i in range(0, len(metadataTags)):
                    checkBox = qt.QCheckBox(metadataTags[i])
                    checkBox.setFont(self.MODULE.GLOBALS.LABEL_FONT) 
                    checkBoxes[key].append(checkBox)

        

        #--------------------
        # Construct grid layout.
        #--------------------
        self.collapsibles = {}
        

        mLabel = qt.QLabel('<b>Info Tab Metadata<b>')
        self.masterLayout.addWidget(mLabel)
        self.masterLayout.addSpacing(20)
        
        self.buttonGrids = {}
        for key in metaKeys:
            self.buttonGrids[key] = qt.QGridLayout()

            
            defaultLabel = qt.QLabel('<b>DEFAULT TYPES:<b>')
            defaultLabel.setFont(self.MODULE.GLOBALS.LABEL_FONT_BOLD)
            self.buttonGrids[key].addWidget(defaultLabel, 0, 0)

            
            rowVal = 1
            columnVal = 0
            for cb in checkBoxes[key]:
                self.buttonGrids[key].addWidget(cb, rowVal, columnVal)
                columnVal += 1
                if columnVal > 2:
                    rowVal += 1
                    columnVal = 0

            rowVal += 1
            spacer = qt.QLabel(' ')
            
            self.buttonGrids[key].addWidget(spacer, rowVal, 0)

            rowVal += 1
            customLabel = qt.QLabel('<b>CUSTOM TYPES:<b>')
            customLabel.setFont(self.MODULE.GLOBALS.LABEL_FONT_BOLD)

            addCustomTypeButton = qt.QPushButton("+ Add Custom Type to '%s'"%(key))
            addCustomTypeButton.setFont(self.MODULE.GLOBALS.LABEL_FONT)
            addCustomTypeButton.setFixedWidth(180)
            addCustomTypeButton.setFixedHeight(35)

            
            self.buttonGrids[key].addWidget(customLabel, rowVal, 0)
            self.buttonGrids[key].addWidget(addCustomTypeButton, rowVal, 1)

        #for key in self.buttonGrids:
            self.collapsibles[key] = XnatAnimatedCollapsible(self, key.title())
            self.collapsibles[key].addToLayout(self.buttonGrids[key])
            
            #self.masterLayout.addLayout(self.buttonGrids[key])
            self.masterLayout.addWidget(self.collapsibles[key])
            self.masterLayout.addSpacing(10)

            


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



            
