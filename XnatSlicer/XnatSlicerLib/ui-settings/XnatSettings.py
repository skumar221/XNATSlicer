from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys

from XnatAnimatedCollapsible import *



comment = """
XnatSettings 

TODO:
"""


        
class XnatSettings(qt.QScrollArea):
    """ 
    """

    def __init__(self, title, MODULE):
        """ Init function.
        """

        self.MODULE = MODULE

        
        #--------------------
        # Call parent init.
        #--------------------
        qt.QScrollArea.__init__(self)


        
        self.setStyleSheet('height: 98%; width: 100%')
        #--------------------
        # NOTE: fixes a scaling error that occurs with the scroll 
        # bar.  Have yet to pinpoint why this happens.
        #--------------------
        self.verticalScrollBar().setStyleSheet('width: 15px')


        
        #--------------------
        # The title/label
        #--------------------
        self.label = qt.QLabel(title)


        
        #--------------------
        # Layout for entire frame
        #--------------------
        self.frame = qt.QFrame()
        self.frame.setStyleSheet("background: rgb(255,255,255)")



        #--------------------
        # Layout for entire frame
        #--------------------
        self.masterLayout = qt.QVBoxLayout()



        #--------------------
        # Meta keys
        #--------------------
        self.metaKeys = ['projects', 'subjects', 'experiments', 'scans', 'slicer', 'files']



        
        

    def addSpacing(self):
        """ As stated.
        """
        self.masterLayout.addSpacing(15) 
        

        

    def addSectionTitle(self, title):
        """ Adds section title to the master layout.
        """
        mLabel = qt.QLabel('<b>%s<b>'%(title))
        self.masterLayout.addWidget(mLabel)
        self.masterLayout.addSpacing(15)
        

        
        
    @property
    def title(self):
        """
        """
        return self.label.text



    def makeMetadataManager(self, asLabels = True, buttonOnClick = None):
        """
        """
        metadataManager = qt.QFrame()
        metadataManagerLayout = qt.QVBoxLayout()


        
        #--------------------
        # Gather checkboxes into groups by XNAT level.
        #--------------------
        labelOrCheckBoxes = {}
        for key in self.metaKeys:
            if key != 'LABELS':
                metadataTags = self.MODULE.XnatIo.relevantMetadataDict[key]
                labelOrCheckBoxes[key] = []                
                for i in range(0, len(metadataTags)):
                    #
                    # Make the metadata a QLabel
                    #
                    if asLabels:
                        labelOrCheckBox = qt.QLabel(metadataTags[i])

                    #
                    # Make the metadata a QCheckBox
                    #
                    else:
                        labelOrCheckBox = qt.QCheckBox(metadataTags[i])

                    labelOrCheckBox.setFont(self.MODULE.GLOBALS.LABEL_FONT) 
                    labelOrCheckBoxes[key].append(labelOrCheckBox)

                    
        
        #--------------------
        # Construct grid layout.
        #--------------------

        #
        # Create. Collapsibles and buttonLayouts.
        #
        self.collapsibles = {}
        self.buttonGrids = {}
        for key in self.metaKeys:
            widgetList = []
            
            #
            # Add 'DEFAULT' label to grid.
            #
            defaultLabel = qt.QLabel('<b>DEFAULT TYPES:<b>')
            defaultLabel.setFont(self.MODULE.GLOBALS.LABEL_FONT_BOLD)
            widgetList.append(defaultLabel)
            
            #
            # Make Button grid layout, add first label.
            #
            self.buttonGrids[key] = qt.QGridLayout()
            self.buttonGrids[key].addWidget(defaultLabel, 0, 0)

            #
            # Add checkboxes to grid
            #
            rowVal = 1
            columnVal = 0
            for cb in labelOrCheckBoxes[key]:
                widgetList.append(cb)
                self.buttonGrids[key].addWidget(cb, rowVal, columnVal)
                columnVal += 1
                if columnVal > 2:
                    rowVal += 1
                    columnVal = 0

            #
            # Add spacer row to grid
            #
            rowVal += 1
            spacer = qt.QLabel(' ')
            widgetList.append(spacer)
            self.buttonGrids[key].addWidget(spacer, rowVal, 0)

            #
            # Add 'CUSTOM' label to grid.
            #
            rowVal += 1
            customLabel = qt.QLabel('<b>CUSTOM TYPES:<b>')
            customLabel.setFont(self.MODULE.GLOBALS.LABEL_FONT_BOLD)
            widgetList.append(customLabel)
            self.buttonGrids[key].addWidget(customLabel, rowVal, 0)
            
            #
            # Add the 'addCustomType' button.
            #
            if not asLabels:
                addCustomTypeButton = self.MODULE.utils.generateButton(iconOrLabel = "Manage custom tags for '%s'"%(key), 
                                                                               toolTip = "Adds a custom metadata tag to display in the 'Info' column.", 
                                                                               font = self.MODULE.GLOBALS.LABEL_FONT,
                                                                               size = qt.QSize(180, 20), 
                                                                               enabled = True)
                self.buttonGrids[key].addWidget(addCustomTypeButton, rowVal, 1)

                #
                # Set the onclick method for the button
                #
                if buttonOnClick:
                    addCustomTypeButton.connect('clicked()', buttonOnClick)



                
                widgetList.append(addCustomTypeButton)

            #
            # Put the buttonGrid, labels, etc. into an AnimatedCollapsible
            #
            self.collapsibles[key] = XnatAnimatedCollapsible(self, key.title())
            self.collapsibles[key].setFrameLayout(self.buttonGrids[key])
            self.collapsibles[key].setContentsWidgets(widgetList)
            self.collapsibles[key].setFixedWidth(500)


            #
            # Add collapsible to metadataManagerLayout.
            #
            metadataManagerLayout.addWidget(self.collapsibles[key])
            metadataManagerLayout.addSpacing(10)



        #
        # Set callback to Update XNATSlicer's layout when animating.
        #
        def onAnimatedCollapsibleAnimate():
            metadataManagerLayout.update()
        for key, collapsible in self.collapsibles.iteritems():
            collapsible.setOnAnimate(onAnimatedCollapsibleAnimate)


            
        #
        # Return metadata object
        #
        metadataManager.setLayout(metadataManagerLayout)
        return metadataManager


