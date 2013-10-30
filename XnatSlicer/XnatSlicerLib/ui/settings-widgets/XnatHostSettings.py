from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys

from XnatSettings import *



comment = """
XnatHostSettings is a widget that fits within the XnatSettingsPopup
that allows the user to edit the hosts that are stored in XnatSettings.
As a result, this class also communicates directly with XnatSettings.

TODO:
"""


        
class XnatHostSettings(XnatSettings):
    """ Embedded within the settings popup.  Manages hosts.
    """

  
    def __init__(self, title, MODULE):
        """ Init function.
        """
        
        #--------------------
        # Call parent init
        #--------------------
        super(XnatHostSettings, self).__init__(title, MODULE)
        


        #
        # Add section Label
        #
        bLabel = qt.QLabel('<b>Manage Hosts</b>')
        self.masterLayout.addWidget(bLabel)
        self.masterLayout.addSpacing(8)

        
        
        #--------------------
        # Current popup opened by user
        #--------------------
        self.currModal = None
        
        
        
        #--------------------
        # Host lister
        #--------------------      
        self.hostTable = HostTable(self.MODULE, clickCallback = self.hostRowClicked)
        
        
        #--------------------
        # Shared popup objects
        #--------------------
        self.urlLine, self.nameLine, self.setDefault, self.usernameLine = makeSharedHostModalObjects(self)
        
        
        
        #--------------------
        # Buttons
        #--------------------
        self.addButton, self.editButton, self.deleteButton = makeButtons(self)
        self.addButton.connect('clicked()', self.showAddHostModal)     
        self.editButton.connect('clicked()', self.showEditHostModal) 
        self.deleteButton.connect('clicked()', self.showDeleteHostModal)  
        

        
        #--------------------
        # Frame for setup window
        #--------------------
        self.makeFrame()
        
        

    
        #--------------------
        # Layout for entire frame
        #--------------------
        self.masterLayout.addStretch()
        self.frame.setLayout(self.masterLayout)
        self.setWidget(self.frame)
        self.frame.setFixedWidth(520)

        
        #--------------------
        # Load hosts into host list
        #--------------------
        self.loadHosts()

        print "HOST SETTNS"




        
        
        
    def hostRowClicked(self):
        """ Callbcak for when a user clicks on a given item
        within the host editor.
        """
        self.setButtonStates(self.hostTable.currentRowItems['name'])
        
        
        
        
    def setButtonStates(self, nameString):   
        """ Enables / Disables button based upon the editable
        quality of the host.  Some hosts cannot be modified.
        """
        print nameString, self.MODULE.settingsFile.isModifiable(nameString) 
        if self.MODULE.settingsFile.isModifiable(nameString):
            self.deleteButton.setEnabled(True)
            self.editButton.setEnabled(True)
        else:
            self.deleteButton.setEnabled(False)
            self.editButton.setEnabled(True)



        
    def loadHosts(self):     
        """ Communicates with XnatSettings to load the stored hosts.
        """
        
        #--------------------
        # Get host dictionary from XnatSettings
        #--------------------
        hostDictionary = self.MODULE.settingsFile.getHostNameAddressDictionary()  
        print "HOST DICT", hostDictionary
        
        
        #--------------------
        # Empty hostList in the editor.
        #--------------------
        self.hostTable.clear()
        
        
        
        #--------------------
        # Iterate through dictionary and apply text to the hostList
        #--------------------
        for name in hostDictionary:
            #
            # Apply style if default
            #
            setModfiable = [True, True]
            if not self.MODULE.settingsFile.isModifiable(name):
                setModfiable = [False, False]
            #
            # Add name and URL to host list
            #
            self.hostTable.addNameAndUrl(name, hostDictionary[name], setModfiable)

            #
            # Get curr username
            #
            currName = self.MODULE.settingsFile.getCurrUsername(name)
            #
            # If there's a username, add it....
            #
            if len(currName) > 0:
                self.hostTable.addUsername(currName) 




    
    def rewriteHost(self):
        """ As stated.  Calls on the internal "writeHost" function.
        """
        self.MODULE.settingsFile.deleteHost(self.prevName)
        self.prevName = None
        self.writeHost()


    
    
    def deleteHost(self):
        """ As described
        """
        
        #--------------------
        # Delete the selected host by
        # applying the text to the settings, and removing from there.
        #--------------------
        hostStr = self.hostTable.currentRowItems
        deleted = self.MODULE.settingsFile.deleteHost(hostStr['name'])
        

        print "DELETED?", deleted
        #--------------------
        # Reload everything
        #--------------------
        if deleted: 
            self.loadHosts()
            self.MODULE.XnatLoginMenu.loadDefaultHost()


            
        #--------------------
        # Close popup
        #--------------------
        self.currModal.close()
        self.currModal = None


    
    
    def writeHost(self):
        """ As described.  See below for details.
        """

        #--------------------
        # Check if the nameLine is part of the defaut set
        #--------------------
        modifiable = self.MODULE.settingsFile.isModifiable(self.nameLine.text.strip(""))



        #--------------------
        # Determine if enetered host was set to default
        #--------------------
        modStr = str(modifiable)
        checkStr = str(self.setDefault.isChecked())
        
        
        
        #--------------------
        # Save Host
        #--------------------
        self.MODULE.settingsFile.saveHost(self.nameLine.text, self.urlLine.text, isModifiable = modifiable, isDefault = self.setDefault.isChecked())

        

        #--------------------
        # Set default if checkbox is check
        #--------------------
        if self.setDefault.isChecked():
            self.MODULE.settingsFile.setDefault(self.nameLine.text)   



        #--------------------
        # Set default username
        #--------------------
        if self.usernameLine.text != "":
            self.MODULE.settingsFile.setCurrUsername(self.nameLine.text, self.usernameLine.text)



        #--------------------
        # Reload hosts
        #--------------------
        self.MODULE.XnatLoginMenu.loadDefaultHost()
        self.loadHosts() 



        #--------------------
        # Close popup
        #--------------------
        self.currModal.close()
        self.currModal = None




    
    def showEditHostModal(self):
        """ As described.
        """
        self.currModal = makeEditHostModal(self)
        self.currModal.setWindowModality(2)
        self.currModal.show()  
        
        
        
        
    def showDeleteHostModal(self, message=None):
        """ As described.
        """
        self.currModal = makeDeleteHostModal(self)
        self.currModal.show()   
            
            
            
            
    def showAddHostModal(self):  
        """ As described.
        """ 
        self.currModal = makeAddHostModal(self)
        self.currModal.show()


    


    def makeFrame(self):
        """ As described.
        """

        
        #--------------------
        # Layout for top part of frame (host list)
        #--------------------
        self.masterLayout.addWidget(self.hostTable)
        
        
        
        #--------------------
        # Layout for bottom part of frame (buttons)
        #--------------------
        buttonLayout = qt.QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.addButton)
        buttonLayout.addWidget(self.editButton)
        buttonLayout.addWidget(self.deleteButton)   
        self.masterLayout.addLayout(buttonLayout)


        

                  
