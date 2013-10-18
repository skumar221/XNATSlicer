from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys

from XnatSettingManager import *



comment = """
XnatTreeViewSettings

TODO:
"""


        
class XnatTreeViewManager(XnatSettingManager):
    """ Embedded within the settings popup.  Manages hosts.
    """
  
    def __init__(self, title, MODULE):
        """ Init function.
        """
        
        #--------------------
        # Call parent init
        #--------------------
        super(XnatTreeViewManager, self).__init__(title, MODULE)

        

        #--------------------
        # Group Boxes
        #--------------------
        groupBoxNames = ['Sort Projects By', "'Info' Column Contents"]
        self.groupBoxes = {}
        for name in groupBoxNames:
            groupBox = qt.QGroupBox(name)
            groupBoxLayout = qt.QGridLayout()
            self.groupBoxes[name] = {'layout': groupBoxLayout, 'widget' : groupBox}
            groupBox.setLayout(groupBoxLayout)
            self.masterLayout.addWidget(groupBox)
            self.addSpacing()



            
        
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
        self.groupBoxes['Sort Projects By']['layout'].addWidget(self.buttons['sort']['accessed'], 0, 0)
        self.groupBoxes['Sort Projects By']['widget'].setFixedHeight(50)
        
        

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
        rowVal = -1
        for key in metaKeys:
            rowVal += 1
            cbLabel = qt.QLabel(key.title())
            cbLabel.setFont(self.MODULE.GLOBALS.LABEL_FONT_BOLD) 
            self.groupBoxes["'Info' Column Contents"]['layout'].addWidget(cbLabel, rowVal, 0)
            cbLayout = qt.QHBoxLayout()
            columnVal = 0
            rowVal += 1
            for cb in checkBoxes[key]:
                self.groupBoxes["'Info' Column Contents"]['layout'].addWidget(cb, rowVal, columnVal)
                columnVal += 1
                if columnVal > 3:
                    rowVal += 1
                    columnVal = 0



        #--------------------
        # Add to frame.
        #--------------------
        self.masterLayout.addStretch()
        self.frame.setLayout(self.masterLayout)
        


        
      
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



            
