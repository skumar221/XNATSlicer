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
        self.defaultMetadataEditors = {}
        self.customMetadataEditors = {}
        self.customMetadataTags = {}
        self.buttons = {}
        self.labels = {}
        self.buttonGrids = {}
        self.editCustomButtons = {}

        self.editCustomButtonGroup = qt.QButtonGroup()
        self.editCustomButtonGroup.connect('buttonClicked(QAbstractButton*)', self.editCustomClicked)



        self.editButtonsVisible = True
        
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
            self.defaultMetadataEditors[key] = XnatDefaultMetadataEditor(self.MODULE, key)
            self.buttonGrids[key].addWidget(self.defaultMetadataEditors[key], 1, 0)



            
            #--------------------
            # Define the custom metadata tags for storing into 
            # the settings file
            #--------------------
            self.customMetadataTags[key] = self.MODULE.GLOBALS.makeCustomMetadataTag(key)



            #--------------------
            # Make the metadata managers
            #--------------------   
            self.customMetadataEditors[key] = XnatCustomMetadataEditor(self.MODULE, key)
            self.buttonGrids[key].addWidget(self.customMetadataEditors[key], 1, 1, 1, 2)
            

            

            #
            # Add 'CUSTOM' label to grid.
            #
            self.labels[key].append(qt.QLabel('<b>CUSTOM<b>'))
            self.labels[key][1].setFont(self.MODULE.GLOBALS.LABEL_FONT_BOLD)
            self.buttonGrids[key].addWidget(self.labels[key][1], 0, 1)
            
            #
            # Add the 'editCustom' button.
            #

            self.editCustomButtons[key] = self.MODULE.utils.generateButton(iconOrLabel = "Edit custom tags for '%s'"%(key), 
                                                                               toolTip = "Adds a custom metadata tag to display in the 'Info' column.", 
                                                                               font = self.MODULE.GLOBALS.LABEL_FONT,
                                                                               size = qt.QSize(180, 20), 
                                                                               enabled = True)

            self.buttonGrids[key].addWidget(self.editCustomButtons[key], 0, 2)
            self.editCustomButtonGroup.addButton(self.editCustomButtons[key])
            



            #
            # Put the buttonGrid, labels, etc. into an AnimatedCollapsible
            #
            self.collapsibles[key] = AnimatedCollapsible( key.title())
            self.collapsibles[key].setFrameLayout(self.buttonGrids[key])
            self.collapsibles[key].addContentsWidgets(self.labels[key], self.editCustomButtons[key], self.defaultMetadataEditors[key], self.customMetadataEditors[key])
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
            #self.update()
        for key, collapsible in self.collapsibles.iteritems():
            collapsible.setOnAnimate(onAnimatedCollapsibleAnimate)


            
        #
        # Return metadata object
        #
        self._layout.addStretch()
        self.setLayout(self._layout)


        #self.currItemType = 'label'
        self.setItemType('label')



        




    def setItemsEnabled(self, enabled):
        """
        """
        if not enabled:
            for key, widget in self.defaultMetadataEditors.iteritems():
                for i in range(0, widget.count):
                    widget.item(i).setFlags(0)
                



                        
    def setItemType(self, itemType):
        """ 
        """

        for key, metadataEditor in self.defaultMetadataEditors.iteritems():
            metadataEditor.setItemType(itemType)

        for key, metadataEditor in self.customMetadataEditors.iteritems():
            metadataEditor.setItemType(itemType)






    def setEditButtonsVisible(self, visible = None):
        """
        """

        print "                 \n\n\nSET EDIT BUTTONS VISIBLE"
        if visible != None:
            self.editButtonsVisible = visible

        #
        # Hide the 'editCustom' buttons
        #
        for key, button in self.editCustomButtons.iteritems():
            button.setVisible(self.editButtonsVisible)

            if not self.editButtonsVisible:
                self.collapsibles[key].removeContentsWidgets(button)

            


    def editCustomClicked(self, button):
        """
        """
        for key, _button in self.editCustomButtons.iteritems():
            if button == _button:
                self.MODULE.xnatSettingsWindow.setCurrentIndex(1) 
                self.MODULE.metadataSettings.XnatMetadataManager.collapsibles[key].setChecked(True)
            else:
                self.MODULE.metadataSettings.XnatMetadataManager.collapsibles[key].setChecked(False)

        

                
    def setCustomEditVisible(self, visible):
        """
        """
        #
        # Custom
        #
        for key, metadataEditor in self.customMetadataEditors.iteritems():
            metadataEditor.setEditLineVisible(visible)


                
                   
    def update(self):
        """
        """
        self.setEditButtonsVisible()
        #self.hostDropdown.setCurrentIndex(self.MODULE.XnatLoginMenu.hostDropdown.currentIndex)
        for key in self.customMetadataEditors:
            self.customMetadataEditors[key].clear() 

            try:
                #customMetadataItems = self.MODULE.settingsFile.getTagValues(self.MODULE.metadataSettings.hostDropdown.currentText, self.customMetadataTags[key])
                self.defaultMetadataEditors[key].update()
                self.customMetadataEditors[key].update()
                print "CURR", self.currItemType
                self.setItemType(self.currItemType)
                
                    
            except Exception, e:
                print self.MODULE.utils.lf()
                print str(e)



    def setOnMetadataCheckedTag(self, tag):
        """
        """

        for key in self.defaultMetadataEditors:
            self.defaultMetadataEditors[key].onMetadataCheckedTag = tag
        for key in self.customMetadataEditors:
            self.customMetadataEditors[key].onMetadataCheckedTag = tag            