class HostTable(qt.QTableWidget):
    """ Inherits qt.QTextEdit to list the hosts in the 
        SettingsModal
    """

    def __init__(self, MODULE, clickCallback = None): 
        """ Init function.
        """
        qt.QTableWidget.__init__(self)
        self.MODULE = MODULE
        self.clickCallback = clickCallback
        self.setup()
        



        
    def setup(self):
        """
        """
        self.columnNames = ['Name', 'Url', 'Stored Login']
        self.setSelectionBehavior(1)
        self.setColumnCount(len(self.columnNames))
        self.setHorizontalHeaderLabels(self.columnNames)
        self.setColumnWidth(0, 150)
        self.setColumnWidth(1, 200)
        self.setColumnWidth(2, 150)
        
        self.setShowGrid(False)
        self.verticalHeader().hide()

        self.currentRowNumber = None
        self.currentRowItems = None      

        self.trackedItems = {}
        
        self.connect('currentCellChanged(int, int, int, int)', self.onCurrentCellChanged)



    def printAll(self):
        """
        """
        print "PRINT ALL", self.rowCount, self.columnCount 


        

    def getRowItems(self, rowNumber = None):
        """
        """
        if not rowNumber:
            rowNumber = self.currentRowNumber


            
        #--------------------
        # This happens after a clear and 
        # reinstantiation of rows.
        #--------------------
        if rowNumber == -1:
            rowNumber = 0



        #--------------------
        # This happens after a clear and 
        # reinstantiation of rows.
        #--------------------
        if self.trackedItems[rowNumber]:
            returner = {}
            for key, item in self.trackedItems[rowNumber].iteritems():
                returner[key] = item.text()
                
            return returner

    

    def clear(self):
        """ Clears the table of all values, then reapplies
            then reapplies the column headers.
        """
        #--------------------
        # We have to delete self.trackedItems
        # because of a very bizarre memory management
        # polciy set forth by QTableWidget
        #--------------------
        del self.trackedItems
        self.trackedItems = {}
        self.setRowCount(0)
        #self.setup()
        
            
    

            
    def onCurrentCellChanged(self, rowNum, colNum, oldRow, oldCol):
        """
        """
        self.currentRowNumber = rowNum
        self.currentRowItems = self.getRowItems()
        #print "onCurrentCellChanged", self.currentRowItems
        self.clickCallback()


        

        
    def getColumn(self, colName):
        """ Returns the column index if it's name matches the
            'colName' argument.
        """
        for i in range(0, self.columnCount):
            if self.horizontalHeaderItem(i).text().lower() == colName.lower():
                return i


            

    def addNameAndUrl(self, name, url, setModfiable = [True, True]):
        """ Adds a name and url to the table by adding a 
            new row.
        """

        #--------------------
        # 
        #--------------------
        flags = []
        for state in setModfiable:
            if state:
                flags.append(None)
            else:
                flags.append(1)
        
        nameItem = qt.QTableWidgetItem(name)
        if flags[0]:
            nameItem.setFlags(flags[0])
        
        urlItem = qt.QTableWidgetItem(url)
        if flags[1]:
            urlItem.setFlags(flags[1])
        
        usernameItem = qt.QTableWidgetItem('No username stored.')

        self.setSortingEnabled(False)
        self.setRowCount(self.rowCount + 1)
    


        #--------------------
        # 
        #--------------------
        self.trackedItems[self.rowCount-1] = {}
        self.trackedItems[self.rowCount-1]['name'] = nameItem
        self.trackedItems[self.rowCount-1]['url'] = urlItem
        self.trackedItems[self.rowCount-1]['stored login'] = usernameItem

        for key, item in self.trackedItems[self.rowCount-1].iteritems():
            item.setFont(self.MODULE.GLOBALS.LABEL_FONT)

        
        self.setItem(self.rowCount-1, self.getColumn('name'), nameItem)
        self.setItem(self.rowCount-1, self.getColumn('url'), urlItem)
        self.setItem(self.rowCount-1, self.getColumn('stored login'), usernameItem)
 

        self.setSortingEnabled(False)
        print self.trackedItems
        
        
        
    def applyIsDefaultStyle(self):
        """ Stylistic display.
        """
        #self.setFontItalic(True)
        #self.setTextColor(qt.QColor(0,0,225))
        #self.insertPlainText("default")


        
        
    def addUsername(self, username):
        """ Stylistic adding of username.
        """
        #self.setFontItalic(True)
        #self.setTextColor(qt.QColor(20,20,20))
        #self.insertPlainText("\t(stored login): " + username + "\n")
        self.trackedItems[self.rowCount-1]['stored login'].setText(username)
        self.setItem(self.rowCount-1, self.getColumn('stored login'), self.trackedItems[self.rowCount-1]['stored login'])







