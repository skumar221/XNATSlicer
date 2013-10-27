from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys

from AnimatedCollapsible import *
from VariableItemListWidget import *


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

