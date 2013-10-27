from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys

from AnimatedCollapsible import *
from XnatMetadataEditor import *



comment = """
XnatMetadataManager

TODO:
"""


        
class XnatMetadataManager(qt.QFrame):
    """ 
    """

    def __init__(self, MODULE):
        """ Init function.
        """

        super(XnatMetadataManager, self).__init__(self)

        self.MODULE = MODULE

        self._layout = qt.QVBoxLayout()
        self.collapsibles = {}
        self.metadataWidgets = {}
        self.defaultScrollWidgets = {}
        self.customScrollWidgets = {}
        self.customMetadataTags = {}
        self.buttons = {}
        self.labels = {}
        self.buttonGrids = {}

        #--------------------
        # Construct grid layout.
        #--------------------

        
        for key in self.MODULE.GLOBALS.XNAT_SLICER_FOLDERS:

            #
            #
            #
            self.labels[key] = []
            self.labels[key].append(qt.QLabel('<b>DEFAULT<b>'))
            self.labels[key][0].setFont(self.MODULE.GLOBALS.LABEL_FONT_BOLD)

            
            #
            # Make Button grid layout, add first label.
            #
            self.buttonGrids[key] = qt.QGridLayout()
            self.buttonGrids[key].addWidget(self.labels[key][0], 0, 0)



            #
            # Gather checkboxes as scrollArea list.
            #
            self.defaultScrollWidgets[key] = XnatDefaultMetadataEditor(self.MODULE, key)
            self.buttonGrids[key].addWidget(self.defaultScrollWidgets[key], 1, 0)



            
            #--------------------
            # Define the custom metadata tags for storing into 
            # the settings file
            #--------------------
           
            self.customMetadataTags[key] = 'customMetadataTags_' + key



            #--------------------
            # Make the metadata managers
            #--------------------   
            self.customScrollWidgets[key] = XnatCustomMetadataEditor(self.MODULE, key)
            self.buttonGrids[key].addWidget(self.customScrollWidgets[key], 1, 1, 1, 2)
            

            

            #
            # Add 'CUSTOM' label to grid.
            #
            self.labels[key].append(qt.QLabel('<b>CUSTOM<b>'))
            self.labels[key][1].setFont(self.MODULE.GLOBALS.LABEL_FONT_BOLD)
            self.buttonGrids[key].addWidget(self.labels[key][1], 0, 1)
            
            #
            # Add the 'addCustomType' button.
            #

            addCustomTypeButton = self.MODULE.utils.generateButton(iconOrLabel = "Edit custom tags", 
                                                                               toolTip = "Adds a custom metadata tag to display in the 'Info' column.", 
                                                                               font = self.MODULE.GLOBALS.LABEL_FONT,
                                                                               size = qt.QSize(180, 20), 
                                                                               enabled = True)
            self.buttonGrids[key].addWidget(addCustomTypeButton, 0, 2)

            #
            # Set the onclick method for the button
            #
            # if buttonOnClick:
            # addCustomTypeButton.connect('clicked()', buttonOnClick)
            if not key in self.buttons:
                self.buttons[key] = []
            self.buttons[key].append(addCustomTypeButton)   


            #
            # Put the buttonGrid, labels, etc. into an AnimatedCollapsible
            #
            self.collapsibles[key] = AnimatedCollapsible( key.title())
            self.collapsibles[key].setFrameLayout(self.buttonGrids[key])
            #self.collapsibles[key].setContentsWidgets(widgetList)
            self.collapsibles[key].setFixedWidth(500)


            #
            # Add collapsible to self._layout.
            #
            self._layout.addWidget(self.collapsibles[key])
            self._layout.addSpacing(10)



        #
        # Set callback to Update XNATSlicer's layout when animating.
        #
        def onAnimatedCollapsibleAnimate():
            self._layout.update()
        for key, collapsible in self.collapsibles.iteritems():
            collapsible.setOnAnimate(onAnimatedCollapsibleAnimate)


            
        #
        # Return metadata object
        #
        self._layout.addStretch()
        self.setLayout(self._layout)




            
        
        

    def saveCustomMetadata(self):
        """ Saves the custom metadata tags to the given host.
        """
        #--------------------
        # Remove existing.
        #--------------------
        #self.MODULE.settingsFile.saveCustomPropertiesToHost('CNDA', {self.customMetadataTags['projects'] : ['asdf','ab','cas','eer']})


        

    def hideButtons(self):
        """
        """
        for key, buttons in self.buttons.iteritems():
            for button in buttons:
                button.hide()




    def setItemsEnabled(self, enabled):
        """
        """
        if not enabled:
            for key, widget in self.defaultScrollWidgets.iteritems():
                for i in range(0, widget.count):
                    widget.item(i).setFlags(0)
                



                        
    def setItemType(self, itemType):
        """
        """
        if itemType == 'checkbox':
            size = qt.QSize(20,20)
            #
            # Default
            #
            for key, widget in self.defaultScrollWidgets.iteritems():
                for i in range(0, widget.count):
                    widget.item(i).setSizeHint(size)
                    widget.item(i).setFlags(4 | 8 | 16 | 32)
                    widget.item(i).setCheckState(0)
            #
            # Custom
            #
            for key, widget in self.customScrollWidgets.iteritems():
                for i in range(0, widget.count):
                   widget.item(i).setSizeHint(size)
                   widget.item(i).setFlags(4 | 8 | 16 | 32)
                   widget.item(i).setCheckState(0)


                   

    def setCustomEditVisible(self, visible):
        """
        """
        #
        # Custom
        #
        for key, widget in self.customScrollWidgets.iteritems():
            widget.setEditLineVisible(visible)


                
                   
    def update(self):
        """
        """
        #self.hostDropdown.setCurrentIndex(self.MODULE.XnatLoginMenu.hostDropdown.currentIndex)
        for key in self.customScrollWidgets:
            self.customScrollWidgets[key].clear() 
            self.customScrollWidgets[key].clear() 

            
            customMetadataItems = self.MODULE.settingsFile.getTagValues(self.hostDropdown.currentText, self.customMetadataTags[key])
            if customMetadataItems:
                customMetadataItems = customMetadataItems.split(',')
                self.customScrollWidgets[key].addItems(customMetadataItems)