def makeAddHostModal(hostEditor):
    """ As stated. 
    """
    
    #--------------------
    # Clear shared object lines
    #--------------------
    hostEditor.nameLine.clear()
    hostEditor.urlLine.clear()



    #--------------------    
    # Buttons
    #--------------------
    saveButton = qt.QPushButton("OK")
    cancelButton = qt.QPushButton("Cancel")



    #--------------------
    # Create for line editors
    #--------------------
    currLayout = qt.QFormLayout()
    currLayout.addRow("Name:", hostEditor.nameLine)
    currLayout.addRow("URL:", hostEditor.urlLine)
    currLayout.addRow(hostEditor.setDefault)



    #--------------------
    # Create layout for buttons
    #--------------------
    buttonLayout = qt.QHBoxLayout()
    buttonLayout.addStretch(1)
    buttonLayout.addWidget(cancelButton)
    buttonLayout.addWidget(saveButton)



    #--------------------
    # Combine both layouts
    #--------------------
    masterForm = qt.QFormLayout()    
    masterForm.addRow(currLayout)
    masterForm.addRow(buttonLayout)



    #--------------------
    # Make window
    #--------------------
    addHostModal = qt.QDialog(hostEditor.addButton)
    addHostModal.setWindowTitle("Add Host")
    addHostModal.setFixedWidth(300)
    addHostModal.setLayout(masterForm)
    addHostModal.setWindowModality(2)



    #--------------------
    # Clear previous host
    #--------------------
    hostEditor.prevName = None

    

    #--------------------
    # Button Connectors
    #--------------------
    cancelButton.connect("clicked()", addHostModal.close)
    saveButton.connect("clicked()", hostEditor.writeHost)   

    
    return addHostModal




