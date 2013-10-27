from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys


from VariableItemListWidget import *


comment = """
XnatMetadataEtior

TODO:
"""



                

class XnatMetadataEditor(qt.QFrame):

    
    def __init__(self, MODULE, xnatLevel):
        """ Init function.
        """

        super(XnatMetadataEditor, self).__init__(self)

        self.xnatLevel = xnatLevel
        
        self.MODULE = MODULE
        self.listWidget = VariableItemListWidget()
        self.listWidget.setStyleSheet('margin-top: 0px; margin-bottom: 0px')

        self._layout = qt.QVBoxLayout()
        self._layout.addWidget(self.listWidget)
        self.setLayout(self._layout)
        
        self.setup()

        



        
        
    @property
    def count(self):
        """
        """
        return self.listWidget.count


    def clear(self):
        """
        """
        self.listWidget.clear()
    

    def item(self, index):
        """
        """
        return self.listWidget.item(index)


    def addItems(self, items):
        self.listWidget.addItems(items)


    
                

        
class XnatDefaultMetadataEditor(XnatMetadataEditor):

    
    def __init__(self, MODULE, xnatLevel):
        """ Init function.
        """

        super(XnatDefaultMetadataEditor, self).__init__(MODULE, xnatLevel)


    
    def setup(self):
        """
        """
        self.listWidget.addItemsByType([tag for tag in self.MODULE.GLOBALS.DEFAULT_XNAT_METADATA[self.xnatLevel]])



        
        
class XnatCustomMetadataEditor(XnatMetadataEditor):

    
    def __init__(self, MODULE, xnatLevel):
        """ Init function.
        """
        buttonHeight = 25
        buttonWidth = 50
        lineWidth = 150


        self.lineEdit = qt.QLineEdit()
        self.lineEdit.setFixedHeight(buttonHeight)
        self.lineEdit.setFixedWidth(lineWidth)
        
        self.addButton = qt.QPushButton('Add')
        self.addButton.setFixedHeight(buttonHeight)
        self.addButton.setFixedWidth(buttonWidth)

        self.deleteButton = qt.QPushButton('Remove')
        self.deleteButton.setFixedHeight(buttonHeight)
        self.deleteButton.setFixedWidth(buttonWidth)


        self.lineLayout = qt.QHBoxLayout()

        
        super(XnatCustomMetadataEditor, self).__init__(MODULE, xnatLevel)


    def setup(self):
        """
        """
        self.lineLayout.addWidget(self.lineEdit)
        self.lineLayout.addWidget(self.addButton)
        self.lineLayout.addWidget(self.deleteButton)
        self._layout.addLayout(self.lineLayout)



    def setEditLineVisible(self, visible):
        """
        """

        try:
            self._layout.removeItem(self.lineLayout)
            self.lineEdit.hide()
            self.addButton.hide()
            self.deleteButton.hide()
            self._layout.update()
        except Exception, e:
            pass
            
        if visible:
            self._layout.addLayout(self.lineLayout)
            self.lineEdit.show()
            self.addButton.show()
            self.deleteButton.show()
            self._layout.update()            

