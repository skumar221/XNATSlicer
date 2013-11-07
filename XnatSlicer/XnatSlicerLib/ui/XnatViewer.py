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
        


        #self.settingsButton = self.MODULE.utils.makeSettingsButton(self.MODULE.XnatTreeViewSettings)



        
        self.noSearchResultsFound = qt.QLabel("<i>No results found.</i>", self)
        self.noSearchResultsFound.setStyleSheet('color: gray; margin-left: 150px; text-align: center')

        
        self.stackedLayout = qt.QStackedLayout(self)
        self.stackedLayout.addWidget(self.noSearchResultsFound)
        self.stackedLayout.addWidget(self.MODULE.XnatView)
        self.stackedLayout.setCurrentIndex(1)
        self.stackedLayout.setStackingMode(1)

        self.stackedWidget = qt.QWidget(self)
        self.stackedWidget.setLayout(self.stackedLayout)

        
        #self.mainWidget = qt.QWidget(self)
        self.viewerLayout = qt.QGridLayout()  
        self.viewerLayout.addWidget(self.MODULE.XnatSearchBar, 0, 0, 1, 1)
        #self.viewerLayout.addWidget(self.settingsButton, 0, 1, 1, 1, 2 | 32)
        #self.viewerLayout.addWidget(self.MODULE.XnatView, 2, 0)
        
        self.viewerLayout.addWidget(self.stackedWidget, 2, 0)
        self.viewerLayout.addLayout(self.MODULE.XnatButtons.loadSaveButtonLayout, 2, 1)
        #self.viewerLayout.setContentsMargins(10,0,0,0)

       
        self.setLayout(self.viewerLayout)




    def setNoResultsWidgetVisible(self, visibile):
        """
        """
        if visibile:
            self.stackedLayout.setCurrentIndex(0)
        else:
            self.stackedLayout.setCurrentIndex(1) 
        


        
