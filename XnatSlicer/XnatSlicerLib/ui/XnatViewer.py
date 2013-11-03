from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil
import csv




comment = """

"""




class XnatViewer(qt.QWidget):

    def __init__(self, MODULE = None):
        """ Sets parent and MODULE parameters.
        """

        super(XnatViewer, self).__init__(self)
        self.MODULE = MODULE
        


        self.settingsButton = self.MODULE.utils.makeSettingsButton(self.MODULE.treeViewSettings)
        
        
        self.viewerLayout = qt.QGridLayout()  
        self.viewerLayout.addWidget(self.MODULE.XnatSearchBar, 0, 0, 1, 1)
        self.viewerLayout.addWidget(self.settingsButton, 0, 1, 1, 1, 2 | 32)
        self.viewerLayout.addWidget(self.MODULE.XnatView, 2, 0)
        self.viewerLayout.addLayout(self.MODULE.XnatButtons.loadSaveButtonLayout, 2, 1)
        #self.viewerLayout.setContentsMargins(10,0,0,0)

       
        self.setLayout(self.viewerLayout)


        