def makeEditHostModal(hostEditor):
    """ As stated.
    """

    #--------------------
    # Get selected strings from host list.
    #--------------------
    selHost = hostEditor.hostTable.currentRowItems


    
    #--------------------
    # Populate the line edits from selecting strings.
    #--------------------
    hostEditor.nameLine.setText(selHost['name'])
    hostEditor.urlLine.setText(selHost['url'])



    #--------------------
    # Prevent editing of default host. 
    #--------------------
    if not hostEditor.MODULE.settingsFile.isModifiable(selHost['name']):
        hostEditor.nameLine.setReadOnly(True)
        hostEditor.nameLine.setFont(hostEditor.MODULE.GLOBALS.LABEL_FONT_ITALIC)
        hostEditor.nameLine.setEnabled(False)
        hostEditor.urlLine.setReadOnly(True)
        hostEditor.urlLine.setFont(hostEditor.MODULE.GLOBALS.LABEL_FONT_ITALIC)
        hostEditor.urlLine.setEnabled(False)


        
    #--------------------
    # Otherwise, go ahead.
    #--------------------
    else:
        hostEditor.nameLine.setEnabled(True)
        hostEditor.urlLine.setEnabled(True)



    #--------------------
    # Buttons.
    #--------------------
    cancelButton = qt.QPushButton("Cancel")   
    saveButton = qt.QPushButton("OK")



    #--------------------
    # Layouts.
    #--------------------
    currLayout = qt.QFormLayout()
    hostEditor.prevName = hostEditor.nameLine.text
    currLayout.addRow("Edit Name:", hostEditor.nameLine)
    currLayout.addRow("Edit URL:", hostEditor.urlLine)



    #--------------------
    # Default checkbox if default.
    #--------------------
    if hostEditor.MODULE.settingsFile.isDefault(hostEditor.nameLine.text):
        hostEditor.setDefault.setCheckState(2)



    #--------------------
    # Labels.
    #--------------------
    spaceLabel = qt.QLabel("")
    unmLabel = qt.QLabel("Stored Username:")


    
    #--------------------
    # Layouts.
    #--------------------
    currLayout.addRow(hostEditor.setDefault)
    hostEditor.usernameLine.setText(hostEditor.MODULE.settingsFile.getCurrUsername(hostEditor.nameLine.text))
    currLayout.addRow(spaceLabel)
    currLayout.addRow(unmLabel)
    currLayout.addRow(hostEditor.usernameLine)
    
    buttonLayout = qt.QHBoxLayout()
    buttonLayout.addStretch(1)
    buttonLayout.addWidget(cancelButton)
    buttonLayout.addWidget(saveButton)
    
    masterForm = qt.QFormLayout()    
    masterForm.addRow(currLayout)
    masterForm.addRow(buttonLayout)


    
    #--------------------
    # The modal.
    #--------------------
    editHostModal = qt.QDialog(hostEditor.addButton)
    editHostModal.setWindowTitle("Edit Host")
    editHostModal.setFixedWidth(300)
    editHostModal.setLayout(masterForm)
    editHostModal.setWindowModality(2)


    
    #--------------------
    # Button Connectors
    #--------------------
    cancelButton.connect("clicked()", editHostModal.close)
    saveButton.connect("clicked()", hostEditor.rewriteHost) 

    return editHostModal




