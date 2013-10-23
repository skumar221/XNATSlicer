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


        
        #--------------------
        # The title/label
        #--------------------
        self.label = qt.QLabel(title)


        
        #--------------------
        # Layout for entire frame
        #--------------------
        self.frame = qt.QFrame()
        self.frame.setStyleSheet("background: rgb(255,255,255)")


        self.masterLayout = qt.QVBoxLayout()
        
        #--------------------
        # Set frame to the 'widget' (part of qt.QScrollArea)
        #--------------------
        #self.setWidget(self.frame)
       
        self.spacer = qt.QLabel(' 000')
        

    def addSpacing(self):
        """ As stated.
        """
        self.masterLayout.addSpacing(15) 
        

        
        
    @property
    def title(self):
        return self.label.text



