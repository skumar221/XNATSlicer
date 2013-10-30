from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys


from VariableItemListWidget import *
from CustomEventFilter import *


comment = """
XnatMetadataEtior

TODO:
"""


        
class XnatMetadataEditor(qt.QFrame):

    
    def __init__(self, MODULE, xnatLevel):
        """ Init function.
        """
        self.onMetadataCheckedTag = "ON_METADATA_CHECKED"
        super(XnatMetadataEditor, self).__init__(self)

        self.xnatLevel = xnatLevel
        
        self.MODULE = MODULE
        self.listWidget = VariableItemListWidget()
        self.listWidget.setStyleSheet('margin-top: 0px; margin-bottom: 0px')

        self._layout = qt.QVBoxLayout()
        self._layout.addWidget(self.listWidget)
        self.setLayout(self._layout)

        #--------------------
        # Set the item size
        #--------------------
        self.itemSize = qt.QSize(20,20)

        
        self.setup()

        self.setItemType('label')
        self.update()


        self.customEventFilter = CustomEventFilter()





        

        
        
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



        
    def setItemType(self, itemType):
        """ Allows the user to set the kind of QListWidgetItems to be displayed, 
            either a label or a checkbox, as provided by the 'itemType' argument.

            Refer to here for more information about the flags for setting the
            item type: 
            http://harmattan-dev.nokia.com/docs/library/html/qt4/qt.html#ItemFlag-enum
        """

        #--------------------
        # Record the internal 'currItemType' variable
        #--------------------
        self.currItemType = itemType


        



        #--------------------
        # Set the flags based on the 'self.currItemType' argument.
        #--------------------
        
        #
        # For 'checkBox'...
        #
        if self.currItemType == 'checkbox':
            self.itemFlags = 16 | 32
            
        #
        # For 'label'...
        #           
        elif self.currItemType == 'label':
            self.itemFlags = 1


            
        for i in range(0, self.listWidget.count):
            self.listWidget.item(i).setSizeHint(self.itemSize)
            self.listWidget.item(i).setFlags(self.itemFlags)
            #self.listWidget.item(i).setEnabled(True)
            if self.currItemType == 'checkbox':
                self.listWidget.item(i).setCheckState(0)
               


                

    def update(self):
        """
        """

        print '*******************SUPERTUPDATE'
        self.setItemType(self.currItemType)
        self.listWidget.connect('itemClicked(QListWidgetItem *)', self.onItemClicked)



        #
        # Load and check items from settings file
        #
        #if self.currItemType == 'checkbox':



        if self.currItemType == 'checkbox':
            try:
                xnatHost = self.MODULE.metadataSettings.hostDropdown.currentText
                savedMetadataItems = self.MODULE.settingsFile.getTagValues(xnatHost, self.onMetadataCheckedTag + self.xnatLevel)
                print "AVEASSSSSSSSSSSSSS", savedMetadataItems
                for i in range(0, self.listWidget.count):
                    item = self.listWidget.item(i)
                    if item.flags() == 48 and item.text() in savedMetadataItems:
                        item.setCheckState(2)                
            except Exception, e:
                print "sUPER METADATA EDITOR UPDATE:", str(e)
                return

            



                
                

        


        
    def onItemClicked(self, item):
        """
        """
        #print "item clicked", item.text(), item.flags()

        xnatHost = self.MODULE.metadataSettings.hostDropdown.currentText
        #--------------------
        # If the item is a checkbox
        #--------------------
        if item.flags() == 48:

            savedMetadataItems = self.MODULE.settingsFile.getTagValues(xnatHost, self.onMetadataCheckedTag + self.xnatLevel)
            
            if item.checkState() == 2:
                #print item.text(), "Checked!"

                checkedMetadataItems = []
                for i in range(0, self.listWidget.count):
                    currItem = self.listWidget.item(i)
                    if currItem.flags() == 48 and currItem.checkState() == 2:
                        checkedMetadataItems.append(currItem.text())


                
                
                #
                # Union the two list
                #
                mergedItems = list(set(savedMetadataItems) | set(checkedMetadataItems))

                
                tagDict = {self.onMetadataCheckedTag + self.xnatLevel : mergedItems}
                self.MODULE.settingsFile.saveCustomPropertiesToHost(xnatHost, tagDict)



                
            if item.checkState() == 0:
                #
                # Union the two list
                #
                differenceItems = list(set(savedMetadataItems) - set([item.text()]))
                #print differenceItems
                
                tagDict = {self.onMetadataCheckedTag + self.xnatLevel : differenceItems}
                self.MODULE.settingsFile.saveCustomPropertiesToHost(xnatHost, tagDict)  


                

        
class XnatDefaultMetadataEditor(XnatMetadataEditor):

    
    def __init__(self, MODULE, xnatLevel):
        """ Init function.
        """

        super(XnatDefaultMetadataEditor, self).__init__(MODULE, xnatLevel)


    
    def setup(self):
        """
        """
        self.listWidget.addItemsByType([tag for tag in self.MODULE.GLOBALS.DEFAULT_XNAT_METADATA[self.xnatLevel]])



        
    def update(self):
        """
        """

        print '*******************DEFAULTUPDATE'
        super(XnatDefaultMetadataEditor, self).update()

            



                
        
        
