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


        self.XnatMetadataManager = XnatMetadataManager(self.MODULE)

        

    def addMetadataManager(self):
        """
        """
        
        self.masterLayout.addWidget(self.XnatMetadataManager)

        

        #--------------------
        # Add to frame.
        #--------------------
        self.masterLayout.addStretch()
        self.frame.setLayout(self.masterLayout)
        if self.XnatMetadataManager.collapsibles:
            for key in self.XnatMetadataManager.collapsibles:
                self.XnatMetadataManager.collapsibles[key].show() 
                self.XnatMetadataManager.collapsibles[key].setChecked(False) 
        self.setWidget(self.frame)

        

        
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

