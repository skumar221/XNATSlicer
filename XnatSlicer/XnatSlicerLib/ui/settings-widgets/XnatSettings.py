from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys

from AnimatedCollapsible import *
from VariableItemListWidget import *
from XnatMetadataManager import *


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



        self.sectionSpacing = 5

        self.setObjectName('xnatSetting')
        self.setStyleSheet('#xnatSetting {height: 100%; width: 100%; border: 1px solid gray;}')
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
        self.frame.setObjectName('settingFrame')
        self.frame.setStyleSheet("#settingFrame {background: white;}")



        #--------------------
        # Layout for entire frame
        #--------------------
        self.masterLayout = qt.QVBoxLayout()
        self.masterLayout.setContentsMargins(10,10,10,10)



        #--------------------
        # Set the Metadata managers object
        #--------------------
        self.XnatMetadataManagers = {}



        #--------------------
        # Add buttons.
        #--------------------


        
        

        self.ON_METADATA_CHECKED_TAGS = {}
        self.defaultSelectedMetadata = {}

        self.tabTitle = title

    

        self.sectionLabels = []

        
        

        
    def createMetadataManagers(self, *args):
        """
        """
        for arg in args:
            self.XnatMetadataManagers[arg] = XnatMetadataManager(self.MODULE)
            self.ON_METADATA_CHECKED_TAGS[arg] = self.__class__.__name__ + "_%s_"%(arg) 
            self.XnatMetadataManagers[arg].setOnMetadataCheckedTag(self.ON_METADATA_CHECKED_TAGS[arg])
            self.defaultSelectedMetadata[arg] = None




            
    def setDefaultSelectedMetadata(self, label, *args):
        """
        """

        #--------------------
        # If the argument is a dictionary, then apply it.
        #--------------------
        if type(args[0]) == dict:
            self.defaultSelectedMetadata[label] = args[0]


        #--------------------
        # If there are no saved selecte metadata, 
        # apply the defaults.
        #--------------------

        xnatHosts = [self.MODULE.XnatMetadataSettings.hostDropdown.itemText(ind) for ind in range(0, self.MODULE.XnatMetadataSettings.hostDropdown.count)]
        for xnatHost in xnatHosts:
            for xnatLevel in self.MODULE.GLOBALS.XNAT_LEVELS:
                
                for key in self.ON_METADATA_CHECKED_TAGS:
                    
                    levelTag = self.ON_METADATA_CHECKED_TAGS[key] + xnatLevel
                    savedMetadataItems = self.MODULE.XnatSettingsFile.getTagValues(xnatHost, levelTag)
                    
                    #
                    # If there are no 'savedMetadataItems', we add them.
                    #
                    if len(savedMetadataItems) == 0:
                        if self.defaultSelectedMetadata[key]:
                            defaultSelectedMetadata = self.defaultSelectedMetadata[key][xnatLevel] 
                            tagDict = {levelTag : defaultSelectedMetadata}
                            self.MODULE.XnatSettingsFile.setTagValues(xnatHost, tagDict)


                        
        
        

    def complete(self):
        """
        """
                

        #--------------------
        # Add to frame.
        #--------------------
        self.masterLayout.addStretch()
        self.frame.setLayout(self.masterLayout)
        for key, manager in self.XnatMetadataManagers.iteritems():
            if manager.collapsibles:
                for key in manager.collapsibles:
                    manager.collapsibles[key].show() 
                    manager.collapsibles[key].setChecked(False) 
            self.setWidget(self.frame)

        




    def addSection(self, title, widgetOrLayout):
        """
        """
        self.sectionLabels.append(qt.QLabel('<b>%s</b>'%(title), self))
        self.masterLayout.addWidget(self.sectionLabels[-1])
        self.masterLayout.addSpacing(self.sectionSpacing)

        
        if 'layout' in widgetOrLayout.className().lower():
            self.masterLayout.addLayout(widgetOrLayout)
        else:
            self.masterLayout.addWidget(widgetOrLayout)


        
        
    def addSpacing(self, spacing = 10):
        """ As stated.
        """
        self.masterLayout.addSpacing(spacing) 
        

        

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




    def addFontSizeDropdown(self, title = "Font Size:" ):
        """
        """
        try:
            self.fontDropdowns.append(qt.QComboBox())
            self.fontDropdowns[-1].addItems([str(i) for i in range(8, 21)])
            self.fontDropdowns[-1].setFixedWidth(100)
            self.addSection(title, self.fontDropdowns[-1])

            
        except Exception, e:
            #print self.MODULE.utils.lf(), str(e)
            self.fontDropdowns = []
            self.addFontSizeDropdown(title)