def makeDeleteHostModal(hostEditor):
    """ As stated.
    """

    #--------------------
    # get selected strings from host list
    #--------------------
    selHost = hostEditor.hostTable.currentRowItems


    
    #--------------------
    # Buttons
    #--------------------
    okButton = qt.QPushButton("OK")
    cancelButton = qt.QPushButton("Cancel")



    #--------------------
    # Labels
    #--------------------
    messageLabel = qt.QTextEdit()
    messageLabel.setReadOnly(True)
    messageLabel.insertPlainText("Are you sure you want to delete the host ") 
    messageLabel.setFontItalic(True)
    messageLabel.setFontWeight(100)    
    messageLabel.insertPlainText(selHost['name'])

    messageLabel.setFontWeight(0)   
    messageLabel.insertPlainText(" ?")
    messageLabel.setFixedHeight(40)
    messageLabel.setFrameShape(0)


    
    #--------------------
    # Layouts
    #--------------------
    currLayout = qt.QVBoxLayout()
    currLayout.addWidget(messageLabel)
    currLayout.addStretch(1)
    
    buttonLayout = qt.QHBoxLayout()
    buttonLayout.addStretch(1)
    buttonLayout.addWidget(cancelButton)
    buttonLayout.addWidget(okButton)
    
    masterForm = qt.QFormLayout()    
    masterForm.addRow(currLayout)
    masterForm.addRow(buttonLayout)



    #--------------------
    # Window
    #--------------------
    deleteHostModal = qt.QDialog(hostEditor.addButton)
    deleteHostModal.setWindowTitle("Delete Host")
    deleteHostModal.setLayout(masterForm)
    deleteHostModal.setWindowModality(2)



    #--------------------
    # Button Connectors
    #--------------------
    cancelButton.connect("clicked()", deleteHostModal.close)
    okButton.connect("clicked()", hostEditor.deleteHost) 
    
    return deleteHostModal

    



def makeButtons(hostEditor):
    """ As described.
    """
    addButton = hostEditor.MODULE.utils.generateButton(iconOrLabel = 'Add', 
                                                                               toolTip = "Need tool-tip.", 
                                                                               font = hostEditor.MODULE.GLOBALS.LABEL_FONT,
                                                                               size = qt.QSize(90, 20), 
                                                                               enabled = True)
    editButton = hostEditor.MODULE.utils.generateButton(iconOrLabel = 'Edit', 
                                                                               toolTip = "Need tool-tip.", 
                                                                               font = hostEditor.MODULE.GLOBALS.LABEL_FONT,
                                                                               size = qt.QSize(90, 20), 
                                                                               enabled = True)
    deleteButton = hostEditor.MODULE.utils.generateButton(iconOrLabel = 'Delete', 
                                                                               toolTip = "Need tool-tip.", 
                                                                               font = hostEditor.MODULE.GLOBALS.LABEL_FONT,
                                                                               size = qt.QSize(90, 20), 
                                                                               enabled = True)
    
    deleteButton.setEnabled(False)
    editButton.setEnabled(False)  

    return addButton, editButton, deleteButton




def makeSharedHostModalObjects(hostEditor):
    """ Makes commonly shared UI objects for the Add, Edit popups.
    """
    urlLine = qt.QLineEdit()
    nameLine = qt.QLineEdit()
    setDefault = qt.QCheckBox("Set As Default?")
    usernameLine = qt.QLineEdit()
        
    urlLine.setEnabled(True)
    nameLine.setEnabled(True) 
    usernameLine.setFont(hostEditor.MODULE.GLOBALS.LABEL_FONT_ITALIC) 

    return urlLine, nameLine, setDefault, usernameLine 
