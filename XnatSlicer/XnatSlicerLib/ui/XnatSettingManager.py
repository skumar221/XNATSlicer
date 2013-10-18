from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys



comment = """
XnatSettingManager 

TODO:
"""


        
class XnatSettingManager(object):
    """ 
    """

    def __init__(self, title, MODULE):
        """ Init function.
        """
      
        self.MODULE = MODULE
        

        
        #--------------------
        # The title/label
        #--------------------
        self.label = qt.QLabel(title)


        
        #--------------------
        # Layout for entire frame
        #--------------------
        self.frame = qt.QFrame()
        self.frame.setStyleSheet("QWidget { background: rgb(255,255,255)}")

        

        #--------------------
        # The title/label
        #--------------------
        self.masterLayout = qt.QVBoxLayout()
        self.masterLayout.addWidget(self.label)
        self.addSpacing()
       

        

    def addSpacing(self):
        """ As stated.
        """
        self.masterLayout.addSpacing(15) 
        

        
        
    @property
    def title(self):
        return self.label.text