class XnatCustomMetadataEditor(XnatMetadataEditor):

    
    def __init__(self, MODULE, xnatLevel):
        """ Init function.
        """
        buttonHeight = 25
        buttonWidth = 50
        lineWidth = 150


        #self.customButtonGroup = qt.QButtonGroup()
        #self.customButtonGroup.connect('buttonClicked(QAbstractButton*)', self.customClicked)
        
        self.lineEdit = qt.QLineEdit()
        self.lineEdit.setFixedHeight(buttonHeight)
        self.lineEdit.setFixedWidth(lineWidth)
        
        
        
        self.addButton = qt.QPushButton('Add')
        self.addButton.setFixedHeight(buttonHeight)
        self.addButton.setFixedWidth(buttonWidth)
        self.addButton.connect('clicked()', self.onAddButtonClicked)


        
        self.deleteButton = qt.QPushButton('Remove')
        self.deleteButton.setFixedHeight(buttonHeight)
        self.deleteButton.setFixedWidth(buttonWidth)
        self.deleteButton.connect('clicked()', self.onDeleteButtonClicked)
        self.deleteButton.setEnabled(False)


        #self.customButtonGroup.addButton(self.addButton)
        #self.customButtonGroup.addButton(self.deleteButton)

        self.lineLayout = qt.QHBoxLayout()


       
        
        
        super(XnatCustomMetadataEditor, self).__init__(MODULE, xnatLevel)



        self.lineEdit.installEventFilter(self.customEventFilter)
        self.customEventFilter.addEventCallback(qt.QEvent.FocusIn, self.onLineEditFocused)


        

    def setup(self):
        """
        """
        self.lineLayout.addWidget(self.lineEdit)
        self.lineLayout.addWidget(self.addButton)
        self.lineLayout.addWidget(self.deleteButton)
        self._layout.addLayout(self.lineLayout)




    def customButtonClicked(self, button):
        """
        """
        #print "BUTTON: ", self.xnatLevel
        
        
        

    def onDeleteButtonClicked(self):
        """
        """

        #print "DELETE"
        xnatHost = self.MODULE.metadataSettings.hostDropdown.currentText
        customMetadataItems = self.MODULE.settingsFile.getTagValues(xnatHost, self.MODULE.GLOBALS.makeCustomMetadataTag(self.xnatLevel))


        updatedMetadataItems = []
        for item in customMetadataItems:
            currItem = self.listWidget.currentItem()

            if item.lower().strip() == currItem.text().lower().strip():
                self.listWidget.removeItemWidget(self.listWidget.currentItem())
            else:
                updatedMetadataItems.append(item)

        
        
        tagDict = {self.MODULE.GLOBALS.makeCustomMetadataTag(self.xnatLevel) : updatedMetadataItems}
        self.MODULE.settingsFile.saveCustomPropertiesToHost(xnatHost, tagDict)


        self.update()


        
    def update(self):
        """
        """

        print '*******************CUSTOMTUPDATE'
        
        try:
            xnatHost = self.MODULE.metadataSettings.hostDropdown.currentText
            customMetadataItems = self.MODULE.settingsFile.getTagValues(xnatHost, self.MODULE.GLOBALS.makeCustomMetadataTag(self.xnatLevel))
            #print "UPDATE", customMetadataItems
            self.listWidget.clear()
            self.listWidget.addItems(customMetadataItems)
            
        except Exception, e:
            print self.MODULE.utils.lf(), str(e)
            

        super(XnatCustomMetadataEditor, self).update()
       
        if self.currItemType == 'label':
            self.itemFlags = 1 | 32

        for i in range(0, self.listWidget.count):
            self.listWidget.item(i).setFlags(self.itemFlags)
            #print "FLAGS", self.listWidget.item(i).flags()
            #self.listWidget.item(i).setCheckState(0)
            

            
            
    def onAddButtonClicked(self):
        """
        """

        
        lineText = self.lineEdit.text
        if len(lineText.strip()) == 0:
            return

        xnatHost = self.MODULE.metadataSettings.hostDropdown.currentText

        customMetadataItems = self.MODULE.settingsFile.getTagValues(xnatHost, self.MODULE.GLOBALS.makeCustomMetadataTag(self.xnatLevel))

        tagDict = {self.MODULE.GLOBALS.makeCustomMetadataTag(self.xnatLevel) : [lineText] + customMetadataItems}
        self.MODULE.settingsFile.saveCustomPropertiesToHost(xnatHost, tagDict)

        self.lineEdit.clear()


        self.MODULE.metadataSettings.hostDropdown.currentText
        self.update()


        

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


            

    def onItemClicked(self, listWidgetItem):
        """
        """


        super(XnatCustomMetadataEditor, self).onItemClicked(listWidgetItem)
        self.deleteButton.setEnabled(True)
        self.addButton.setEnabled(False)
        self.lineEdit.clear()



    def onLineEditFocused(self, *args):
        """
        """
        if self.listWidget.currentItem():
            self.listWidget.currentItem().setSelected(False)
        self.addButton.setEnabled(True)
        self.deleteButton.setEnabled(False)
        


